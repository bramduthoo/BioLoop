"""Quality control over every extracted composition value, before anything is loaded.

    ../.venv/Scripts/python tools/qc_values.py            # report
    ../.venv/Scripts/python tools/qc_values.py --json     # machine-readable, for the page

Three passes, and they answer three different questions.

PASS 1 - IS THE ROW WELL FORMED? Does the unit suit the parameter at all (dry matter in
mg/kg is not a transcription slip, it is a mapping error), does the basis suit it, is the
magnitude possible (a percentage above 100, a g/kg fraction above 1000), does the value
parse as a number.

PASS 2 - DOES THE ROW AGREE WITH ITS SIBLINGS IN THE SAME ANALYSIS? Two structural
identities hold inside any one analysis and neither needs a second source to check:

  * WEENDE CLOSURE. ash + crude protein + crude fat + crude fibre + nitrogen-free extract
    should sum to 1000 g/kg of dry matter, because the Weende scheme is a PARTITION - the
    nitrogen-free extract is defined as whatever is left. A sum far off 1000 means one of
    the five was mis-transcribed, mis-mapped, or is on a different basis than it claims.
  * DETERGENT ORDER. NDF >= ADF >= lignin, always, because each fraction is the residue of
    the previous one. A violation is either a transcription error or two different
    determinations wearing one parameter.

PASS 3 - DO THE SOURCES AGREE WITH EACH OTHER? Per stream and parameter, every value is
brought to one unit (% and g/kg are the same dimension, so this is arithmetic and not a
basis conversion) and the spread is reported. A wide spread is NOT automatically an error:
two sources may be measuring genuinely different material under one name, which is exactly
what the review is for. The job here is to SURFACE it with enough context to judge.

Nothing is corrected automatically. A finding is a finding.
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACT = ROOT / "extraction"
ROUNDS = ["round1_measurements.csv", "round2_measurements.csv", "round3_measurements.csv"]

# dimension each parameter must be measured in
FRACTION = {"dry_matter", "moisture", "ash", "organic_matter", "crude_protein", "total_nitrogen",
            "true_protein", "fat_total", "crude_fibre", "nfe", "insoluble_ash", "ndf", "adf",
            "cellulose", "hemicellulose", "lignin", "pectin", "total_dietary_fibre", "starch",
            "total_sugars", "glucose", "fructose", "sucrose", "lactose", "volatile_matter",
            "fixed_carbon", "hydrogen", "oxygen", "total_carbon", "sulphur", "chloride",
            "phosphorus", "phosphorus_p2o5", "potassium", "potassium_k2o", "calcium",
            "magnesium", "sodium"}
FRACTION_UNITS = {"%", "g/kg", "g/100g"}
# a macro element is a mass fraction but is routinely printed at trace scale too
MINERAL = {"phosphorus", "phosphorus_p2o5", "potassium", "potassium_k2o", "calcium",
           "magnesium", "sodium", "sulphur", "chloride"}
TRACE_UNITS = {"mg/kg", "ug/kg", "mg/100g", "g/kg", "%"}
ENERGY = {"hhv", "lhv"}

TO_PCT = {"%": 1.0, "g/kg": 0.1, "g/100g": 1.0}       # -> percent
TO_MGKG = {"mg/kg": 1.0, "g/kg": 1000.0, "%": 10000.0, "ug/kg": 0.001}

WEENDE = ["ash", "crude_protein", "fat_total", "crude_fibre", "nfe"]


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(fh, delimiter=";")]


def num(x: str):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None


def load() -> list[dict]:
    rows = []
    for i, f in enumerate(ROUNDS, 1):
        for r in read(EXTRACT / f):
            r["_round"] = i
            rows.append(r)
    return rows


def pass1(rows) -> list[dict]:
    out = []
    for i, r in enumerate(rows):
        p, u, b = r["parameter_code"], r["unit_code"], r["basis_code"]
        v = num(r["value_num"]) if r.get("value_type", "point") == "point" else None
        lo, hi = num(r["value_min"]), num(r["value_max"])

        def flag(kind, msg):
            out.append(dict(kind=kind, stream=r["stream_code"], parameter=p, unit=u, basis=b,
                            value=r["value_num"] or f"{r['value_min']}-{r['value_max']}",
                            source=r["source_ref"], message=msg))

        if r.get("value_type", "point") == "point" and v is None:
            flag("unparsable", "the value does not parse as a number")
            continue
        if p in FRACTION and u not in (FRACTION_UNITS | ({"mg/kg"} if p in MINERAL else set())):
            flag("unit-dimension", f"{p} is a mass fraction but the unit is {u}")
        if p in ENERGY and u not in {"MJ/kg", "kJ/kg", "kcal/kg"}:
            flag("unit-dimension", f"{p} is an energy density but the unit is {u}")
        for val in (v, lo, hi):
            if val is None:
                continue
            if u == "%" and val > 100:
                flag("impossible", f"{val} % is above 100")
            if u == "g/kg" and val > 1000 and p in FRACTION:
                flag("impossible", f"{val} g/kg is above 1000 for a mass fraction")
            if val < 0:
                flag("impossible", f"{val} is negative")
        if p == "dry_matter" and b == "dry":
            flag("basis", "dry matter reported ON a dry basis is circular - it should be fresh")
        if p in {"ph", "c_n_ratio", "water_activity"} and b not in {"n.a.", "unknown"}:
            flag("basis", f"{p} has no reference weight, so the basis should be n.a.")
    return out


def pass2(rows) -> list[dict]:
    """structural identities inside ONE analysis (same stream, source and variant)"""
    out = []
    groups = collections.defaultdict(dict)
    for r in rows:
        if r.get("value_type", "point") != "point":
            continue
        key = (r["stream_code"], r["source_ref"], r["variant"], r["basis_code"])
        v, u = num(r["value_num"]), r["unit_code"]
        if v is None or u not in TO_PCT:
            continue
        groups[key].setdefault(r["parameter_code"], v * TO_PCT[u])

    # dry matter per (stream, source, variant), for the product-basis closure
    dm = {}
    for r in rows:
        if r["parameter_code"] == "dry_matter" and r["basis_code"] == "fresh":
            v, u = num(r["value_num"]), r["unit_code"]
            if v is not None and u in TO_PCT:
                dm[(r["stream_code"], r["source_ref"], r["variant"])] = v * TO_PCT[u]

    for (stream, source, variant, basis), d in groups.items():
        if basis == "dry":
            target, what = 100.0, "100 % of dry matter"
        else:
            target = dm.get((stream, source, variant))
            if target is None:
                continue
            what = f"its own dry matter, {target:.1f} %"
        if all(k in d for k in WEENDE):
            total = sum(d[k] for k in WEENDE)
            if abs(total - target) > 5:
                out.append(dict(kind="weende-closure", stream=stream, parameter="+".join(WEENDE),
                                unit="%", basis=basis, value=f"{total:.1f}", source=source,
                                message=(f"the five Weende fractions sum to {total:.1f} % "
                                         f"instead of {what} - one of them is wrong, on another "
                                         f"basis, or the source's partition differs "
                                         f"({variant})")))
        # the individual amino acids cannot exceed the source's own sum of them, and the
        # sum cannot exceed crude protein - a hydrolysate is made OF the protein
        AAS = ["lysine", "methionine", "cystine", "threonine", "tryptophan", "isoleucine",
               "arginine", "phenylalanine", "histidine", "leucine", "tyrosine", "valine",
               "alanine", "aspartic_acid", "glutamic_acid", "glycine", "proline", "serine"]
        present = [k for k in AAS if k in d]
        if len(present) >= 10 and "amino_acids_total" in d:
            s_aa = sum(d[k] for k in present)
            if abs(s_aa - d["amino_acids_total"]) > max(2.0, 0.1 * d["amino_acids_total"]):
                out.append(dict(kind="amino-acid-sum", stream=stream,
                                parameter="sum(amino acids) vs total", unit="%", basis=basis,
                                value=f"{s_aa:.1f} vs {d['amino_acids_total']:.1f}", source=source,
                                message=(f"the individual amino acids sum to {s_aa:.1f} where the "
                                         f"source's own total says {d['amino_acids_total']:.1f} "
                                         f"({variant})")))
        if "amino_acids_total" in d and "crude_protein" in d and                 d["amino_acids_total"] > d["crude_protein"] * 1.15:
            out.append(dict(kind="amino-acid-sum", stream=stream,
                            parameter="amino acids vs crude protein", unit="%", basis=basis,
                            value=f"{d['amino_acids_total']:.1f} vs {d['crude_protein']:.1f}",
                            source=source,
                            message=(f"total amino acids exceed crude protein - a hydrolysate is "
                                     f"made OF the protein, so this cannot be right ({variant})")))

        # the individual fatty acids cannot exceed the source's own sum of them, and that
        # sum cannot exceed the fat - the acids are what the fat is made of
        FAS = ["fa_c10_or_less", "fa_c12_0", "fa_c14_0", "fa_c16_0", "fa_c16_1", "fa_c18_0",
               "fa_c18_1", "fa_c18_2", "fa_c18_3", "fa_c20_or_more"]
        fa_present = [k for k in FAS if k in d]
        if len(fa_present) >= 6 and "fatty_acids_total" in d:
            s_fa = sum(d[k] for k in fa_present)
            if abs(s_fa - d["fatty_acids_total"]) > max(1.0, 0.1 * d["fatty_acids_total"]):
                out.append(dict(kind="fatty-acid-sum", stream=stream,
                                parameter="sum(fatty acids) vs total", unit="%", basis=basis,
                                value=f"{s_fa:.1f} vs {d['fatty_acids_total']:.1f}", source=source,
                                message=(f"the individual fatty acids sum to {s_fa:.1f} where the "
                                         f"source's own total says {d['fatty_acids_total']:.1f} "
                                         f"({variant})")))
        if "fatty_acids_total" in d and "fat_total" in d and                 d["fatty_acids_total"] > d["fat_total"] * 1.05:
            out.append(dict(kind="fatty-acid-sum", stream=stream,
                            parameter="fatty acids vs total fat", unit="%", basis=basis,
                            value=f"{d['fatty_acids_total']:.1f} vs {d['fat_total']:.1f}",
                            source=source,
                            message=(f"total fatty acids exceed total fat - the acids are what "
                                     f"the fat is made OF, so this cannot be right ({variant})")))

        for a, b in (("ndf", "adf"), ("adf", "lignin"), ("ndf", "lignin")):  # noqa: E501
            if a in d and b in d and d[a] < d[b] - 0.5:
                out.append(dict(kind="detergent-order", stream=stream, parameter=f"{a} < {b}",
                                unit="%", basis=basis, value=f"{d[a]:.1f} < {d[b]:.1f}",
                                source=source,
                                message=(f"{a} must be at least {b}: each detergent fraction is "
                                         f"the residue of the one before it ({variant})")))
    return out


def pass3(rows) -> list[dict]:
    """Spread within one (stream, parameter, basis), CLASSIFIED by what explains it.

    A wide spread is not automatically a disagreement, and lumping the kinds together is
    what made the first version of this pass unreadable. Four causes, in the order they
    are tested:

      METHOD      the values come from different determinations of one analyte. CVB prints
                  starch twice on one page, 67 g/kg by polarimetry and 8 g/kg enzymatically;
                  that 8x is the two methods, not two opinions. The method axis added on
                  2026-09-10 is what makes this visible instead of mysterious.
      TRADE FORM  dry matter on a fresh basis, across materials the object bundles. Pressed
                  beet pulp is 24 % dry matter and dried beet pulp 89 %; both are beet pulp.
                  The dry-basis composition is what has to agree, and it does.
      VARIANT     one source, several product grades - CVB's raapzaadschroot RE<370 beside
                  RE>370, its three whey protein classes. The source is telling us the
                  material varies, which is information rather than conflict.
      SOURCE      what is left: two independent sources on nominally the same material.
                  These are the ones worth a human eye.
    """
    out = []
    bucket = collections.defaultdict(list)
    for r in rows:
        if r.get("value_type", "point") != "point":
            continue
        v, u, p = num(r["value_num"]), r["unit_code"], r["parameter_code"]
        if v is None:
            continue
        if u in TO_PCT and p in FRACTION:
            norm, unit = v * TO_PCT[u], "%"
        elif u in TO_MGKG and p not in FRACTION:
            norm, unit = v * TO_MGKG[u], "mg/kg"
        elif u == "MJ/kg":
            norm, unit = v, "MJ/kg"
        else:
            continue
        bucket[(r["stream_code"], p, r["basis_code"], unit)].append(
            dict(v=norm, src=r["source_key"], ref=r["source_ref"], variant=r["variant"],
                 method=r.get("method_code", ""),
                 treated=r.get("flag", "").startswith("TREATED")))

    for (stream, p, basis, unit), vals in bucket.items():
        if len(vals) < 2:
            continue
        lo_e = min(vals, key=lambda d: d["v"])
        hi_e = max(vals, key=lambda d: d["v"])
        lo, hi = lo_e["v"], hi_e["v"]
        if lo <= 0:
            continue
        ratio = hi / lo
        if ratio < 1.5 and (hi - lo) < 5:
            continue

        if lo_e.get("treated") != hi_e.get("treated"):
            cause = "treatment"
            why = ("one of the two samples was TREATED (ammoniated, fermented, ensiled) and "
                   "the other was not - a processed material against the raw stream")
        elif lo_e["method"] != hi_e["method"]:
            cause = "method"
            why = (f"different determinations of one analyte: "
                   f"{lo_e['method'] or 'not stated'} vs {hi_e['method'] or 'not stated'}")
        elif p == "dry_matter" and basis == "fresh":
            cause = "trade-form"
            why = ("dry matter across the trade forms this object bundles - the dry-basis "
                   "composition is what has to agree, and the Weende closure says it does")
        elif lo_e["src"] == hi_e["src"]:
            cause = "variant"
            why = "one source, several product grades of the same material"
        else:
            cause = "source"
            why = "two independent sources on nominally the same material"

        out.append(dict(kind="spread", cause=cause, stream=stream, parameter=p, unit=unit,
                        basis=basis, value=f"{lo:g} - {hi:g}", ratio=round(ratio, 2),
                        n_values=len(vals), n_sources=len({d["src"] for d in vals}),
                        low=f"{lo:g} · {lo_e['ref']} [{lo_e['variant']}]",
                        high=f"{hi:g} · {hi_e['ref']} [{hi_e['variant']}]",
                        source="", message=why))
    order = {"source": 0, "treatment": 1, "variant": 2, "method": 3, "trade-form": 4}
    out.sort(key=lambda f: (order[f["cause"]], -f["ratio"]))
    return out


def main() -> None:
    rows = load()
    f1, f2, f3 = pass1(rows), pass2(rows), pass3(rows)
    if "--json" in sys.argv:
        print(json.dumps({"wellformed": f1, "identities": f2, "spreads": f3},
                         ensure_ascii=False))
        return

    print(f"{len(rows)} values checked\n")
    print(f"PASS 1 - well-formedness: {len(f1)} findings")
    for f in f1:
        print(f"  [{f['kind']}] {f['stream']} / {f['parameter']}: {f['message']}")
    print(f"\nPASS 2 - structural identities: {len(f2)} findings")
    for f in f2:
        print(f"  [{f['kind']}] {f['stream']}: {f['message']}")
    by_cause = collections.Counter(f["cause"] for f in f3)
    print(f"\nPASS 3 - spread within one stream and parameter: {len(f3)} findings "
          f"(>= 1,5x or >= 5 points apart)")
    print(f"  by cause: {dict(by_cause)}")
    for cause in ("source", "treatment", "variant", "method", "trade-form"):
        sel = [f for f in f3 if f["cause"] == cause]
        if not sel:
            continue
        print(f"\n  --- {cause.upper()} ({len(sel)}) : {sel[0]['message']}")
        for f in sel[:14]:
            print(f"    {f['ratio']:>6.1f}x  {f['stream']:<26} {f['parameter']:<16} "
                  f"{f['value']:>16} {f['unit']:<6} {f['basis']}")
            if cause == "source":
                print(f"            {f['low'][:104]}")
                print(f"            {f['high'][:104]}")


if __name__ == "__main__":
    main()
