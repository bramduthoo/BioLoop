"""Round 5: the thin-vector streams, from primary literature rather than from databases.

    ../.venv/Scripts/python tools/round5_data.py    ->  ../extraction/round5/<code>.json

Rounds 1-4 emptied the databases. What the coverage analysis left behind is three
objects that the databases DO NOT AND WILL NOT HOLD, because none of them is a traded
feed: potato haulm, cauliflower leaf, sprout stalk. Round 5 goes at those with the
primary literature, and it takes two findings that matter more than the rows.

FIRST: THE DATABASES' SILENCE IS NOW A CHECKED FACT, not an impression. Round 2
concluded that "nothing measures" the leaf and haulm streams after typing words into
search boxes. This round pulled Feedipedia's whole feed index (779 datasheets) and
Phyllis2's whole record index (3289 records) and grepped them. Feedipedia has no
cauliflower, no cabbage, no Brussels sprouts and no potato haulm at all - its only
`haulm` is Bambara groundnut. That is the difference between "I did not find it" and
"it is not there", and only the second is worth writing down.

SECOND: A REFERENCE FEED IS A MEASUREMENT. Both Madrid papers analysed sugar beet pulp
and wheat DDGS alongside their subject material, as yardsticks. The beet pulp column is
a full proximate and detergent-fibre analysis of a stream BioMobi already holds, done in
a named laboratory to cited methods - so it is taken. But it is taken ONCE: the two
papers print the same figures for it (48,0 NDF, 24,2 ADF, 9,44 CP) because it is the
same sample from the same group. Two papers citing one analysis are one measurement,
which is the rule that dropped 258 FoodWasteEXplorer rows in round 3, applied to
literature instead of to a database.

ON SEM AND THE `sd` COLUMN. Both papers print SEM, not SD, and their SEM is for the
vegetable x fraction INTERACTION across both vegetables - it is not the spread of these
three samples. It therefore does NOT go in `sd`, which would silently turn a
between-treatment error into a within-material spread. It goes in the notes, as printed.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction" / "round5"

SOURCES = {
    "deEvan2020CauliflowerRomanesco": dict(
        source_type="zotero", year=2020, kind="primary", country="ES",
        title="de Evan, Vintimilla, Molina-Alcaide, Ranilla & Carro (2020). Potential of "
              "Recycling Cauliflower and Romanesco Wastes in Ruminant Feeding: In Vitro "
              "Studies. Animals 10(8), 1247",
        url="https://doi.org/10.3390/ani10081247",
        notes="Universidad Politecnica de Madrid. Material from local markets on three "
              "different weeks between October and December 2017, pooled per week, SEPARATED "
              "INTO LEAVES, STEMS AND SPROUTS and analysed per fraction - which is the split "
              "BioMobi's objects need and which no database made. Methods cited per "
              "determination: AOAC 934.01 dry matter, 942.05 ash, 920.39 ether extract; "
              "nitrogen by Dumas on a Leco TruSpec CN; NDF by Van Soest, ADF and lignin by "
              "Robertson & Van Soest, all on an Ankom 220 and EXPRESSED EXCLUSIVE OF RESIDUAL "
              "ASH. Also carries sugar beet pulp and wheat DDGS as reference feeds, n = 1."),
    "koli2019PotatoHaulms": dict(
        source_type="zotero", year=2019, kind="primary", country="IN",
        title="Koli, Misra & Singh (2019). Utilization of Potato Haulms: An Alternate Feed "
              "Resource for Livestock. Acta Scientific Agriculture 3(8), 83-85",
        url="https://doi.org/10.31080/ASAG.2019.03.0568",
        notes="Indian Grassland and Fodder Research Institute, Jhansi. TAKEN WITH ITS WEAKNESS "
              "STATED: the institute is a real ICAR research body but Acta Scientific is a weak "
              "journal, and the composition of the starting material is given in the ABSTRACT "
              "rather than in a table, so no SD, no n and no method set. It is recorded because "
              "aardappel-loof had exactly one source and the two disagree in a way that is "
              "itself informative - not because this is a good paper."),
}

ITEMS: dict[str, dict] = {}

ITEMS["bloemkool-loof"] = dict(
    status="done",
    note="THE FIRST SOURCE THAT ANALYSED THE LEAF AS THE LEAF. Round 3 left this object on "
         "FoodWasteEXplorer alone, and that harvest turned out to be thinner than its row count "
         "suggested: eight of its parameters appear TWICE with identical figures to the last "
         "decimal - ADF 19,4 / ash 13,7 / calcium 2,17 / cellulose 15,2 / fat 4,2 / "
         "hemicellulose 8,1 / magnesium 0,44 / organic matter 86,4 - once citing `Vegetable "
         "waste as animal feed` and once citing `Utilization of fruit and vegetable wastes, "
         "FAO`. Two references to one analysis, the FAO compilation quoting the paper. The rows "
         "stay as the source printed them, per `record what the source said`, but 197 kt of "
         "cauliflower leaf rested on about eight real numbers. "
         "de Evan et al. 2020 separated leaves, stems and sprouts and analysed each, with a "
         "method cited per determination. Ten parameters on the LEAF, n = 3. "
         "CELLULOSE AND HEMICELLULOSE ARE MARKED `calculated`, AND THAT IS CHECKED RATHER THAN "
         "ASSUMED: the paper cites determinations for NDF, ADF and lignin only, and its figures "
         "reproduce exactly by difference - 20,4 - 2,42 = 17,98 against a printed cellulose of "
         "18,0, and 32,3 - 20,4 = 11,9 against a printed hemicellulose of 11,9. "
         "ASH IS NOT RECORDED although the paper analysed it: it prints ORGANIC MATTER, and "
         "100 - OM would be my arithmetic, not their measurement. "
         "THE CAVEAT THE REVIEWER SHOULD WEIGH: this is MARKET waste from Madrid, not Flemish "
         "field or packing-line residue. Retail trimmings are younger and less weathered than "
         "leaf left standing after the curd is cut.",
    searched=["Feedipedia - FULL FEED INDEX PULLED, 779 datasheets, grepped: no cauliflower, no "
              "cabbage, no Brassica leaf of any kind. The round-2 conclusion is now a checked "
              "fact rather than a failed search",
              "Phyllis2 - FULL INDEX PULLED, 3289 records: `cauliflower` #1564/#1565/#1566 only, "
              "and all three are the 1993 Dutch GFT household-waste survey with the plant part "
              "unstated. Refused in tools/fetch_phyllis.py",
              "CVB Veevoedertabel 2023 - no cauliflower sheet",
              "de Evan et al. 2020, Animals 10(8):1247 - THE MATCH",
              "de Evan et al. 2019, Animals 9(9):588 (the sibling cabbage paper) - Brussels "
              "sprouts, white/Savoy/red cabbage, all as the VEGETABLE, no leaf fraction"],
    tables=[("deEvan2020CauliflowerRomanesco", "de Evan et al. 2020, Table 1, column `Cauliflower - Leaves`",
             "Cauliflower leaves, Madrid market waste, Oct-Dec 2017", [
        ("dry_matter",     "%", "6.86",  "fresh", "dm-oven-105",    "measured",   "AOAC 934.01. SEM 0,403 (vegetable x fraction interaction, not a within-material SD)"),
        ("organic_matter", "%", "85.4",  "dry",   "",               "measured",   "SEM 0,56. The paper prints OM and not ash; 100 - OM would be our arithmetic"),
        ("crude_protein",  "%", "21.9",  "dry",   "dumas",          "measured",   "N by Dumas on a Leco TruSpec CN. SEM 1,26"),
        ("fat_total",      "%", "3.62",  "dry",   "ee-diethyl",     "measured",   "printed as Ether extract, AOAC 920.39. SEM 0,278"),
        ("total_sugars",   "%", "25.5",  "dry",   "",               "measured",   "method of Marcos et al. SEM 2,36"),
        ("ndf",            "%", "32.3",  "dry",   "ndf-ash-corrected", "measured", "Van Soest, Ankom 220, exclusive of residual ash. SEM 1,16"),
        ("adf",            "%", "20.4",  "dry",   "",               "measured",   "Robertson & Van Soest, exclusive of residual ash. SEM 0,64"),
        ("lignin",         "%", "2.42",  "dry",   "lignin-adl",     "measured",   "Robertson & Van Soest - the acid-detergent lignin of the sequence, said by the paper rather than inferred by us. SEM 0,568"),
        ("cellulose",      "%", "18.0",  "dry",   "fibre-van-soest", "calculated", "ADF - lignin: 20,4 - 2,42 = 17,98 against the printed 18,0. SEM 0,81"),
        ("hemicellulose",  "%", "11.9",  "dry",   "fibre-van-soest", "calculated", "NDF - ADF: 32,3 - 20,4 = 11,9, the printed figure exactly. SEM 0,83"),
    ])],
    flag="Market waste from Madrid, not Flemish field residue. And NDICP (neutral detergent "
         "insoluble crude protein, 13,1 % OF CRUDE PROTEIN) is NOT recorded: it is a share of "
         "another parameter rather than a content, the same objection that keeps `% of total "
         "fatty acids` out. Registering it would need a unit the catalogue does not have.",
)

ITEMS["suikerbiet-pulp"] = dict(
    status="done",
    note="A REFERENCE FEED IS STILL A MEASUREMENT. de Evan et al. ran sugar beet pulp alongside "
         "the cauliflower as a yardstick, to the same cited methods in the same laboratory, and "
         "printed a full proximate and detergent-fibre column for it. That is a measurement of a "
         "stream BioMobi holds and it is taken. "
         "TAKEN ONCE, AND THAT IS THE POINT. The sibling cabbage paper (Animals 9(9):588, same "
         "group, same year) prints the SAME beet-pulp column - NDF 48,0, ADF 24,2, CP 9,44, "
         "sugars 13,5 - down to a 23,8/23,9 rounding difference on hemicellulose. It is one "
         "sample reported in two papers, not two analyses. Recording both would have invented a "
         "second measurement out of a citation, which is exactly what the FoodWasteEXplorer "
         "deduplication rule exists to prevent. "
         "n = 1, stated by the paper, and the material is a DEHYDRATED pulp at 89,1 % dry matter "
         "- which is why it lands beside CVB's dried grade and not beside the pressed one.",
    searched=["de Evan et al. 2020, Animals 10(8):1247, Table 1 reference-feed column - TAKEN",
              "de Evan et al. 2019, Animals 9(9):588, Table 1 reference-feed column - the same "
              "sample, deliberately NOT taken a second time"],
    tables=[("deEvan2020CauliflowerRomanesco", "de Evan et al. 2020, Table 1, reference feed `Sugar Beet Pulp`",
             "Sugar beet pulp, dehydrated, reference feed, n = 1", [
        ("dry_matter",     "%", "89.1", "fresh", "dm-oven-105", "measured",   "AOAC 934.01"),
        ("organic_matter", "%", "94.9", "dry",   "",            "measured",   ""),
        ("crude_protein",  "%", "9.44", "dry",   "dumas",       "measured",   "N by Dumas on a Leco TruSpec CN"),
        ("fat_total",      "%", "0.80", "dry",   "ee-diethyl",  "measured",   "printed as Ether extract, AOAC 920.39"),
        ("total_sugars",   "%", "13.5", "dry",   "",            "measured",   ""),
        ("ndf",            "%", "48.0", "dry",   "ndf-ash-corrected", "measured", "exclusive of residual ash"),
        ("adf",            "%", "24.2", "dry",   "",            "measured",   "exclusive of residual ash"),
        ("lignin",         "%", "2.16", "dry",   "lignin-adl",  "measured",   ""),
        ("cellulose",      "%", "22.0", "dry",   "fibre-van-soest", "calculated", "ADF - lignin: 24,2 - 2,16 = 22,04 against the printed 22,0"),
        ("hemicellulose",  "%", "23.8", "dry",   "fibre-van-soest", "calculated", "NDF - ADF: 48,0 - 24,2 = 23,8. The sibling paper prints 23,9 for the same sample"),
    ])],
    flag="n = 1, and it is a reference feed rather than the paper's subject - so it carries none "
         "of the sampling care the cauliflower columns do.",
)

ITEMS["aardappel-loof"] = dict(
    status="thin",
    note="STILL THE WORST-COVERED LARGE STREAM, and round 5 does not close it - it adds a second "
         "source and, more usefully, establishes that the silence is real. "
         "WHAT WAS SETTLED: Feedipedia's full 779-datasheet index holds no potato haulm (its only "
         "`haulm` is Bambara groundnut) and Phyllis2's full 3289-record index holds none either. "
         "Round 2 and round 3 said `absent` after using the search boxes; that is now a grep over "
         "both complete indexes. 800 kt/yr of material that no feed or fuel database has ever "
         "analysed is a FINDING about the material, not a failure of the harvest. "
         "WHAT WAS ADDED: Koli et al. 2019 gives the composition of the fresh haulm they went on "
         "to ensile. It brings DRY MATTER and ETHER EXTRACT, neither of which Kaplan's abstract "
         "carried, plus a second reading of CP, NDF, ADF and ash. "
         "AND THE TWO SOURCES DISAGREE, COHERENTLY. Koli reads CP 18,45 / NDF 28,45 / ADF 19,4 / "
         "ash 10,23 against Kaplan's ranges of 10,85-14,48 / 47,99-60,91 / 22,46-33,94 / "
         "5,22-9,10. Higher protein with much lower fibre is GREEN haulm; Kaplan's is senescent "
         "material at harvest, and his own figures are dry-herbage yields. The 16,81 % dry matter "
         "Koli reports is itself the evidence - that is a standing green crop, not a desiccated "
         "one. This is a MATURITY difference, not a contradiction to resolve, and it is exactly "
         "the axis Flemish haulm sits on the wrong side of: here the crop is CHEMICALLY "
         "DESICCATED before harvest, so neither source describes the material BioMobi means. "
         "WHAT WOULD ACTUALLY CLOSE IT: an analysis of desiccated haulm at lifting, in NW Europe. "
         "Nothing found so far is that.",
    searched=["Feedipedia - FULL FEED INDEX PULLED (779 datasheets) and grepped for potato, "
              "haulm, vine, leaf, leaves, top: nothing. Node 23075 `Potato by-products` is pulp, "
              "peel, steamed peel and fried, all tuber",
              "Phyllis2 - FULL RECORD INDEX PULLED (3289) and grepped: nine potato records, every "
              "one of them tuber, peel or starch-industry material. No haulm, no leaf, no stem",
              "S2BIOM D2.4 - the agricultural-residue block has rice/wheat/rape straw, maize "
              "stover, sugarbeet tops and sunflower straw. No potato haulm (round 3)",
              "CVB Veevoedertabel 2023 - has cichoreiloof, erwtenloof and bietenblad but no "
              "aardappelloof; the absence is specific to potato (round 3)",
              "FoodWasteEXplorer `Potato haulm` - zero rows (round 3)",
              "Koli, Misra & Singh 2019, Acta Scientific Agriculture 3(8) - TAKEN, with its "
              "weakness stated",
              "Kaplan et al. 2018, Progress in Nutrition - round 3's source, abstract only",
              "Carruthers 1975 (Biotechnol. Bioeng.) and Hanczakowski (Potato Research) both "
              "analyse PROTEIN CONCENTRATE extracted from haulm, which is a process output and "
              "not the stream. Paywalled as well. Not pursued"],
    tables=[("koli2019PotatoHaulms", "Koli et al. 2019, abstract", "Potato haulms, India, before ensiling", [
        ("dry_matter",    "%", "16.81", "fresh", "", "measured", "green haulm - this figure is why the disagreement with Kaplan reads as maturity"),
        ("crude_protein", "%", "18.45", "dry",   "", "measured", "against Kaplan's 10,85-14,48 % on five Turkish cultivars"),
        ("ndf",           "%", "28.45", "dry",   "", "measured", "against Kaplan's 47,99-60,91 %"),
        ("adf",           "%", "19.4",  "dry",   "", "measured", "against Kaplan's 22,46-33,94 %"),
        ("fat_total",     "%", "6.27",  "dry",   "", "measured", "printed as EE; the solvent is not stated, so no method is assigned"),
        ("ash",           "%", "10.23", "dry",   "", "measured", "against Kaplan's 5,22-9,10 %"),
    ])],
    flag="Every figure here is read off an ABSTRACT, not a table: no SD, no n, no method set. And "
         "the material is Indian green haulm where BioMobi means Flemish desiccated haulm. Both "
         "sources for this stream are now non-European and neither describes the desiccated "
         "material. THE STREAM IS COVERED ON PAPER AND NOT IN FACT - 800 kt/yr.",
)

ITEMS["spruitstokken"] = dict(
    status="noted",
    note="NO NEW ROWS, and the reason is worth recording because the near-miss is close enough "
         "to be tempting. de Evan et al. 2019 (Animals 9(9):588) analyses Brussels sprouts "
         "properly - n = 3, same laboratory and methods as the cauliflower paper, DM 16,3 %, CP "
         "24,8, sugars 41,4, NDF 17,5 on dry. But its object is the SPROUT, bought at a Madrid "
         "market. spruitstokken is the STALK the sprouts were picked off, which is precisely the "
         "distinction CVB p. 657/658 makes and this paper does not. "
         "Taking it would be putting the vegetable's composition on its stem - the same error as "
         "potato on potato peel, and the third time this round a Brassica near-miss had to be "
         "turned down. The stream keeps CVB p. 658 as its only source, 8 parameters.",
    searched=["de Evan et al. 2019, Animals 9(9):588 - Brussels sprouts as the vegetable, "
              "REJECTED for this object",
              "Phyllis2 full index - `Brussels sprouts` #1560/#1561 only, 1993 GFT survey, "
              "already refused",
              "Feedipedia full index - no Brassica of any kind"],
    tables=[],
)


def expand(code: str, item: dict) -> dict:
    rows, used = [], {}
    for src, ref, variant, table in item.get("tables", []):
        used[src] = dict(SOURCES[src], citation_key=src)
        for param, unit, val, basis, method, origin, note in table:
            rows.append(dict(
                stream_code=code, parameter_code=param, value_type="point",
                value_num=val, value_min="", value_max="", sd="", n_samples="",
                unit_code=unit, basis_code=basis, method_code=method,
                value_origin=origin, source_key=src, source_ref=ref,
                year=str(SOURCES[src]["year"]), reported_label="", variant=variant,
                restatement="no", flag=item.get("flag", ""), transcription="machine",
                DECISION="", notes=note,
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
