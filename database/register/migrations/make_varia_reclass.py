"""Propose the `Gemengd` -> `Varia` reclassification for the register workbook.

REVISION 2 (2026-08-31), after the human review of revision 1. Three things changed:

  * The reviewer's `no` decisions removed 59 of the 100 rows from the tree, which emptied 5 of
    the 11 proposed L3 buckets outright - including BOTH new dictionary members revision 1 had
    invented (`Mengvoeder en diervoeder`, `Overige voedingsmiddelen`). Neither is created.
  * Two L3 buckets were NACE lumps rather than commodity subgroups, and are split:
        Suiker, chocolade, bereide maaltijden, enz.  ->  Chocolade  (+ Suiker, uncaptured)
        Deegwaren, dieetvoeding, zetmeel, maalderij  ->  Zetmeel en zetmeelproducten
    Only the populated halves become dictionary members; the empty halves are named in the
    aggregates' coverage instead, per the protocol's "do not invent structure speculatively"
    and the v2.3 rule that an aggregate must say which of its parts were not captured.
  * The 8 retail rows are NOT commodities. They are the retail chain stage split by collection
    channel, and each pair sums exactly to the stage total already in the register, so they
    become `component_set` aggregates - the same treatment as C-111/C-112.

Because the proposal changed for some rows, this script CLEARS the DECISION on exactly those
rows and says why in `revision`. Rows whose proposal is unchanged keep the decision already
made. Nothing is applied here - `apply_reclass.py` does that.

    database/.venv/Scripts/python.exe database/register/make_varia_reclass.py
"""
import csv, io, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "streams_export.csv"
OUT = HERE / "crosswalks" / "varia_reclass.csv"
AGG_PREFIX = "AGGREGAAT - "

COLUMNS = ["claim_id", "source_short", "reference_year", "chain_L2", "quantity_type",
           "volume_t_per_yr", "name", "current_L2", "current_level", "proposed_class",
           "proposed_L2", "proposed_L3", "proposed_L4", "proposed_level", "proposed_name",
           "basis", "note", "revision", "DECISION"]

# --- the Varia L3 vocabulary. Only subgroups that actually hold a surviving row. -----------
BAKKERIJ = "Bakkerij"
DRANKEN  = "Dranken"
OLIEN    = "Olien, vetten"
CHOCO    = "Chocolade"                       # split out of the NACE "suiker en chocolade" lump
ZETMEEL  = "Zetmeel en zetmeelproducten"     # split out of the NACE "maalderij/deegwaren" lump

# Named in aggregate coverage but holding no captured row -> deliberately NOT dictionary members.
UNCAPTURED = "Suiker / Bereide maaltijden / Deegwaren / Maalderijproducten / Dieetvoeding"

C = "component"
A = "aggregate"

# claim_id -> (class, L3, L4-or-None, level, basis)
# L4 None means "the row is the subgroup total itself" and sits at L3.
PLAN = {
    # --- OVAM subsector rows: one figure per processing subsector -------------------------
    "C-093": (C, BAKKERIJ, None, 3, "OVAM subsector: bakkerij"),
    "C-194": (C, BAKKERIJ, None, 3, "OVAM subsector: bakkerij"),
    "C-095": (C, DRANKEN,  None, 3, "OVAM subsector: dranken"),
    "C-196": (C, DRANKEN,  None, 3, "OVAM subsector: dranken"),
    "C-096": (C, OLIEN,    None, 3, "OVAM subsector: olien en vetten"),
    "C-197": (C, OLIEN,    None, 3, "OVAM subsector: olien en vetten"),
    # subsector lumps the reviewer asked to treat as aggregates over several L3s
    "C-097": (A, "", None, 3, "OVAM subsector lump -> aggregate over Chocolade + Suiker + Bereide maaltijden"),
    "C-198": (A, "", None, 3, "OVAM subsector lump -> aggregate over Chocolade + Suiker + Bereide maaltijden"),
    "C-099": (A, "", None, 3, "OVAM subsector lump -> aggregate over Zetmeel + Deegwaren + Maalderij + Dieetvoeding"),
    "C-199": (A, "", None, 3, "OVAM subsector lump -> aggregate over Zetmeel + Deegwaren + Maalderij + Dieetvoeding"),
    # --- totals of commodity groups that already exist elsewhere in the tree --------------
    "C-094": (A, "", None, 2, "totals potatoes + vegetables + fruit, which live under 2 L2 parents"),
    "C-195": (A, "", None, 2, "totals potatoes + vegetables + fruit, which live under 2 L2 parents"),
    "C-098": (A, "", None, 2, "totals meat + fish (Dierlijk - vee + Dierlijk - vis)"),
    "C-201": (A, "", None, 2, "totals meat + fish (Dierlijk - vee + Dierlijk - vis)"),
    # --- MONBIO NACE-class aggregates -----------------------------------------------------
    "C-279": (A, OLIEN, None, 3, "NACE 10.4 olien en vetten"),
    "C-280": (A, OLIEN, None, 3, "NACE 10.4 olien en vetten"),
    "C-464": (A, OLIEN, None, 3, "NACE 10.4 olien en vetten"),
    "C-465": (A, OLIEN, None, 3, "NACE 10.4 olien en vetten"),
    "C-287": (A, DRANKEN, None, 3, "NACE 11 dranken"),
    "C-472": (A, DRANKEN, None, 3, "NACE 11 dranken"),
    "C-283": (A, "", None, 3, "NACE 10.6/10.7 -> aggregate over Bakkerij + Zetmeel + Deegwaren + Maalderij"),
    "C-284": (A, "", None, 3, "NACE 10.6/10.7 -> aggregate over Bakkerij + Zetmeel + Deegwaren + Maalderij"),
    "C-468": (A, "", None, 3, "NACE 10.6/10.7 -> aggregate over Bakkerij + Zetmeel + Deegwaren + Maalderij"),
    "C-469": (A, "", None, 3, "NACE 10.6/10.7 -> aggregate over Bakkerij + Zetmeel + Deegwaren + Maalderij"),
    "C-285": (A, "", None, 3, "NACE 10.8 suiker en chocolade -> aggregate over Chocolade + Suiker"),
    "C-286": (A, "", None, 3, "NACE 10.8 suiker en chocolade -> aggregate over Chocolade + Suiker"),
    "C-470": (A, "", None, 3, "NACE 10.8 suiker en chocolade -> aggregate over Chocolade + Suiker"),
    "C-471": (A, "", None, 3, "NACE 10.8 suiker en chocolade -> aggregate over Chocolade + Suiker"),
    # --- Prodcom product rows: L4 under their subgroup ------------------------------------
    "C-341": (C, OLIEN,   "Margarine en andere eetbare vetten", 4, "Prodcom 104210"),
    "C-531": (C, OLIEN,   "Margarine en andere eetbare vetten", 4, "Prodcom 104210"),
    "C-355": (C, ZETMEEL, "Zetmeel, inuline, tarwegluten, dextrine en ander gewijzigd zetmeel", 4, "Prodcom 106211"),
    "C-546": (C, ZETMEEL, "Zetmeel, inuline, tarwegluten, dextrine en ander gewijzigd zetmeel", 4, "Prodcom 106211"),
    "C-356": (C, ZETMEEL, "Glucose en glucosestroop, fructose en fructosestroop, invertsuiker", 4, "Prodcom 106213"),
    "C-547": (C, ZETMEEL, "Glucose en glucosestroop, fructose en fructosestroop, invertsuiker", 4, "Prodcom 106213"),
    "C-550": (C, ZETMEEL, "Afvallen van zetmeelfabrieken en dergelijke afvallen", 4, "Prodcom 106220"),
    "C-360": (C, BAKKERIJ, "Ontbijtkoek, koekjes en biscuits, wafels en wafeltjes", 4, "Prodcom 107212"),
    "C-552": (C, BAKKERIJ, "Ontbijtkoek, koekjes en biscuits, wafels en wafeltjes", 4, "Prodcom 107212"),
    "C-365": (C, CHOCO,   "Chocolade en andere cacaobevattende bereidingen, in grote verpakkingen", 4, "Prodcom 108221"),
    "C-558": (C, CHOCO,   "Chocolade en andere cacaobevattende bereidingen, in grote verpakkingen", 4, "Prodcom 108221"),
    # the Flemish chocolate estimate sits ABOVE the single Prodcom class (900.000 > 554.394)
    "C-383": (A, CHOCO, None, 4, "Vlaamse chocoladeproductie: totals the L4 chocolate rows beneath"),
    "C-576": (A, CHOCO, None, 4, "Vlaamse chocoladeproductie: totals the L4 chocolate rows beneath"),
    # --- retail: not a commodity. Chain stage split by collection channel; the pair sums. ---
    "C-103": (A, "", None, 2, "retail stage, grootdistributie half; sums with C-104 to C-105"),
    "C-104": (A, "", None, 2, "retail stage, detailhandel half; sums with C-103 to C-105"),
    "C-106": (A, "", None, 2, "retail stage, grootdistributie half; sums with C-107 to C-108"),
    "C-107": (A, "", None, 2, "retail stage, detailhandel half; sums with C-106 to C-108"),
    "C-203": (A, "", None, 2, "retail stage, grootdistributie half; sums with C-204 to C-205"),
    "C-204": (A, "", None, 2, "retail stage, detailhandel half; sums with C-203 to C-205"),
    "C-208": (A, "", None, 2, "retail stage, grootdistributie half; sums with C-209 to C-206"),
    "C-209": (A, "", None, 2, "retail stage, detailhandel half; sums with C-208 to C-206"),
}
# rows the reviewer excluded outright: no placement is needed, they leave the tree
EXCLUDE_NOTE = ("reviewer marked this claim excluded - it leaves the overview entirely, so no "
                "Varia placement is proposed")


def propose(r, prior):
    cid = r["claim_id"]
    name = r["stream_name_NL"].strip()
    row = dict(claim_id=cid, source_short=r["source_short"], reference_year=r["reference_year"],
               chain_L2=r["chain_L2"], quantity_type=r["quantity_type"],
               volume_t_per_yr=r["volume_t_per_yr"], name=name,
               current_L2=r["L2_commodity_group"], current_level=r["level_1to5"],
               proposed_L4="", note="", revision="", DECISION="")
    decided = (prior.get(cid, {}).get("DECISION") or "").strip().lower()

    if cid not in PLAN:                                  # excluded by the reviewer
        row.update(proposed_class="excluded", proposed_L2="", proposed_L3="", proposed_level="",
                   proposed_name=name, basis="reviewer decision", note=EXCLUDE_NOTE,
                   DECISION="skip",
                   revision="unchanged - stays out" if decided == "no" else "")
        return row

    klass, l3, l4, lvl, basis = PLAN[cid]
    is_agg = klass == A
    newname = name if name.upper().startswith("AGGREGAAT") else (AGG_PREFIX + name if is_agg else name)
    row.update(proposed_class=klass,
               proposed_L2="Varia" if l3 else ("Aggregaat" if is_agg else "Varia"),
               proposed_L3=l3, proposed_L4=l4 or "", proposed_level=str(lvl),
               proposed_name=newname, basis=basis)

    # what changed against revision 1, so the reviewer only re-reads what moved
    old = prior.get(cid, {})
    moved = [f for f, new in (("proposed_L3", l3), ("proposed_class", klass),
                              ("proposed_level", str(lvl)), ("proposed_name", newname))
             if (old.get(f) or "").strip() != new]
    if not old:
        row["revision"] = "new"
    elif moved:
        row["revision"] = "CHANGED (" + ", ".join(moved) + ") - re-review"
        row["DECISION"] = ""                                    # clear it: the proposal moved
    else:
        row["revision"] = "unchanged"
        row["DECISION"] = "ok" if decided in ("yes", "ok") else ("skip" if decided in ("no", "skip") else "")
    if is_agg and not l3:
        row["note"] = "placement and coverage for this aggregate are set in aggregate_coverage.csv"
    if l3 in (CHOCO, ZETMEEL):
        row["note"] = ("subgroup split out of a NACE lump; the uncaptured halves ("
                       + UNCAPTURED + ") are named in the aggregates' coverage, not created as "
                       "empty dictionary members")
    return row


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC.name} - run prep/export first")
    rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig"), delimiter=";"))
    targets = [r for r in rows if r["L2_commodity_group"].strip() == "Gemengd"]

    prior = {}
    if OUT.exists():
        for r in csv.DictReader(io.open(OUT, encoding="utf-8-sig"), delimiter=";"):
            prior[r["claim_id"]] = r

    out = [propose(r, prior) for r in targets]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    changed = [r["claim_id"] for r in out if r["revision"].startswith("CHANGED")]
    blank = [r["claim_id"] for r in out if not r["DECISION"].strip()]
    unplanned = [r["claim_id"] for r in targets if r["claim_id"] not in PLAN
                 and (prior.get(r["claim_id"], {}).get("DECISION") or "").strip().lower() != "no"]
    print(f"{OUT.relative_to(HERE.parent)}: {len(out)} rows")
    print(f"  kept in the tree : {sum(1 for r in out if r['proposed_class'] != 'excluded')}")
    print(f"  excluded         : {sum(1 for r in out if r['proposed_class'] == 'excluded')}")
    print("  L3 subgroups used: " + ", ".join(sorted({r['proposed_L3'] for r in out if r['proposed_L3']})))
    print(f"  proposal changed -> DECISION cleared: {len(changed)}")
    if changed:
        for i in range(0, len(changed), 10):
            print("     " + ", ".join(changed[i:i+10]))
    if unplanned:
        print(f"  ! kept by the reviewer but absent from PLAN: {', '.join(unplanned)}")
    print(f"awaiting DECISION: {len(blank)}")


if __name__ == "__main__":
    main()
