"""Map FoodWasteEXplorer's component vocabulary onto BioMobi's parameter catalogue.

    ../.venv/Scripts/python tools/map_fwe.py --emit-crosswalk   # write the proposal
    ../.venv/Scripts/python tools/map_fwe.py --emit-rows        # apply it to the raw CSVs

FoodWasteEXplorer names 157 distinct components across the streams harvested here. The
mapping is written down as `crosswalks/fwe_components.csv` rather than buried in code, so
what was taken, what was skipped and WHY is a file the reviewer can read.

THREE RULES DECIDE WHAT IS TAKEN.

1. A ROW WHOSE REFERENCE IS ALREADY A SOURCE IN THIS DATASET IS NOT A SECOND MEASUREMENT.
   Much of FoodWasteEXplorer is compiled from Feedipedia and from ECN Phyllis 2, both of
   which this harvest already reads directly. Taking those rows would turn one analysis
   into two and make a stream look better-sourced than it is. They are dropped and
   counted, and the count is reported -- it is a useful measure of how much this source
   actually ADDS.

2. A DIGESTIBILITY OR AN ANIMAL-SPECIFIC ENERGY VALUE IS NOT A PROPERTY OF THE STREAM.
   `Energy, digestible, growing pig` is a fact about a material AND an animal; it belongs
   to the model's rule layer, not to a facts-only data layer. Every `Energy digestibility
   ...`, `Energy, net ...`, `Energy, metabolisable ...` and `... degradability` row is
   skipped on that ground -- the charter's data/rules line, applied.

3. WHERE THE SOURCE NAMES THE DETERMINATION, IT BECOMES A METHOD, NOT A PARAMETER.
   `Lignin, Klason` and `Lignin, acid detergent` are one analyte with two methods;
   `Fat, crude` and `Fat, crude, HCl hydrolysis` likewise. That is the axis the schema
   gained on 2026-09-10 and this is the first source that exercises it properly.
"""

from __future__ import annotations

import csv
import glob
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "extraction" / "fwe_raw"
CROSSWALK = ROOT / "crosswalks" / "fwe_components.csv"

# sources this harvest already reads directly -- their rows here are duplicates
ALREADY_HELD = {"feedipedia", "ecn phyllis 2", "ecn phyllis2", "phyllis"}

# component -> (parameter, method, note). Unit and basis come from the unit map.
TAKE: dict[str, tuple[str, str, str]] = {
    "Dry Matter": ("dry_matter", "", ""),
    "Ash": ("ash", "", ""),
    "Ash, crude": ("ash", "", "the source writes 'crude ash'; same determination"),
    "Organic matter": ("organic_matter", "", ""),
    "Protein, crude": ("crude_protein", "", ""),
    "Fat": ("fat_total", "", "the source does not name the extraction"),
    "Fat, crude": ("fat_total", "ee-diethyl", ""),
    "Fat, crude, HCl hydrolysis": ("fat_total", "ee-hcl", ""),
    "Fibre, crude": ("crude_fibre", "", ""),
    "Acid Detergent Fibre (ADF)": ("adf", "", ""),
    "Neutral Detergent Fibre": ("ndf", "", ""),
    "eNeutral Detergent Fibre": ("ndf", "ndf-amylase", "the source's 'e' prefix marks the enzymatic (amylase) variant"),
    "Cellulose": ("cellulose", "", ""),
    "Hemicellulose": ("hemicellulose", "", ""),
    "Lignin": ("lignin", "", "the source does not name the determination"),
    "Lignin, Klason": ("lignin", "lignin-klason", ""),
    "Lignin, acid detergent": ("lignin", "lignin-adl", ""),
    "Fibre, dietary": ("total_dietary_fibre", "", ""),
    "Carbohydrate, water soluble": ("total_sugars", "", "water-soluble carbohydrate, the source's wording"),
    "Lactose": ("lactose", "", ""),
    "Energy, gross": ("hhv", "", "gross energy is the calorific value fuel sources call HHV"),
    "Heating value, high": ("hhv", "", ""),
    "Heating value, low": ("lhv", "", ""),
    "Calcium": ("calcium", "", ""),
    "Phosphorus": ("phosphorus", "", ""),
    "Potassium": ("potassium", "", ""),
    "Sodium": ("sodium", "", ""),
    "Magnesium": ("magnesium", "", ""),
    "Iron": ("iron", "", ""),
    "Zinc": ("zinc", "", ""),
    "Copper": ("copper", "", ""),
    "Manganese": ("manganese", "", ""),
    "Chloride": ("chloride", "", ""),
    "Carbon": ("total_carbon", "", ""),
    "Hydrogen": ("hydrogen", "", ""),
    "Carbon, fixed": ("fixed_carbon", "", ""),
    "Carbon/nitrogen ratio": ("c_n_ratio", "", ""),
    "Cadmium": ("cadmium", "", ""),
    "Lead": ("lead", "", ""),
    "Arsenic": ("arsenic", "", ""),
    "Chromium": ("chromium", "", ""),
    "Nickel": ("nickel", "", ""),
    "Phenolics, total": ("total_polyphenols", "", ""),
    "Chemical oxygen demand, total": ("cod", "", ""),
}

SKIP_PATTERNS: list[tuple[str, str]] = [
    (r"^Energy\s*[,(]?\s*(digestib|net\b|\(net\)|metabolis|apparent|Total Digestible)",
     "a digestibility or an animal-specific energy value is a fact about a material AND an "
     "animal - model rule layer, not a facts-only data layer"),
    (r"^Energy \(Total Digestible Nutrients\)", "same: an animal-nutrition derived value"),
    (r"degradability|degradation rate|digestib", "derived against an animal or a process, not a stream property"),
    (r"^(Alanine|Arginine|Aspartic|Cysteine|Cystine|Glutamic|Glycine|Histidine|Isoleucine|"
     r"Leucine|Lysine|Methionine|Phenylalanine|Proline|Serine|Threonine|Tryptophan|Tyrosine|"
     r"Valine|Amino acids)",
     "AMINO ACIDS - real composition and INFOODS carries the family, but the source expresses "
     "them as 'g/16g N' and '% protein', which are EXPRESSIONS relative to protein rather than "
     "units. BioMobi has no expression axis yet, so entering them would bury that in prose. "
     "Deferred as a named decision, not dropped"),
    (r"^(Albumin|Globulin|Glutelin|Casein|Lactoglobulin|Glycosylation)",
     "protein fractions, same expression problem as the amino acids"),
    (r"^Biogas|^Methane", "BIOGAS AND METHANE YIELD - a measured property of the material, but "
                          "also the output of a process applied to it. Which side of the "
                          "charter's data/rules line it falls on is a reviewer decision, so it "
                          "is located and not taken"),
    (r"^(Aerobic count|Aspergillus|Clostridium)", "microbiological - out of scope since 2026-09-10"),
    (r"^(Antimony|Barium|Beryllium|Bismuth|Caesium|Gallium|Germanium|Gold|Indium)",
     "a single ICP scan of one sample. Nine parameters for nine values would make the "
     "catalogue's shape reflect one instrument run"),
    (r"^(Arabinan|Arabinose|Arabinoxylan|Galactose|Glucose|Mannose|Fructan)$",
     "individual non-starch polysaccharide sugars, reported only as NCP fractions by one study"),
    (r"Neutral Detergent Solubles|Neutral detergent fibre digestib|Nitrogen (degradability|digestib)|"
     r"Nitrogen, (immediately|potentially)|Hourly degradation|Insoluble but potential|"
     r"Net gas production|Buffering capacity|DPPH|Volatile solids content|Carbon content",
     "derived or assay-specific, not an intrinsic composition figure"),
    (r"^Carbohydrate", "the source gives several different by-difference carbohydrate definitions; "
                       "which one maps to `nfe` needs the source's own formula, which it does not print"),
    (r"^Fibre, (dietary, insoluble|dietary, soluble|insoluble non-starch|soluble non-starch|"
     r"non-starch polysaccharides)", "fibre sub-fractions with no catalogue parameter yet"),
    (r"^Chemical oxygen demand, (soluble|insoluble)", "soluble/insoluble COD split has no parameter yet"),
    (r"^(Caffeic acid|Chlorogenic|Gallic acid)", "individual phenolic compounds - the bioactive "
                                                 "branch holds only totals so far"),
    (r"^(Aflatoxin)", "mycotoxin - no parameter yet, and it belongs with contaminants"),
    (r"^(Aluminium|Cobalt|Molybdenum|Sulphur|Sulfur)", "no catalogue parameter yet for this element"),
    (r"^Acid Detergent Fibre Crude Protein", "ADF-bound crude protein, a damage indicator rather "
                                             "than a composition fraction"),
]

# the source's unit string -> (catalogue unit, basis, note)
UNITS: dict[str, tuple[str, str, str]] = {
    "%": ("%", "unknown", "the source does not state the basis"),
    "% DM": ("%", "dry", ""),
    "% d.b.": ("%", "dry", ""),
    "% DM basis": ("%", "dry", ""),
    "% wet weight": ("%", "fresh", ""),
    "g/kg": ("g/kg", "unknown", "the source does not state the basis"),
    "g/kg DM": ("g/kg", "dry", ""),
    "g/kg FM": ("g/kg", "fresh", ""),
    "g/kg dry matter": ("g/kg", "dry", ""),
    "mg/kg": ("mg/kg", "unknown", ""),
    "mg/kg DM": ("mg/kg", "dry", ""),
    "mg/1000g": ("mg/kg", "unknown", "mg per 1000 g is mg/kg"),
    "ppm": ("mg/kg", "unknown", "ppm read as mg/kg"),
    "ppm d.b.": ("mg/kg", "dry", "ppm read as mg/kg"),
    "ppm .d.b": ("mg/kg", "dry", "ppm read as mg/kg; the source's typo kept out of the value"),
    "g/100g": ("g/100g", "unknown", ""),
    "mg/100g": ("mg/100g", "unknown", ""),
    "MJ/kg DM": ("MJ/kg", "dry", ""),
    "MJ/kg d.b.": ("MJ/kg", "dry", ""),
    "mg/l": ("mg/L", "n.a.", ""),
    "-": ("ratio", "n.a.", ""),
    "N/A": ("ratio", "n.a.", ""),
}


def skip_reason(component: str) -> str:
    for pat, why in SKIP_PATTERNS:
        if re.search(pat, component, re.I):
            return why
    return ""


def load_raw() -> list[dict]:
    rows = []
    for f in sorted(RAW.glob("*.csv")):
        for r in csv.DictReader(f.open(encoding="utf-8-sig"), delimiter=";"):
            r["_file"] = f.stem
            rows.append(r)
    return rows


def emit_crosswalk() -> None:
    rows = load_raw()
    seen: dict[tuple[str, str], int] = {}
    for r in rows:
        seen[(r["Component"], r["Unit"])] = seen.get((r["Component"], r["Unit"]), 0) + 1

    out = []
    for (comp, unit), n in sorted(seen.items()):
        why = skip_reason(comp)
        param, method, note = TAKE.get(comp, ("", "", ""))
        u, basis, unote = UNITS.get(unit, ("", "", ""))
        if param and not u:
            why = why or f"unit {unit!r} has no mapping - the source's expression is not a unit"
        action = "take" if (param and u and not why) else "skip"
        out.append(dict(
            fwe_component=comp, fwe_unit=unit, rows=n, action=action,
            parameter_code=param if action == "take" else "",
            unit_code=u if action == "take" else "",
            basis_code=basis if action == "take" else "",
            method_code=method if action == "take" else "",
            reason=why if action == "skip" else " ".join(x for x in (note, unote) if x),
            DECISION="",
        ))

    CROSSWALK.parent.mkdir(parents=True, exist_ok=True)
    fields = ["fwe_component", "fwe_unit", "rows", "action", "parameter_code", "unit_code",
              "basis_code", "method_code", "reason", "DECISION"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    CROSSWALK.write_text(buf.getvalue(), encoding="utf-8-sig")
    taken = sum(1 for o in out if o["action"] == "take")
    taken_rows = sum(o["rows"] for o in out if o["action"] == "take")
    print(f"wrote {CROSSWALK}")
    print(f"  {len(out)} component/unit pairs: {taken} take, {len(out) - taken} skip")
    print(f"  {taken_rows} of {sum(o['rows'] for o in out)} raw values mapped")


def main() -> None:
    if "--emit-crosswalk" in sys.argv:
        emit_crosswalk()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# applying the crosswalk
# ---------------------------------------------------------------------------

# FoodWasteEXplorer side stream -> BioMobi stream code. Only the 19 in-scope
# targets are mapped; a harvest that matches nothing is reported, not guessed at.
STREAM_MAP = {
    "__cauliflower-leaves": "bloemkool-loof",
    "__cauliflower-stem": "bloemkool-loof",
    "__sugar-beet-leaves": "suikerbiet-loof",
    "sugar-beet__sugar-beet-pulp": "suikerbiet-pulp",
    "potato__potato-peel": "aardappel-stoomschillen",
    "__wheat-straw": "tarwe-stro",
    "__wheat-bran": "zemelen",
    "__rapeseed-meal": "raapzaad-schroot",
    "__soybean-meal": "soja-schroot",
    "__linseed-meal": "lijnzaad-schroot",
    "__whey": "zuivelnevenstroom",
    "__brewer-s-grains": "bostel",
    "__offal-meal": "niet-eetbare-slachtafvallen",
    "__animal-fats": "dierlijk-vet",
    "__brussels-sprouts": "spruitstokken",
    # potato pulp is a STARCH-industry residue, not one of the 19 objects; harvested
    # and deliberately unmapped -- it is where `zetmeel-reststroom` would look if G-19
    # ever names that material.
}


def emit_rows() -> None:
    cw = {}
    for r in csv.DictReader(CROSSWALK.open(encoding="utf-8-sig"), delimiter=";"):
        cw[(r["fwe_component"], r["fwe_unit"])] = r

    rows, dropped_dup, unmapped_files, skipped, empty = [], 0, set(), 0, 0
    for f in sorted(RAW.glob("*.csv")):
        code = STREAM_MAP.get(f.stem)
        if not code:
            unmapped_files.add(f.stem)
            continue
        for r in csv.DictReader(f.open(encoding="utf-8-sig"), delimiter=";"):
            ref = (r.get("Reference") or "").strip()
            if ref.lower() in ALREADY_HELD:
                dropped_dup += 1
                continue
            m = cw.get((r["Component"], r["Unit"]))
            if not m or m["action"] != "take":
                skipped += 1
                continue
            # the site prints an empty Value on a handful of rows; a point measurement
            # with no number is not a measurement, and the schema's value_shape CHECK
            # would refuse it. Dropped and counted rather than stored as a blank.
            if not (r.get("Value") or "").strip():
                empty += 1
                continue
            desc = (r.get("Description") or "").strip()
            rows.append(dict(
                stream_code=code, parameter_code=m["parameter_code"], value_type="point",
                value_num=r["Value"], value_min="", value_max="", sd="", n_samples="",
                unit_code=m["unit_code"], basis_code=m["basis_code"],
                method_code=m["method_code"], value_origin="measured",
                source_key="foodwasteexplorer-eurofir", source_ref=f"FoodWasteEXplorer: {ref}",
                year="", reported_label=f"{r['Side stream']} / {r['Component']}",
                variant=r["Side stream"] + (f" - {desc}" if desc else ""),
                restatement="no", flag="", transcription="machine", DECISION="",
                notes=" ".join(x for x in (m["reason"], desc) if x),
            ))

    out = ROOT / "extraction" / "fwe_rows.csv"
    fields = list(rows[0].keys()) if rows else []
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    out.write_text(buf.getvalue(), encoding="utf-8-sig")

    per = {}
    for r in rows:
        per[r["stream_code"]] = per.get(r["stream_code"], 0) + 1
    print(f"wrote {out}: {len(rows)} rows over {len(per)} streams")
    print(f"  {dropped_dup} rows dropped as duplicates of Feedipedia / ECN Phyllis 2")
    print(f"  {skipped} rows skipped by the crosswalk")
    print(f"  {empty} rows dropped for an empty Value cell")
    if unmapped_files:
        print(f"  harvests not mapped to a target: {sorted(unmapped_files)}")
    for c, n in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"    {n:>4}  {c}")
