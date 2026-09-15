"""Round 4: closing the holes the coverage analysis named.

    ../.venv/Scripts/python tools/round4_data.py    ->  ../extraction/round4/<code>.json

Round 3 left three objects with nothing and three with a thin vector on a large tonnage.
This round goes after them one at a time, and writes each the moment it is finished.

WHAT IT ADDS, and where it came from. Phyllis2's index was searched properly this time
rather than for straw alone, and it turned out to hold records for two of the three empty
objects. `animal fat` (#3491) and `meat and bone meal` (#3492) are both ECN lab analyses
of material sampled in ROTTERDAM in 2009 to CEN/TS methods - the closest thing in this
whole harvest to a Flemish measurement, and the first fuel-side data on the animal
streams. `potato shreds, sorting waste` (#1066) is the register's `snippers` under
another name.

THE DAF COLUMN OF THE 2009 ECN RECORDS IS NOT TAKEN. On #3492 it reads carbon 1.25 and
hydrogen 1.28 wt% against 40.74 and 5.52 on dry - a rendering artefact, not a
restatement. Same treatment as the apple-pomace sugars row and the S2BIOM ash oxides: an
internally impossible column is not recorded under either reading.

A BELOW-DETECTION-LIMIT VALUE IS NOT RECORDED. #3491 gives fluorine as `< 10 mg/kg`.
That is a censored value, and BioMobi has no way to store one - `range` means the spread
of observed values, not an upper bound on a single one. Left out and noted rather than
turned into a number nobody measured.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction" / "round4"

SOURCES = {
    "phyllis2-tno": dict(
        source_type="dataset", year=2026, kind="primary-indexed", country="NL",
        title="Phyllis2 - database for the physico-chemical composition of (treated) "
              "lignocellulosic biomass",
        url="https://phyllis.nl/",
        notes="Each record cites its own literature reference or its own lab and method, so "
              "provenance resolves below the database. The 2009 ECN series used here (#3491, "
              "#3492) is material sampled in Rotterdam and analysed at ECN to CEN/TS methods - "
              "Dutch, dated, and traceable to a laboratory rather than to a compilation."),
}

ITEMS: dict[str, dict] = {}

ITEMS["dierlijk-vet"] = dict(
    status="done",
    note="THE FIRST REAL DATA ON THIS STREAM. Round 3 left it on two rows because Feedipedia's "
         "Fats datasheet carries no table and says DO NOT QUOTE, and because the catalogue had "
         "no vector for a fat. Phyllis2 #3491 is an ECN analysis of animal fat sampled in "
         "Rotterdam on 2009-01-03 - the fuel side of the material, which is the side that "
         "matters for a stream whose realistic routes are rendering and energy. LHV 38,8 MJ/kg "
         "dry is more than twice any plant stream in this harvest and is the single number that "
         "makes the case for it. "
         "STILL MISSING, and it is the same hole as before: the FATTY ACID PROFILE, free fatty "
         "acids, iodine value and slip melting point. Those decide whether the fat goes to feed, "
         "oleochemistry or biodiesel, and no source read so far prints them for a rendered "
         "animal fat.",
    searched=["Phyllis2 index - `animal fat` #3491 found (round 3 searched the index for straw "
              "and stover only, which is how this was missed)",
              "Feedipedia node 69 Fats - no tables, marked DO NOT QUOTE",
              "FoodWasteEXplorer `Animal fats` - 4 rows, all from the Online European Feedstock "
              "Atlas, taken in round 3"],
    tables=[("phyllis2-tno", "Phyllis2 record #3491", "Animal fat, Rotterdam NL, sampled 2009-01-03", [
        ("moisture",       "%",     "1.21",  "fresh", ""),
        ("total_carbon",   "%",     "76.19", "dry",   ""),
        ("hydrogen",       "%",     "12.55", "dry",   ""),
        ("total_nitrogen", "%",     "0.12",  "dry",   ""),
        ("bromine",        "mg/kg", "2.0",   "fresh", "the record gives bromine on the as-received column only"),
        ("lhv",            "MJ/kg", "38.80", "dry",
         "more than twice the calorific value of any plant stream in this harvest"),
    ])],
    flag="Fluorine is reported as `< 10 mg/kg` and is NOT recorded: a below-detection-limit "
         "value is a censored value, and the schema has no way to hold one. The `daf` column of "
         "this ECN series is also left out - on its sibling record #3492 it reads carbon 1,25 "
         "wt% against 40,74 on dry, which is a rendering artefact rather than a restatement.",
)

ITEMS["niet-eetbare-slachtafvallen"] = dict(
    status="done",
    note="Round 3 had Feedipedia's meat-and-bone-meal Weende and minerals and nothing else, so "
         "the vector was 14 parameters of nutrition with no fuel side at all. Phyllis2 #3492 is "
         "the same material analysed as a FUEL, at ECN, on Rotterdam material sampled "
         "2009-01-02, to CEN/TS 14774 / 15104 / 14918 / 15297. Nitrogen at 8,25 % dry is the "
         "protein; the halogens are what decide whether it can be co-fired. "
         "The species split that gap G-04 asks for is still absent, and this source cannot "
         "supply it either - meat and bone meal bundles species by construction.",
    searched=["Phyllis2 index - meat and bone meal at #1892, #2193, #2313, #2826, #2827, #2836, "
              "#3053, #3492, #3493; also `animal blood` #2693 and `Milled bones and meat from "
              "chicken` #3346, both different objects and not taken",
              "#3492 taken as the most recent and the only one with a named lab and method set"],
    tables=[("phyllis2-tno", "Phyllis2 record #3492",
             "Meat and bone meal, Rotterdam NL, sampled 2009-01-02", [
        ("moisture",       "%",     "2.71",  "fresh", ""),
        ("total_carbon",   "%",     "40.74", "dry",   ""),
        ("hydrogen",       "%",     "5.52",  "dry",   ""),
        ("total_nitrogen", "%",     "8.25",  "dry",   "the protein, seen from the fuel side"),
        ("bromine",        "mg/kg", "16.0",  "dry",   ""),
        ("fluorine",       "mg/kg", "13.0",  "dry",   ""),
        ("lhv",            "MJ/kg", "17.19", "dry",   ""),
    ])],
    flag="The `daf` column of this record is internally impossible - carbon 1,25 and hydrogen "
         "1,28 wt% against 40,74 and 5,52 on dry - and is not recorded under either reading.",
)

ITEMS["aardappel-snippers"] = dict(
    status="done",
    note="Round 3 recorded this as having no matching material anywhere, because Feedipedia's "
         "four potato variants are pulp, peels, steamed peels and fried, and none is raw "
         "cuttings. Phyllis2 has it under another name: `potato shreds, sorting waste` (#1066). "
         "That IS snippers - cuttings from the sorting and cutting line. "
         "The figures are weak and the weakness is the point: they come from the same 1997 "
         "confidential ECN report as the beet-green record #1053, and they are round numbers - "
         "ash 10,00, cellulose 10,00, starch 70,00. They read as an estimate rather than a "
         "measurement. Taken because the object had nothing at all and a labelled estimate is "
         "better than a blank, NOT because they are good.",
    searched=["Phyllis2 index - `potato shreds, sorting waste` #1066 and `potato sorting waste` "
              "#1067; also `potato rests` #1068, `potato fibres` #1065 and `potato mash` #2841, "
              "which are starch-industry materials and belong to the blocked zetmeel-reststroom "
              "rather than here",
              "Feedipedia node 23075 - 4 variants, none is raw cuttings (round 3)"],
    tables=[("phyllis2-tno", "Phyllis2 record #1066", "Potato shreds, sorting waste", [
        ("ash",       "%", "10.00", "fresh", "a round number from a 1997 confidential report"),
        ("cellulose", "%", "10.00", "dry",   "a round number from a 1997 confidential report"),
        ("starch",    "%", "70.00", "dry",   "a round number from a 1997 confidential report"),
    ])],
    flag="LOW CONFIDENCE. Every value is a round number from R. J. Leemhuis and R. M. de Jong, "
         "`Biomassa: biochemische samenstelling en conversiemethoden` (confidential, ECN "
         "7.2072-GR 2, 1997) - the same report behind the beet-green record #1053, and it reads "
         "as an estimate rather than a measurement. Replace it as soon as anything better "
         "appears.",
)

ITEMS["spruitstokken"] = dict(
    status="no-source",
    note="STILL EMPTY after a fourth pass, and the near-misses are what make it worth recording. "
         "Phyllis2 DOES hold brassica stalk material - `kale, stalk` (#1559) - and it holds "
         "`Brussels sprouts` (#1560, #1561). Neither is this object. The kale stalk is a "
         "different crop, and the Brussels sprouts record is the SPROUT: it carries six heavy "
         "metals and nothing else, comes from a 1993 literature survey of household organic "
         "waste, and does not say which plant part it is. Putting either on the field stalk "
         "would break the rule this folder opens with. "
         "The one located candidate remains out of reach: `Evaluation of Brassica Vegetables as "
         "Potential Feed for Ruminants` (Animals 2019, doi 10.3390/ani9090588) compares sprouts "
         "with savoy and red cabbage - and describes the SPROUT, not the stalk, so even reached "
         "it would be the wrong fraction. 138.000 t and nothing behind it.",
    searched=["Phyllis2 index - `kale, stalk` #1559 (wrong crop), `Brussels sprouts` #1560/#1561 "
              "(the sprout, heavy metals only, plant part unstated) - both located and rejected",
              "FoodWasteEXplorer `Brussels sprouts` - 13 rows, all from ECN Phyllis 2, so the "
              "same record twice",
              "CVB Veevoedertabel 2023 - `Kool (spruitkool)` p. 657 is the sprout as a vegetable",
              "literature search on brussels sprout stem/stalk composition - nothing with a table"],
    tables=[],
)

ITEMS["zetmeel-reststroom"] = dict(
    status="no-source",
    note="STILL BLOCKED, and this round found exactly what it would take. Phyllis2 holds "
         "`potato fibres` (#1065), `potato rests` (#1068) and `potato mash` (#2841); CVB holds "
         "`Aardappelvezels, gedroogd` in three protein classes, `Aardappeleiwit` in two, and "
         "`Aardappelzetmeel`. So the material is well described - IF the object were a potato "
         "starch residue. It is Prodcom 106220, `afvallen van zetmeelfabrieken`, which names a "
         "factory and not a material (gap G-19), and Flanders crushes WHEAT starch rather than "
         "potato. Attaching any of the above would name a material no source named and probably "
         "the wrong one. 284.549 t waiting on a naming decision, not on a search.",
    searched=["Phyllis2 - potato fibres #1065, potato rests #1068, potato mash #2841 (located, "
              "not taken)",
              "CVB Veevoedertabel 2023 - aardappelvezels p. 93/95/97, aardappeleiwit p. 87/89, "
              "aardappelzetmeel p. 99 (located, not taken)"],
    tables=[],
)


def expand(code: str, item: dict) -> dict:
    rows, used = [], {}
    for src, ref, variant, table in item.get("tables", []):
        used[src] = dict(SOURCES[src], citation_key=src)
        for param, unit, val, basis, note in table:
            rows.append(dict(
                stream_code=code, parameter_code=param, value_type="point",
                value_num=val, value_min="", value_max="", sd="", n_samples="",
                unit_code=unit, basis_code=basis, method_code="", value_origin="measured",
                source_key=src, source_ref=ref, year="", reported_label="",
                variant=variant, restatement="no", flag=item.get("flag", ""),
                transcription="machine", DECISION="", notes=note,
            ))
    return dict(stream_code=code, status=item["status"], note=item.get("note", ""),
                searched=item.get("searched", []), sources=list(used.values()), rows=rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for code, item in ITEMS.items():
        payload = expand(code, item)
        (OUT / f"{code}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {code:<30} {payload['status']:<10} {len(payload['rows']):>3} rows")
    print(f"{len(ITEMS)} items written to {OUT}")


if __name__ == "__main__":
    main()
