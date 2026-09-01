"""Structural integrity check over the register. Run it after every extraction.

Every check here came from a defect that cost a review round in Aug-Sep 2026. None of them is
tied to a source: they are all rules about the register's own shape, so a new source is caught
the same way OVAM and MONBIO were.

    database/.venv/Scripts/python.exe database/register/audit_register.py
    database/.venv/Scripts/python.exe database/register/audit_register.py --source S091
    database/.venv/Scripts/python.exe database/register/audit_register.py --csv    # -> a fix sheet

Checks
------
1  product-at-wrong-level   A row naming a product (a Prodcom/PRODCOM code, or an L3 whose name is
                            clearly one article) sits at L3 with no L4. It is then invisible to a
                            selection, which only reaches L4/L5.
2  level-mismatch           `level_1to5` disagrees with the deepest commodity column filled. The
                            level is the row's own depth; what an aggregate totals belongs in
                            aggregate_coverage.totals_level.
3  unmarked-total           The row equals the sum of its siblings, or its name says *totaal*, but
                            it carries no `AGGREGAAT - ` prefix, so it sums with its own parts.
4  unmarked-residual-class  The row is a leftover class of a nomenclature ("Andere ...", "n.e.g.",
                            "van alle soorten", several species in one cell). It is a real volume
                            but not a named stream, so it must not sum with named siblings.
5  aggregate-without-entry  An `AGGREGAAT - ` row with no line in aggregate_coverage.csv: the view
                            cannot place it and silently shows it as unallocated.
6  orphan-registry-entry    A line in aggregate_coverage.csv whose claim no longer exists.
7  missing-provenance       A live claim without page or table/figure - it cannot be re-checked.

Exit code is 0 when nothing is found, 1 otherwise, so it can gate a session.
"""
import argparse, csv, io, json, pathlib, re, sys, collections

HERE = pathlib.Path(__file__).resolve().parent
EXPORT = HERE / "streams_export.csv"
REGISTRY = HERE / "crosswalks" / "aggregate_coverage.csv"
OUT_CSV = HERE / "crosswalks" / "AUDIT_findings.csv"
AGG = "AGGREGAAT"

# A row that cites a statistical product code is naming an ARTICLE, not a subgroup, so it belongs
# at L4. Listed by nomenclature rather than hardcoded to one source: MONBIO uses Prodcom, but a
# customs- or NACE-based source names its articles the same way, and should be caught the same way.
# Add a marker here when a new source brings its own nomenclature.
PRODUCT_CODE_RE = re.compile(
    r"\bprodcom\b|\bnace\b|\bcn[- ]?code\b|\bgn[- ]?code\b|\bhs[- ]?code\b|\bnaric\b|\bcpa\b",
    re.I)
TOTAL_RE = re.compile(r"\btotaal\b|\btotale\b", re.I)


def _load_collection_rule():
    """Reuse the residual-class rule that the registry proposer already owns."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("mac", HERE / "make_aggregate_coverage.py")
    mac = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mac)
    return mac.is_collection


def depth_of(r):
    for col, d in (("L5_fraction_as_named", 5), ("L4_ingredient", 4),
                   ("L3_commodity_subgroup", 3), ("L2_commodity_group", 2)):
        if (r.get(col) or "").strip():
            return d
    return 1


def path_of(r):
    return " > ".join((r.get(c) or "").strip() for c in
                      ("L2_commodity_group", "L3_commodity_subgroup", "L4_ingredient",
                       "L5_fraction_as_named") if (r.get(c) or "").strip())


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="limit to one source_short")
    ap.add_argument("--csv", action="store_true", help="also write a fix sheet")
    args = ap.parse_args()

    if not EXPORT.exists():
        sys.exit(f"missing {EXPORT.name} - run prep/export first")
    rows = list(csv.DictReader(io.open(EXPORT, encoding="utf-8-sig"), delimiter=";"))
    live = [r for r in rows if not (r.get("DECISION_expert") or "").strip().lower()
            .startswith(("no", "nee", "exclude", "uitsluiten", "drop"))]
    if args.source:
        live = [r for r in live if r.get("source_short") == args.source]
    is_collection = _load_collection_rule()

    reg = {}
    if REGISTRY.exists():
        reg = {r["claim_id"]: r for r in
               csv.DictReader(io.open(REGISTRY, encoding="utf-8-sig"), delimiter=";")}

    F = []

    def flag(kind, r, detail, fix=""):
        F.append(dict(check=kind, claim_id=r.get("claim_id", ""),
                      source_short=r.get("source_short", ""),
                      volume_t_per_yr=r.get("volume_t_per_yr", ""),
                      path=path_of(r), name=(r.get("stream_name_NL") or "")[:120],
                      detail=detail, suggested_fix=fix))

    for r in live:
        name = (r.get("stream_name_NL") or "").strip()
        agg = name.upper().startswith(AGG)
        d = depth_of(r)

        # 1 — a named product parked above L4
        if PRODUCT_CODE_RE.search(name) and d < 4 and not agg:
            flag("product-at-wrong-level", r, f"names a product but sits at L{d}",
                 "set level_1to5 = 4 and L4_ingredient to the product name")

        # 2 — level vs filled columns
        lvl = (r.get("level_1to5") or "").strip()
        if lvl and lvl.isdigit() and int(lvl) != d:
            flag("level-mismatch", r, f"level_1to5 = {lvl} but the deepest filled column is L{d}",
                 f"set level_1to5 = {d}")

        # 3 — says it is a total but is not marked
        if TOTAL_RE.search(name) and not agg:
            flag("unmarked-total", r, "the source calls this a total",
                 "prefix the name with 'AGGREGAAT - '")

        # 4 — residual nomenclature class not marked
        if not agg and is_collection(name):
            flag("unmarked-residual-class", r,
                 "a leftover class of the nomenclature, not a named stream",
                 "prefix with 'AGGREGAAT - '; it will sit in the unallocated band")

        # 5 — aggregate with no registry line
        if agg and r["claim_id"] not in reg:
            flag("aggregate-without-entry", r, "no line in aggregate_coverage.csv",
                 "run make_aggregate_coverage.py and decide the new row")

        # 7 — provenance
        if not (r.get("source_page") or "").strip() or not (r.get("source_table_figure") or "").strip():
            flag("missing-provenance", r, "no source_page and/or source_table_figure",
                 "record where the figure was read from")

    # 3b — arithmetic: a component equal to the sum of its siblings
    groups = collections.defaultdict(list)
    for r in live:
        if (r.get("stream_name_NL") or "").upper().startswith(AGG):
            continue
        key = (r.get("source_short"), r.get("L1_role"), path_of(r), r.get("quantity_type"),
               r.get("reference_year"), r.get("chain_L2"))
        groups[key].append(r)
    for key, cs in groups.items():
        if not 3 <= len(cs) <= 13:
            continue
        for cand in cs:
            v = num(cand.get("volume_t_per_yr"))
            if v <= 0:
                continue
            others = [x for x in cs if x is not cand and num(x.get("volume_t_per_yr")) > 0]
            n = len(others)
            hit = None
            for mask in range(1, 1 << n):
                members = [others[i] for i in range(n) if mask & (1 << i)]
                if len(members) < 2:
                    continue
                if abs(sum(num(m["volume_t_per_yr"]) for m in members) - v) <= max(2, v * 0.005):
                    hit = members
                    break
            if hit:
                flag("unmarked-total", cand,
                     "equals the sum of " + " + ".join(m["claim_id"] for m in hit),
                     "prefix with 'AGGREGAAT - ' if it really is their total")
                break

    # 6 — orphan registry lines
    ids = {r["claim_id"] for r in rows}
    for cid in reg:
        if cid not in ids:
            F.append(dict(check="orphan-registry-entry", claim_id=cid, source_short="",
                          volume_t_per_yr="", path="", name=reg[cid].get("name", "")[:120],
                          detail="claim no longer exists in the workbook",
                          suggested_fix="delete the line from aggregate_coverage.csv"))

    by = collections.Counter(f["check"] for f in F)
    scope = f" (source {args.source})" if args.source else ""
    print(f"audit over {len(live)} live claims{scope}: {len(F)} finding(s)\n")
    for k in sorted(by):
        vol = sum(num(f["volume_t_per_yr"]) for f in F if f["check"] == k)
        print(f"  {k:26} {by[k]:>4}   {vol:>14,.0f} t/yr")
    if F:
        print("\n  largest:")
        for f in sorted(F, key=lambda x: -num(x["volume_t_per_yr"]))[:10]:
            print(f"    {f['claim_id']:7} {num(f['volume_t_per_yr']):>12,.0f}  {f['check']:24} "
                  f"{f['name'][:44]}")
    if args.csv and F:
        cols = ["check", "claim_id", "source_short", "volume_t_per_yr", "path", "name",
                "detail", "suggested_fix", "DECISION_fix"]
        with io.open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, delimiter=";", extrasaction="ignore")
            w.writeheader()
            for f in F:
                w.writerow(dict(f, DECISION_fix=""))
        print(f"\nwrote {OUT_CSV.relative_to(HERE.parent)}")
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
