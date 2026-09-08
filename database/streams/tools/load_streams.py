"""Register the 80%-selection streams of the candidate stream register into BioMobi.

The register (`database/register/`, closed 2026-09-04) ranked 67 selectable streams and found
80% of a 7.292.982 t/yr envelope in the top 13 commodities. This loader turns that selection
into BioMobi vocabulary: `stream` rows, plus two classification facets.

WHAT THIS LOADS, AND WHAT IT DELIBERATELY DOES NOT
    Loads:      stream, classification_scheme, classification_term, stream_classification.
    Does NOT:   supply_observation. The tonnages in the manifest are context for the human
                decision, not data. A volume row needs `source_key NOT NULL`, and all eight
                archived register PDFs still carry a blank citation_key (flag F-002). Loading
                the numbers would also skip the per-claim curation gate: 687 of the register's
                801 claims are still `awaiting verification`.

GRAIN -- why 21 rows and not 13
    The hub's canonical-grain rule is "define each canonical stream at the finest grain any
    target source distinguishes". Four of the 13 selected commodities are not one material:
    Suikerbiet is loof + pulp + the beet itself, Aardappel is loof + tuber + processing
    residue, Kool- en raapzaad is straw + crush meal, Spruiten is stem mass + the sprout.
    The register measures those halves separately, so they enter as separate streams.
    Stream identity is the MATERIAL, never the chain stage: rejected cauliflower at the
    auction and at the processor is one stream carrying two `bioloop-keten` terms.

    Consequence, and it matters: the manifest's per-stream figures MUST NOT be summed. The
    register's 80/20 arithmetic runs at commodity level (largest figure any one source gives
    a commodity), so a sum over split rows is a different and unsupported quantity. Each row
    carries its commodity's authoritative rank and figure alongside its own largest claim.

WHAT LOADS IS NOT THIS SCRIPT'S DECISION. Every row must be marked `include` / `exclude` by
a human in the DECISION column of database/crosswalks/register_streams.csv. The script
refuses to run while any cell is blank.

Idempotency. This loader owns exactly the stream codes named in the manifest and the two
classification schemes below. Each run rebuilds their `stream_classification` rows inside one
transaction, so flipping a DECISION to `exclude` withdraws the classifications rather than
orphaning them. Reference vocabulary is never deleted -- `stream_classification` cascades on
stream delete, and an ingestion script must not be able to destroy classification work. An
excluded stream therefore keeps its row and is reported, not removed.

Usage (from database/streams/):
    python tools/load_streams.py --dry-run                       # parse + check, touch nothing
    python tools/load_streams.py --emit-sql build/streams.sql    # write the SQL, run nothing
    python tools/load_streams.py                                 # load into the local stack
    python tools/load_streams.py --dsn ... --allow-remote        # deliberate: the live project
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import psycopg

HERE = Path(__file__).resolve().parent          # database/streams/tools
STREAMS = HERE.parent                           # database/streams
DB = STREAMS.parent                             # database
MANIFEST = STREAMS / "crosswalks" / "register_streams.csv"
REGISTER_JSON = DB / "register" / "build" / "streams.json"

# The local Supabase stack. The live project is never a default target.
LOCAL_DSN = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

SELECTION = "BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities)"

# ONE facet, and it classifies the object by what it is: the register workbook's own commodity
# levels (dictionaries/commodity_hierarchy.md), loaded as a two-level ladder -- L2 is the parent
# term, L3 the child, and a stream is linked to its L3.
#
# Chain stage is deliberately NOT a facet. Where a stream arises is a property of an OBSERVATION
# of it, not of the object, and `supply_observation` already carries geography/year/source for
# exactly that. An earlier version made it a stream facet, which is what produced stage-named
# pseudo-objects like `aardappel-industrie`.
SCHEME = "bioloop-commodity"
SCHEME_NAME = "Commodityniveau (BIOLOOP-register L2 -> L3)"

REQUIRED_COLS = ["code", "canonical_name", "commodity_l2", "commodity_l3", "register_l4",
                 "fractie", "l4_rank", "l4_t_per_jaar", "grootste_claim_t", "grootste_claim",
                 "geografie", "n_claims", "claim_ids", "omschrijving", "DECISION"]


def term_code(label: str) -> str:
    """A stable term code from a register label. Kept readable, ASCII, no accents in use."""
    out = []
    for ch in label.lower():
        out.append(ch if ch.isalnum() else "-")
    return "-".join(p for p in "".join(out).split("-") if p)


def read_manifest(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Manifest not found: {path}\nIt is committed; check out the repo properly.")
    # Written for Belgian Excel: ';' delimiter, UTF-8 BOM.
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    if not rows:
        sys.exit(f"Manifest is empty: {path}")
    missing = [c for c in REQUIRED_COLS if c not in rows[0]]
    if missing:
        sys.exit(f"Manifest is missing column(s): {', '.join(missing)}")
    return rows


def check_gate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """The human gate. Blank blocks the load; the caller never sees a partly-decided manifest."""
    blank, bad = [], []
    for r in rows:
        d = (r["DECISION"] or "").strip().lower()
        if not d:
            blank.append(r)
        elif d not in ("include", "exclude"):
            bad.append(r)
    if blank or bad:
        print("\nRefusing to load -- the curation gate is not closed.\n", file=sys.stderr)
        for r in blank:
            print(f"  blank DECISION : {r['code']:<26} {r['canonical_name']}", file=sys.stderr)
        for r in bad:
            print(f"  bad DECISION   : {r['code']:<26} {r['DECISION']!r} "
                  f"(expected include/exclude)", file=sys.stderr)
        print(f"\n{len(blank)} blank, {len(bad)} invalid, of {len(rows)} rows in {MANIFEST}",
              file=sys.stderr)
        sys.exit(1)
    inc = [r for r in rows if r["DECISION"].strip().lower() == "include"]
    exc = [r for r in rows if r["DECISION"].strip().lower() == "exclude"]
    return inc, exc


def check_against_register(rows: list[dict]) -> list[str]:
    """Re-read every claim id in the manifest against the register corpus.

    The manifest is authored, not generated, so this is what stops it drifting away from the
    corpus it claims to summarise: a renamed, retired or re-levelled claim shows up here.
    """
    if not REGISTER_JSON.exists():
        return [f"register corpus not built ({REGISTER_JSON} missing); "
                f"run register/tools/build_overview.py to enable this check"]
    claims = {c["id"]: c for c in json.loads(REGISTER_JSON.read_text(encoding="utf-8"))["claims"]}
    problems = []
    seen: dict[str, str] = {}
    for r in rows:
        ids = r["claim_ids"].split()
        if len(ids) != int(r["n_claims"]):
            problems.append(f"{r['code']}: n_claims={r['n_claims']} but {len(ids)} ids listed")
        top = 0
        for cid in ids:
            c = claims.get(cid)
            if c is None:
                problems.append(f"{r['code']}: claim {cid} is not in the corpus")
                continue
            if cid in seen:
                problems.append(f"{r['code']}: claim {cid} is already used by {seen[cid]}")
            seen[cid] = r["code"]
            if c["l4"] != r["register_l4"]:
                problems.append(f"{r['code']}: claim {cid} sits under L4 {c['l4']!r}, "
                                f"manifest says {r['register_l4']!r}")
            top = max(top, round(c["v"] or 0))
        if top and top != int(r["grootste_claim_t"]):
            problems.append(f"{r['code']}: largest claim is {top} t, manifest says "
                            f"{r['grootste_claim_t']} t")
    return problems


def terms_of(rows: list[dict]) -> tuple[dict[str, str], dict[str, str]]:
    """The commodity ladder the manifest uses: ({L2 code: label}, {L3 code: parent L2 code}).

    Insertion order matters -- every parent is created before the child that references it.
    """
    parents: dict[str, str] = {}
    children: dict[str, str] = {}
    labels: dict[str, str] = {}
    for r in rows:
        l2, l3 = r["commodity_l2"].strip(), r["commodity_l3"].strip()
        parents[term_code(l2)] = l2
        labels[term_code(l3)] = l3
        children[term_code(l3)] = term_code(l2)
    return parents, {c: (labels[c], p) for c, p in children.items()}


def nl(n: int) -> str:
    """Belgian thousands separator. Formats the number only -- an earlier version did a
    blanket comma->dot replace over the whole sentence and ate the prose commas with it."""
    return f"{n:,}".replace(",", ".")


def notes_for(r: dict) -> str:
    geo = r["geografie"]
    caveat = ""
    if "Belgie" in geo and "Vlaanderen" not in geo:
        caveat = (" LET OP: het cijfer is Belgisch, niet Vlaams -- open vraag in state.md "
                  "of BioMobi een Belgisch cijfer als Vlaams stroomvolume aanvaardt.")
    elif "Belgie" in geo:
        caveat = " Claims mengen Vlaamse en Belgische geografie."
    return (f"Geregistreerd uit {SELECTION}. "
            f"Commodity '{r['register_l4']}' staat op rang {r['l4_rank']} met "
            f"{nl(int(r['l4_t_per_jaar']))} t/jaar (register-methode: het grootste cijfer dat een "
            f"enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). "
            f"Fractie '{r['fractie']}'; grootste eigen claim {nl(int(r['grootste_claim_t']))} t "
            f"({r['grootste_claim']}). Claims: {r['claim_ids']}. Geografie: {geo}.{caveat} "
            f"Nog geen supply_observation -- zie F-002.")


def q(v) -> str:
    """Quote a literal for the emitted SQL. Review rendering only -- the loader itself
    parameterises every statement rather than building strings."""
    if v is None:
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def emit_sql(inc: list[dict], all_rows: list[dict], migration: bool = False) -> str:
    """The statements load() would run, in order, as readable SQL.

    Kept directly beside load() so that a change to one is visibly a change to the other.

    `migration=True` shapes the file for database/supabase/migrations/: no BEGIN/COMMIT (the
    Supabase CLI wraps each migration in its own transaction) and a header saying what
    regenerates it. Every statement is ON CONFLICT-guarded, so the file is safe to re-apply
    and `supabase db reset` reproduces these rows from migrations alone.
    """
    parents, children = terms_of(inc)
    if migration:
        L = [f"-- BioMobi vocabulary: the register's 80% stream selection, at object grain.",
             f"-- {SELECTION}",
             "--",
             "-- GENERATED -- do not hand-edit. Regenerate with, from database/streams/:",
             "--   ../.venv/Scripts/python tools/load_streams.py --emit-migration <path>",
             "-- The source of truth is crosswalks/register_streams.csv (human DECISION gate)",
             "-- plus the register corpus it is checked against on every run.",
             "--",
             "-- When the selection changes -- resolved gaps adding or renaming objects -- write",
             "-- a NEW migration from the updated manifest; never edit this one. Every statement",
             "-- is ON CONFLICT-guarded, so re-applying it is a no-op.",
             "--",
             f"-- {len(inc)} objects, {len(parents)} + {len(children)} commodity terms, 1 scheme.",
             "-- No supply_observation rows: source_key is NOT NULL and the register's PDFs have",
             "-- no citation keys yet (flag F-002).",
             "",
             "-- 1. the facet"]
    else:
        L = [f"-- {SELECTION}",
             "-- Generated by tools/load_streams.py --emit-sql. A review rendering of what the",
             "-- loader will execute -- do not apply this file by hand; run the loader.",
             f"-- {len(inc)} objects, {len(parents)} + {len(children)} commodity terms, 1 scheme.",
             "-- No supply_observation rows: see F-002.",
             "",
             "BEGIN;",
             "",
             "-- 1. the facet"]
    L.append(f"INSERT INTO classification_scheme (code, name)"
             f" VALUES ({q(SCHEME)}, {q(SCHEME_NAME)})")
    L.append("  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;")
    L += ["", "-- 2. the commodity ladder: L2 parents first, then L3 children pointing at them"]
    for tcode, label in parents.items():
        L.append(f"INSERT INTO classification_term (scheme_code, code, label)"
                 f" VALUES ({q(SCHEME)}, {q(tcode)}, {q(label)})")
        L.append("  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label;")
    for tcode, (label, parent) in children.items():
        L.append(f"INSERT INTO classification_term (scheme_code, code, label, parent_term_id)")
        L.append(f"  SELECT {q(SCHEME)}, {q(tcode)}, {q(label)}, term_id"
                 f" FROM classification_term")
        L.append(f"   WHERE scheme_code = {q(SCHEME)} AND code = {q(parent)}")
        L.append("  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,")
        L.append("    parent_term_id = EXCLUDED.parent_term_id;")
    L += ["", "-- 3. the objects"]
    for r in inc:
        L.append("INSERT INTO stream (code, canonical_name, description, notes) VALUES (")
        L.append(f"  {q(r['code'])},")
        L.append(f"  {q(r['canonical_name'])},")
        L.append(f"  {q(r['omschrijving'])},")
        L.append(f"  {q(notes_for(r))})")
        L.append("  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,")
        L.append("    description = EXCLUDED.description, notes = EXCLUDED.notes;")
    L += ["",
          "-- 4. rebuild this loader's classification links -- its ownership namespace is",
          "--    every code the manifest names, inside the scheme above. Nothing else is",
          "--    touched, and no stream row is ever deleted.",
          "DELETE FROM stream_classification sc USING classification_term t",
          "  WHERE sc.term_id = t.term_id",
          f"    AND t.scheme_code = {q(SCHEME)}",
          f"    AND sc.stream_code IN ({', '.join(q(r['code']) for r in all_rows)});",
          "",
          "-- each object is linked to its L3; the L2 is reachable through parent_term_id."]
    for r in inc:
        L.append("INSERT INTO stream_classification (stream_code, term_id)")
        L.append(f"  SELECT {q(r['code'])}, term_id FROM classification_term")
        L.append(f"   WHERE scheme_code = {q(SCHEME)}"
                 f" AND code = {q(term_code(r['commodity_l3']))}")
        L.append("  ON CONFLICT DO NOTHING;")
    L += ["", ""] if migration else ["", "COMMIT;", ""]
    return "\n".join(L)


def load(dsn: str, inc: list[dict], exc: list[dict], all_rows: list[dict]) -> dict:
    parents, children = terms_of(inc)
    stats = {"streams": 0, "terms": 0, "links": 0, "unlinked": 0}
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        # One transaction: on any error nothing changes.
        cur.execute("INSERT INTO classification_scheme (code, name) VALUES (%s,%s) "
                    "ON CONFLICT (code) DO UPDATE SET name=EXCLUDED.name",
                    (SCHEME, SCHEME_NAME))

        term_id: dict[str, int] = {}
        # L2 parents first, so each L3 child can point at a term_id that already exists.
        for tcode, label in parents.items():
            cur.execute(
                "INSERT INTO classification_term (scheme_code, code, label) VALUES (%s,%s,%s) "
                "ON CONFLICT (scheme_code, code) DO UPDATE SET label=EXCLUDED.label "
                "RETURNING term_id", (SCHEME, tcode, label))
            term_id[tcode] = cur.fetchone()[0]
            stats["terms"] += 1
        for tcode, (label, parent) in children.items():
            cur.execute(
                "INSERT INTO classification_term (scheme_code, code, label, parent_term_id) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (scheme_code, code) DO UPDATE SET "
                "label=EXCLUDED.label, parent_term_id=EXCLUDED.parent_term_id "
                "RETURNING term_id", (SCHEME, tcode, label, term_id[parent]))
            term_id[tcode] = cur.fetchone()[0]
            stats["terms"] += 1

        for r in inc:
            cur.execute(
                "INSERT INTO stream (code, canonical_name, description, notes) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (code) DO UPDATE SET "
                "canonical_name=EXCLUDED.canonical_name, description=EXCLUDED.description, "
                "notes=EXCLUDED.notes",
                (r["code"], r["canonical_name"], r["omschrijving"], notes_for(r)))
            stats["streams"] += 1

        # Rebuild the bridge for every code this manifest names -- included or not -- inside
        # the scheme this loader owns. Nothing else is touched.
        codes = [r["code"] for r in all_rows]
        cur.execute(
            "DELETE FROM stream_classification sc USING classification_term t "
            "WHERE sc.term_id = t.term_id AND t.scheme_code = %s AND sc.stream_code = ANY(%s)",
            (SCHEME, codes))
        stats["unlinked"] = cur.rowcount

        # One link per object, to its L3. The L2 is reachable through parent_term_id, so
        # rolling up by branch is a recursive walk, not a second stored link.
        for r in inc:
            cur.execute(
                "INSERT INTO stream_classification (stream_code, term_id) VALUES (%s,%s) "
                "ON CONFLICT DO NOTHING",
                (r["code"], term_id[term_code(r["commodity_l3"])]))
            stats["links"] += cur.rowcount
        conn.commit()
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=LOCAL_DSN, help="Postgres DSN (default: local stack)")
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and check, touch no database")
    ap.add_argument("--emit-sql", type=Path, metavar="PATH",
                    help="write the SQL this loader would run, then exit without running it")
    ap.add_argument("--emit-migration", type=Path, metavar="PATH",
                    help="write the same SQL shaped for database/supabase/migrations/ "
                         "(no BEGIN/COMMIT; the CLI wraps it), then exit")
    ap.add_argument("--allow-remote", action="store_true",
                    help="permit a non-local DSN (deliberate; the live project is downstream)")
    ap.add_argument("--skip-register-check", action="store_true",
                    help="do not re-check the manifest's claim ids against the register corpus")
    args = ap.parse_args()

    rows = read_manifest(args.manifest)
    inc, exc = check_gate(rows)

    if not args.skip_register_check:
        problems = check_against_register(rows)
        if problems:
            print("\nManifest does not agree with the register corpus:\n", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            sys.exit(2)

    parents, children = terms_of(inc)
    print(f"\n{args.manifest.name}: {len(rows)} rows -> {len(inc)} include, {len(exc)} exclude")
    print(f"facet {SCHEME}: {len(parents)} L2 + {len(children)} L3 terms")
    for tcode, label in parents.items():
        print(f"  {label}")
        for ccode, (clabel, parent) in children.items():
            if parent != tcode:
                continue
            print(f"    {clabel}")
            for r in inc:
                if term_code(r["commodity_l3"]) == ccode:
                    print(f"      {r['code']:<26} {r['canonical_name'][:38]:<40} "
                          f"rank {r['l4_rank']:>2}")
    for r in exc:
        print(f"  [excluded] {r['code']:<26} keeps any existing stream row; "
              f"classifications withdrawn")

    for target, is_migration in ((args.emit_sql, False), (args.emit_migration, True)):
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(emit_sql(inc, rows, migration=is_migration), encoding="utf-8")
            print(f"\nwrote {target} -- review it; no database was touched.")
    if args.emit_sql or args.emit_migration:
        return

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return

    local = any(h in args.dsn for h in ("127.0.0.1", "localhost"))
    if not local and not args.allow_remote:
        sys.exit("\nRefusing a non-local DSN without --allow-remote. "
                 "Data belongs on the local stack first.")
    if not local:
        print(f"\n!! non-local target: {args.dsn.split('@')[-1]}")

    s = load(args.dsn, inc, exc, rows)
    print(f"\nloaded: {s['streams']} stream rows, {s['terms']} classification terms, "
          f"{s['links']} stream-classification links ({s['unlinked']} rebuilt).")
    print("No supply_observation rows were written -- see F-002.")


if __name__ == "__main__":
    main()
