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
