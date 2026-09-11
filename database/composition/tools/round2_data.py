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
