# -*- coding: utf-8 -*-
"""find_hidden_streams.py - the screen that catches what audit_register.py structurally cannot.

    database/.venv/Scripts/python database/register/find_hidden_streams.py

WHY THIS EXISTS
---------------
`audit_register.py` catches a misplaced row by reading its NAME: check 1 fires on a product code
(Prodcom / NACE / CN), check 4 on a leftover-class phrase ("Andere ...", "n.e.g.", "van alle
soorten"). A live residual row that sits at L2 or L3 with a plain, ordinary name passes every
check in the file - and is invisible to the selection, which only reaches L4/L5.

That blind spot cost real mass. Found on 2026-09-03, all three by hand:

    C-334 / C-523   Meel/schroot uit andere oliehoudende zaden      68.000 t each
    C-381 / C-574   Melasse op Vlaamse productiesites               47.805 / 56.806 t
    C-273 / C-457   Teruggegooide vis (ongewenste bijvangst)         7.500 /  7.707 t

None carries a product code; none matched a residual-class phrase. This script enumerates the
whole class instead of relying on a name pattern, and hands it to a human, because the call is
genuinely a judgement: most of these rows are legitimate - OVAM publishes *Dranken*, *Bakkerij*
and *groenten openlucht* at subgroup level and nothing finer, so an L3 row there is the finest
grain that source has. The question the reviewer answers per row is:

    subgroup-figure  the source really does report only at this level. Leave it. Not a defect;
                     it is a DATA gap, and belongs in OPEN_GAPS.md.
    promote          the row names one real stream and simply sits too high. Give it an L4.
    aggregate        the row is a total or a leftover class. Prefix it with 'AGGREGAAT - '.

Writes crosswalks/HIDDEN_STREAMS.csv (';'-delimited, UTF-8 BOM, per database/CLAUDE.md) with a
blank DECISION column, and refuses to overwrite once any DECISION has been filled.
"""
import csv, io, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_aggregate_coverage import is_collection   # one rule, one place

HERE = pathlib.Path(__file__).resolve().parent
EXPORT = HERE / "streams_export.csv"
OUT = HERE / "crosswalks" / "HIDDEN_STREAMS.csv"

COLS = ["claim_id", "source_short", "reference_year", "volume_t_per_yr", "level_1to5",
        "chain_L2", "L2_commodity_group", "L3_commodity_subgroup", "stream_name_NL",
        "branch_has_L4", "proposal", "why", "DECISION", "NOTES"]

# A name that reads as ONE named material rather than a statistical grouping. Deliberately
# conservative: it only drives the *proposal*, never the decision.
NAMED_RE = re.compile(
    r"^(melasse|bietenpulp|teruggegooide vis|zemelen|gries|bostel|draf|vinasse|wei|kaaswei|"
    r"perskoek|schroot|stro|loof|schillen|pulp)\b", re.I)
GROUPING_RE = re.compile(
    r"voedselreststro|voedselverlie|nevenstro|levensmiddelenafval|totaal|totale|"
    r"reststromen|niet verkocht product", re.I)


def main():
    if not EXPORT.exists():
        sys.exit("streams_export.csv not found - run the export first.")
    rows = list(csv.DictReader(io.open(EXPORT, encoding="utf-8-sig"), delimiter=";"))

    def num(r):
        try:
            return float((r.get("volume_t_per_yr") or "0").replace(",", "."))
        except ValueError:
            return 0.0

    live = [r for r in rows if not (r.get("DECISION_expert") or "").strip()]
    # which (source, L2, L3) branches already have a selectable row, so the reviewer can see
    # whether this row is the only thing in its branch or sits beside real detail
    has_l4 = set()
    for r in live:
        if (r.get("L1_role") == "Reststroom"
                and not (r.get("stream_name_NL") or "").startswith("AGGREGAAT - ")
                and (r.get("level_1to5") or "") in ("4", "5")):
            has_l4.add((r["source_short"], r["L2_commodity_group"], r["L3_commodity_subgroup"]))

    out = []
    for r in live:
        if r.get("L1_role") != "Reststroom":
            continue
        if (r.get("stream_name_NL") or "").startswith("AGGREGAAT - "):
            continue
        if (r.get("level_1to5") or "") not in ("2", "3"):
            continue
        name = r.get("stream_name_NL") or ""
        branch = (r["source_short"], r["L2_commodity_group"], r["L3_commodity_subgroup"])
        if is_collection(name, r["claim_id"]):
            prop, why = "aggregate", "a leftover class of the nomenclature (same rule as audit check 4)"
        elif NAMED_RE.match(name):
            prop, why = "promote", "the name is one named material, not a statistical grouping"
        elif GROUPING_RE.search(name):
            prop, why = ("subgroup-figure",
                         "the name is the source's own subgroup wording - probably its finest grain")
        else:
            prop, why = "", "no clear signal either way - read the row against the source"
        out.append(dict(
            claim_id=r["claim_id"], source_short=r["source_short"],
            reference_year=r.get("reference_year", ""),
            volume_t_per_yr=r.get("volume_t_per_yr", ""), level_1to5=r.get("level_1to5", ""),
            chain_L2=r.get("chain_L2", ""), L2_commodity_group=r["L2_commodity_group"],
            L3_commodity_subgroup=r["L3_commodity_subgroup"], stream_name_NL=name,
            branch_has_L4="yes" if branch in has_l4 else "no",
            proposal=prop, why=why, DECISION="", NOTES=""))

    out.sort(key=lambda x: -float((x["volume_t_per_yr"] or "0").replace(",", ".")))

    if OUT.exists():
        prev = list(csv.DictReader(io.open(OUT, encoding="utf-8-sig"), delimiter=";"))
        if any((p.get("DECISION") or "").strip() for p in prev):
            sys.exit("REFUSING: %s already has filled DECISION cells. Delete it deliberately, or "
                     "apply it, before regenerating." % OUT.name)

    OUT.parent.mkdir(exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, delimiter=";")
        w.writeheader(); w.writerows(out)

    tot = sum(float((x["volume_t_per_yr"] or "0").replace(",", ".")) for x in out)
    print("%s: %d live residual rows above L4 with no AGGREGAAT prefix, %s t/yr"
          % (OUT.name, len(out), format(round(tot), ",d").replace(",", ".")))
    for x in out[:12]:
        print("  %-7s %12s  L%s %-13.13s %-24.24s %s"
              % (x["claim_id"], x["volume_t_per_yr"], x["level_1to5"],
                 x["source_short"], x["L3_commodity_subgroup"] or x["L2_commodity_group"],
                 x["stream_name_NL"][:58]))
    print("  ... fill the DECISION column: promote | subgroup-figure | aggregate")


if __name__ == "__main__":
    main()
