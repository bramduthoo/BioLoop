"""Round 3 of the composition harvest: per-stream, multi-source, to the reviewer's rules.

    ../.venv/Scripts/python tools/round3_data.py    ->  ../extraction/round3/<code>.json

WHAT CHANGED FROM ROUND 2, and why this file exists at all. Round 2 leaned on two
databases that happened to be open -- Feedipedia and Phyllis2 -- when the agreed method
was a targeted hunt PER STREAM across databases AND literature. Round 3 does that.

THE RULES, settled with the reviewer on 2026-09-12:

1. SCOPE is the 80% cumulative line, not an open list. The 2026-09-11 selection reaches
   80% at rank 15 (Zuivelnevenstroom, 81,2% cumulative). Within those 15 commodities the
   50 kt/yr filter removes small fractions -- it exists to keep `raapzaad-stro` at 7.818 t
   and `aardappel gebakken nevenstroom` at 9.671 t out of BioMobi, NOT to widen the list.
   That gives 20 objects, minus `aardappel-industrieresidu` which the reviewer struck:
   NINETEEN targets.

2. QUALITY: primary papers with their own measurements, research-institute reports,
   curated databases that state method and n, PLUS regional grey and sector sources
   (CVB, Belgapom, BEMEFA, Fevia). Every source carries its `kind`, so the reviewer can
   filter by pedigree rather than having to trust the harvest's judgement.

3. GEOGRAPHY: a non-European measurement is admissible -- composition is intrinsic to the
   object -- but `country` and `year` ride on every source, so a figure can never pass
   silently as Flemish.

4. DEPTH: keep searching a stream until a new source stops adding new parameters, with a
   floor of three independent sources where three exist. Contradictions are kept as
   separate rows, never averaged: two sources disagreeing is data, not a problem.

A table entry is:
    ("<source_key>", "<source_ref>", "<variant as the source names it>", "<basis>",
     [ (parameter, unit, value, sd, min, max, n, predicted, *optional note), ... ])
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction" / "round3"

SOURCES = {
    "s2biom-d24-biomass-properties": dict(
        source_type="dataset", year=2016, kind="institutional-database",
        country="EU",
        title="S2BIOM D2.4 - Database for standardized biomass characterisation "
              "(biomass properties table, public version 1 November 2016)",
        url="https://s2biom.wenr.wur.nl/biomass-characteristics",
        notes="The third of the three composition databases the field has, beside Phyllis2 and "
              "FoodWasteEXplorer, and the one round 2 never opened. FP7 project, property table "
              "compiled by VTT and WUR across 118 European biomass categories with a typical, a "
              "minimum and a maximum per property. It carries things no other source in this "
              "harvest does: ash melting behaviour, bulk/bale/particle/basic density, and "
              "cellulose, hemicellulose and lignin as a measured triple rather than as a Van "
              "Soest detergent sequence. No n per value - the spread IS the evidence."),
}

SOURCES["kaplan2018PotatoHaulm"] = dict(
    source_type="zotero", year=2018, kind="primary", country="TR",
    title="Kaplan, M.; Ulger, I.; Kokten, K.; Uzun, S.; Varhan Oral, E.; Ozaktan, H.; "
          "Temizgul, R.; Kale, H. Nutritional composition of potato (Solanum tuberosum L.) "
          "haulms. Progress in Nutrition 2018, 20(1-S), 90-95",
    url="https://doi.org/10.23751/pn.v20i1-S.5541",
    notes="The ONLY primary composition study found for potato haulm after three sessions of "
          "looking, and the stream is 800.480 t - the second largest target in the round. Five "
          "cultivars (Milva, Laura, Granola, Europrima, Jelly) grown in TURKEY. The figures are "
          "the RANGE ACROSS CULTIVARS, not a mean with a spread, so they are recorded as ranges "
          "with n = 5 cultivars. Geography is admissible by reviewer decision of 2026-09-12 - "
          "composition is intrinsic to the object - but Turkish cultivars, soils and harvest "
          "timing are not Flemish ones, and a Flemish haulm is chemically DESICCATED before "
          "harvest, which this study's material was probably not. Treat as indicative.")

ITEMS: dict[str, dict] = {}

ITEMS["aardappel-loof"] = dict(
    status="done",
    flag="RANGE ACROSS FIVE CULTIVARS, NOT A MEAN WITH A SPREAD - and Turkish, not Flemish. "
         "Only the abstract was reachable, so ADL, ether extract and dry matter are absent even "
         "though the paper reports them. The single most important caveat: Flemish potato haulm "
         "is chemically DESICCATED before harvest and this material was almost certainly not, "
         "which changes exactly the fractions a valorisation route would care about.",
    note="Closes three sessions of nothing. F-004 moves from 'no composition source anywhere' "
         "to 'one primary study, non-European, abstract only' - which is progress and not a "
         "close. What would close it: a European haulm analysis, or the full text of this paper "
         "for its ADL and mineral table.",
    searched=["Phyllis2 index - absent", "Feedipedia - no datasheet",
              "FoodWasteEXplorer 'Potato haulm' - zero rows",
              "CVB Veevoedertabel 2023 - no aardappelloof sheet (it has cichoreiloof, "
              "erwtenloof and bietenblad, so the absence is specific to potato)",
              "S2BIOM D2.4 - the agricultural-residue block has rice/wheat/rape straw, maize "
              "stover, sugarbeet tops and sunflower straw, and no potato haulm",
              "Kaplan et al. 2018, Progress in Nutrition - the one hit"],
    tables=[],
    ranges=[("kaplan2018PotatoHaulm", "doi:10.23751/pn.v20i1-S.5541",
             "Potato haulm, 5 cultivars, Turkey", "dry", [
        ("crude_protein", "%",     "10.85", "14.48", "5"),
        ("ash",           "%",     "5.22",  "9.10",  "5"),
        ("adf",           "%",     "22.46", "33.94", "5"),
        ("ndf",           "%",     "47.99", "60.91", "5"),
        ("iron",          "mg/kg", "47.35", "180.07", "5"),
        ("manganese",     "mg/kg", "28.14", "85.15", "5"),
        ("nickel",        "mg/kg", "3.40",  "8.60",  "5"),
        ("copper",        "mg/kg", "10.84", "15.35", "5"),
        ("zinc",          "mg/kg", "4.14",  "15.60", "5"),
        ("cadmium",       "mg/kg", "1.02",  "1.55",  "5"),
        ("lead",          "mg/kg", "6.74",  "9.80",  "5"),
    ])],
)

# --------------------------------------------------------------------------
# S2BIOM covers four of the nineteen targets. One table, four streams.
# --------------------------------------------------------------------------

_S2_COLS = {
    "tarwe-stro": ("2.2.1.2 Cereal (wheat) straw", {
        "moisture":        ("%",     "15",    "10",   "20"),
        "bulk_density":    ("kg/m3", "175",   "150",  "200"),
        "particle_density": ("kg/m3", "80",   "",     ""),
        "lhv":             ("MJ/kg", "15.95", "14.49", "17.4"),
        "hhv":             ("MJ/kg", "17.15", "15.7", "18.6"),
        "ash":             ("%",     "6.5",   "1.1",  "13.5"),
        "ash_melting_dt":  ("degC",  "892",   "780",  "1080"),
        "lignin":          ("%",     "18",    "8",    "30"),
        "cellulose":       ("%",     "37",    "28.8", "51.5"),
        "hemicellulose":   ("%",     "27.6",  "10.5", "39.1"),
        "total_nitrogen":  ("%",     "0.61",  "0.29", "2.08"),
        "chlorine":        ("%",     "0.3",   "0.02", "2.3"),
        "sulphur":         ("%",     "0.12",  "0.03", "0.46"),
    }),
    "mais-stro": ("2.2.1.4 Maize stover", {
        "moisture":        ("%",     "15",    "15",   "60"),
        "bulk_density":    ("kg/m3", "175",   "150",  "200"),
        "particle_density": ("kg/m3", "80",   "",     ""),
        "basic_density":   ("kg/m3", "126",   "",     ""),
        "lhv":             ("MJ/kg", "17.04", "16.35", "17.73"),
        "hhv":             ("MJ/kg", "18.325", "17.65", "19"),
        "ash":             ("%",     "5.58",  "3.7",  "9.7"),
        "ash_melting_dt":  ("degC",  "1277",  "",     ""),
        "lignin":          ("%",     "15",    "11",   "17"),
        "cellulose":       ("%",     "37",    "28",   "52"),
        "hemicellulose":   ("%",     "25",    "19",   "31"),
        "total_nitrogen":  ("%",     "0.65",  "0.6",  "1.14"),
        "chlorine":        ("%",     "0.28",  "0",    "0.6"),
        "sulphur":         ("%",     "0.11",  "0.1",  "0.12"),
    }),
    "suikerbiet-loof": ("2.2.1.5 Sugarbeet tops/leaves", {
        "moisture":        ("%",     "85",    "",     ""),
        "bulk_density":    ("kg/m3", "175",   "",     ""),
        "lhv":             ("MJ/kg", "16.6",  "",     ""),
        "ash":             ("%",     "10",    "5",    "23"),
        "lignin":          ("%",     "3.3",   "",     ""),
        "cellulose":       ("%",     "10.3",  "",     ""),
        "hemicellulose":   ("%",     "9.6",   "",     ""),
        "total_nitrogen":  ("%",     "1.92",  "",     ""),
        "chlorine":        ("%",     "0.05",  "",     ""),
    }),
    "zemelen": ("4.2.1.5 Cereal bran", {
        "moisture":        ("%",     "9",     "",     ""),
        "lhv":             ("MJ/kg", "20.85", "",     ""),
        "hhv":             ("MJ/kg", "20.03", "19.07", "20.98"),
        "ash":             ("%",     "7",     "",     ""),
        "ash_melting_dt":  ("degC",  "1340",  "",     ""),
        "lignin":          ("%",     "11.1",  "3",    "14"),
        "cellulose":       ("%",     "13.8",  "12",   "33.3"),
        "hemicellulose":   ("%",     "26.9",  "25.2", "36"),
        "total_nitrogen":  ("%",     "1.32",  "1.06", "2.94"),
        "chlorine":        ("%",     "0.329", "",     ""),
        "sulphur":         ("%",     "0.12",  "0.11", "0.12"),
    }),
}

_S2_NOTE = {
    "moisture": "S2BIOM reports moisture as received, so this row is on the FRESH basis while "
                "every other row from this source is on dry",
    "ash_melting_dt": "oxidising conditions; the reducing-atmosphere value is a different "
                      "determination and S2BIOM does not print it",
    "lignin": "S2BIOM gives lignin, cellulose and hemicellulose as a measured triple, NOT as a "
              "Van Soest detergent sequence - which is why it is `lignin` here and not ADL",
}

_S2_FLAG = ("S2BIOM prints a TYPICAL value with a minimum and a maximum and NO sample count. The "
            "spread is the evidence, so the min/max columns matter more here than on a source "
            "that reports n. Its ash-oxide block (Na2O, P2O5, K2O, Fe2O3, CaO, MgO) is NOT taken: "
            "the unit column says `w-% dry` while the values run to 46, which can only be percent "
            "OF ASH. Same treatment as the apple-pomace sugars row - an internally impossible "
            "unit is not recorded under either reading.")

for _code, (_variant, _rows) in _S2_COLS.items():
    ITEMS[_code] = dict(
        status="done",
        flag=_S2_FLAG,
        note=f"S2BIOM column `{_variant}`. Adds ash melting behaviour, densities and the "
             f"cellulose/hemicellulose/lignin triple, none of which Feedipedia or Phyllis2 "
             f"carries for this stream.",
        searched=["S2BIOM D2.4 public biomass properties table (118 columns) - "
                  "columns for rice straw, cereal (wheat) straw, oil seed rape straw, maize "
                  "stover, sugarbeet tops/leaves, sunflower straw and cereal bran"],
        tables=[("s2biom-d24-biomass-properties", "S2BIOM D2.4 properties table", _variant,
                 "dry",
                 [(p, u, v, "", lo, hi, "", "", _S2_NOTE.get(p, ""))
                  for p, (u, v, lo, hi) in _rows.items()])],
    )
    # moisture is reported as received, not on dry
    for _t in ITEMS[_code]["tables"]:
        for _i, _r in enumerate(_t[4]):
            if _r[0] == "moisture":
                _t[4][_i] = _r  # basis handled at expand time


def expand(code: str, item: dict) -> dict:
    rows, used = [], {}
    for src, ref, variant, basis, table in item.get("tables", []):
        used[src] = dict(SOURCES[src], citation_key=src)
        for r in table:
            param, unit, val, sd, vmin, vmax, n, pred = r[:8]
            note = r[8] if len(r) > 8 else ""
            rows.append(dict(
                stream_code=code, parameter_code=param, value_type="point",
                value_num=val, value_min=vmin, value_max=vmax, sd=sd, n_samples=n,
                unit_code=unit,
                basis_code="fresh" if param == "moisture" else basis,
                method_code="ash-dt-oxidising" if param == "ash_melting_dt" else "",
                value_origin="predicted" if pred else "measured",
                source_key=src, source_ref=ref, year=str(SOURCES[src]["year"]),
                reported_label="", variant=variant, restatement="no",
                flag=item.get("flag", ""), transcription="machine", DECISION="", notes=note,
            ))
    for src, ref, variant, basis, table in item.get("ranges", []):
        used[src] = dict(SOURCES[src], citation_key=src)
        for param, unit, lo, hi, n in table:
            rows.append(dict(
                stream_code=code, parameter_code=param, value_type="range",
                value_num="", value_min=lo, value_max=hi, sd="", n_samples=n,
                unit_code=unit, basis_code=basis, method_code="", value_origin="measured",
                source_key=src, source_ref=ref, year=str(SOURCES[src]["year"]),
                reported_label="", variant=variant, restatement="no",
                flag=item.get("flag", ""), transcription="machine", DECISION="",
                notes="range across cultivars, not a mean with a spread",
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
