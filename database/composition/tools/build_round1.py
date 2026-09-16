"""Round 1 of the composition harvest: the extracted values, as data.

This script holds what was read off each source on 2026-09-09 and expands it into
two review CSVs under ../extraction/:

    round1_sources.csv        one row per source  -> candidate `source` rows
    round1_measurements.csv   one row per value   -> candidate `property_measurement` rows

NOTHING HERE IS LOADED. Every measurement row carries a blank `DECISION` and the
loader that will eventually read this file must refuse to run while any is blank,
per the workstream's curation rule. The review surface built from these CSVs is
`tools/build_review.py`.

The values were transcribed from the source pages by a model, not by a human, so
each row carries `transcription` = machine and a `flag` naming anything that
looked wrong on the way past. That is what the review is for.

    ../.venv/Scripts/python tools/build_round1.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction"

# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------
# citation_key is provisional. Zotero was unreachable on 2026-09-09 so no BBT key
# could be checked against the library; source FKs are ON UPDATE CASCADE, so these
# are safe to rename later (flag F-002).

SOURCES = [
    # key, type, title, url, year, kind, notes
    ("feedtables-inrae-cirad-afz-fao", "dataset",
     "Tables of composition and nutritional values of feed materials (INRAE, CIRAD, AFZ, FAO)",
     "https://www.feedipedia.org/", 2017, "compilation",
     "Curated compilation of published analyses. Every table gives mean, SD, min, max and n. "
     "Values marked with an asterisk are PREDICTED from equations, not measured - carried through "
     "on the `predicted` column by reviewer decision 2026-09-09."),
    ("phyllis2-tno", "dataset",
     "Phyllis2 - database for the physico-chemical composition of (treated) lignocellulosic biomass",
     "https://phyllis.nl/", 2026, "primary-indexed",
     "Each record cites its own literature reference, so provenance resolves to a paper rather than "
     "to the database. Fuel-oriented parameter set: proximate, ultimate CHONS, Cl, LHV/HHV, ash "
     "oxides - no Weende and no Van Soest fibre. "
     "SIBLING-FRACTION RECORDS EXIST AND ARE DELIBERATELY NOT USED (2026-09-10). Phyllis2 files "
     "records for a crop's individual fractions beside records for the whole residue: under maize "
     "it holds corn stover (7), corn stalks (6), corn cob (11), maize leaf and maize shoots. That "
     "is a consequence of what each submitter happened to analyse, not a classification - and "
     "maize and corn are the same plant, British and American English, not two materials. Only the "
     "STOVER records feed a whole-residue object; a stalk-only or cob-only analysis on `mais-stro` "
     "would be the same error as potato composition on potato peel. The fraction records stay "
     "useful: if the register ever distinguishes a maize fraction as its own object, the data is "
     "already there."),
    ("deEvan2020Cauliflower", "zotero",
     "De Evan, T.; Vintimilla, A.; Molina-Alcaide, E.; Ranilla, M.J.; Carro, M.D. "
     "Potential of Recycling Cauliflower and Romanesco Wastes in Ruminant Feeding: In Vitro Studies. "
     "Animals 2020, 10, 1247",
     "https://doi.org/10.3390/ani10081247", 2020, "primary",
     "IDENTIFIED BUT NOT EXTRACTED. Reports leaves, stems and sprouts as separate fractions - the "
     "only source found that splits cauliflower the way BioMobi's objects are split. PMC returned a "
     "captcha, MDPI a 403 and the CSIC repository an access denial, so the per-fraction table was "
     "never read. Needs manual retrieval."),
]

# --------------------------------------------------------------------------
# Feedipedia "Main analysis" tables, transcribed 2026-09-09
# --------------------------------------------------------------------------
# row = (feedipedia label, avg, sd, min, max, n, predicted)
# "" means the table left the cell empty.

FEEDIPEDIA = {
    # stream_code: (node, variant as the page names it, rows)
    "raapzaad-schroot": ("52", "Rapeseed meal, solvent-extracted, 00 type, oil < 5%", [
        ("Dry matter",                "89",   "0.9", "84.3", "94.5", "7005", ""),
        ("Crude protein",             "38.1", "1.3", "32.6", "44.8", "7056", ""),
        ("Crude fibre",               "14.3", "1.2", "8.6",  "18.1", "6136", ""),
        ("Neutral detergent fibre",   "31.6", "3.5", "20.5", "41.6", "241",  "*"),
        ("Acid detergent fibre",      "20.7", "1.6", "16.8", "26.6", "239",  "*"),
        ("Lignin",                    "9.7",  "1.2", "7.1",  "13.8", "285",  "*"),
        ("Ether extract",             "2.4",  "0.7", "0.3",  "5.7",  "5758", ""),
        ("Ash",                       "7.6",  "0.4", "6.5",  "10.4", "1164", ""),
        ("Insoluble ash",             "0.3",  "",    "",     "",     "",     ""),
        ("Starch (polarimetry)",      "6.3",  "1.6", "0.6",  "8.1",  "99",   ""),
        ("Starch (enzymatic)",        "1.6",  "",    "1.3",  "1.8",  "2",    ""),
        ("Total sugars",              "10.5", "0.9", "8.2",  "13.6", "80",   ""),
        ("Gross energy",              "19.3", "0.4", "18.3", "20",   "28",   "*"),
    ]),
    "suikerbiet-pulp": ("710", "Sugar beet pulp, pressed", [
        ("Dry matter",                "24.3", "3",   "15",   "35.1", "110",  ""),
        ("Crude protein",             "8.7",  "0.7", "6.7",  "12.3", "679",  ""),
        ("Crude fibre",               "20.8", "1.4", "17.3", "26",   "671",  ""),
        ("Ether extract",             "0.5",  "0.2", "0.2",  "0.8",  "9",    ""),
        ("Ash",                       "6.8",  "1.6", "3.9",  "14.3", "752",  ""),
        ("Insoluble ash",             "1.5",  "1.3", "0.2",  "7.4",  "646",  "*"),
        ("Neutral detergent fibre",   "49.5", "2.9", "48.4", "55.7", "6",    "*"),
        ("Acid detergent fibre",      "24.8", "1.6", "22.4", "26.6", "6",    "*"),
        ("Lignin",                    "1.8",  "0.1", "1.7",  "2",    "6",    ""),
        ("Starch (polarimetry)",      "0.5",  "",    "",     "",     "",     ""),
        ("Total sugars",              "5.2",  "2.2", "0.4",  "11.8", "638",  ""),
        ("Gross energy",              "17.1", "",    "",     "",     "",     ""),
    ]),
    "lijnzaad-schroot": ("735", "Linseed meal, solvent-extracted", [
        ("Dry matter",                "87.6", "1.0", "86.1", "90.4", "99",   ""),
        ("Crude protein",             "36.3", "1.3", "33.3", "39.5", "100",  ""),
        ("Crude fibre",               "11.6", "1.2", "9.2",  "13.5", "93",   ""),
        ("Neutral detergent fibre",   "27.4", "",    "",     "",     "",     "*"),
        ("Acid detergent fibre",      "15.7", "",    "",     "",     "",     "*"),
        ("Lignin",                    "4.9",  "1.0", "3.7",  "6.4",  "25",   ""),
        ("Ether extract",             "3.6",  "1.1", "2.0",  "5.6",  "40",   ""),
        ("Ether extract, HCl hydrolysis", "4.7", "0.6", "3.2", "5.6", "58",  ""),
        ("Ash",                       "6.4",  "0.2", "6.0",  "7.5",  "84",   ""),
        ("Total sugars",              "4.3",  "0.2", "4.1",  "4.6",  "24",   ""),
        ("Gross energy",              "19.4", "",    "19.4", "20.3", "2",    "*"),
    ]),
    "zemelen": ("12751", "Wheat bran", [
        ("Dry matter",                "87.0", "1.1", "83.6", "90.3", "19914", ""),
        ("Crude protein",             "17.3", "1.0", "14.1", "20.5", "19450", ""),
        ("Crude fibre",               "10.4", "1.3", "6.3",  "14.7", "19300", ""),
        ("Neutral detergent fibre",   "45.2", "4.6", "32.4", "56.5", "743",   "*"),
        ("Acid detergent fibre",      "13.4", "1.6", "8.4",  "17.6", "754",   "*"),
        ("Lignin",                    "3.8",  "0.7", "1.9",  "5.3",  "452",   "*"),
        ("Ether extract",             "3.9",  "0.6", "2.1",  "5.7",  "9117",  ""),
        ("Ash",                       "5.6",  "0.5", "4.0",  "7.3",  "11055", ""),
        ("Starch (polarimetry)",      "23.1", "4.0", "11.1", "35.4", "17115", ""),
        ("Total sugars",              "7.2",  "1.6", "3.7",  "10.5", "152",   ""),
        ("Gross energy",              "18.9", "0.3", "18.0", "19.9", "65",    "*"),
    ]),
    "aardappel": ("547", "Potato tubers, raw", [
        ("Dry matter",                "20.6", "2.6", "10.1", "27.3", "60",   ""),
        ("Crude protein",             "10.8", "0.9", "9.2",  "13",   "37",   ""),
        ("Crude fibre",               "2.5",  "0.5", "1.5",  "3.9",  "30",   ""),
        ("Ether extract",             "0.5",  "0.2", "0.2",  "1.3",  "51",   ""),
        ("Ash",                       "7.3",  "2.9", "4.4",  "15.8", "33",   ""),
        ("Insoluble ash",             "2.5",  "3",   "0.5",  "11.5", "16",   "*"),
        ("Neutral detergent fibre",   "8.3",  "",    "",     "",     "",     "*"),
        ("Acid detergent fibre",      "3.6",  "0.5", "2.6",  "4.9",  "22",   "*"),
        ("Lignin",                    "0.9",  "0.4", "0.4",  "2.2",  "22",   "*"),
        ("Starch (polarimetry)",      "71.9", "11.2","56.2", "82.3", "5",    "*"),
        ("Total sugars",              "6.6",  "2.5", "2.3",  "10.5", "11",   ""),
        ("Gross energy",              "16.8", "0.2", "16.7", "17.4", "13",   "*"),
    ]),
    "suikerbiet-loof": ("709", "Beet tops, fresh", [
        ("Dry matter",                "27.9", "",    "25.3", "30.4", "2",    ""),
        ("Crude protein",             "11.6", "4.7", "8.8",  "17.0", "3",    ""),
        ("Crude fibre",               "10.9", "",    "10.3", "11.4", "2",    ""),
        ("Neutral detergent fibre",   "34.7", "",    "34.5", "34.8", "2",    ""),
        ("Acid detergent fibre",      "21.0", "",    "18.0", "23.9", "2",    ""),
        ("Lignin",                    "5.5",  "",    "4.6",  "6.4",  "2",    ""),
        ("Ether extract",             "1.3",  "",    "0.9",  "1.6",  "2",    ""),
        ("Ash",                       "14.1", "",    "5.1",  "23.1", "2",    ""),
        ("Gross energy",              "16.1", "",    "",     "",     "",     "*"),
    ]),
    "suikerbiet": ("535", "Beet root, sugar type, fresh", [
        ("Dry matter",                "18.8", "4.2", "14.5", "24.1", "4",    ""),
        ("Crude protein",             "7.8",  "1.5", "6.2",  "9.9",  "5",    ""),
        ("Crude fibre",               "8.1",  "4.4", "5.6",  "14.7", "4",    ""),
        ("Neutral detergent fibre",   "20.4", "",    "10.8", "30.0", "2",    ""),
        ("Acid detergent fibre",      "12.7", "",    "5.5",  "19.8", "2",    ""),
        ("Lignin",                    "1.9",  "",    "",     "",     "1",    ""),
        ("Ether extract",             "0.5",  "0.2", "0.2",  "0.6",  "3",    ""),
        ("Ash",                       "6.9",  "4.2", "3.5",  "13.0", "4",    ""),
        ("Gross energy",              "16.9", "",    "",     "",     "",     "*"),
    ]),
    "mais-stro": ("16072", "Maize stover, dry", [
        ("Dry matter",                "92.8", "2.8", "84.1", "98",   "76",   ""),
        ("Crude protein",             "3.9",  "1.5", "1.8",  "11.5", "80",   ""),
        ("Crude fibre",               "40.7", "4.1", "29",   "48.2", "62",   ""),
        ("Neutral detergent fibre",   "75",   "13.6","39.5", "87.8", "60",   ""),
        ("Acid detergent fibre",      "49.6", "6.2", "37",   "59.4", "57",   ""),
        ("Lignin",                    "7.4",  "2.4", "3",    "13.5", "53",   ""),
        ("Ether extract",             "0.9",  "0.5", "0.2",  "2.2",  "42",   ""),
        ("Ash",                       "7.1",  "2",   "3.9",  "12.9", "73",   ""),
        ("Insoluble ash",             "2.1",  "1.5", "0.5",  "8.5",  "32",   ""),
        ("Starch (polarimetry)",      "11.4", "",    "10.9", "11.9", "2",    ""),
        ("Gross energy",              "18.2", "",    "",     "",     "",     "*"),
    ]),
    "soja-schroot": ("26068", "Soybean meal, type 48 and similar", [
        ("Dry matter",                "88",   "0.7", "80.1", "96.3", "9654", ""),
        ("Crude protein",             "52.6", "1.1", "43.8", "58.4", "9722", ""),
        ("Crude fibre",               "6.8",  "0.7", "4.8",  "10.7", "3328", ""),
        ("Neutral detergent fibre",   "14.2", "2.9", "6.6",  "19.5", "269",  "*"),
        ("Acid detergent fibre",      "8.4",  "2.3", "3.4",  "14.8", "238",  "*"),
        ("Lignin",                    "0.6",  "0.4", "0.1",  "1.8",  "213",  ""),
        ("Ether extract",             "1.8",  "0.5", "0.3",  "5.5",  "7801", ""),
        ("Ash",                       "7.1",  "0.6", "5.7",  "11.2", "2899", ""),
        ("Insoluble ash",             "0.6",  "0.5", "0",    "2.4",  "72",   ""),
        ("Starch (polarimetry)",      "5.7",  "1.4", "0.2",  "11.4", "367",  ""),
        ("Starch (enzymatic)",        "1.9",  "",    "1.4",  "2.7",  "4",    ""),
        ("Total sugars",              "9.2",  "1",   "7.2",  "13.7", "211",  ""),
        ("Gross energy",              "19.7", "0.6", "17",   "22.6", "136",  "*"),
    ]),
}

# Feedipedia label -> (parameter_code, unit, basis, method_code, note)
# The method is an AXIS on the measurement, not part of the parameter (2026-09-10).
# An empty method_code is a real state: the source did not say which determination.
FEED_MAP = {
    "Dry matter":              ("dry_matter",   "%",     "fresh", "",
                                "Feedipedia does not print the drying temperature"),
    "Crude protein":           ("crude_protein","%",     "dry",   "",
                                "Feedipedia does not print the N factor used"),
    "Crude fibre":             ("crude_fibre",  "%",     "dry",   "", ""),
    "Neutral detergent fibre": ("ndf",          "%",     "dry",   "",
                                "Feedipedia does not say whether amylase was used (aNDF) or ash corrected for (aNDFom)"),
    "Acid detergent fibre":    ("adf",          "%",     "dry",   "", ""),
    "Lignin":                  ("lignin",       "%",     "dry",   "",
                                "The column is headed only Lignin. The feedtables glossary says it is USUALLY the Van Soest ADL, and that hedge is why the method is left unknown here rather than set to lignin-adl"),
    "Ether extract":           ("fat_total",    "%",     "dry",   "ee-diethyl", ""),
    "Ether extract, HCl hydrolysis": ("fat_total", "%",  "dry",   "ee-hcl", ""),
    "Ash":                     ("ash",          "%",     "dry",   "",
                                "Feedipedia does not print the ashing temperature"),
    "Insoluble ash":           ("insoluble_ash","%",     "dry",   "", ""),
    "Starch (polarimetry)":    ("starch",       "%",     "dry",   "starch-polarimetric", ""),
    "Starch (enzymatic)":      ("starch",       "%",     "dry",   "starch-enzymatic", ""),
    "Total sugars":            ("total_sugars", "%",     "dry",   "", ""),
    "Gross energy":            ("hhv",          "MJ/kg", "dry",   "",
                                "Printed as gross energy (GE), the same quantity fuel sources call HHV"),
}

# --------------------------------------------------------------------------
# Phyllis2 records: NO LONGER TRANSCRIBED HERE.
# --------------------------------------------------------------------------
# The five records this file used to carry by hand (#704, #1053, #1564, #3131, #3161) moved
# to tools/fetch_phyllis.py on 2026-09-16, after a transcription-fidelity audit found this
# block held the ONLY wrong stored numbers in the whole corpus - 7 of its 79 values had a
# wrong basis and one had a wrong number, all from one mechanism: Phyllis leaves the `ar`
# cell EMPTY when the page computes it, and reading the row by eye then shifts every
# remaining number one column left.
#
# Two things follow, and the second is the one worth keeping.
# 1. The fix is re-extraction, not correction. A parser reads the column by its class and
#    cannot slip; a person reading a three-column table with a hole in it can, and did,
#    three separate times.
# 2. IT ALSO COSTS 20 ROWS, ON PURPOSE. #704 and #3161 had 20 values taken from `ar` cells
#    that Phyllis COMPUTES from the stored dry figure. Round 1 was honest about them
#    (`restatement=yes`), but fetch_phyllis.py refuses a computed cell by design, and that
#    rule already governs 93 rows. Applying it to 93 rows and not to these 20 was the
#    inconsistency. The numbers are not lost - they are the source's own arithmetic on
#    values we still hold.

# Phyllis2 label -> (parameter_code, method_code, value_origin, note)
PHYL_MAP = {
    "Moisture content":            ("moisture",        "", "measured", ""),
    "Ash content at 550 C":        ("ash",             "ash-550", "measured", ""),
    "Volatile matter":             ("volatile_matter", "", "measured", ""),
    "Fixed carbon":                ("fixed_carbon",    "", "calculated",
                                    "100 minus moisture, ash and volatile matter - arithmetic by the source"),
    "Carbon":                      ("total_carbon",    "", "measured", ""),
    "Hydrogen":                    ("hydrogen",        "", "measured", ""),
    "Oxygen":                      ("oxygen",          "", "unknown",
                                    "usually taken by difference rather than determined, and the record does not say which"),
    "Nitrogen":                    ("total_nitrogen",  "", "measured", ""),
    "Sulphur":                     ("sulphur",         "", "measured", ""),
    "Chlorine (Cl)":               ("chlorine",        "", "measured",
                                    "total Cl from elemental analysis, not water-soluble chloride"),
    "Net calorific value (LHV)":   ("lhv",             "", "calculated",
                                    "recomputed per basis from HHV and the water actually present - NOT a rescaling of the other bases"),
    "Gross calorific value (HHV)": ("hhv",             "", "measured", ""),
    "Cellulose":                   ("cellulose",       "", "measured", ""),
    "Hemicellulose":               ("hemicellulose",   "", "measured", ""),
    "Lignin":                      ("lignin",          "", "measured",
                                    "the record says only lignin - neither ADL nor Klason is named"),
    "Cadmium (Cd)":                ("cadmium",         "", "measured", ""),
    "Lead (Pb)":                   ("lead",            "", "measured", ""),
}

BASIS_COL = {"ar": "fresh", "dry": "dry", "daf": "dry_ash_free"}

# objects with no data, and why
NO_DATA = {
    "aardappel-loof": ("no source", "F-004",
        "Absent from the Phyllis2 index (searched, not assumed) and no Feedipedia datasheet, while "
        "every other field residue in this round is in one or both. 744.945 t - the largest "
        "component of the #3 commodity."),
    "zetmeel-reststroom": ("blocked", "G-19",
        "The object is Prodcom 106220 'afvallen van zetmeelfabrieken' and no source says what the "
        "material is. Starch side-stream composition is abundant in the literature and was "
        "deliberately NOT attached: it would name a material no source named, and Flanders crushes "
        "wheat rather than potato, so the obvious literature is probably the wrong material too."),
    "bloemkool-loof": ("source found, not extracted", "F-005",
        "De Evan et al. 2020 splits cauliflower into leaves, stems and sprouts - the only source "
        "found that matches BioMobi's object split. Full text was unreachable this session (PMC "
        "captcha, MDPI 403, CSIC access denied). Needs manual retrieval."),
    "bloemkool-harten": ("source found, not extracted", "F-005",
        "Same source and same blocker as bloemkool-loof: the stem fraction of De Evan et al. 2020."),
}


def build():
    OUT.mkdir(parents=True, exist_ok=True)

    with (OUT / "round1_sources.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["citation_key", "source_type", "title", "url", "year", "kind", "notes"])
        for row in SOURCES:
            w.writerow(row)

    rows: list[dict] = []

    for stream, (node, variant, table) in FEEDIPEDIA.items():
        for label, avg, sd, vmin, vmax, n, pred in table:
            code, unit, basis, method, note = FEED_MAP[label]
            rows.append(dict(
                stream_code=stream, parameter_code=code, value_type="point",
                value_num=avg, value_min=vmin, value_max=vmax, sd=sd, n_samples=n,
                unit_code=unit, basis_code=basis, method_code=method,
                value_origin="predicted" if pred else "measured",
                source_key="feedtables-inrae-cirad-afz-fao",
                source_ref=f"Feedipedia node {node}", year="",
                reported_label=label, variant=variant,
                predicted="yes" if pred else "no",
                restatement="no", flag="", transcription="machine", DECISION="",
                notes=note,
            ))

    fields = ["stream_code", "parameter_code", "value_type", "value_num", "value_min",
              "value_max", "sd", "n_samples", "unit_code", "basis_code", "method_code",
              "value_origin", "source_key", "source_ref", "year", "reported_label",
              "variant", "predicted", "restatement", "flag", "transcription",
              "DECISION", "notes"]
    with (OUT / "round1_measurements.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(rows)

    with (OUT / "round1_nodata.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["stream_code", "state", "raised_as", "why"])
        for stream, (state, flag, why) in NO_DATA.items():
            w.writerow([stream, state, flag, why])

    kept = sum(1 for r in rows if r["restatement"] == "no")
    print(f"{len(rows)} candidate measurement rows over "
          f"{len({r['stream_code'] for r in rows})} objects")
    print(f"  {kept} on their primary basis, {len(rows) - kept} basis restatements")
    import collections
    print(f"  value_origin: {dict(collections.Counter(r['value_origin'] for r in rows))}")
    print(f"  with a named method: {sum(1 for r in rows if r['method_code'])}")
    print(f"  {sum(1 for r in rows if r['flag'])} carry a transcription/quality flag")
    print(f"{len(NO_DATA)} objects with no data")
    print(f"written to {OUT}")


if __name__ == "__main__":
    build()
