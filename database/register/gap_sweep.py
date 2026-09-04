# -*- coding: utf-8 -*-
"""gap_sweep.py - the whole gap analysis in one pass, emitted as JSON.

    database/.venv/Scripts/python database/register/gap_sweep.py out.json

Runs the five screens the 2026-09-03/04 sweep was built on and dumps every one of them in full,
so the gap register can be rebuilt from the workbook instead of from notes:

  sources_summary   per source: residual rows, aggregates, selectable rows and their mass
  stages            per chain_L2: the same, plus the largest aggregate on that stage
  branches          per L2 x L3: the largest figure any one source gives the branch, and how much
                    of it reaches a selectable L4/L5 row. The difference is the unresolved mass.
  hidden            crosswalks/HIDDEN_STREAMS.csv - live residual rows above L4 with no prefix
  retired           every row carrying a DECISION_expert, so nothing large is lost silently
  prod_lookalike    Productievolume rows whose NAME reads like residue (the misfiling hypothesis)
  checklist         41 named Flemish side streams asked of the whole workbook, any role, any status
  prod_only_l4      L4 members with a production row and NO residual row - the cleanest gap signal
  monbio_fi         every live MONBIO residual row at the food-industry stage (the Prodcom set)
  ovam_fi           the same for the two OVAM monitors (subgroup level, nothing finer)
  sources           all 91 rows of the Sources sheet, with the on-disk status and a gap mapping

Two notes on reading the output. (1) Masses are never summed across sources: a branch's `tot` is
the largest single measurement, and the stage table's `selMass` is a count of what exists, not a
Flanders total. (2) The Sources sheet's own `extraction_status` column is stale - it reads
NOT EXTRACTED for all 91 - so status is derived from what is actually in archive/ and inbox/.

GAPMAP and the ARCHIVED / INBOX sets below are the only hand-maintained parts; update them when a
source is extracted or a gap is closed.
"""
import pandas as pd, openpyxl, json, io, csv, pathlib, re, sys, collections

sys.path.insert(0, ".")
from make_aggregate_coverage import is_collection

OUT = pathlib.Path(sys.argv[1])

df = pd.read_csv("streams_export.csv", sep=";", encoding="utf-8-sig", dtype=str).fillna("")
df["vol"] = pd.to_numeric(df.volume_t_per_yr.str.replace(",", "."), errors="coerce").fillna(0)
df["agg"] = df.stream_name_NL.str.startswith("AGGREGAAT - ")
df["live"] = df.DECISION_expert.str.strip() == ""
R = df[(df.L1_role == "Reststroom") & df["live"]]
P = df[(df.L1_role == "Productievolume") & df["live"]]
D = {}

# ---------------------------------------------------------------- per source
sel_all = R[~R["agg"] & R.level_1to5.isin(["4", "5"])]
srcs = []
for s, g in R.groupby("source_short"):
    sg = g[~g["agg"] & g.level_1to5.isin(["4", "5"])]
    srcs.append(dict(src=s, rows=len(g), aggRows=int(g["agg"].sum()), selRows=len(sg),
                     selMass=float(sg.vol.sum()),
                     years=sorted(set(x for x in g.reference_year if x))[:4],
                     stages=sorted(set(g.chain_L2))))
D["sources_summary"] = sorted(srcs, key=lambda x: -x["selMass"])

# ---------------------------------------------------------------- chain stage
st = []
for s, g in R.groupby("chain_L2"):
    sg = g[~g["agg"] & g.level_1to5.isin(["4", "5"])]
    st.append(dict(stage=s, rows=len(g), aggRows=int(g["agg"].sum()),
                   aggMax=float(g[g["agg"]].vol.max() if g["agg"].any() else 0),
                   selRows=len(sg), selMass=float(sg.vol.sum()),
                   srcs=sorted(set(g.source_short))))
D["stages"] = sorted(st, key=lambda x: -x["aggMax"])

# ---------------------------------------------------------------- branches
br = []
for (l2, l3), g in R.groupby(["L2_commodity_group", "L3_commodity_subgroup"]):
    best = None
    for s, gg in g.groupby("source_short"):
        selm = float(gg[~gg["agg"] & gg.level_1to5.isin(["4", "5"])].vol.sum())
        tot = max(float(gg[gg["agg"]].vol.max()) if gg["agg"].any() else 0.0, selm,
                  float(gg[~gg["agg"]].vol.max()) if (~gg["agg"]).any() else 0.0)
        if best is None or tot > best["tot"]:
            best = dict(src=s, tot=tot, sel=selm)
    br.append(dict(l2=l2, l3=l3 or "(geen subgroep)", src=best["src"], tot=best["tot"],
                   sel=best["sel"], rows=len(g), stages=sorted(set(g.chain_L2))))
D["branches"] = sorted([b for b in br if b["tot"] >= 500], key=lambda b: -(b["tot"] - b["sel"]))

# ---------------------------------------------------------------- screen 1
hs = list(csv.DictReader(io.open("crosswalks/HIDDEN_STREAMS.csv", encoding="utf-8-sig"), delimiter=";"))
for h in hs:
    h["vol"] = float((h["volume_t_per_yr"] or "0").replace(",", "."))
D["hidden"] = sorted(hs, key=lambda h: -h["vol"])

# ---------------------------------------------------------------- screen 2
ret = df[~df["live"]].sort_values("vol", ascending=False)
D["retired"] = [dict(id=x.claim_id, v=float(x.vol), role=x.L1_role, src=x.source_short,
                     name=x.stream_name_NL, why=x.DECISION_expert) for _, x in ret.iterrows()]

# ---------------------------------------------------------------- screen 3
SIDE = (r"schroot|perskoek|pulp|zemel|gries|bostel|draf|melasse|\bwei\b|karnemelk|slachtafval|"
        r"afval|restst|nevenstro|loof|stro\b|schil|kaf\b|dop(pen)?\b|gist\b|vinasse|slib|kiem|"
        r"gluten|residu|verlies|uitval|doordraai|overschot|snijafval|veren|bloed|beender|"
        r"bot(ten)?\b|huiden|vet\b|vetten|stengel|blad|wortelmassa|stokken|koffiedik|cacao|pers")
look = P[P.stream_name_NL.str.lower().str.contains(SIDE, regex=True, na=False)].sort_values("vol", ascending=False)
D["prod_lookalike"] = [dict(id=x.claim_id, v=float(x.vol), src=x.source_short, lvl=x.level_1to5,
                            stage=x.chain_L2, name=x.stream_name_NL, l4=x.L4_ingredient)
                       for _, x in look.iterrows()]

# ---------------------------------------------------------------- screen 5
blob = (df.stream_name_NL + " || " + df.L4_ingredient + " || " + df.L5_fraction_as_named
        + " || " + df.source_type_label).str.lower()
CHECK = [
 ("wei / kaaswei (whey)", r"\bwei\b|kaaswei|wei-|whey|weipoeder|melkserum", "zuivelverwerking"),
 ("melkpermeaat / retentaat", r"permeaat|retentaat", "zuivelverwerking"),
 ("lactose", r"lactose", "zuivelverwerking"),
 ("karnemelk", r"karnemelk", "zuivelverwerking"),
 ("cacaodoppen / cacaoschillen", r"cacaodop|cacaoschil|cacaoschaal|cacaoafval", "cacao"),
 ("cacaoperskoek", r"cacaoperskoek|cacaokoek", "cacao"),
 ("koffiedik / koffieresidu", r"koffiedik|koffie", "dranken"),
 ("aardappelschillen", r"aardappelschil|schillen van aardappel", "aardappelverwerking"),
 ("aardappelstoomschillen", r"stoomschil", "aardappelverwerking"),
 ("aardappelvezel / -eiwit", r"aardappelvezel|aardappeleiwit|protamyl", "aardappelverwerking"),
 ("frituurvet / afgewerkt vet", r"frituurvet|gebruikt.{0,6}vet|afgewerkt.{0,6}vet", "olien, vetten"),
 ("brood / bakkerijretour", r"\bbrood|bakkerijretour|banket|deeg", "bakkerij"),
 ("gist / biergist", r"\bgist\b|biergist|gistcreme", "dranken"),
 ("bierbostel", r"bostel", "dranken"),
 ("draf / DDGS", r"\bdraf\b|distillers|ddgs", "dranken"),
 ("vinasse", r"vinasse", "suiker"),
 ("bietenpuntjes / staartjes", r"puntjes|staartjes|bietenstaart", "suiker"),
 ("schuimaarde / carbokalk", r"schuimaarde|carbokalk|kalkslib", "suiker"),
 ("cichoreipulp / inuline-rest", r"cichorei|inuline|witloofwortel", "suiker"),
 ("appelpulp / perspulp fruit", r"appelpulp|fruitpulp|perspulp|persresidu", "fruit"),
 ("citruspulp", r"citrus|sinaasappel", "fruit"),
 ("eierschalen", r"eierschaal|eierschil", "eieren"),
 ("veren / pluimen", r"\bveren\b|pluimen", "slachterij"),
 ("bloed (slachthuis)", r"\bbloed\b", "slachterij"),
 ("beenderen / botten", r"beender|\bbotten\b", "slachterij"),
 ("huiden / vellen", r"huiden|\bvellen\b", "slachterij"),
 ("verenmeel / diermeel", r"verenmeel|diermeel|bloedmeel|vleesbeendermeel", "slachterij"),
 ("categorie 1/2/3 materiaal", r"categorie\s?[123]|cat\.?\s?[123]\b", "slachterij"),
 ("visafval / visresten", r"visafval|visresten|visgraat|viskop", "visverwerking"),
 ("teruggegooide vis (discards)", r"teruggegooid|discard|bijvangst", "visserij"),
 ("tarwegluten / glutenvoer", r"gluten", "zetmeel"),
 ("maiskiemen / kiemschroot", r"kiem", "zetmeel"),
 ("rijstzemelen", r"rijstzemel", "maalderij"),
 ("mout / moutkiemen", r"\bmout", "dranken"),
 ("sojahullen / -schillen", r"sojahul|sojaschil", "olien, vetten"),
 ("perskoek (algemeen)", r"perskoek", "olien, vetten"),
 ("snijafval / panklaar groente", r"snijafval|panklaar|groenteafval", "groenteverwerking"),
 ("champost / substraat", r"champost|substraat", "tuinbouw"),
 ("bermgras / maaisel", r"bermgras|maaisel|natuurgras", "open ruimte"),
 ("stro (algemeen)", r"\bstro\b|stro,", "akkerbouw"),
 ("zemelen", r"zemel", "maalderij"),
]
chk = []
for label, rx, fam in CHECK:
    hit = df[blob.str.contains(rx, regex=True, na=False)]
    if hit.empty:
        chk.append(dict(label=label, fam=fam, state="absent", n=0, maxv=0, ids=[], note=""))
        continue
    lr = hit[(hit.L1_role == "Reststroom") & hit["live"]]
    sel = lr[~lr["agg"] & lr.level_1to5.isin(["4", "5"])]
    state = ("selectable" if len(sel) else ("residual, not selectable" if len(lr)
             else "production / retired only"))
    chk.append(dict(label=label, fam=fam, state=state, n=int(len(hit)),
                    maxv=float(sel.vol.max() if len(sel) else hit.vol.max()),
                    ids=list((sel if len(sel) else hit).claim_id.head(4)),
                    note=(sel if len(sel) else hit).iloc[0].stream_name_NL[:70]))
order = {"absent": 0, "production / retired only": 1, "residual, not selectable": 2, "selectable": 3}
D["checklist"] = sorted(chk, key=lambda c: (order[c["state"]], -c["maxv"]))

# ---------------------------------------------------------------- dictionary
res_l4 = set(x.strip().lower() for x in R.L4_ingredient if x.strip())
prod_l4 = {}
for _, x in P.iterrows():
    n = x.L4_ingredient.strip()
    if not n or n.lower() in res_l4:
        continue
    if n.lower() not in prod_l4 or x.vol > prod_l4[n.lower()]["v"]:
        prod_l4[n.lower()] = dict(name=n, v=float(x.vol), id=x.claim_id, src=x.source_short,
                                  l2=x.L2_commodity_group, l3=x.L3_commodity_subgroup,
                                  stage=x.chain_L2)
D["prod_only_l4"] = sorted(prod_l4.values(), key=lambda x: -x["v"])

# ---------------------------------------------------------------- MONBIO food industry
fi = []
for s in ["MONBIO 4.0", "MONBIO 3.0"]:
    g = R[(R.source_short == s) & (R.chain_L2 == "Voedingsindustrie")]
    for _, x in g.sort_values(["L2_commodity_group", "L3_commodity_subgroup", "vol"],
                              ascending=[True, True, False]).iterrows():
        fi.append(dict(src=s, id=x.claim_id, v=float(x.vol), lvl=x.level_1to5,
                       agg=bool(x["agg"]), l2=x.L2_commodity_group, l3=x.L3_commodity_subgroup,
                       l4=x.L4_ingredient, l5=x.L5_fraction_as_named, geo=x.geography,
                       name=x.stream_name_NL))
D["monbio_fi"] = fi

# ---------------------------------------------------------------- OVAM food industry
ov = []
g = R[(R.source_short.str.startswith("OVAM")) & (R.chain_L2 == "Voedingsindustrie")]
for _, x in g.sort_values("vol", ascending=False).iterrows():
    ov.append(dict(src=x.source_short, id=x.claim_id, v=float(x.vol), lvl=x.level_1to5,
                   agg=bool(x["agg"]), l2=x.L2_commodity_group, l3=x.L3_commodity_subgroup,
                   qt=x.quantity_type, yr=x.reference_year, name=x.stream_name_NL))
D["ovam_fi"] = ov

# ---------------------------------------------------------------- Sources sheet
wb = openpyxl.load_workbook("BIOLOOP_streams_and_sources.xlsx", data_only=True)
ws = wb["Sources"]
hdr = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
srows = [dict(zip(hdr, r)) for r in ws.iter_rows(min_row=2, values_only=True)
         if dict(zip(hdr, r)).get("id")]
ARCHIVED = {"S002", "S007", "S010", "S065", "S066", "S080", "S087", "S091"}
INBOX_RETIRED = {"S001", "S005", "S006", "S086"}
INBOX_LIVE = {"S004"}
GAPMAP = {
 "S001": ["G-04", "G-14"], "S005": ["G-11", "G-18"], "S006": ["G-18"],
 "S025": ["G-13", "G-10"], "S058": ["G-10", "G-06"], "S067": ["G-01", "G-13"],
 "S035": ["G-01"], "S041": ["G-01", "G-13"], "S077": ["G-15"], "S078": ["G-18"],
 "S086": ["G-14"], "S009": ["G-10"], "S053": ["G-11"], "S012": ["G-11"],
 "S056": ["G-11", "G-15"], "S055": ["G-15"], "S003": [], "S004": [],
}
def txt(v, n=400):
    return ("" if v is None else str(v))[:n]
out = []
for r in srows:
    sid = r["id"]
    status = ("archived - extracted" if sid in ARCHIVED else
              "inbox - RETIRED" if sid in INBOX_RETIRED else
              "inbox - live" if sid in INBOX_LIVE else "no PDF")
    out.append(dict(id=sid, title=txt(r.get("title"), 150), pub=txt(r.get("publisher"), 60),
                    year=txt(r.get("year_edition"), 40), typ=txt(r.get("type"), 60),
                    prio=txt(r.get("priority"), 60), vol=txt(r.get("flag_volume_data"), 90),
                    side=txt(r.get("flag_agrifood_sidestreams"), 60),
                    geo=txt(r.get("flag_flanders"), 40), conf=txt(r.get("confidence"), 40),
                    why=txt(r.get("verdict_reasoning") or r.get("notes"), 420),
                    url=txt(r.get("url"), 300), status=status, gaps=GAPMAP.get(sid, [])))
prio_rank = {"1": 0, "2": 1, "3": 2, "4": 3, "X": 9}
out.sort(key=lambda s: (prio_rank.get((s["prio"] or "Z")[0], 8), s["id"]))
D["sources"] = out

OUT.write_text(json.dumps(D, ensure_ascii=False), encoding="utf-8")
print("wrote", OUT, OUT.stat().st_size, "bytes")
for k, v in D.items():
    print("  %-18s %d" % (k, len(v)))
