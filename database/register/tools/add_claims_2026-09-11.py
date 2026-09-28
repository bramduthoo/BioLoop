# -*- coding: utf-8 -*-
"""Eenmalig: voeg de 18 door de reviewer goedgekeurde claims toe als C-806 e.v.

Goedgekeurd op het gapfix-reviewbord (artifact fef6aa36), 2026-09-11, alle 20 voorstellen
op `include`. Twee daarvan zijn geen claim maar een corpusactie (C-532/C-342 naar L4) en een
bronfoutnotitie; die staan in log.md, niet hier.

Leest en schrijft de sheet PER KOLOMKOP, nooit op positie — de reviewer heeft de kolommen
herschikt (source_page staat vooraan). Draai dit maar een keer; daarna hoort het in migrations/.
"""
import sys, re, shutil, datetime
from pathlib import Path
import openpyxl

XLSX = Path(__file__).resolve().parents[1] / "BIOLOOP_streams_and_sources.xlsx"

# ---------------------------------------------------------------- de rijen
# (naam, L2, L3, L4, L5, level, chain_stage, chain_L2, source_id, source_short,
#  jaar, volume, value_as_reported, unit, factor, qty_type, label, geo, page, tabfig, also)
TB   = ("S058", "TransBio D3.4A")
S4F  = ("S092", "Starch4Feed (UGent TETRA)")
MON4 = ("S091", "MONBIO 4.0")
MON3 = ("S007", "MONBIO 3.0")
STB  = ("S093", "Statbel slachtstatistiek")

def tb(naam, l4, l5, vol, coef):
    return (naam, "Plantaardig - tuinbouw", "Groenten openlucht", l4, l5, 5,
            "Oogstresten groenteteelt", "Primaire productie", *TB, "2016", vol, vol, "ton", 1,
            "agri-food waste", f"oogstrest; bron rekent {coef} x areaal 2016 (Statbel)",
            "Vlaanderen", "14", "Tabel 8", "")

ROWS = [
 # ---- s2 : het aggregaat krijgt eindelijk een benoemde stroom ----------------
 ("Voederbietenloof", "Plantaardig - akkerbouw", "Voedergewassen", "Voederbiet",
  "loof", 5, "Plantaardige landbouwteelten", "Primaire productie", *MON4, "2021",
  101780, 101780, "ton", 1, "agri-food waste",
  "nevenstroom voedergewassen; Figuur 14 toont voor Voedergewassen een enkele balk over 100%",
  "Vlaanderen", "48", "Figuur 14",
  "sluit het gat onder aggregaat C-242; TransBio D3.4A Tabel 17 geeft 16.518 ton DS voor "
  "dezelfde stroom = 16,2% DS, dus zelfde stroom in een andere eenheid - NIET apart opnemen"),

 # ---- g05 : negen gewassen die MONBIO's tak niet benoemt ---------------------
 tb("Spinazieloof (oogstrest)",        "Spinazie",        "loof", 21225, "<10 t/ha"),
 tb("Witloofwortelloof (oogstrest)",   "Witloofwortelen", "loof", 18850, "25 t/ha"),
 tb("Selderloof (oogstrest)",          "Selder",          "loof", 16681, "50-60 t/ha"),
 tb("Buitenste bladeren witte kool (oogstrest)",  "Witte kool",  "blad", 13072, "30-50 t/ha"),
 tb("Buitenste bladeren savooikool (oogstrest)",  "Savooikool",  "blad", 11592, "40-60 t/ha"),
 tb("Broccoliloof (oogstrest)",        "Broccoli",        "loof",  9146, "30-50 t/ha"),
 tb("Buitenste bladeren rode kool (oogstrest)",   "Rode kool",   "blad",  8966, "40-60 t/ha"),
 tb("Knolselderloof (oogstrest)",      "Knolselder",      "loof",  8250, "10 t/ha"),
 tb("Courgetteloof (oogstrest)",       "Courgette",       "loof",  6305, "10 t/ha"),

 # ---- s1 : vier materialen, elk een totaal van de bedrijfscellen ------------
 ("AGGREGAAT - Aardappelstoomschillen, 5 bedrijven (incl. Nederlandse vestigingen Farmfrites)",
  "Plantaardig - akkerbouw", "Aardappelen en knolgewassen", "Aardappel", "stoomschillen", 5,
  "Aardappelverwerking", "Voedingsindustrie", *S4F, "2017", 261740, 261740, "ton", 1,
  "nevenstroom", "som van de bedrijfscellen; bron drukt geen totaal af", "Belgie",
  "n.v.t. (figuur in register/patat_industrie+compositie.png)", "Tabel 2",
  "Lutosa 90.000 + Agristo 70.800 + Farmfrites 85.400 + Mydibel 3.800 + Bart's 11.740. "
  "ONDERGRENS: bron zegt dat ontbrekende waarden niet meegedeeld zijn. Farmfrites-kolom is "
  "'BE en NL' samen, daarom geography=Belgie"),
 ("AGGREGAAT - Aardappelsnippers, 4 bedrijven (incl. Nederlandse vestigingen Farmfrites)",
  "Plantaardig - akkerbouw", "Aardappelen en knolgewassen", "Aardappel", "snippers", 5,
  "Aardappelverwerking", "Voedingsindustrie", *S4F, "2017", 95000, 95000, "ton", 1,
  "nevenstroom", "som van de bedrijfscellen; bron drukt geen totaal af", "Belgie",
  "n.v.t. (figuur in register/patat_industrie+compositie.png)", "Tabel 2",
  "Lutosa 20.000 + Agristo 29.400 + Farmfrites 38.700 + Bart's 6.900"),
 ("AGGREGAAT - Aardappelvoerzetmeel, 3 bedrijven (incl. Nederlandse vestigingen Farmfrites)",
  "Plantaardig - akkerbouw", "Aardappelen en knolgewassen", "Aardappel", "voerzetmeel", 5,
  "Aardappelverwerking", "Voedingsindustrie", *S4F, "2017", 23905, 23905, "ton", 1,
  "nevenstroom", "som van de bedrijfscellen; bron drukt geen totaal af", "Belgie",
  "n.v.t. (figuur in register/patat_industrie+compositie.png)", "Tabel 2",
  "Agristo 4.680 + Farmfrites 18.800 + Bart's 425"),
 ("AGGREGAAT - Gebakken aardappelnevenstromen, 4 bedrijven (incl. Nederlandse vestigingen Farmfrites)",
  "Plantaardig - akkerbouw", "Aardappelen en knolgewassen", "Aardappel", "gebakken nevenstroom", 5,
  "Aardappelverwerking", "Voedingsindustrie", *S4F, "2017", 9671, 9671, "ton", 1,
  "nevenstroom", "som van de bedrijfscellen; bron drukt geen totaal af", "Belgie",
  "n.v.t. (figuur in register/patat_industrie+compositie.png)", "Tabel 2",
  "Agristo 3.840 + Farmfrites 3.537 + Mydibel 1.794 + Bart's 500"),

 # ---- g04 : AFGELEID, protocol-uitzondering (zie log.md) --------------------
 ("Eetbare slachtafvallen van varkens (AFGELEID uit C-295 naar Vlaams slachtgewicht)",
  "Dierlijk - vee", "Vlees", "Varkens", "eetbare slachtafvallen", 5,
  "Vlees- en gevogelteverwerking", "Voedingsindustrie", *STB, "2021",
  70478, 70478, "ton", 1, "nevenstroom",
  "AFLEIDING, geen meting: C-295 (82.576 t) x 85,35% = Vlaams slachtgewicht varkens "
  "(1.062.129 t) / totaal rood vlees (1.244.452 t). Statbel geeft uitsluitend slachtgewichten, "
  "geen verliescijfers; de aanname is dat eetbaar slachtafval per kg karkas vergelijkbaar is "
  "tussen soorten", "Vlaanderen", "blad 2021", "jaarresultaten",
  "verdeelt C-295; NOOIT optellen bij C-295 - het is dezelfde massa"),
 ("Eetbare slachtafvallen van runderen (AFGELEID uit C-295 naar Vlaams slachtgewicht)",
  "Dierlijk - vee", "Vlees", "Runderen", "eetbare slachtafvallen", 5,
  "Vlees- en gevogelteverwerking", "Voedingsindustrie", *STB, "2021",
  11934, 11934, "ton", 1, "nevenstroom",
  "AFLEIDING, geen meting: C-295 x 14,45% (Vlaams slachtgewicht runderen 179.856 t)",
  "Vlaanderen", "blad 2021", "jaarresultaten",
  "verdeelt C-295; NOOIT optellen bij C-295"),
 ("Eetbare slachtafvallen van schapen, geiten en paarden (AFGELEID uit C-295)",
  "Dierlijk - vee", "Vlees", "Schapen, geiten en paarden", "eetbare slachtafvallen", 5,
  "Vlees- en gevogelteverwerking", "Voedingsindustrie", *STB, "2021",
  164, 164, "ton", 1, "nevenstroom",
  "AFLEIDING, geen meting: C-295 x 0,20%", "Vlaanderen", "blad 2021", "jaarresultaten",
  "verdeelt C-295; NOOIT optellen bij C-295"),

 # ---- g02 : AFGELEID, protocol-uitzondering --------------------------------
 ("Moutscheuten (AFGELEID uit de Vlaamse moutproductie)", "Varia", "Dranken", "Mout",
  "moutscheuten", 5, "Mouterij", "Voedingsindustrie", *MON3, "2020",
  40051, 40051, "ton", 1, "nevenstroom",
  "AFLEIDING, geen meting: Prodcom 110610 mout Vlaanderen 890.015 t x 4,5% opbrengst. "
  "De opbrengstfactor is een literatuurwaarde zonder geciteerde bron - nog te onderbouwen. "
  "MONBIO zegt zelf dat de nevenstromen van de mouterijen NIET in Prodcom geregistreerd zijn",
  "Vlaanderen", "266", "Tabel 87",
  "moutscheuten hebben geen enkele eigen rij in het corpus"),
]

def main():
    if not XLSX.exists():
        sys.exit(f"werkmap niet gevonden: {XLSX}")
    lock = XLSX.with_name("~$" + XLSX.name)
    if lock.exists():
        sys.exit("De werkmap staat open in Excel (~$-lockbestand). Sluit ze en draai opnieuw.")

    bak = XLSX.with_name(XLSX.stem + f"_pre-C806_{datetime.date.today()}.xlsx")
    shutil.copy2(XLSX, bak)
    print("back-up:", bak.name)

    wb = openpyxl.load_workbook(XLSX)
    ws = wb["Streams"]
    hdr = [c.value for c in ws[1]]
    ix = {h: i for i, h in enumerate(hdr) if h}

    have = {ws.cell(r, ix["claim_id"] + 1).value for r in range(2, ws.max_row + 1)}
    nums = [int(m.group(1)) for v in have if v and (m := re.match(r"C-(\d+)", str(v)))]
    nxt = max(nums) + 1
    print("eerstvolgende claim_id: C-%03d" % nxt)

    FIELDS = ["stream_name_NL", "L2_commodity_group", "L3_commodity_subgroup", "L4_ingredient",
              "L5_fraction_as_named", "level_1to5", "chain_stage", "chain_L2", "source_id",
              "source_short", "reference_year", "volume_t_per_yr", "value_as_reported",
              "unit_as_reported", "conversion_factor_to_t_per_yr", "quantity_type",
              "source_type_label", "geography", "source_page", "source_table_figure",
              "also_stated_in"]

    r = ws.max_row + 1
    for row in ROWS:
        cid = "C-%03d" % nxt; nxt += 1
        vals = dict(zip(FIELDS, row))
        vals["claim_id"] = cid
        vals["L1_role"] = "Reststroom"
        vals["provenance"] = "read in PDF"
        vals["type_assumed"] = "TRUE" if vals["quantity_type"] == "agri-food waste" else "FALSE"
        for h, i in ix.items():
            if h in vals:
                ws.cell(r, i + 1, vals[h])
        r += 1
    wb.save(XLSX)
    print(f"{len(ROWS)} rijen toegevoegd, t/m C-%03d" % (nxt - 1))

if __name__ == "__main__":
    main()
