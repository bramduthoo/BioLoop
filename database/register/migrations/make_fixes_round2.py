"""Round 2 of the structural fixes, rebuilt from the reviewer's remarks on round 1.

Round 1 asked one question ("this Prodcom row is at L3, should it be L4?") and the reviewer's
answers showed the question was too blunt. Three distinct things were hiding inside it:

  1. "If the name is a sum of things or a collection of parts which already exist, this will
     almost always be an aggregate."  ->  the row gets the `AGGREGAAT - ` prefix instead of an L4.
     Prodcom residual categories are exactly this: *Andere ...*, *... en andere ...*, *van alle
     soorten*, *n.e.g.* are nomenclature buckets, not products.
  2. "We kind of made 2 distinctions in the commodity ladder, with the crops but also some sectors
     in varia."  ->  a processing product filed under the CROP it came from belongs under the
     Varia SECTOR instead. Bread is not a cereal; refined sugar is not a beet.
  3. The rest are genuine single products and simply move to L4, as round 1 proposed.

It also carries the placement corrections the reviewer wrote on `REVIEW_2026-08-31.csv`, and the
`B-level-mismatch` rows re-proposed the way the reviewer asked ("why level 2 suddenly?") - by
giving the row its real L2 (`Varia`) instead of the placeholder `Aggregaat`, so that level 2 means
"this row sits at L2" and the level it *totals* stays in aggregate_coverage.totals_level.

    database/.venv/Scripts/python.exe database/register/make_fixes_round2.py
"""
import csv, io, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "streams.json"
ROUND1 = HERE / "crosswalks" / "FIXES_2026-09-01.csv"
OUT = HERE / "crosswalks" / "FIXES_ROUND2.csv"
AGG = "AGGREGAAT - "
CODE_RE = re.compile(r"\s*\(Prodcom[^)]*\)\s*$")

COLUMNS = ["fix_id", "rule", "claim_id", "source_short", "L1_role", "chain_L2",
           "volume_t_per_yr", "current_path", "current_name",
           "SET_L2_commodity_group", "SET_L3_commodity_subgroup", "SET_L4_ingredient",
           "SET_level_1to5", "SET_stream_name_NL",
           "why", "confidence", "DECISION_fix"]

VARIA, BAK, SUIK, ZET, CHOC = "Varia", "Bakkerij", "Suiker", "Zetmeel en zetmeelproducten", "Chocolade"

# --- decisions keyed by the product name, so both editions of a stream get the same answer ----
# ("A", ...)  -> becomes an AGGREGAAT: a nomenclature bucket, not a product
# ("L4", L2, L3) -> a genuine product; None keeps the row's current L2/L3
AGGREGATE_NAMES = {
    # the reviewer marked these explicitly on round 1
    "Zemelen, slijpsel en andere resten van het bewerken van granen": "residual bucket: 'en andere resten'",
    "Andere bereidingen en conserven, van vlees, van slachtafval of van bloed": "residual bucket: 'Andere ...'",
    "Niet-eetbare ruwe slachtafvallen": "covers every inedible offal type, not one product",
    "Rund-, schapen-, geiten- of varkensvet": "four species in one cell",
    "Worst van alle soorten, van vlees, van slachtafval of van bloed": "'van alle soorten'",
    "Eetbare slachtafvallen van runderen, varkens, schapen, geiten en paarden, vers of gekoeld": "five species in one cell",
    "Perskoeken en andere vaste afvallen van plantaardige olien en vetten": "residual bucket: 'en andere vaste afvallen'",
    "Bietenpulp, uitgeperst suikerriet en andere afvallen van de suikerindustrie": "residual bucket: 'en andere afvallen'",
    # same pattern, applied to the rows the reviewer deferred
    "Ander vlees en andere eetbare slachtafvallen, vers, gekoeld of bevroren": "residual bucket: 'Ander ... en andere ...'",
    "Ander vlees en eetbare slachtafval, gezouten, gepekeld, gedroogd of gerookt": "residual bucket: 'Ander vlees ...'",
    "Andere plantaardige olien, ruw": "residual bucket: 'Andere ...'",
    "Andere olien en fracties daarvan, geraffineerd": "residual bucket: 'Andere ...'",
    "Andere bereide, gedroogde of verduurzaamde vruchten": "residual bucket: 'Andere ...'",
    "Andere groenten, op andere wijze verduurzaamd dan in azijn of azijnzuur (dus NIET in azijn)": "residual bucket: 'Andere ...'",
    "Ontbijtgranen en andere graanproducten": "residual bucket: 'en andere graanproducten'",
    "Gries, griesmeel en pellets van granen, n.e.g.": "three forms in one cell, and n.e.g.",
    "Meel van andere granen": "residual bucket: 'andere granen'",
    "Vis, op andere wijze bereid of verduurzaamd": "residual bucket: 'op andere wijze'",
    "Visfilets en ander visvlees, vers of gekoeld": "residual bucket: 'en ander visvlees'",
    "Yoghurt en andere gegiste of aangezuurde melk of room": "residual bucket: 'en andere ...'",
    "Vogeleieren uit de schaal en eigeel, vers of verduurzaamd, ovoalbumine": "three distinct products in one cell",
    "Jam, vruchtengelei, vruchtenmoes en vruchtenpasta": "four products in one cell",
    "Vruchten en noten, ook indien gestoomd of in water gekookt, bevroren": "fruit and nuts in one cell",
    "Bostel (brouwerijafval) en afvallen van branderijen": "brewery and distillery residues in one cell",
}
# name -> (L2, L3) when the row must move from the crop ladder to a Varia sector
MOVE = {
    "Vers brood": (VARIA, BAK, "bread is a bakery product, not a cereal"),
    "Mengsels voor de bereiding van bakkerijproducten": (VARIA, BAK, "a bakery input, not a cereal"),
    "Riet- en beetwortelsuiker, geraffineerd - productie van het Vlaamse bedrijf (sites in Vlaanderen en Wallonie)":
        (VARIA, SUIK, "refined sugar from cane AND beet - a sector product, not one crop"),
    "Melasse": (VARIA, SUIK, "a sugar-refining product, not a beet"),
    "Bietenpulp, uitgeperst suikerriet en andere afvallen van de suikerindustrie":
        (VARIA, SUIK, "a sugar-industry residue; sits oddly beside an L4 of suikerbieten"),
}
# the reviewer's placement corrections written on REVIEW_2026-08-31.csv
REVIEW_FIX = {
    "C-355": (VARIA, ZET, None, "A", "zetmeel, inuline, tarwegluten and dextrine are each L4 under "
              "this L3, so the row is their aggregate"),
    "C-546": (VARIA, ZET, None, "A", "as C-355"),
    "C-356": (VARIA, SUIK, None, "A", "glucose, fructose and invertsuiker are sugars, NOT starch - "
              "they belong under a new L3 Suiker, and the row is their aggregate"),
    "C-547": (VARIA, SUIK, None, "A", "as C-356"),
    "C-365": (VARIA, CHOC, None, "A", "aggregate within L3 Chocolade over the cacao products"),
    "C-558": (VARIA, CHOC, None, "A", "as C-365"),
    "C-550": (VARIA, ZET, "Zetmeel", "L4", "the waste figure belonging to L4 Zetmeel"),
}


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC.name} - run prep_data.py first")
    claims = {c["id"]: c for c in json.load(io.open(SRC, encoding="utf-8"))["claims"]}
    if not ROUND1.exists():
        sys.exit(f"missing {ROUND1.name}")
    r1 = list(csv.DictReader(io.open(ROUND1, encoding="utf-8-sig"), delimiter=";"))
    prior = {}
    if OUT.exists():
        for r in csv.DictReader(io.open(OUT, encoding="utf-8-sig"), delimiter=";"):
            prior[r["claim_id"]] = r.get("DECISION_fix", "")

    rows = []

    def emit(cid, rule, why, conf, l2="", l3="", l4="", lvl="", nm=""):
        c = claims.get(cid)
        if not c:
            return
        rows.append(dict(rule=rule, claim_id=cid, source_short=c.get("ed") or "",
                         L1_role=c.get("role") or "", chain_L2=c.get("st") or "",
                         volume_t_per_yr=c.get("v") or 0,
                         current_path=" > ".join(x for x in (c.get("l2"), c.get("l3"), c.get("l4")) if x),
                         current_name=c.get("name") or "",
                         SET_L2_commodity_group=l2, SET_L3_commodity_subgroup=l3,
                         SET_L4_ingredient=l4, SET_level_1to5=lvl, SET_stream_name_NL=nm,
                         why=why, confidence=conf, DECISION_fix=prior.get(cid, "")))

    # --- the reviewer's own placement corrections ----------------------------------------
    for cid, (l2, l3, l4, kind, why) in REVIEW_FIX.items():
        c = claims.get(cid)
        if not c:
            continue
        if kind == "A":
            nm = c["name"] if c["name"].upper().startswith("AGGREGAAT") else AGG + c["name"]
            emit(cid, "review-fix -> aggregate", why, "high", l2, l3, "", "3", nm)
        else:
            emit(cid, "review-fix -> L4", why, "high", l2, l3, l4, "4", "")

    # --- B rows, re-proposed the way the reviewer asked ------------------------------------
    for r in r1:
        if r["fix_class"] != "B-level-mismatch":
            continue
        if (r.get("DECISION_fix") or "").strip().lower() != "fix":
            continue
        emit(r["claim_id"], "B - give the row its real L2",
             "it sits at L2 under Varia and totals L3 entries; 'Aggregaat' was a placeholder L2. "
             "level 2 = where the row sits; what it totals stays in aggregate_coverage.totals_level",
             "high", VARIA, "", "", "2", "")

    # --- A rows still open ------------------------------------------------------------------
    for r in r1:
        if r["fix_class"] != "A-prodcom-level":
            continue
        d = (r.get("DECISION_fix") or "").strip().lower()
        if d not in ("fix", "0", ""):
            continue
        cid = r["claim_id"]
        c = claims.get(cid)
        if not c or cid in REVIEW_FIX:
            continue
        prod = CODE_RE.sub("", c["name"]).strip()
        mv = MOVE.get(prod)
        if prod in AGGREGATE_NAMES:
            why = AGGREGATE_NAMES[prod]
            l2, l3 = (mv[0], mv[1]) if mv else ("", "")
            nm = c["name"] if c["name"].upper().startswith("AGGREGAAT") else AGG + c["name"]
            emit(cid, "A -> aggregate (collection, not a product)",
                 why + (" · " + mv[2] if mv else ""), "high" if not mv else "medium",
                 l2, l3, "", "3" if l3 else "", nm)
        elif mv:
            emit(cid, "A -> move to a Varia sector, then L4", mv[2], "medium",
                 mv[0], mv[1], prod, "4", "")
        else:
            # A Prodcom dairy class routinely pairs two products ("Melk en room", "Kaas en
            # wrongel"). Strictly that is the collection pattern, but the reviewer approved the
            # analogous "Verwerkte vloeibare melk (incl. karnemelk)" and "Zuivelproducten, n.e.g."
            # as L4 in round 1, so these follow that precedent - flagged, not assumed.
            paired = bool(re.search(r"\ben\s+(room|wrongel|zuivelpasta|roompoeder)", prod, re.I))
            emit(cid, "A -> L4 (single product)",
                 ("names two products, but the reviewer approved the analogous dairy rows as L4 "
                  "in round 1 - confirm or flip the whole dairy block together"
                  if paired else "no collection wording in the name; a genuine single product"),
                 "medium" if paired else "high", "", "", prod, "4", "")

    order = {"review-fix": 0, "B -": 1, "A -> aggregate": 2, "A -> move": 3, "A -> L4": 4}
    rows.sort(key=lambda r: (min((v for k, v in order.items() if r["rule"].startswith(k)), default=9),
                             -(r["volume_t_per_yr"] or 0)))
    for i, r in enumerate(rows, 1):
        r["fix_id"] = f"G-{i:03d}"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter=";", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    import collections
    cnt = collections.Counter(r["rule"] for r in rows)
    print(f"{OUT.relative_to(HERE.parent)}: {len(rows)} rows")
    for k, v in cnt.most_common():
        vol = sum(r["volume_t_per_yr"] or 0 for r in rows if r["rule"] == k)
        print(f"   {k:44} {v:>3} rows  {vol:>13,.0f} t/yr")
    newmem = sorted({r["SET_L3_commodity_subgroup"] for r in rows if r["SET_L3_commodity_subgroup"]})
    print("   L3 subgroups used: " + ", ".join(newmem))
    print(f"awaiting DECISION_fix: {sum(1 for r in rows if not (r['DECISION_fix'] or '').strip())}")


if __name__ == "__main__":
    main()
