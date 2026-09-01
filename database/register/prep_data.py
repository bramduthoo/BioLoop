"""Read the BIOLOOP register workbook -> clean claim JSON for the stream overview.
Emits only the fields the view needs; the view is a pure function of these rows.

Every claim is a COMPONENT (it sums with its siblings) or an AGGREGATE (an `AGGREGAAT - ` row,
which claims to be the total of other rows and is therefore a denominator, never a summand).
An aggregate carries its placement from the human-gated registry

    crosswalks/aggregate_coverage.csv     DECISION: ok | unallocated | (blank = unreviewed)

A blank DECISION means the proposal is used but flagged in the view as unreviewed; `unallocated`
keeps the figure visible without letting it control anything. An aggregate with no registry row
at all is treated as unallocated.

Workbook location is resolved in this order:
  1. a path given on the command line:  python prep_data.py /path/to/workbook.xlsx
  2. the BIOLOOP_XLSX environment variable
  3. BIOLOOP_streams_and_sources.xlsx sitting next to this script
  4. any single *.xlsx in this folder
"""
import pandas as pd, json, re, pathlib, sys, os, csv, io
HERE = pathlib.Path(__file__).resolve().parent
REGISTRY = HERE / "crosswalks" / "aggregate_coverage.csv"
AGG_PREFIX = "AGGREGAAT"
REVIEWED_OK = {"ok", "include", "yes", "j", "ja"}
# A reviewer's DECISION_expert starting with one of these retires the claim: it leaves the
# overview entirely and can never reach a sum, an average or a denominator. Anything else in
# that column is a comment, and the claim stays.
EXPERT_EXCLUDES = ("no", "nee", "exclude", "uitsluiten", "drop")

def find_workbook():
    if len(sys.argv) > 1:                       return pathlib.Path(sys.argv[1]).expanduser()
    if os.environ.get("BIOLOOP_XLSX"):          return pathlib.Path(os.environ["BIOLOOP_XLSX"]).expanduser()
    named = HERE / "BIOLOOP_streams_and_sources.xlsx"
    if named.exists():                          return named
    xls = sorted(HERE.glob("*.xlsx"))
    if len(xls) == 1:                           return xls[0]
    raise SystemExit(
        "Workbook not found. Put BIOLOOP_streams_and_sources.xlsx next to this script, "
        "or pass its path:  python prep_data.py /path/to/workbook.xlsx")

SRC = find_workbook()
OUT = HERE / "streams.json"
print(f"reading workbook: {SRC}")
df = pd.read_excel(SRC, sheet_name="Streams")

def yr(v):
    if pd.isna(v): return None
    m = re.search(r"(19|20)\d{2}", str(v));  return int(m.group(0)) if m else None
def cl(v):
    if pd.isna(v): return None
    s = str(v).strip();  return s if s and s.lower() != "nan" else None

def load_registry():
    if not REGISTRY.exists():
        print(f"  ! {REGISTRY.name} not found - every aggregate will show as unallocated")
        return {}
    reg = {}
    for r in csv.DictReader(io.open(REGISTRY, encoding="utf-8-sig"), delimiter=";"):
        d = (r.get("DECISION") or "").strip().lower()
        cov = (r.get("commodity_coverage") or "full").strip()
        reg[r["claim_id"]] = {
            "level": (r.get("totals_level") or "").strip(),
            "parent": (r.get("parent_row") or "").strip(),
            "cov": "full" if cov.lower() == "full" else [x.strip() for x in cov.split(",") if x.strip()],
            "stages": [x.strip() for x in (r.get("stage_coverage") or "").split(",") if x.strip()],
            "treatment": (r.get("treatment") or "variant").strip(),
            "note": (r.get("note") or "").strip(),
            "reviewed": d in REVIEWED_OK,
            "shelved": d == "unallocated" or (r.get("allocatable") or "yes").strip().lower() == "no",
        }
    return reg

REG = load_registry()

def expert_excluded(v):
    """True when the reviewer retired this claim in DECISION_expert."""
    s = (cl(v) or "").strip().lower()
    return bool(s) and s.split()[0].strip(":-,.") in EXPERT_EXCLUDES


rows, n_agg, n_unreviewed, n_shelved = [], 0, 0, 0
retired = []
for _, r in df.iterrows():
    name = cl(r["stream_name_NL"]) or ""
    if "DECISION_expert" in df.columns and expert_excluded(r["DECISION_expert"]):
        retired.append({"id": cl(r["claim_id"]), "name": name,
                        "why": cl(r["DECISION_expert"]),
                        "v": float(r["volume_t_per_yr"]) if pd.notna(r["volume_t_per_yr"]) else 0.0})
        continue
    row = {
        "id":cl(r["claim_id"]), "role":cl(r["L1_role"]), "name":name,
        "l2":cl(r["L2_commodity_group"]), "l3":cl(r["L3_commodity_subgroup"]),
        "l4":cl(r["L4_ingredient"]), "l5":cl(r["L5_fraction_as_named"]),
        "lvl":int(r["level_1to5"]), "st":cl(r["chain_L2"]), "qt":cl(r["quantity_type"]),
        "ed":cl(r["source_short"]), "yr":yr(r["reference_year"]),
        "v":float(r["volume_t_per_yr"]) if pd.notna(r["volume_t_per_yr"]) else 0.0,
        "asm":bool(r["type_assumed"]), "alt":cl(r["also_stated_in"]), "geo":cl(r["geography"]),
        "label":cl(r["source_type_label"]), "page":cl(r["source_page"]),
        "tbl":cl(r["source_table_figure"]),
    }
    if name.upper().startswith(AGG_PREFIX):
        n_agg += 1
        placement = REG.get(row["id"])
        if placement is None:
            row["agg"] = {"level":"", "parent":"", "cov":"full", "stages":[],
                          "treatment":"variant", "reviewed":False,
                          "note":"no row in aggregate_coverage.csv"}
            n_shelved += 1
        elif placement["shelved"]:
            row["agg"] = dict(placement, parent="")           # keep it visible, let it control nothing
            n_shelved += 1
        else:
            row["agg"] = placement
            if not placement["reviewed"]: n_unreviewed += 1
    rows.append(row)

json.dump({"claims":rows, "generated_from":SRC.name, "n_claims":len(rows),
           "n_aggregates":n_agg, "n_unreviewed":n_unreviewed, "retired":retired},
          open(OUT,"w",encoding="utf-8"), ensure_ascii=False)
print(f"wrote {OUT.name}  ({len(rows)} claims · {n_agg} aggregates, "
      f"{n_unreviewed} unreviewed, {n_shelved} unallocated)")
if retired:
    print(f"  {len(retired)} claim(s) retired by DECISION_expert - excluded from every figure:")
    for r in retired:
        print(f"    {r['id']:7} {r['v']:>12,.0f}  {r['name'][:56]}")
