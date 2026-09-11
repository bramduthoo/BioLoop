"""Round 2 of the composition harvest: what was read off each source, as data.

    ../.venv/Scripts/python tools/round2_data.py    ->  ../extraction/round2/<code>.json

This file is APPEND-ONLY and is the transcription of record for round 2. One entry per
target stream; running the script rewrites that stream's JSON. A correction is made
HERE, never in the database and never in the generated review page.

Round 2 is ADDITIVE to round 1. Where a stream was already extracted on 2026-09-09
(`build_round1.py`), this file holds only what round 1 did not take -- chiefly
Feedipedia's Minerals and Secondary metabolites tables, which round 1 skipped, and
further Phyllis2 records. The review merges both.

A table entry is:
    ("<source_key>", "<source_ref>", "<variant as the source names it>", "<basis>",
     [ (parameter, unit, avg, sd, min, max, n, predicted, *optional note), ... ])
`predicted` is the source's asterisk; it becomes value_origin. An empty string is an
empty cell in the source, never a zero.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction" / "round2"

# Sources introduced in round 2. Round-1 keys are reused unchanged.
SOURCES = {
    "feedtables-inrae-cirad-afz-fao": dict(
        source_type="dataset", year=2017, kind="compilation",
        title="Tables of composition and nutritional values of feed materials (INRAE, CIRAD, AFZ, FAO)",
        url="https://www.feedipedia.org/",
        notes="Compilation of analyses from private and public feed laboratories, mostly France "
              "and Western Europe (feedtables.com, Principles and methods). Mean, SD, min, max and "
              "n on every value. An asterisk marks a value PREDICTED from a regression equation; "
              "which equation is not published, so a predicted value cannot be checked, only "
              "judged plausible."),
    "phyllis2-tno": dict(
        source_type="dataset", year=2026, kind="primary-indexed",
        title="Phyllis2 - database for the physico-chemical composition of (treated) lignocellulosic biomass",
        url="https://phyllis.nl/",
        notes="Each record cites its own literature reference, so provenance resolves to a paper. "
              "Fuel-oriented set: proximate, ultimate CHONS, Cl, LHV/HHV, ash oxides - no Weende "
              "and no Van Soest fibre. Sibling-fraction records exist for several crops and are "
              "used only where they match the object (see the maize stover note)."),
}

# ---------------------------------------------------------------------------
# The items, in descending tonnage order. Append as each is finished.
# ---------------------------------------------------------------------------

ITEMS: dict[str, dict] = {}

ITEMS["mais-stro"] = dict(
    status="done",
    note="Round 1 took Feedipedia's Main analysis (node 16072) and Phyllis2 #704. Round 2 adds "
         "the Minerals and Secondary metabolites tables that round 1 skipped. Only STOVER "
         "records feed this object; Phyllis2's corn stalks / corn cob / maize leaf records are "
         "fractions of it and are deliberately not used.",
    searched=["Feedipedia node 16072 (Main analysis, Minerals, Secondary metabolites)",
              "Phyllis2 plain list: 7 corn stover, 6 corn stalks, 11 corn cob, maize leaf, maize shoots"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 16072", "Maize stover, dry", "dry", [
            ("calcium",    "g/kg",  "3.2",  "1.8", "1.6",  "11.7", "38", ""),
            ("phosphorus", "g/kg",  "0.8",  "0.6", "0.2",  "2.6",  "37", ""),
            ("potassium",  "g/kg",  "14",   "6.3", "5.4",  "28",   "30", ""),
            ("sodium",     "g/kg",  "0.24", "0.26", "0.04", "0.75", "13", ""),
            ("magnesium",  "g/kg",  "2.3",  "0.3", "1.7",  "3",    "29", ""),
            ("sulphur",    "g/kg",  "0.9",  "",    "0.9",  "0.9",  "3",  ""),
            ("manganese",  "mg/kg", "107",  "78",  "16",   "242",  "16", ""),
            ("zinc",       "mg/kg", "17",   "8",   "9",    "32",   "16", ""),
            ("copper",     "mg/kg", "4",    "1",   "2",    "6",    "16", ""),
            ("iron",       "mg/kg", "975",  "",    "",     "",     "",   ""),
            ("tannins",    "g/kg",  "2",    "",    "2",    "2",    "3",  "",
             "expressed as tannic acid equivalent"),
        ]),
    ],
)

ITEMS["raapzaad-schroot"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 52). Round 2 adds the Minerals table. "
         "Feedipedia prints NO secondary-metabolites table for this feed, so the "
         "glucosinolate content - the constraint that actually decides how much rapeseed "
         "meal a ration can carry - is not available from this source and stays open.",
    searched=["Feedipedia node 52 (Main analysis, Minerals; no Secondary metabolites table)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 52",
         "Rapeseed meal, solvent-extracted, 00 type, oil < 5%", "dry", [
            ("calcium",    "g/kg",  "8.6",  "1.0", "5.1",  "11.3", "433", ""),
            ("phosphorus", "g/kg",  "12.7", "1.0", "10.2", "20.8", "511", ""),
            ("potassium",  "g/kg",  "14.1", "",    "",     "",     "",    ""),
            ("sodium",     "g/kg",  "0.29", "",    "",     "",     "",    ""),
            ("chlorine",   "g/kg",  "0.7",  "",    "",     "",     "",    "",
             "Feedipedia heads this Chlorine, in the minerals table rather than an ultimate analysis"),
            ("magnesium",  "g/kg",  "4.6",  "",    "3.1",  "5.4",  "4",   ""),
            ("sulphur",    "g/kg",  "8.3",  "",    "",     "",     "1",   ""),
            ("manganese",  "mg/kg", "68",   "11",  "49",   "86",   "10",  ""),
            ("zinc",       "mg/kg", "78",   "25",  "56",   "142",  "18",  ""),
            ("copper",     "mg/kg", "9",    "7",   "2",    "25",   "17",  ""),
            ("iron",       "mg/kg", "183",  "36",  "110",  "202",  "5",   ""),
            ("selenium",   "mg/kg", "1",    "",    "",     "",     "",    ""),
        ]),
    ],
)

ITEMS["suikerbiet-pulp"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 710, pressed pulp). Round 2 adds the Minerals "
         "table. Note the calcium figure: 14,3 g/kg DM with n=673 and marked PREDICTED, which "
         "is high for a plant material and reflects the lime added in sugar extraction - a "
         "process artefact, not a property of beet.",
    searched=["Feedipedia node 710 (Main analysis, Minerals)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 710", "Sugar beet pulp, pressed", "dry", [
            ("calcium",    "g/kg",  "14.3", "2.7", "5",   "29.5", "673", "*",
             "high for a plant material - carry-over of the lime used in sugar extraction"),
            ("phosphorus", "g/kg",  "1",    "0.2", "0.3", "1.5",  "26",  "*"),
            ("magnesium",  "g/kg",  "1.7",  "0.4", "1.2", "2.4",  "13",  ""),
            ("potassium",  "g/kg",  "4.7",  "1.4", "2.4", "8.1",  "15",  ""),
            ("sodium",     "g/kg",  "3.31", "0.16", "",   "",     "",    ""),
            ("sulphur",    "g/kg",  "1.9",  "0.6", "0.6", "4.9",  "766", ""),
            ("manganese",  "mg/kg", "70",   "10",  "52",  "85",   "11",  ""),
            ("zinc",       "mg/kg", "17",   "4",   "13",  "26",   "11",  ""),
            ("copper",     "mg/kg", "5",    "1",   "3",   "7",    "11",  ""),
            ("iron",       "mg/kg", "471",  "161", "221", "767",  "11",  "",
             "471 mg/kg is soil iron carried in with the beet, not plant iron"),
        ]),
    ],
)

ITEMS["zemelen"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 12751). Round 2 adds Minerals and Secondary "
         "metabolites. Phosphorus at 11,1 g/kg DM is the bran-specific figure that matters: "
         "most of it is phytate-bound, which is why bran is a phosphorus source on paper and "
         "not in a monogastric gut.",
    searched=["Feedipedia node 12751 (Main analysis, Minerals, Secondary metabolites)",
              "Phyllis2 plain list: wheat bran ABSENT"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 12751", "Wheat bran", "dry", [
            ("calcium",           "g/kg",  "1.4",  "0.4", "0.2", "2.9",  "684", ""),
            ("phosphorus",        "g/kg",  "11.1", "1.2", "7.8", "14.6", "890", "*"),
            ("potassium",         "g/kg",  "13.7", "2.4", "8.3", "18.4", "81",  "*"),
            ("sodium",            "g/kg",  "0.1",  "0.1", "0.0", "0.3",  "128", ""),
            ("magnesium",         "g/kg",  "4.5",  "1.1", "2.2", "7.0",  "66",  ""),
            ("manganese",         "mg/kg", "114",  "35",  "41",  "188",  "38",  ""),
            ("zinc",              "mg/kg", "89",   "19",  "55",  "136",  "37",  ""),
            ("copper",            "mg/kg", "13",   "4",   "2",   "21",   "40",  ""),
            ("iron",              "mg/kg", "155",  "45",  "58",  "253",  "26",  ""),
            ("tannins",           "g/kg",  "1.3",  "",    "",    "",     "1",   "",
             "as tannic acid equivalent"),
            ("condensed_tannins", "g/kg",  "0.0",  "",    "",    "",     "1",   "",
             "as catechin equivalent - a reported ZERO on n=1, not an absence of data"),
        ]),
    ],
)

ITEMS["aardappel-stoomschillen"] = dict(
    status="done",
    note="Feedipedia's Potato by-products datasheet carries four variants with their own Main "
         "analysis: potato pulp (dehydrated), potato peels (fresh), STEAMED POTATO PEELS (liquid "
         "potato feed) and french fries (with oil). The third is this object exactly - the "
         "register calls it stoomschillen and the source calls it steamed potato peels. Both the "
         "fresh-peel and the steam-peel table are taken, because they are DIFFERENT MATERIALS: "
         "steaming gelatinises the starch and the figures move (starch 45,5 vs not reported, "
         "crude fibre 4,7 vs 11,4). This is the composition half of gap G-10; what G-10 is "
         "really missing is the Flemish TONNAGE, not the chemistry.",
    searched=["Feedipedia node 23075 (Potato by-products: 4 variants, Main analysis each)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 23075",
         "Steamed potato peels (liquid potato feed)", "dry", [
            ("dry_matter",    "%",     "17",   "4.5", "9.9",  "24.6", "14", "",
             "the source reports dry matter on an as-fed basis"),
            ("crude_protein", "%",     "12.8", "3.1", "7.1",  "18.5", "16", ""),
            ("crude_fibre",   "%",     "4.7",  "1.6", "2.7",  "6.8",  "11", ""),
            ("ndf",           "%",     "11",   "7.4", "7",    "24.2", "5",  "*"),
            ("adf",           "%",     "5.9",  "",    "4.7",  "8.1",  "3",  "*"),
            ("lignin",        "%",     "1.6",  "",    "0.6",  "1.7",  "3",  "*"),
            ("fat_total",     "%",     "1.3",  "1.8", "0.2",  "5.7",  "8",  ""),
            ("ash",           "%",     "7.1",  "3.2", "2.8",  "12.2", "14", ""),
            ("insoluble_ash", "%",     "2.4",  "",    "",     "",     "",   "*"),
            ("starch",        "%",     "45.5", "8.4", "30.9", "55.9", "8",  "",
             "polarimetric determination"),
            ("starch",        "%",     "43.5", "",    "",     "",     "",   "*",
             "enzymatic determination"),
            ("total_sugars",  "%",     "2.1",  "",    "",     "",     "",   ""),
            ("hhv",           "MJ/kg", "16.8", "",    "",     "",     "",   "*"),
        ]),
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 23075",
         "Potato peels, fresh (NOT steamed - a different material)", "dry", [
            ("dry_matter",    "%",     "20.1", "", "14.3", "24.7", "3", "",
             "the source reports dry matter on an as-fed basis"),
            ("crude_protein", "%",     "10",   "", "5.5",  "16.3", "4", ""),
            ("crude_fibre",   "%",     "11.4", "", "3.3",  "19.5", "2", ""),
            ("ndf",           "%",     "19.4", "", "",     "",     "1", "*"),
            ("adf",           "%",     "13.2", "", "5.5",  "13.3", "2", "*"),
            ("lignin",        "%",     "3.7",  "", "",     "",     "1", "*"),
            ("fat_total",     "%",     "0.7",  "", "0.2",  "1.5",  "3", ""),
            ("ash",           "%",     "5.5",  "", "5.1",  "6.1",  "3", ""),
            ("insoluble_ash", "%",     "0.8",  "", "",     "",     "",  "*"),
            ("hhv",           "MJ/kg", "17.1", "", "",     "",     "",  "*"),
        ]),
    ],
)

ITEMS["aardappel"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 547, raw tubers). Round 2 adds the Minerals "
         "table. Feedipedia carries NO quantitative secondary-metabolites table for potato: it "
         "discusses glycoalkaloids (solanine, alpha-chaconine) in prose under Potential "
         "constraints and prints no figure. For a stream whose admissible uses are decided by "
         "exactly that number, this is a real hole and not a rounding error.",
    searched=["Feedipedia node 547 (Main analysis, Minerals; secondary metabolites in prose only)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 547", "Potato tubers, raw", "dry", [
            ("calcium",    "g/kg",  "0.7",  "",    "0.3",  "1",    "4", ""),
            ("phosphorus", "g/kg",  "2.2",  "0.3", "1.9",  "2.5",  "6", ""),
            ("magnesium",  "g/kg",  "1",    "",    "1",    "1",    "2", ""),
            ("potassium",  "g/kg",  "23.6", "",    "23",   "24.1", "2", "",
             "potato is a potassium accumulator - the highest K figure in this round"),
            ("sodium",     "g/kg",  "0.2",  "",    "0.2",  "0.2",  "2", ""),
            ("sulphur",    "g/kg",  "1",    "",    "",     "",     "",  ""),
            ("manganese",  "mg/kg", "21",   "",    "",     "",     "",  ""),
            ("zinc",       "mg/kg", "28",   "",    "",     "",     "",  ""),
            ("copper",     "mg/kg", "7",    "",    "6",    "8",    "2", ""),
            ("iron",       "mg/kg", "65",   "",    "",     "",     "",  ""),
        ]),
    ],
)

ITEMS["suikerbiet-loof"] = dict(
    status="done",
    flag="The 27,9% dry matter round 1 flagged as implausible IS what the source prints for "
         "BEET TOPS, FRESH - checked against the page on 2026-09-11, which carries three "
         "variants (fresh 27,9 / silage 21,9 / dried 86,7) and the figure sits in the fresh "
         "table. It remains high for fresh leaf material, where the literature usually gives "
         "12-18%, and n = 2. Recorded as the source states it; worth a reviewer's eye.",
    note="Round 1 took the Main analysis (node 709, beet tops fresh). The variant question is "
         "now settled. Feedipedia prints NO minerals table for beet tops; the only mineral "
         "figures on the page sit under a separate 'Beet leaves, fresh' section and are two "
         "rows whose min/max columns are internally inconsistent (Ca min 19,6 above a mean of "
         "11,0), so they are deliberately NOT taken.",
    searched=["Feedipedia node 709 (3 variants: tops fresh / silage / dried; no minerals table "
              "for tops; the Beet leaves section's 2 mineral rows are internally inconsistent)",
              "Phyllis2 #1053 beet tail and beet green - taken in round 1, low confidence"],
    tables=[],
)

ITEMS["aardappel-loof"] = dict(
    status="no-source",
    note="CHECKED AND EMPTY, and this is the second time. Potato haulm is absent from Phyllis2's "
         "index and has no Feedipedia datasheet - confirmed again on 2026-09-11 - while every "
         "other field residue in this round sits in one or both. Three literature routes were "
         "tried this session and none produced a usable table: the Acta Scientific Agriculture "
         "2019 paper (Koli, Misra & Singh, DOI 10.31080/ASAG.2019.03.0568) is about haulm "
         "SILAGE blended with oat and its tables did not extract; the Current Science 115(2) "
         "PDF that a search attributed to potato haulm turns out to be a Pakistani "
         "agricultural-substrate study that does not cover potato at all. At 800.480 t this is "
         "the SECOND LARGEST target in the round and the largest with nothing behind it. "
         "F-004 stands, with two database routes still untried: S2BIOM (I) and the Dutch CVB "
         "Veevoedertabel. NOTE for whoever picks this up: haulm is chemically desiccated before "
         "harvest, which is a plausible reason feed databases skip it and a reason to check "
         "what a haulm analysis was taken BEFORE or AFTER desiccation.",
    searched=["Phyllis2 plain-list index - absent",
              "Feedipedia - no datasheet",
              "Acta Scientific Agriculture 2019 (haulm silage) - tables did not extract",
              "Current Science 115(2) 0292 - wrong paper, does not cover potato"],
    tables=[],
)

ITEMS["aardappel-snippers"] = dict(
    status="no-source",
    note="NO MATCHING MATERIAL FOUND, and the near-misses are the point. Feedipedia's potato "
         "by-products datasheet has four variants and none of them is snippers: potato pulp is "
         "a STARCH-INDUSTRY residue, steamed peels are the peeling line, french fries are a "
         "FRIED product. Snippers are raw cut-offs from the cutting line - essentially potato "
         "flesh with little peel. The tempting move is to give it the raw-tuber figures from "
         "node 547, and that is exactly what this folder's rule forbids: a fraction does not "
         "inherit its commodity's composition. Left empty at 95.000 t.",
    searched=["Feedipedia node 23075 - 4 variants, none is raw cuttings",
              "Feedipedia node 547 - the tuber, deliberately NOT reused for a fraction"],
    tables=[],
)

ITEMS["aardappel-industrieresidu"] = dict(
    status="no-source",
    note="The object itself is unresolved, so there is nothing to search for yet. This is the "
         "56.585 t the register places at the food industry under Aardappel with no fraction "
         "named - the row 2c described as `aardappel` absorbing a Prodcom 103113 processing "
         "residue because no source names a finer potato object. Now that stoomschillen and "
         "snippers ARE named separately in the 2026-09-11 selection, this residual row needs a "
         "placement decision before it can carry composition: it is either the remainder after "
         "those two, or it double-counts them. A register question, not a literature one.",
    searched=[],
    tables=[],
)

ITEMS["zetmeel-reststroom"] = dict(
    status="no-source",
    note="BLOCKED ON PURPOSE, unchanged from round 1. Prodcom 106220 'afvallen van "
         "zetmeelfabrieken' names a factory, not a material (gap G-19). Composition for starch "
         "side streams is abundant - Feedipedia alone prints a full Main analysis for "
         "dehydrated potato pulp on node 23075, and the potato fruit juice / potato fibre / "
         "potato protein literature is rich - so this is not a search problem. Attaching any of "
         "it would put a material name in a source's mouth, and Flanders crushes WHEAT starch "
         "rather than potato, so the obvious literature is probably the wrong material as well. "
         "284.549 t waiting on a naming decision.",
    searched=["not searched - the object is undefined, so a search cannot be scoped"],
    tables=[],
)

ITEMS["bostel"] = dict(
    status="done",
    note="Feedipedia node 74, the FRESH (wet) variant, which is what leaves a Flemish brewery - "
         "a dried variant exists on the same page and is a different material by moisture, not "
         "by chemistry. Main analysis and Minerals both taken. Note crude protein 25,9 % DM and "
         "ether extract 7,0 %: bostel is the protein-richest plant stream in this round, which "
         "is why it already has a feed market and why a higher-value use has to beat that market "
         "rather than an disposal cost.",
    searched=["Feedipedia node 74 (Main analysis + Minerals, fresh variant)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 74", "Brewers grains, fresh", "dry", [
            ("dry_matter",    "%",     "24.9", "2.3",  "21.7", "28.9", "18", "",
             "the source reports dry matter on an as-fed basis"),
            ("crude_protein", "%",     "25.9", "2.8",  "20.3", "30.6", "29", ""),
            ("crude_fibre",   "%",     "16.4", "3.6",  "7.8",  "21.2", "14", ""),
            ("ndf",           "%",     "49.6", "10.7", "34.3", "62.5", "19", ""),
            ("adf",           "%",     "20.8", "2.3",  "17.2", "24.8", "16", ""),
            ("lignin",        "%",     "5.7",  "1.1",  "3.5",  "8.0",  "19", ""),
            ("fat_total",     "%",     "7.0",  "0.9",  "5.8",  "9.3",  "18", ""),
            ("ash",           "%",     "4.1",  "0.5",  "2.7",  "4.9",  "26", ""),
            ("starch",        "%",     "5.7",  "2.7",  "3.3",  "9.6",  "6",  "",
             "enzymatic determination"),
            ("total_sugars",  "%",     "1.0",  "0.2",  "0.7",  "1.3",  "6",  ""),
            ("hhv",           "MJ/kg", "20.3", "0.4",  "20.3", "21.8", "8",  ""),
            ("calcium",       "g/kg",  "3.0",  "1.4",  "1.3",  "6.3",  "18", ""),
            ("phosphorus",    "g/kg",  "5.8",  "1.4",  "2.7",  "7.6",  "19", ""),
            ("potassium",     "g/kg",  "1.6",  "1.3",  "0.1",  "3.4",  "17", ""),
            ("sodium",        "g/kg",  "0.3",  "0.2",  "0.0",  "0.9",  "17", ""),
            ("magnesium",     "g/kg",  "2.3",  "0.6",  "1.1",  "3.2",  "18", ""),
            ("manganese",     "mg/kg", "43",   "10",   "25",   "56",   "16", ""),
            ("zinc",          "mg/kg", "83",   "13",   "60",   "105",  "16", ""),
            ("copper",        "mg/kg", "14",   "7",    "7",    "31",   "16", ""),
            ("iron",          "mg/kg", "138",  "18",   "108",  "163",  "10", ""),
        ]),
    ],
)

ITEMS["zuivelnevenstroom"] = dict(
    status="done",
    flag="TWO MISMATCHES, and neither is small. (1) The OBJECT is wider than whey: MONBIO says "
         "the dairy sector's residuals are melkwei AND zuiveringsslib, so a whey table does not "
         "describe the whole 126.251 t. (2) The MATERIAL is not the Flemish one: Feedipedia has "
         "no table for liquid whey - its datasheet is explicitly pending revision, with contents "
         "from FAO 1991-2002 - so what is taken here is DEHYDRATED, SKIMMED sweet whey. "
         "Dehydration is only a basis question and the dry-basis figures survive it, but "
         "SKIMMING removes fat before the analysis, so the fat figure describes a processed "
         "product and not the stream. Treat every row as indicative until a liquid-whey analysis "
         "replaces it.",
    note="Best available rather than right. Lactose at 71,1 % DM on n=18 is the figure that "
         "matters for valorisation and it is a real measurement, not a predicted one.",
    searched=["Feedipedia node 730 (Whey) - NO liquid/fresh variant; two dehydrated skimmed "
              "variants only, sweet and acid. Datasheet marked pending revision"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 730",
         "Whey, sweet, dehydrated, skimmed (NOT the liquid Flemish stream)", "dry", [
            ("dry_matter",    "%",     "97.0",  "1.2",  "93.7", "98.4",  "98", "",
             "as-fed basis, and it is a DRIED product - not the stream's own moisture"),
            ("crude_protein", "%",     "12.5",  "0.9",  "11.1", "15.1",  "95", ""),
            ("fat_total",     "%",     "1.3",   "0.5",  "0.6",  "2.3",   "28", "",
             "HCl-hydrolysis extraction, and the product is SKIMMED - not the stream's fat"),
            ("ash",           "%",     "8.2",   "0.5",  "7.2",  "9.3",   "78", ""),
            ("lactose",       "%",     "71.06", "2.80", "65.90", "75.16", "18", ""),
            ("hhv",           "MJ/kg", "16.1",  "1.0",  "14.3", "16.2",  "3",  "*"),
            ("calcium",       "g/kg",  "5.1",   "0.9",  "3.7",  "7.9",   "29", ""),
            ("phosphorus",    "g/kg",  "6.4",   "0.6",  "5.3",  "7.6",   "36", ""),
            ("potassium",     "g/kg",  "21.0",  "1",    "",     "",      "1",  ""),
            ("sodium",        "g/kg",  "7.0",   "1.1",  "5.5",  "9.9",   "32", ""),
            ("magnesium",     "g/kg",  "1.0",   "",     "",     "",      "1",  ""),
            ("copper",        "mg/kg", "7",     "",     "",     "",      "1",  ""),
            ("iron",          "mg/kg", "7",     "",     "",     "",      "1",  ""),
        ]),
    ],
)

ITEMS["zonnebloem-schroot"] = dict(
    status="done",
    note="Feedipedia node 732, the solvent-extracted non-dehulled variant. Dehulled variants "
         "exist on the same page and are a different material - hulls carry most of the fibre, "
         "so crude fibre swings from ~29 % to ~15 % between them. The register's figure is a "
         "FEDIOL crush statistic for Belgium, which does not say which. Non-dehulled taken as "
         "the default and the choice recorded rather than hidden.",
    searched=["Feedipedia node 732 (Main analysis + Minerals, solvent-extracted non-dehulled)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 732",
         "Sunflower meal, solvent-extracted, non-dehulled", "dry", [
            ("dry_matter",    "%",     "88.9", "1.3", "85.5", "93.7", "8052", "",
             "as-fed basis"),
            ("crude_protein", "%",     "31.3", "1.9", "24.4", "36.7", "8045", ""),
            ("crude_fibre",   "%",     "29.1", "2.2", "22.6", "37.2", "7925", ""),
            ("ndf",           "%",     "46.4", "3.1", "40.3", "53.2", "188",  "*"),
            ("adf",           "%",     "33.2", "2.4", "27.9", "38.9", "189",  "*"),
            ("lignin",        "%",     "11.2", "1.1", "8.8",  "13.5", "222",  "*"),
            ("fat_total",     "%",     "2.3",  "0.8", "0.6",  "5.3",  "5279", ""),
            ("ash",           "%",     "7.0",  "0.6", "5.6",  "8.9",  "3054", ""),
            ("total_sugars",  "%",     "5.9",  "0.7", "4.4",  "7.5",  "97",   ""),
            ("hhv",           "MJ/kg", "19.4", "0.2", "19.1", "20.2", "17",   "*"),
            ("calcium",       "g/kg",  "4.3",  "0.6", "3.2",  "6.2",  "582",  ""),
            ("phosphorus",    "g/kg",  "11.1", "1.3", "8.7",  "14.5", "628",  ""),
            ("potassium",     "g/kg",  "16.0", "1.8", "12.5", "18.8", "9",    ""),
            ("sodium",        "g/kg",  "0.1",  "0.1", "0.0",  "0.5",  "85",   ""),
            ("magnesium",     "g/kg",  "5.3",  "1.0", "3.0",  "6.4",  "9",    ""),
            ("manganese",     "mg/kg", "43",   "7",   "35",   "53",   "7",    ""),
            ("zinc",          "mg/kg", "92",   "4",   "88",   "97",   "7",    ""),
            ("copper",        "mg/kg", "30",   "3",   "25",   "33",   "8",    ""),
            ("iron",          "mg/kg", "274",  "",    "248",  "299",  "2",    ""),
        ]),
    ],
)

ITEMS["lijnzaad-schroot"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 735). Round 2 adds the Minerals table, which is "
         "thin: five elements, three of them on n=1. No secondary-metabolites table, although "
         "the datasheet discusses cyanogenic glucosides, linatine and mucilage in prose - the "
         "antinutritional factors that bound how much linseed meal a ration can carry. Same hole "
         "as rapeseed meal: the constraint is described and never quantified.",
    searched=["Feedipedia node 735 (Main analysis + Minerals; no Secondary metabolites table)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 735",
         "Linseed meal, solvent-extracted", "dry", [
            ("calcium",    "g/kg", "4.4",  "0.6", "3.3", "6.1",  "30", ""),
            ("phosphorus", "g/kg", "9.6",  "0.6", "8.1", "10.7", "30", ""),
            ("potassium",  "g/kg", "11.6", "",    "",    "",     "1",  ""),
            ("sodium",     "g/kg", "1.4",  "",    "",    "",     "1",  ""),
            ("magnesium",  "g/kg", "4.8",  "",    "",    "",     "1",  ""),
        ]),
    ],
)

ITEMS["soja-schroot"] = dict(
    status="done",
    note="Round 1 took the Main analysis (node 26068, type 48). Round 2 adds the Minerals table. "
         "No secondary-metabolites table, so trypsin inhibitor, isoflavones and phytate - the "
         "three numbers anyone processing soybean meal actually asks for - are absent. Note the "
         "iron row: mean 274 mg/kg with SD 166 over a 13-617 range, which is soil and mill "
         "contamination spread, not biology.",
    searched=["Feedipedia node 26068 (Main analysis + Minerals; no Secondary metabolites table)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 26068",
         "Soybean meal, type 48 and similar", "dry", [
            ("calcium",    "g/kg",  "3.8",  "0.9",  "1.6",  "7.9",  "1729", "*"),
            ("phosphorus", "g/kg",  "7.1",  "0.6",  "4.4",  "8.1",  "47",   "*"),
            ("potassium",  "g/kg",  "23.8", "1.4",  "20.9", "28.6", "76",   "*"),
            ("sodium",     "g/kg",  "0.16", "0.25", "0",    "1.49", "275",  ""),
            ("chlorine",   "g/kg",  "0.3",  "0.2",  "0.1",  "0.9",  "95",   "",
             "Feedipedia lists this in the minerals table rather than an ultimate analysis"),
            ("magnesium",  "g/kg",  "3.1",  "0.4",  "2.5",  "4.1",  "21",   "*"),
            ("sulphur",    "g/kg",  "4.5",  "0.2",  "4.3",  "4.9",  "5",    ""),
            ("manganese",  "mg/kg", "45",   "13",   "25",   "88",   "66",   ""),
            ("zinc",       "mg/kg", "62",   "39",   "29",   "303",  "43",   ""),
            ("copper",     "mg/kg", "19",   "7",    "7",    "61",   "44",   ""),
            ("iron",       "mg/kg", "274",  "166",  "13",   "617",  "18",   "",
             "SD 166 over a 13-617 range is contamination spread, not biology"),
            ("selenium",   "mg/kg", "0.2",  "",     "",     "",     "",     ""),
        ]),
    ],
)

ITEMS["melasse"] = dict(
    status="done",
    note="Feedipedia node 711, beet molasses. Main analysis and Minerals both taken. This entry "
         "is the cleanest illustration in the round of why a ZERO must be recorded as a zero and "
         "not as absence: crude fibre, NDF, ADF, lignin and starch are all printed as 0, which is "
         "correct - molasses is a sugar syrup with no cell wall left in it - and a loader that "
         "treated 0 as missing would throw away a real measurement. Potassium at 51,2 g/kg DM is "
         "the highest figure anywhere in this round and is why beet molasses is a fertiliser "
         "question as much as a feed one.",
    searched=["Feedipedia node 711 (Main analysis + Minerals, beet molasses)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 711", "Molasses, beet", "dry", [
            ("dry_matter",    "%",     "75.4", "2.7",  "56.6", "82.8", "599", "",
             "as-fed basis"),
            ("crude_protein", "%",     "14.2", "2",    "8.9",  "19.3", "529", "",
             "largely non-protein nitrogen (betaine, amino acids), not true protein"),
            ("crude_fibre",   "%",     "0",    "0.09", "0",    "0.3",  "9",   "",
             "a MEASURED zero on n=9, not a missing value"),
            ("fat_total",     "%",     "0.2",  "",     "0.1",  "0.3",  "4",   ""),
            ("ash",           "%",     "12.7", "2",    "8",    "21.1", "527", ""),
            ("insoluble_ash", "%",     "0.01", "",     "0.01", "0.01", "2",   ""),
            ("ndf",           "%",     "0",    "",     "",     "",     "",    "",
             "measured zero - no cell wall left after sugar extraction"),
            ("adf",           "%",     "0",    "",     "",     "",     "",    "", "measured zero"),
            ("lignin",        "%",     "0",    "",     "",     "",     "",    "", "measured zero"),
            ("starch",        "%",     "0",    "",     "",     "",     "",    "",
             "measured zero, polarimetric determination"),
            ("total_sugars",  "%",     "63.4", "4.7",  "49.1", "76.8", "464", ""),
            ("hhv",           "MJ/kg", "15.5", "0.5",  "14.7", "16.6", "10",  "*"),
            ("calcium",       "g/kg",  "1.2",  "0.8",  "0",    "4.2",  "119", "*"),
            ("phosphorus",    "g/kg",  "0.3",  "0.2",  "0.04", "1.1",  "120", "*"),
            ("magnesium",     "g/kg",  "0.3",  "0.2",  "0.06", "0.7",  "8",   ""),
            ("potassium",     "g/kg",  "51.2", "12",   "13.2", "81.6", "70",  "*",
             "the highest potassium figure in the whole round"),
            ("sodium",        "g/kg",  "6.91", "2.02", "3.24", "11.56", "134", ""),
            ("sulphur",       "g/kg",  "5.6",  "",     "",     "",     "",    ""),
            ("manganese",     "mg/kg", "38",   "",     "",     "",     "",    ""),
            ("zinc",          "mg/kg", "22",   "",     "",     "",     "",    ""),
            ("copper",        "mg/kg", "17",   "",     "",     "",     "",    ""),
            ("iron",          "mg/kg", "154",  "",     "",     "",     "",    ""),
        ]),
    ],
)

ITEMS["tarwe-stro"] = dict(
    status="done",
    note="Round 1 took Phyllis2 #3161, which is a FUEL analysis - proximate, ultimate CHONS, "
         "Cl, calorific value, on three bases. Round 2 adds the complementary half from "
         "Feedipedia node 60: Weende, Van Soest and minerals, none of which Phyllis2 carries. "
         "Together these two sources give tarwe-stro the widest vector in the round, and they "
         "overlap on almost nothing - which is the argument for using both rather than picking "
         "the better database. Six further Phyllis2 wheat-straw records (#945, #991, #1271, "
         "#1368, #2038, #3201) remain untaken; each is its own source and its own rows.",
    searched=["Feedipedia node 60 Straws (Main analysis + Minerals, wheat straw variant)",
              "Phyllis2: 7 wheat straw records, 1 taken in round 1"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 60", "Wheat straw", "dry", [
            ("dry_matter",    "%",     "91.0", "1.3", "87.3", "93.8", "438", "", "as-fed basis"),
            ("crude_protein", "%",     "4.2",  "0.7", "2.6",  "6.0",  "428", ""),
            ("crude_fibre",   "%",     "41.5", "2.1", "36.6", "46.2", "438", ""),
            ("ndf",           "%",     "77.5", "4.2", "65.4", "86.0", "85",  "*"),
            ("adf",           "%",     "50.0", "3.5", "43.3", "57.0", "80",  "*"),
            ("lignin",        "%",     "7.2",  "1.0", "5.3",  "9.7",  "203", ""),
            ("fat_total",     "%",     "1.4",  "0.5", "0.7",  "2.8",  "53",  ""),
            ("ash",           "%",     "6.7",  "1.2", "4.4",  "10.0", "433", ""),
            ("starch",        "%",     "1.0",  "0.6", "0.1",  "2.6",  "114", "",
             "polarimetric determination"),
            ("total_sugars",  "%",     "1.2",  "0.9", "0.3",  "5.7",  "138", ""),
            ("hhv",           "MJ/kg", "18.5", "0.6", "16.0", "18.5", "18",  "*",
             "compare Phyllis2 #3161, which measured 18,94 MJ/kg on a dry basis - two sources, "
             "two rows, no averaging"),
            ("calcium",       "g/kg",  "4.8",  "1.1", "2.8",  "7.9",  "226", ""),
            ("phosphorus",    "g/kg",  "0.7",  "0.2", "0.3",  "1.2",  "226", ""),
            ("potassium",     "g/kg",  "11.2", "4.6", "5.4",  "21.2", "40",  ""),
            ("sodium",        "g/kg",  "0.1",  "0.1", "0.0",  "0.4",  "143", ""),
            ("magnesium",     "g/kg",  "1.2",  "1.2", "0.4",  "5.4",  "18",  ""),
            ("manganese",     "mg/kg", "32",   "19",  "12",   "60",   "5",   ""),
            ("zinc",          "mg/kg", "17",   "7",   "8",    "28",   "10",  ""),
            ("copper",        "mg/kg", "4",    "2",   "2",    "9",    "10",  ""),
            ("iron",          "mg/kg", "184",  "201", "52",   "643",  "8",   "",
             "SD larger than the mean - soil contamination, not plant iron"),
        ]),
    ],
)

ITEMS["voederbiet"] = dict(
    status="done",
    flag="Iron reads 3.189 mg/kg DM with SD 2.158 over a 736-6.450 range. That is SOIL, not "
         "beet: a root crop lifted from the ground carries earth into the sample, and the same "
         "signature shows up on beet pulp (471) and, far worse, on poultry offal meal. Any "
         "model that reads this as a mineral content of the material will be wrong. The same "
         "applies to the ash range, 3,5-32,7 % DM on n=29.",
    note="Feedipedia node 534, fresh fodder beet root. Main analysis and Minerals both taken. "
         "Starch is printed as 0 on both determinations, which is correct and measured - a beet "
         "stores sugar, not starch - and sits beside total sugars at 65,8 % DM.",
    searched=["Feedipedia node 534 (Main analysis + Minerals, fresh fodder beet root)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 534",
         "Beet root, fodder type, fresh", "dry", [
            ("dry_matter",    "%",     "16.1", "3.2",  "7.9",  "21.4", "23", "", "as-fed basis"),
            ("crude_protein", "%",     "7.9",  "2.5",  "4.6",  "14.6", "31", ""),
            ("crude_fibre",   "%",     "6",    "1.5",  "4.3",  "11.6", "21", ""),
            ("ndf",           "%",     "16",   "5.1",  "10.2", "27.2", "20", ""),
            ("adf",           "%",     "9.5",  "3.6",  "5.4",  "17",   "19", ""),
            ("lignin",        "%",     "0.9",  "",     "0.8",  "1",    "2",  ""),
            ("fat_total",     "%",     "0.5",  "0.7",  "0.1",  "2.8",  "14", ""),
            ("ash",           "%",     "10.6", "7.4",  "3.5",  "32.7", "29", "",
             "the 32,7 % maximum is soil, not beet"),
            ("insoluble_ash", "%",     "4",    "",     "",     "",     "",   "*"),
            ("starch",        "%",     "0",    "",     "",     "",     "",   "",
             "measured zero, polarimetric - a beet stores sugar, not starch"),
            ("starch",        "%",     "0",    "",     "",     "",     "1",  "",
             "measured zero, enzymatic determination"),
            ("total_sugars",  "%",     "65.8", "7.4",  "54.7", "81.9", "15", ""),
            ("hhv",           "MJ/kg", "16.2", "0.4",  "15.6", "16.6", "10", "*"),
            ("calcium",       "g/kg",  "5.5",  "4.6",  "0.8",  "14",   "18", ""),
            ("phosphorus",    "g/kg",  "2.4",  "1.2",  "1",    "5",    "17", ""),
            ("potassium",     "g/kg",  "31",   "14.4", "9.7",  "46",   "8",  ""),
            ("sodium",        "g/kg",  "6.81", "4.71", "1.1",  "15",   "12", ""),
            ("chlorine",      "g/kg",  "0.7",  "",     "",     "",     "1",  ""),
            ("magnesium",     "g/kg",  "3.6",  "2.9",  "1.1",  "9",    "17", ""),
            ("sulphur",       "g/kg",  "1.5",  "",     "",     "",     "",   ""),
            ("manganese",     "mg/kg", "209",  "83",   "115",  "312",  "6",  ""),
            ("zinc",          "mg/kg", "59",   "7",    "53",   "70",   "6",  ""),
            ("copper",        "mg/kg", "21",   "5",    "16",   "27",   "6",  ""),
            ("iron",          "mg/kg", "3189", "2158", "736",  "6450", "6",  "",
             "soil carried in with the root - not a property of the beet"),
        ]),
    ],
)

ITEMS["gevogelte"] = dict(
    status="done",
    flag="THE MATERIAL IS A RENDERED PRODUCT, NOT THE STREAM. Poultry offal meal is slaughter "
         "by-product that has been cooked, pressed and dried; the Flemish stream at 86.856 t is "
         "WET offal leaving the slaughterhouse. Dry-basis protein and ash carry across, fat does "
         "not (pressing removes it: 27,9 % ether extract here against 24,4 % after HCl "
         "hydrolysis, both on the rendered product), and the iron figure - 5.107 mg/kg DM with "
         "SD 4.872 over 212-13.825 - is blood and process contamination, not tissue.",
    note="Feedipedia node 214. The best available match; the mismatch is the finding. A wet "
         "poultry-offal analysis would come from a rendering-sector source, which is exactly "
         "what gap G-04 says the corpus does not have.",
    searched=["Feedipedia node 214 Poultry by-product meal (Main analysis + Minerals)"],
    tables=[
        ("feedtables-inrae-cirad-afz-fao", "Feedipedia node 214",
         "Poultry offal meal (RENDERED - not the wet stream)", "dry", [
            ("dry_matter",    "%",     "92.3", "2.4",  "85.3", "97.8",  "1902", "",
             "as-fed basis, and it is a DRIED product"),
            ("crude_protein", "%",     "60.2", "7.3",  "47.3", "86.1",  "1929", ""),
            ("fat_total",     "%",     "27.9", "6.9",  "8.6",  "38.7",  "1403", "",
             "ether extraction - the rendered product is pressed, so this is not the stream's fat"),
            ("fat_total",     "%",     "24.4", "6.4",  "12.1", "35.0",  "482",  "",
             "HCl-hydrolysis extraction - a different determination on the same material"),
            ("ash",           "%",     "10.6", "4.6",  "2.7",  "23.8",  "1892", ""),
            ("hhv",           "MJ/kg", "24.4", "2.5",  "19.9", "27.4",  "23",   "*",
             "the highest calorific value in the round - it is a fat-rich animal product"),
            ("calcium",       "g/kg",  "20.3", "9.6",  "6.7",  "55.8",  "1481", "",
             "bone content, and it varies with how much bone the offal carries"),
            ("phosphorus",    "g/kg",  "10.1", "4.8",  "2.0",  "28.3",  "1489", ""),
            ("potassium",     "g/kg",  "4.1",  "0.8",  "2.9",  "5.5",   "13",   ""),
            ("sodium",        "g/kg",  "2.7",  "0.6",  "1.6",  "4.8",   "168",  ""),
            ("magnesium",     "g/kg",  "0.7",  "0.2",  "0.5",  "0.9",   "7",    ""),
            ("manganese",     "mg/kg", "18",   "9",    "11",   "34",    "7",    ""),
            ("zinc",          "mg/kg", "67",   "41",   "10",   "126",   "7",    ""),
            ("copper",        "mg/kg", "41",   "59",   "5",    "157",   "7",    ""),
            ("iron",          "mg/kg", "5107", "4872", "212",  "13825", "87",   "",
             "blood and process contamination, not tissue iron"),
        ]),
    ],
)


# ---------------------------------------------------------------------------

def expand(code: str, item: dict) -> dict:
    rows = []
    used_sources = {}
    for src, ref, variant, basis, table in item.get("tables", []):
        used_sources[src] = dict(SOURCES[src], citation_key=src)
        for r in table:
            param, unit, avg, sd, vmin, vmax, n, pred = r[:8]
            note = r[8] if len(r) > 8 else ""
            rows.append(dict(
                stream_code=code, parameter_code=param, value_type="point",
                value_num=avg, value_min=vmin, value_max=vmax, sd=sd, n_samples=n,
                unit_code=unit, basis_code=basis, method_code="",
                value_origin="predicted" if pred else "measured",
                source_key=src, source_ref=ref, year="", reported_label="",
                variant=variant, restatement="no", flag=item.get("flag", ""),
                transcription="machine", DECISION="", notes=note,
            ))
    return dict(stream_code=code, status=item["status"], note=item.get("note", ""),
                searched=item.get("searched", []),
                sources=list(used_sources.values()), rows=rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for code, item in ITEMS.items():
        payload = expand(code, item)
        (OUT / f"{code}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {code:<34} {payload['status']:<10} {len(payload['rows']):>3} rows")
    print(f"{len(ITEMS)} items written to {OUT}")


if __name__ == "__main__":
    main()
