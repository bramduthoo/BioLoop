"""Seed the legacy internal workbook (BioMobi_Biomass_RevA.xlsx) into BioMobi.

Phase 2 of the database build plan. Only the `Template_biomass` sheet is ingested:
the `Streams` / `Thoughts` / `Sheet1` sheets were reviewed and dropped, and manure,
OFMSW and wood are out of scope (see database/hub.md).

WHAT LOADS IS NOT THIS SCRIPT'S DECISION. Every stream and every source must be
marked `include` / `exclude` by a human in the manifests under database/crosswalks/.
The script refuses to run while any DECISION cell is blank.

Idempotency -- "wipe my own work, then redo it". Every source row this loader
creates carries the `xls-` prefix, which is its ownership namespace. Each run first
deletes the fact rows belonging to those sources, then reloads from the workbook,
all inside one transaction. Re-running converges: flipping a DECISION to `exclude`
removes the corresponding rows rather than orphaning them. Nothing outside the
`xls-` namespace is ever touched.

Usage:
    python load_biomobi_excel.py --emit-manifests   # regenerate the review CSVs
    python load_biomobi_excel.py --dry-run          # parse + validate, touch nothing
    python load_biomobi_excel.py                    # load into the local stack
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
import psycopg

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
XLSX = REPO / "data" / "raw" / "BioMobi_Biomass_RevA.xlsx"
CROSSWALKS = REPO / "crosswalks"
SHEET = "Template_biomass"

# The local Supabase stack. The live project is never a default target.
LOCAL_DSN = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

# The workbook itself, recorded so every derived source has a documented parent.
WORKBOOK_KEY = "xls-biomobi-revA"
NAMESPACE = "xls-"
TRANSCRIPTION_NOTE = (
    "Transcribed from BioMobi_Biomass_RevA.xlsx (legacy internal workbook). "
    "Secondhand and unverified against the original publication."
)

# --- reference vocabulary -----------------------------------------------------
# Seeded to exactly what this workbook needs, no speculative extras.
UNITS = {
    "%": "percent",
    "g/kg": "grams per kilogram",
    "mg/L": "milligrams per litre",
    "cm": "centimetre",
    "kg/m3": "kilograms per cubic metre",
    "MJ/kg": "megajoules per kilogram",
    "NL/kg": "normal litres per kilogram",
    "L/kg": "litres per kilogram",
    "pH": "pH units (dimensionless)",
    "n.a.": "dimensionless / not applicable",
    "unknown": "Unit was not recorded by the source. Not an assumption of any unit.",
}
BASES = {
    "dry": "Dry matter basis (dry solids / db).",
    "as_received": "As received / fresh basis.",
    "vs": "Per unit of volatile solids.",
    "unknown": "Basis was not recorded by the source. Not an assumption of fresh or dry.",
    "not_applicable": "Basis does not apply (e.g. pH, physical state).",
}

# The workbook's `Unit` column conflates unit with basis; the schema keeps them
# apart and forbids compound units, so every spelling is split explicitly here.
UNIT_SPLIT = {
    "%DS": ("%", "dry"),
    "% (db)": ("%", "dry"),
    "% DS": ("%", "dry"),
    "g/kg DS": ("g/kg", "dry"),
    "%": ("%", "unknown"),        # bare -- basis genuinely never recorded
    "g/kg": ("g/kg", "unknown"),  # bare -- idem
    "NL/kg VS": ("NL/kg", "vs"),
    "L/kg VS": ("L/kg", "vs"),
    "mg/L": ("mg/L", "as_received"),
    "cm": ("cm", "as_received"),
    "kg/m3": ("kg/m3", "as_received"),
    "MJ/kg": ("MJ/kg", "as_received"),
    "pH": ("pH", "not_applicable"),
    # An explicit 'n/a' or '-' means the author judged the unit inapplicable.
    "n/a": ("n.a.", "not_applicable"),
    "-": ("n.a.", "not_applicable"),
    # A BLANK cell means nobody recorded one. That is not the same claim, and
    # collapsing the two would assert something the source never said.
    None: ("unknown", "unknown"),
    "": ("unknown", "unknown"),
}

PHYSICAL_PARAMS = {
    "State", "Particle size", "Bulk density", "Net Calorific Value",
    "DS", "TS", "Total solids", "TSS", "FS", "FSS", "VS", "Volatile solids", "VM",
}
# Spelling variants of one analyte. Anything not listed keeps its own code --
# `Crude protein`, `VM`, `TKN`, `sCOD` etc. are deliberately NOT merged.
COLLAPSE = {
    "Protein": "protein", "Proteins": "protein", "Total proteins": "protein",
    "Lipids/fat": "lipids_fat", "Total lipids": "lipids_fat",
    "DS": "dry_solids", "TS": "dry_solids", "Total solids": "dry_solids",
    "VS": "volatile_solids", "Volatile solids": "volatile_solids",
    "Carbohydrate": "total_carbohydrates", "Total carbohydrates": "total_carbohydrates",
}
KEEP_SEPARATE = {
    "Crude protein": "different assay from Protein - deliberately NOT merged",
    "VM": "volatile MATTER (proximate) != volatile SOLIDS",
    "Nitrogen": "kept apart from TN/TKN/TAN - the Notes column shows different assays",
    "TN": "total nitrogen", "TKN": "total Kjeldahl nitrogen",
    "TAN": "total ammoniacal nitrogen", "sCOD": "soluble COD != COD",
    "Soluble lignin": "!= Lignin", "Insoluble lignin": "!= Lignin",
    "Glucan (excl. starch)": "!= Glucan", "Inorganic phosphate": "!= Phosphorus",
    "Free sugars": "!= Total sugars", "Other sugars": "!= Total sugars",
}

DOI_RE = re.compile(r"10\.\d{4,9}/\S+")
KEY_OVERRIDE_PREFIX = {"E.F. Castillo M.,": "xls-castillo2006"}


def slug(s: str, n: int = 40) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()[:n].strip("-")


def propose_source_key(src: str) -> tuple[str, str]:
    """Return (citation_key, doi) for a raw Excel source string."""
    for prefix, key in KEY_OVERRIDE_PREFIX.items():
        if src.startswith(prefix):
            m = DOI_RE.search(src)
            return key, (m.group(0).rstrip(".") if m else "")
    m = DOI_RE.search(src)
    if m:  # full citation string -> firstauthor+year
        surname = (src.split(",")[0].strip().split() or ["anon"])[-1]
        years = re.findall(r"\b((?:19|20)\d{2})\b", src)
        return f"{NAMESPACE}{slug(surname, 20)}{years[-1] if years else ''}", m.group(0).rstrip(".")
    return f"{NAMESPACE}{slug(src)}", ""


# --- workbook -----------------------------------------------------------------
def read_sheet() -> list[dict]:
    if not XLSX.exists():
        sys.exit(
            f"Workbook not found: {XLSX}\n"
            "Raw source data is deliberately not versioned (see .gitignore); "
            "place the file there to run this loader."
        )
    ws = openpyxl.load_workbook(XLSX, data_only=True)[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    idx = {h: i for i, h in enumerate(rows[0]) if h}
    out = []
    for n, r in enumerate(rows[1:], start=2):
        if all(c in (None, "") for c in r):
            continue
        out.append({"_row": n, **{k: r[i] for k, i in idx.items()}})
    return out


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def classify(rec: dict) -> tuple[str | None, str]:
    """Decide the schema's value_type for a workbook row, or (None, reason)."""
    vt, val = rec["Value Type"], rec["Value"]
    lo, hi = rec["Min Value"], rec["Max Value"]
    if vt == "Range":
        if not (is_num(lo) and is_num(hi)):
            return None, "range with non-numeric or missing min/max"
        if lo > hi:  # violates the schema's range_order CHECK
            return None, f"range_order violation: min {lo} > max {hi}"
        return "range", ""
    if vt == "Value":
        if is_num(val):
            return "point", ""
        if val not in (None, ""):
            return "qualitative", ""
        return None, "value_type=Value but the Value cell is empty"
    return None, "no value_type -- empty placeholder row (absence = not measured)"


# --- manifests ----------------------------------------------------------------
def read_manifest(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Missing manifest: {path}\nRun with --emit-manifests first.")
    # Written for Belgian Excel: ';' delimiter, UTF-8 BOM.
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write_manifest(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(header)
        w.writerows(rows)


def emit_manifests(recs: list[dict]) -> None:
    """(Re)generate the review CSVs, preserving any DECISION already filled in."""
    CROSSWALKS.mkdir(parents=True, exist_ok=True)

    def existing(path: Path, key: str, col: str) -> dict[str, str]:
        if not path.exists():
            return {}
        return {r[key]: (r.get(col) or "").strip() for r in read_manifest(path)}

    # -- streams
    p = CROSSWALKS / "biomobi_excel_streams.csv"
    prior = existing(p, "excel_name", "DECISION")
    total = Counter(r["Biomass Type"] for r in recs)
    loadable = Counter(r["Biomass Type"] for r in recs
                       if r["Parameter type"] == "Physicochemical"
                       and r["Source"] not in (None, "")
                       and classify(r)[0])
    rows = []
    for name, _ in total.most_common():
        rows.append([name, total[name], loadable.get(name, 0), "", "", "", prior.get(name, "")])
    write_manifest(p, ["excel_name", "n_rows", "n_loadable", "proposed_code",
                       "proposed_canonical_name", "note", "DECISION"], rows)

    # -- sources
    p = CROSSWALKS / "biomobi_excel_sources.csv"
    prior = existing(p, "excel_source", "DECISION")
    stotal = Counter(r["Source"] for r in recs if r["Source"] not in (None, ""))
    rows, seen = [], {}
    for s, n in stotal.most_common():
        key, doi = propose_source_key(s)
        if key in seen and seen[key] != s:
            sys.exit(f"Source key collision on {key!r}:\n  {seen[key]!r}\n  {s!r}")
        seen[key] = s
        rows.append([s, n, "", key, "internal", doi, "", prior.get(s, "")])
    write_manifest(p, ["excel_source", "n_rows_total", "n_rows_on_candidate_streams",
                       "proposed_key", "proposed_type", "doi", "note", "DECISION"], rows)

    # -- parameters (a review, not a gate: blank = accept the proposal)
    p = CROSSWALKS / "biomobi_excel_parameters.csv"
    prior_code = existing(p, "excel_parameter", "CORRECTED_CODE")
    prior_cat = existing(p, "excel_parameter", "CORRECTED_CATEGORY")
    params = Counter(r["Parameter"] for r in recs if r["Parameter type"] == "Physicochemical")
    rows = []
    for name, n in sorted(params.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        code = COLLAPSE.get(name, slug(name).replace("-", "_"))
        rows.append([name, n, code, "physical" if name in PHYSICAL_PARAMS else "chemical",
                     ("MERGED -> " + code) if name in COLLAPSE else KEEP_SEPARATE.get(name, ""),
                     prior_code.get(name, ""), prior_cat.get(name, "")])
    write_manifest(p, ["excel_parameter", "n_rows", "proposed_code", "proposed_category",
                       "note", "CORRECTED_CODE", "CORRECTED_CATEGORY"], rows)
    print(f"Wrote 3 manifests to {CROSSWALKS}")


def load_decisions() -> tuple[dict, dict, dict]:
    """Read the manifests and refuse to continue while any DECISION is blank."""
    streams = read_manifest(CROSSWALKS / "biomobi_excel_streams.csv")
    sources = read_manifest(CROSSWALKS / "biomobi_excel_sources.csv")
    params = read_manifest(CROSSWALKS / "biomobi_excel_parameters.csv")

    unreviewed = []
    for r in streams:
        if (r.get("DECISION") or "").strip().lower() not in ("include", "exclude"):
            unreviewed.append(f"  streams  : {r['excel_name']}")
    for r in sources:
        if (r.get("DECISION") or "").strip().lower() not in ("include", "exclude"):
            unreviewed.append(f"  sources  : {r['excel_source'][:80]}")
    if unreviewed:
        sys.exit(
            "Refusing to load: {} manifest row(s) have no DECISION.\n"
            "Fill each DECISION cell with 'include' or 'exclude', then re-run.\n\n".format(len(unreviewed))
            + "\n".join(unreviewed[:40])
            + ("\n  ... and more" if len(unreviewed) > 40 else "")
        )

    stream_map = {}
    for r in streams:
        if r["DECISION"].strip().lower() == "include":
            code = (r.get("proposed_code") or "").strip()
            if not code:
                sys.exit(f"Stream {r['excel_name']!r} is 'include' but proposed_code is empty.")
            if code.endswith("-REVIEW"):
                sys.exit(
                    f"Stream {r['excel_name']!r} still carries the placeholder code {code!r}.\n"
                    "Resolve the naming question and set a real code before loading -- "
                    "stream.code is a primary key and other tables will reference it."
                )
            stream_map[r["excel_name"]] = (
                code, (r.get("proposed_canonical_name") or code).strip())

    source_map = {}
    for r in sources:
        if r["DECISION"].strip().lower() == "include":
            source_map[r["excel_source"]] = {
                "key": r["proposed_key"].strip(),
                "type": (r.get("proposed_type") or "internal").strip(),
                "doi": (r.get("doi") or "").strip(),
            }
    for s in source_map.values():
        if not s["key"].startswith(NAMESPACE):
            sys.exit(
                f"Source key {s['key']!r} does not start with {NAMESPACE!r}.\n"
                "That prefix is the loader's ownership namespace -- without it, the "
                "delete-then-reload step cannot tell which rows are safe to remove."
            )

    param_map = {}
    for r in params:
        name = r["excel_parameter"]
        code = (r.get("CORRECTED_CODE") or "").strip() or r["proposed_code"].strip()
        cat = (r.get("CORRECTED_CATEGORY") or "").strip() or r["proposed_category"].strip()
        param_map[name] = (code, cat)
    return stream_map, source_map, param_map


# --- build --------------------------------------------------------------------
def build(recs, stream_map, source_map, param_map, dedupe: bool):
    measurements, skipped = [], Counter()
    for r in recs:
        if r["Parameter type"] != "Physicochemical":
            skipped[f"parameter type '{r['Parameter type']}' (model-layer / out of scope)"] += 1
            continue
        if r["Biomass Type"] not in stream_map:
            skipped["stream excluded in manifest"] += 1
            continue
        if r["Source"] in (None, "") or r["Source"] not in source_map:
            skipped["no source, or source excluded in manifest"] += 1
            continue
        vtype, why = classify(r)
        if vtype is None:
            skipped[why] += 1
            continue
        pcode, pcat = param_map.get(r["Parameter"], (slug(r["Parameter"]).replace("-", "_"), "chemical"))
        unit, basis = UNIT_SPLIT.get(r["Unit"], (None, None))
        if unit is None:
            skipped[f"unmapped unit {r['Unit']!r}"] += 1
            continue
        measurements.append({
            "stream_code": stream_map[r["Biomass Type"]][0],
            "parameter_code": pcode,
            "parameter_category": pcat,
            "value_type": vtype,
            "value_num": r["Value"] if vtype == "point" else None,
            "value_min": r["Min Value"] if vtype == "range" else None,
            "value_max": r["Max Value"] if vtype == "range" else None,
            "value_avg": r["Avg Value"] if (vtype == "range" and is_num(r["Avg Value"])) else None,
            "value_text": str(r["Value"]) if vtype == "qualitative" else None,
            "sd": r["SD"] if is_num(r["SD"]) else None,
            "unit_code": unit,
            "basis_code": basis,
            "source_key": source_map[r["Source"]]["key"],
            "year": None,               # the workbook's `year` column is empty in all 631 rows
            "temporal_resolution": "unknown",
            "notes": r["Notes"] or None,
            "_row": r["_row"],
        })

    dupes = Counter()
    for m in measurements:
        dupes[(m["stream_code"], m["parameter_code"], m["value_type"], m["value_num"],
               m["value_min"], m["value_max"], m["unit_code"], m["basis_code"],
               m["source_key"])] += 1
    n_dupes = sum(v - 1 for v in dupes.values() if v > 1)
    if n_dupes and dedupe:
        seen, deduped = set(), []
        for m in measurements:
            k = (m["stream_code"], m["parameter_code"], m["value_type"], m["value_num"],
                 m["value_min"], m["value_max"], m["unit_code"], m["basis_code"], m["source_key"])
            if k in seen:
                continue
            seen.add(k)
            deduped.append(m)
        measurements = deduped
    return measurements, skipped, n_dupes


# --- load ---------------------------------------------------------------------
def load(dsn: str, measurements: list[dict], source_map: dict, param_map: dict,
         stream_map: dict) -> dict:
    used_params = {(m["parameter_code"], m["parameter_category"]) for m in measurements}
    used_units = {m["unit_code"] for m in measurements}
    used_bases = {m["basis_code"] for m in measurements}

    # A parameter's default unit = the one it is most often reported in here.
    # 'unknown' is never a default -- it records an absence, not a convention.
    modal = defaultdict(Counter)
    for m in measurements:
        if m["unit_code"] != "unknown":
            modal[m["parameter_code"]][m["unit_code"]] += 1

    # Where several Excel spellings collapse to one code, the most frequent
    # spelling wins the display name (param_map is ordered by row count).
    param_names = {}
    for excel_name, (code, _) in param_map.items():
        param_names.setdefault(code, excel_name)

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        # One transaction: on any error nothing changes.
        cur.execute(
            "INSERT INTO source (citation_key, source_type, title, notes) VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (citation_key) DO UPDATE SET source_type=EXCLUDED.source_type, "
            "title=EXCLUDED.title, notes=EXCLUDED.notes",
            (WORKBOOK_KEY, "internal", "BioMobi_Biomass_RevA.xlsx - legacy internal workbook",
             "Phase-2 seed. Parent record for every source transcribed out of this workbook."))

        for raw, s in source_map.items():
            cur.execute(
                "INSERT INTO source (citation_key, source_type, title, url, notes) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (citation_key) DO UPDATE SET "
                "source_type=EXCLUDED.source_type, title=EXCLUDED.title, "
                "url=EXCLUDED.url, notes=EXCLUDED.notes",
                (s["key"], s["type"], raw[:500],
                 f"https://doi.org/{s['doi']}" if s["doi"] else None, TRANSCRIPTION_NOTE))

        for code in sorted(used_units):
            cur.execute("INSERT INTO unit (code, description) VALUES (%s,%s) "
                        "ON CONFLICT (code) DO UPDATE SET description=EXCLUDED.description",
                        (code, UNITS[code]))
        for code in sorted(used_bases):
            cur.execute("INSERT INTO basis (code, description) VALUES (%s,%s) "
                        "ON CONFLICT (code) DO UPDATE SET description=EXCLUDED.description",
                        (code, BASES[code]))
        for code, cat in sorted(used_params):
            cur.execute(
                "INSERT INTO parameter (code, name, category, default_unit_code) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (code) DO UPDATE SET "
                "name=EXCLUDED.name, category=EXCLUDED.category, "
                "default_unit_code=EXCLUDED.default_unit_code",
                (code, param_names.get(code, code), cat,
                 modal[code].most_common(1)[0][0] if modal[code] else None))
        for excel_name, (code, canonical) in sorted(stream_map.items()):
            cur.execute(
                "INSERT INTO stream (code, canonical_name, notes) VALUES (%s,%s,%s) "
                "ON CONFLICT (code) DO UPDATE SET canonical_name=EXCLUDED.canonical_name, "
                "notes=EXCLUDED.notes",
                (code, canonical, f"Seeded from {XLSX.name}, sheet {SHEET}, "
                                  f"where it appears as '{excel_name}'."))

        # Delete only what this loader owns, then reload.
        cur.execute("DELETE FROM property_measurement WHERE source_key LIKE %s",
                    (NAMESPACE + "%",))
        removed = cur.rowcount
        cur.execute("DELETE FROM supply_observation WHERE source_key LIKE %s",
                    (NAMESPACE + "%",))
        removed_obs = cur.rowcount

        cur.executemany(
            "INSERT INTO property_measurement (stream_code, parameter_code, value_type, "
            "value_num, value_min, value_max, value_avg, value_text, sd, unit_code, "
            "basis_code, source_key, year, temporal_resolution, notes) "
            "VALUES (%(stream_code)s,%(parameter_code)s,%(value_type)s,%(value_num)s,"
            "%(value_min)s,%(value_max)s,%(value_avg)s,%(value_text)s,%(sd)s,%(unit_code)s,"
            "%(basis_code)s,%(source_key)s,%(year)s,%(temporal_resolution)s,%(notes)s)",
            measurements)
        conn.commit()
    return {"removed": removed, "removed_obs": removed_obs, "inserted": len(measurements)}


def main() -> None:
    global CROSSWALKS
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=LOCAL_DSN, help="Postgres DSN (default: local stack)")
    ap.add_argument("--emit-manifests", action="store_true",
                    help="regenerate the review CSVs, preserving filled-in DECISIONs")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and validate, but write nothing")
    ap.add_argument("--dedupe", action="store_true",
                    help="collapse rows identical on stream+parameter+value+unit+source")
    ap.add_argument("--allow-remote", action="store_true",
                    help="permit a non-local DSN (you almost certainly do not want this)")
    ap.add_argument("--crosswalks", type=Path, default=CROSSWALKS,
                    help="manifest directory (override only for testing)")
    args = ap.parse_args()
    CROSSWALKS = args.crosswalks

    recs = read_sheet()
    print(f"{XLSX.name} / {SHEET}: {len(recs)} non-empty rows")

    if args.emit_manifests:
        emit_manifests(recs)
        return

    stream_map, source_map, param_map = load_decisions()
    print(f"manifests: {len(stream_map)} stream(s) and {len(source_map)} source(s) marked include")

    measurements, skipped, n_dupes = build(recs, stream_map, source_map, param_map, args.dedupe)

    print("\nskipped:")
    for reason, n in skipped.most_common():
        print(f"  {n:4d}  {reason}")
    if n_dupes:
        print(f"\n  NOTE: {n_dupes} row(s) are identical on "
              f"stream+parameter+value+unit+source."
              + ("  Collapsed (--dedupe)." if args.dedupe
                 else "  Kept as-is; pass --dedupe to collapse them."))

    # A parameter recorded in more than one unit/basis is either a genuine mix of
    # reporting conventions or a transcription error. The loader stores what the
    # source said and reports the ambiguity rather than silently harmonising it.
    combos = defaultdict(set)
    for m in measurements:
        combos[m["parameter_code"]].add((m["unit_code"], m["basis_code"]))
    mixed = {p: c for p, c in combos.items() if len(c) > 1}
    if mixed:
        print("\nunit/basis inconsistency -- same parameter, several conventions:")
        for p, c in sorted(mixed.items()):
            print(f"  {p:22s} {', '.join(sorted(f'{u} [{b}]' for u, b in c))}")

    # Inherently dimensionless quantities carrying a dimensional unit are a
    # transcription error in the workbook, not a reporting convention.
    DIMENSIONLESS = {"ph", "c_n"}
    bad_unit = sorted({(m["parameter_code"], m["unit_code"]) for m in measurements
                       if m["parameter_code"] in DIMENSIONLESS
                       and m["unit_code"] not in ("pH", "n.a.", "unknown")})
    if bad_unit:
        print("\nsuspect unit -- dimensionless parameter given a dimensional unit "
              "(workbook error, loaded as recorded):")
        for p, u in bad_unit:
            print(f"  {p} recorded in {u}")

    spread = defaultdict(list)
    for m in measurements:
        v = m["value_num"] if m["value_num"] is not None else m["value_min"]
        if v is not None:
            spread[(m["stream_code"], m["parameter_code"], m["unit_code"])].append(float(v))
    wide = {k: v for k, v in spread.items()
            if len(v) > 2 and min(v) > 0 and max(v) / min(v) >= 5}
    if wide:
        print("\nimplausible spread -- same stream+parameter+unit varying >=5x "
              "(suggests two different materials share one name):")
        for (s, p, u), v in sorted(wide.items()):
            print(f"  {s} / {p} [{u}]: {min(v):g} .. {max(v):g}  (n={len(v)})")

    by_stream = Counter(m["stream_code"] for m in measurements)
    print(f"\nto load: {len(measurements)} measurement(s)")
    for code, n in by_stream.most_common():
        print(f"  {n:4d}  {code}")
    print("  value types: " + ", ".join(
        f"{k}={v}" for k, v in Counter(m["value_type"] for m in measurements).most_common()))

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return
    if not any(h in args.dsn for h in ("127.0.0.1", "localhost")) and not args.allow_remote:
        sys.exit("\nRefusing a non-local DSN without --allow-remote. "
                 "Schema and data changes belong on the local stack first.")

    r = load(args.dsn, measurements, source_map, param_map, stream_map)
    print(f"\nremoved {r['removed']} prior measurement(s) and {r['removed_obs']} "
          f"observation(s) in the '{NAMESPACE}' namespace")
    print(f"inserted {r['inserted']} measurement(s). Committed.")


if __name__ == "__main__":
    main()
