# -*- coding: utf-8 -*-
"""final_check.py - can anything in the workbook still be a selectable stream that is not one?

    database/.venv/Scripts/python database/register/final_check.py

This is the closing check on the register's completeness. It partitions EVERY claim into exactly
one disposition and then asserts the property that makes that disposition safe. Nothing is sampled
and nothing is assumed: a claim that fails its assertion is printed in full.

    A  retired                  a reviewer decision sits in DECISION_expert -> out of every figure
    B  productievolume          hoofdstroom; the selection is residual-only by definition
    C  selectable               live Reststroom, no AGGREGAAT prefix, an L4 or L5 filled
    D  residual above L4        live Reststroom, no prefix, only L2/L3 -> INVISIBLE to a selection
    E  declared total           the source's own word: totaal / totale
    F  whole-stage total        L2 = 'Aggregaat': a stage or chain total, carries no commodity
    G  nomenclature leftover    'Andere ...', 'n.e.g.', 'van alle soorten', 'uit andere ...'
    H  branch total             an aggregate that is none of the above

ASSERTIONS
  1  A+B+C+D+E+F+G+H == every claim, with no claim in two buckets
  2  no live residual row claims level 4/5 with both commodity columns empty
  3  no live residual row carries a commodity under the 'Aggregaat' placeholder
  4  every aggregate (E,F,G,H) has a line in aggregate_coverage.csv
  5  every bucket-D row is one of: on the fix list as skipped, or a source's own subgroup wording
     (i.e. the finest grain that source publishes) - the reviewer's disposition, not a guess
  6  every bucket-G row is either on the fix list or a genuine leftover by the collection rule
  7  every bucket-H row's name reads as a branch/sector total, not as one material

Buckets D and G are the only two that could hide a selectable stream. They are printed in full
every run, so the judgement stays visible instead of being buried in a pass/fail.
"""
import csv, io, pathlib, re, sys, collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_aggregate_coverage import is_collection

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent                      # register/ - HERE is register/tools/
EXPORT = ROOT / "streams_export.csv"
REGISTRY = ROOT / "crosswalks" / "aggregate_coverage.csv"
TOTAL_RE = re.compile(r"\btotaal\b|\btotale\b", re.I)

# Bucket-D rows the reviewer has dispositioned. Anything NOT here and not a subgroup wording is a
# finding, so a new source cannot quietly add an invisible stream.
D_DISPOSED = {
    "C-273": "FIX_LIST F4 - skipped: discards go back to sea, not valorisable (reviewer 2026-09-04)",
    "C-457": "FIX_LIST F4 - skipped: discards go back to sea, not valorisable (reviewer 2026-09-04)",
}
SUBGROUP_RE = re.compile(
    r"voedselreststro|voedselverlie|nevenstro|levensmiddelenafval|reststromen|"
    r"niet verkocht product|opgehouden vis", re.I)


def num(s):
    try: return float((s or "0").replace(",", "."))
    except ValueError: return 0.0


def main():
    rows = list(csv.DictReader(io.open(EXPORT, encoding="utf-8-sig"), delimiter=";"))
    reg = {r["claim_id"] for r in
           csv.DictReader(io.open(REGISTRY, encoding="utf-8-sig"), delimiter=";")}
    findings = []

    def bucket(r):
        name = r["stream_name_NL"] or ""
        if (r.get("DECISION_expert") or "").strip():        return "A retired"
        if r["L1_role"] != "Reststroom":                    return "B productievolume"
        if not name.startswith("AGGREGAAT - "):
            if (r["L4_ingredient"] or "").strip() or (r["L5_fraction_as_named"] or "").strip():
                return "C selectable"
            return "D residual above L4"
        if TOTAL_RE.search(name):                           return "E declared total"
        if r["L2_commodity_group"] == "Aggregaat":          return "F whole-stage total"
        if is_collection(name, r["claim_id"]):              return "G nomenclature leftover"
        return "H branch total"

    for r in rows: r["_b"] = bucket(r)
    by = collections.defaultdict(list)
    for r in rows: by[r["_b"]].append(r)

    print("=" * 112)
    print("DISPOSITION OF ALL %d CLAIMS" % len(rows))
    print("=" * 112)
    for b in sorted(by):
        g = by[b]
        print("  %-24s %4d claims   %14s t" % (b, len(g),
              format(int(sum(num(r["volume_t_per_yr"]) for r in g)), ",d").replace(",", ".")))
    if sum(len(v) for v in by.values()) != len(rows):
        findings.append("assertion 1: buckets do not partition the claims")

    # 2 / 3 -------------------------------------------------------------------------------
    for r in rows:
        if r["_b"] in ("C selectable", "D residual above L4"):
            if r["level_1to5"] in ("4", "5") and not (r["L4_ingredient"] or "").strip() \
                    and not (r["L5_fraction_as_named"] or "").strip():
                findings.append("assertion 2: %s claims level %s with no commodity column"
                                % (r["claim_id"], r["level_1to5"]))
            if r["L2_commodity_group"] == "Aggregaat" and (
                    (r["L3_commodity_subgroup"] or "").strip() or (r["L4_ingredient"] or "").strip()):
                findings.append("assertion 3: %s carries a commodity under the Aggregaat placeholder"
                                % r["claim_id"])
    # 4 ------------------------------------------------------------------------------------
    for b in ("E declared total", "F whole-stage total", "G nomenclature leftover", "H branch total"):
        for r in by[b]:
            if r["claim_id"] not in reg:
                findings.append("assertion 4: %s is an aggregate with no registry line" % r["claim_id"])

    # 5 - bucket D in full ------------------------------------------------------------------
    print("\n" + "=" * 112)
    print("BUCKET D - live residual rows above L4. These are invisible to any selection.")
    print("=" * 112)
    for r in sorted(by["D residual above L4"], key=lambda x: -num(x["volume_t_per_yr"])):
        name = r["stream_name_NL"]
        if r["claim_id"] in D_DISPOSED:
            why = D_DISPOSED[r["claim_id"]]
        elif SUBGROUP_RE.search(name):
            why = "the source's own subgroup wording - its finest published grain (a DATA gap)"
        else:
            why = "*** UNDISPOSED - read this row ***"
            findings.append("assertion 5: %s (%s t) sits above L4 with no disposition: %s"
                            % (r["claim_id"], r["volume_t_per_yr"], name[:60]))
        print("  %-7s %11s  %-13.13s %-30.30s %s"
              % (r["claim_id"], format(int(num(r["volume_t_per_yr"])), ",d").replace(",", "."),
                 r["source_short"], name[:30], why))

    # 6 - bucket G in full ------------------------------------------------------------------
    print("\n" + "=" * 112)
    print("BUCKET G - nomenclature leftovers. Each was read against the zemelen test:")
    print("           does the bundle arise together as one material, or is it a statistical tail?")
    print("=" * 112)
    for r in sorted(by["G nomenclature leftover"], key=lambda x: -num(x["volume_t_per_yr"])):
        print("  %-7s %11s  %-13.13s %s"
              % (r["claim_id"], format(int(num(r["volume_t_per_yr"])), ",d").replace(",", "."),
                 r["source_short"], (r["stream_name_NL"] or "")[12:84]))

    # 7 - bucket H names --------------------------------------------------------------------
    BRANCH_RE = re.compile(
        r"nevenstromen en productieresiduen|oogstresten|voedselreststro|voedselverlie|nevenstroom|"
        r"vervaardiging van|verwerking|productie nevenstromen|organisch-biologische verliezen|"
        r"overige groenten|overig fruit|groenten openlucht|groenten beschut|fruit \(tuinbouw\)", re.I)
    for r in by["H branch total"]:
        if not BRANCH_RE.search(r["stream_name_NL"] or ""):
            findings.append("assertion 7: %s reads as a material, not a branch total: %s"
                            % (r["claim_id"], (r["stream_name_NL"] or "")[:70]))

    print("\n" + "=" * 112)
    if findings:
        print("FAIL - %d finding(s)" % len(findings))
        for f in findings: print("   " + f)
        sys.exit(1)
    print("PASS - every claim is dispositioned; nothing in the workbook can still be a selectable")
    print("       stream that is not one, on the rules recorded in this file.")
    print("=" * 112)


if __name__ == "__main__":
    main()
