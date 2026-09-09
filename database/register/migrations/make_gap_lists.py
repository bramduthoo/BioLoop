# -*- coding: utf-8 -*-
"""SUPERSEDED 2026-09-09 - DO NOT RUN.

This wrote the hand-maintained crosswalks/GAP_LIST.csv, which is retired to
migrations/GAP_LIST_retired_2026-09-09.csv. The gap list is now DERIVED from the data by
tools/make_gap_list.js - note the near-identical name, and that THAT is the live one.
The method is written up in deliverables/README.md. Kept for provenance only.
"""
"""make_gap_lists.py - write the two lists the gap screening exists to produce.

    database/.venv/Scripts/python database/register/make_gap_lists.py

  crosswalks/FIX_LIST.csv   what is WRONG IN THE CURRENT DATA and can be fixed without any new
                            source: a stream sitting above L4, or one marked AGGREGAAT because its
                            name bundles two items when the bundle is itself one physical stream.
                            Human-gated: fill DECISION, then apply.

  crosswalks/GAP_LIST.csv   what is GENUINELY MISSING: a sector or product where a large total
                            exists but the detail beneath it was never published, so no
                            re-levelling can reach it. This is the list to hunt sources with.

Both are ';'-delimited with a UTF-8 BOM (Belgian-locale Excel), per database/CLAUDE.md.
FIX_LIST refuses to overwrite once any DECISION is filled.

THE TEST THAT SEPARATES THE TWO LISTS, and it is the reviewer's own:
    a row whose name bundles several items is still ONE SELECTABLE STREAM when those items
    ARISE TOGETHER and cannot be separated in practice - 'Zemelen, slijpsel en andere resten van
    het bewerken van granen' leaves the mill as one material. It is a GAP when the bundle hides
    distinctions a buyer would need and only a new source can supply - 'Eetbare slachtafvallen
    van runderen, varkens, schapen, geiten en paarden' can be sold as one stream, but nothing in
    the corpus says how much of it is beef and how much is pork.

Some rows are on BOTH lists, and that is correct: promoting the offal bundles makes two usable
streams available today (FIX_LIST F1, F2) while the per-species split stays an open gap (G-04).

NOTE ON SOURCES: sources carrying `_RETIRED` in inbox/ (S001, S005, S006, S086) are excluded from
every candidate below. They were retired deliberately and are not to be proposed again.
"""
import csv, io, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "crosswalks" / "FIX_LIST.csv"
GAP = HERE / "crosswalks" / "GAP_LIST.csv"

FIX_COLS = ["fix_id", "claim_ids", "source", "current_state", "proposed_fix", "new_L4_name",
            "mass_t_per_yr", "effect_on_selection", "caution", "DECISION", "NOTES"]

FIX_ROWS = [
 dict(fix_id="F1", claim_ids="C-298; C-483", source="MONBIO 4.0; MONBIO 3.0",
   current_state="AGGREGAAT at L3, allocatable=no - invisible to the selection",
   proposed_fix="promote to L4: a defined material category collected and rendered as ONE stream, "
     "not a leftover class of the nomenclature",
   new_L4_name="Niet-eetbare slachtafvallen",
   mass_t_per_yr="169051; 142405",
   effect_on_selection="ENTERS the shortlist at rank 11 (simulated)",
   caution="Prodcom 101160. Still says nothing about which species it came from - that half stays "
     "open as G-04.",
   DECISION="", NOTES=""),

 dict(fix_id="F2", claim_ids="C-295; C-480", source="MONBIO 4.0; MONBIO 3.0",
   current_state="AGGREGAAT at L3, allocatable=no - invisible to the selection",
   proposed_fix="promote to L4: edible offal of the red-meat species, saleable as one stream",
   new_L4_name="Eetbare slachtafvallen (rood vlees)",
   mass_t_per_yr="82576; 75397",
   effect_on_selection="ENTERS the shortlist at rank 22 (simulated)",
   caution="Bundles runderen, varkens, schapen, geiten and paarden. Accepting it means accepting "
     "a mixed-species stream; the per-species split is G-04 and needs a source.",
   DECISION="", NOTES=""),

 dict(fix_id="F3", claim_ids="C-381; C-574  (vs C-362; C-554)", source="MONBIO 4.0; MONBIO 3.0",
   current_state="L3 with L4 blank - the grondgebied melasse is invisible while its Prodcom twin "
     "sits at L4 under Varia > Suiker",
   proposed_fix="put the grondgebied rows at L4 'Melasse' under Varia > Suiker AND pick ONE basis "
     "for the node - grondgebied (what arises on Flemish sites) or export-proxy (a share of "
     "Belgian production). Retire or cross-reference the other, as the bietenpulp pair already does.",
   new_L4_name="Melasse",
   mass_t_per_yr="47805; 56806   (export-proxy twin: 91958; 111298)",
   effect_on_selection="stays in the shortlist either way; rank 15 on the export-proxy basis, 25 "
     "on grondgebied",
   caution="DO NOT APPLY MECHANICALLY. Promoting without choosing a basis makes the two siblings "
     "and derive.js ADDS them: melasse reads 168.104 t, a 51% inflation. Putting it on the crop "
     "ladder instead creates a SECOND 'Melasse' stream and pushes Appel out of the shortlist.",
   DECISION="", NOTES=""),

 dict(fix_id="F4", claim_ids="C-273; C-457", source="MONBIO 4.0; MONBIO 3.0",
   current_state="L3 with L4 blank",
   proposed_fix="promote to L4 - a single named stream, and the ONLY residual figure the Visserij "
     "stage has",
   new_L4_name="Teruggegooide vis",
   mass_t_per_yr="7500; 7707",
   effect_on_selection="becomes selectable at rank 39 - outside the shortlist of 24",
   caution="The corpus' entire selectable fish mass is 839 t across 32 rows, so this single row is "
     "nine times everything else in fisheries.",
   DECISION="", NOTES=""),

 dict(fix_id="F5", claim_ids="C-334; C-523", source="MONBIO 4.0; MONBIO 3.0",
   current_state="L3, L4 blank, NO AGGREGAAT prefix - neither selectable nor an aggregate, so "
     "68.000 t appears in no figure at all",
   proposed_fix="prefix with 'AGGREGAAT - ', allocatable=no, and add the registry line. It is a "
     "genuine leftover class ('uit ANDERE oliehoudende zaden') and stays unselectable.",
   new_L4_name="",
   mass_t_per_yr="68000; 68000",
   effect_on_selection="none directly - but it REPAIRS MONBIO's reported totals: L1 rises from "
     "5.451.052 to 6.341.552 (4.0) and 5.944.027 to 6.935.676 (3.0), and the impossible ceilings "
     "104,6% / 102,8% fall to 90,6% / 89,3%",
   caution="The registry line is not optional. Without it derive re-reads the whole oilseed branch.",
   DECISION="", NOTES=""),

 dict(fix_id="F6", claim_ids="C-284; C-469; C-286; C-471", source="MONBIO 4.0; MONBIO 3.0",
   current_state="AGGREGAAT at L2 under Varia with L3 blank, while the rows they total sit under "
     "Plantaardig - akkerbouw > Granen and Varia > Zetmeel / Suiker",
   proposed_fix="re-parent them onto the branch they actually total, in aggregate_coverage.csv. "
     "The compositions are known and exact: 563.000 = zemelen 278.865 + zetmeelafvallen 284.549; "
     "394.000 = melasse 56.806 + bietenpulp 337.649.",
   new_L4_name="",
   mass_t_per_yr="671000; 563000; 403000; 394000",
   effect_on_selection="none - these are totals and never selectable. It makes them reconcilable "
     "against their components instead of against nothing.",
   caution="This is the same open decision as G-05: does a processing residue live under its crop "
     "or under its Varia sector? Answer that once and apply it to zemelen/gries/bostel too.",
   DECISION="", NOTES=""),

 dict(fix_id="F7", claim_ids="C-342; C-532", source="MONBIO 4.0; MONBIO 3.0",
   current_state="AGGREGAAT at L3, allocatable=no",
   proposed_fix="LEAVE AS IS - recorded here so it is not proposed again",
   new_L4_name="",
   mass_t_per_yr="1019363; 1349271",
   effect_on_selection="none, deliberately",
   caution="'Perskoeken en andere vaste afvallen van plantaardige olien en vetten (Prodcom 104141)' "
     "looks like the zemelen case and is not: it is a RIVAL Prodcom measurement of the same "
     "material as C-335/C-524, whose components (Kool- en raapzaad 681.000, Lijnzaad, Soja, "
     "Zonnebloem) are already selectable. Promoting it double-counts 1,0-1,35 Mt. This was tried "
     "on 2026-09-03 and reverted.",
   DECISION="", NOTES=""),
]

GAP_COLS = ["gap_id", "sector_or_product", "chain_stage", "what_exists_now", "claim_ids",
            "mass_t_per_yr", "what_detail_is_missing", "why_it_matters",
            "source_type_to_find", "named_candidate_in_sheet", "status"]

GAP_ROWS = [
 dict(gap_id="G-10", sector_or_product="Aardappelverwerking", chain_stage="Voedingsindustrie",
   what_exists_now="one sector total, zero component rows",
   claim_ids="C-094 (2023); C-195 (2020)", mass_t_per_yr="621063; 653463",
   what_detail_is_missing="aardappelschillen, stoomschillen, aardappelvezel, aardappeleiwit - none "
     "of these words appears anywhere in the 801 claims. The only potato food-industry residual "
     "row is C-314/C-501, which is a dried-potato PRODUCT, not residue.",
   why_it_matters="The largest food-industry block with no detail at all, in the sector Flanders "
     "leads in Europe. Each fraction would be a named, homogeneous, well-characterised L4 stream.",
   source_type_to_find="a processing-sector source that carves by PROCESS: peeling, steam peeling, "
     "cutting, drying",
   named_candidate_in_sheet="S058 (ILVO TransBio WP3) - no PDF yet; otherwise Belgapom / VLAM, "
     "not in the sheet",
   status="open"),

 dict(gap_id="G-04", sector_or_product="Vlees - per diersoort", chain_stage="Voedingsindustrie",
   what_exists_now="a sector total and two category totals; after FIX_LIST F1+F2 also two "
     "mixed-species streams",
   claim_ids="C-277 / C-462 (sector); C-308 / C-493 (eetbaar totaal); C-298 / C-295 (promotable)",
   mass_t_per_yr="631000; 217672; 169051; 82576",
   what_detail_is_missing="a per-species split. The register holds production per species "
     "(varken 1.253.312 t, rund 263.322 t) but nothing linking production to offal yield, so the "
     "split cannot be derived - and deriving it would break the register's own rule.",
   why_it_matters="Applying F1 and F2 gives two usable streams today, but a buyer needs to know "
     "how much is beef and how much is pork. That half only a source can answer.",
   source_type_to_find="a slaughterhouse or rendering-sector source reporting by-products per "
     "species, or a species-resolved rendering figure",
   named_candidate_in_sheet="none - the sheet has no slaughter/rendering source that is not retired",
   status="open (half fixable now via F1/F2)"),

 dict(gap_id="G-09", sector_or_product="Zuivelverwerking - wei", chain_stage="Voedingsindustrie",
   what_exists_now="one sector nevenstroom figure with no components",
   claim_ids="C-282; C-467 (70.000 each); OVAM Melk C-100 / C-200",
   mass_t_per_yr="70000; 135226",
   what_detail_is_missing="wei / kaaswei / weipoeder / melkserum / permeaat / retentaat / lactose - "
     "NOT ONE of these appears anywhere in the workbook, in any role or status.",
   why_it_matters="The register holds koemelk 4.450.280 t and kaas en wrongel 101.256 t. Cheese "
     "separates roughly nine parts whey to one part curd (industry rule of thumb, deliberately not "
     "derived here), so a 70.000 t dairy nevenstroom cannot be counting whey. Whey is treated as a "
     "product and falls outside both monitors' definitions.",
   source_type_to_find="a dairy-sector source: BCZ, or a Flemish dairy-processing study",
   named_candidate_in_sheet="none - no dairy-processing source in the 91-row sheet",
   status="open"),

 dict(gap_id="G-11", sector_or_product="Dranken", chain_stage="Voedingsindustrie",
   what_exists_now="a subgroup total; exactly one named beverage stream in the whole corpus",
   claim_ids="C-095 (2023); C-196 (2020); bostel C-397 / C-590",
   mass_t_per_yr="378539; 343166",
   what_detail_is_missing="draf / DDGS, biergist, vinasse, sapresidu. Bostel (134.653 t) is the "
     "only named beverage side stream, so at most a third of the OVAM figure has a name. Gist "
     "appears only as a production row.",
   why_it_matters="Brewing and distilling are large, well-characterised Flemish sectors and their "
     "side streams are among the best documented in the literature - just not here.",
   source_type_to_find="a brewers' / distillers' federation figure, or a biomethane-potential "
     "study that lists its input streams",
   named_candidate_in_sheet="S053 (Biogas-E, input streams) or S012 (Vlaco) - both destination-side "
     "and partial; S058",
   status="open"),

 dict(gap_id="G-12", sector_or_product="Cacao en chocolade", chain_stage="Voedingsindustrie",
   what_exists_now="an aggregate NAMED for the sector that contains none of it",
   claim_ids="C-286; C-471 (MONBIO); C-097; C-198 (OVAM)",
   mass_t_per_yr="403000; 394000; 191054; 130271",
   what_detail_is_missing="cacaodoppen, cacaoschillen, cacaoperskoek - absent from the workbook. "
     "The 'suiker EN CHOCOLADE' aggregate is provably all sugar: melasse 56.806 + bietenpulp "
     "337.649 = 394.455 against a printed 394 kton.",
   why_it_matters="Belgium is one of Europe's largest cocoa processors and the plants are in "
     "Flanders. Cocoa shell is clean, dry and has an established market. OVAM lumps it with sugar and prepared meals (C-097, 191.054 t) and never goes below that lump either.",
   source_type_to_find="a cocoa/chocolate sector source or a plant-level study",
   named_candidate_in_sheet="none - Choprabisco is not in the sheet",
   status="open"),

 dict(gap_id="G-01", sector_or_product="Retail en grootdistributie", chain_stage="Retail & grootdistributie",
   what_exists_now="17 rows, every one an aggregate at level 2, zero component rows",
   claim_ids="C-105; C-103; C-104; C-203..C-214", mass_t_per_yr="132082",
   what_detail_is_missing="any product-group split. Retail waste concentrates in bakery goods, "
     "bananas and soft fruit, ready meals and fresh produce nearing date.",
   why_it_matters="Narrow, high-volume, well-known streams - exactly what BioMobi selects - and "
     "the stage is reported as one number.",
   source_type_to_find="a retailer-federation study reporting by product group",
   named_candidate_in_sheet="S067 (Comeos, 64.271 t) - no PDF yet; S035 (Foodsavers); S041 "
     "(Eurostat NACE G47, Belgium only)",
   status="open"),

 dict(gap_id="G-13", sector_or_product="Bakkerij", chain_stage="Voedingsindustrie",
   what_exists_now="a subgroup total, zero components",
   claim_ids="C-093 (2023); C-194 (2020)", mass_t_per_yr="122276; 37755",
   what_detail_is_missing="broodoverschot, bakkerijretour, deegresten. The register holds Vers "
     "brood production 303.437 t and no bread-waste stream.",
   why_it_matters="Also note the 3,2x jump between the two OVAM editions (37.755 -> 122.276), "
     "unexplained on the rows - a real change or a method change.",
   source_type_to_find="a NACE- or EURAL-carved waste statistic, or a bakery-federation figure",
   named_candidate_in_sheet="S025 (OVAM bedrijfsafval, ref. yr 2022, EURAL carving) - no PDF yet; "
     "S067 for the retail half",
   status="open"),

 dict(gap_id="G-14", sector_or_product="Olien en vetten, en frituurvet", chain_stage="Voedingsindustrie",
   what_exists_now="a subgroup total, zero components",
   claim_ids="C-096 (2023); C-197 (2020)", mass_t_per_yr="95895; 57723",
   what_detail_is_missing="frituurvet / afgewerkt vet - absent from the workbook. MONBIO's oilseed "
     "meal sits in a different branch and is Belgian (G-06).",
   why_it_matters="Used frying fat is separately collected in Flanders, so a collector figure "
     "should exist.",
   source_type_to_find="used-oil collector or federation data; a NACE/EURAL waste statistic",
   named_candidate_in_sheet="S025 - no PDF yet",
   status="open"),

 dict(gap_id="G-15", sector_or_product="Voedergewassen, industriele gewassen, peulvruchten",
   chain_stage="Primaire productie",
   what_exists_now="three L3 residual aggregates with ZERO component rows in either edition",
   claim_ids="C-242 / C-423; C-243 / C-424; C-244 / C-425",
   mass_t_per_yr="101780; 55065; 46542  (MONBIO 4.0)",
   what_detail_is_missing="a per-crop residue figure for any of the three.",
   why_it_matters="The asymmetry is the tell: the PRODUCTION side of these same groups is fully "
     "resolved to L4 - Voedermais 5.395.992 t, Gras 3.939.458 t, Voederbiet 360.547 t, Cichorei "
     "90.000 t, Vlas 23.000 t. The dictionary has the members; only the residual side is missing.",
   source_type_to_find="a field-residue ratio source per fodder / fibre / pulse crop",
   named_candidate_in_sheet="S077 (Vlaanderen Circulair, 14 crop types) - a re-aggregation of "
     "MONBIO, not a new measurement",
   status="open"),

 dict(gap_id="G-06", sector_or_product="Oliezaadschroot - geografie", chain_stage="Voedingsindustrie",
   what_exists_now="four selectable streams, all on a BELGIAN figure",
   claim_ids="C-330..C-333; C-519..C-522",
   mass_t_per_yr="857931 (Kool- en raapzaad); 245000; 170000; 58000",
   what_detail_is_missing="a Flemish crush or press figure. MONBIO prints these as 'ruwe productie "
     "(Belgie)' because crushing statistics are only published nationally.",
   why_it_matters="Includes the corpus' #2 stream. Every other figure in the selection is Flemish, "
     "so the shortlist rests on a national denominator at its second-largest entry. The register's "
     "one sanctioned Belgium->Flanders equivalence covers fishing ports only.",
   source_type_to_find="a Flemish crush figure, or a source stating the Flemish share of Belgian crush",
   named_candidate_in_sheet="S058 - no PDF yet", status="open"),

 dict(gap_id="G-17", sector_or_product="Visverwerking", chain_stage="Voedingsindustrie / Visserij",
   what_exists_now="32 selectable rows totalling 839 t, all opgehouden vis at the auctions",
   claim_ids="C-022..C-034; C-130..C-143", mass_t_per_yr="839",
   what_detail_is_missing="visafval, visresten, visgraat, viskop - absent. The Visserij stage has "
     "zero L4/L5 rows; its only figure is the discards row of FIX_LIST F4.",
   why_it_matters="Fish processing residue is a characterised protein and oil stream and the "
     "register has none of it.",
   source_type_to_find="an ILVO fisheries or fish-processing source",
   named_candidate_in_sheet="one sheet row is flagged 'yes (FISHERIES side streams)' - locate it",
   status="open"),

 dict(gap_id="G-02", sector_or_product="Producentenorganisaties en veilingen",
   chain_stage="Producentenorganisaties/veilingen",
   what_exists_now="the stage reported at level 2 only, plus seven auction rows from S065",
   claim_ids="C-087..C-089; C-186..C-188; C-769..C-775", mass_t_per_yr="15189; 5190",
   what_detail_is_missing="whether the 15.189 t is the whole stage or only EU-subsidised withdrawal.",
   why_it_matters="Two readings lead to opposite conclusions. If doordraai is genuinely small "
     "because the GMO regime is a crisis instrument, this is NOT a gap and the entry closes.",
   source_type_to_find="FACT-CHECK FIRST, do not commission: VBT or one auction's jaarverslag "
     "against the 15.189 t",
   named_candidate_in_sheet="n/a", status="needs fact-check before it is treated as a gap"),

 dict(gap_id="G-16", sector_or_product="Eieren en eierschalen", chain_stage="Primaire productie",
   what_exists_now="five rows, all at L3, no L4 anywhere",
   claim_ids="C-047; C-060; C-170; C-071; C-182", mass_t_per_yr="1282",
   what_detail_is_missing="eierschalen - absent from the workbook.",
   why_it_matters="Small in tonnage, but a complete absence in a sector Flanders has.",
   source_type_to_find="a poultry / egg sector source", named_candidate_in_sheet="none",
   status="open"),

 dict(gap_id="G-19", sector_or_product="Deegwaren, bereide maaltijden en dieetvoeding",
   chain_stage="Voedingsindustrie",
   what_exists_now="two OVAM subgroup lumps, no components; MONBIO resolves only the maalderij and "
     "zetmeel part of them (Zemelen, Gries, Zetmeel)",
   claim_ids="C-099; C-199 (deegwaren/dieetvoeding/zetmeel/maalderijen); C-097; C-198 (suiker/"
     "chocolade/bereide maaltijden)",
   mass_t_per_yr="167446; 78995; 191054; 130271",
   what_detail_is_missing="anything below the lump for deegwaren, bereide maaltijden, dieetvoeding "
     "and sauzen. Their PRODUCTION rows exist but were retired by the reviewer, so the register "
     "carries neither side.",
   why_it_matters="Completes the OVAM food-industry partition: its eight subgroups sum to 2.017.721 "
     "against a printed 2.017.748, so nothing else is hiding there. This is the last unclaimed "
     "piece. LOW PRIORITY - prepared-food waste is heterogeneous and a poor BioMobi candidate; it "
     "is listed so the partition is complete, not because it should be hunted.",
   source_type_to_find="a NACE- or EURAL-carved waste statistic",
   named_candidate_in_sheet="S025 - no PDF yet", status="open, low priority"),

 dict(gap_id="G-18", sector_or_product="Zeven MONBIO 4.0 cellen, vertrouwelijk",
   chain_stage="Voedingsindustrie",
   what_exists_now="values for 2020 only; the 2021 edition suppresses them",
   claim_ids="C-550 (zetmeel); C-555 (bietenpulp); C-560 (koffie) + 4 more",
   mass_t_per_yr="284549; 661550; 36953",
   what_detail_is_missing="the 2021 values. A confidential Prodcom cell is an absence, never a "
     "zero, so no re-reading of S091 will produce them.",
   why_it_matters="Zetmeel is the #5 stream in the shortlist and is single-source for this reason "
     "alone - not because the register missed it.",
   source_type_to_find="suppression is per year, so a later edition may un-suppress a different "
     "subset; also Eurostat Prodcom directly",
   named_candidate_in_sheet="S078 (MONBIO web portal) - a scraping route, not a PDF",
   status="open"),
]


def write(path, cols, rows, gated):
    if gated and path.exists():
        prev = list(csv.DictReader(io.open(path, encoding="utf-8-sig"), delimiter=";"))
        if any((p.get("DECISION") or "").strip() for p in prev):
            sys.exit("REFUSING: %s already has filled DECISION cells." % path.name)
    path.parent.mkdir(exist_ok=True)
    with io.open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter=";")
        w.writeheader(); w.writerows(rows)
    print("wrote %-14s %d rows" % (path.name, len(rows)))


if __name__ == "__main__":
    write(FIX, FIX_COLS, FIX_ROWS, gated=True)
    write(GAP, GAP_COLS, GAP_ROWS, gated=False)
    print("\nFIX_LIST: %d fixes, of which %d change the shortlist"
          % (len(FIX_ROWS), sum("ENTERS" in r["effect_on_selection"] for r in FIX_ROWS)))
    print("GAP_LIST: %d gaps needing a source" % len(GAP_ROWS))
