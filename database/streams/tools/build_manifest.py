"""Build the object manifest from the register, mechanically.

Two inputs, both owned by the register:

  1. the selection      register/tools/select_streams.js --json   (which commodities, ranked)
  2. the corpus         register/build/streams.json               (every claim, with its
                                                                   commodity levels and fraction)

From those, one object per (commodity, fraction) group:

    an L5 fraction (`stro`, `loof`, `pulp`, `harten`, `stokken`) is its own object;
    the claims with no fraction are the commodity itself.

That grouping is the whole grain rule, applied by the data rather than by hand. Everything a
manifest row needs -- commodity levels, rank, tonnage, claim ids, geography, and a proposed code
and name -- comes out of it.

WHAT A HUMAN STILL OWNS, and it is deliberately small:

  crosswalks/object_decisions.csv   the exceptions -- fraction synonyms to merge, and codes or
                                    names where the derived one is wrong. Nine rows today.

  the `omschrijving` column         prose. Proposed from the source's own label, then edited in
                                    place; regeneration PRESERVES what a human wrote and never
                                    overwrites it.

THE GATE. The script exits non-zero when it meets something it cannot resolve on its own:
a commodity group whose derived name looks unsafe (a no-fraction group whose claims do not
name the commodity), a `merge_naar` pointing at a fraction that does not exist, or a decision
row that matches no group. Those are the cases to settle in object_decisions.csv -- not by
editing the generated manifest.

Usage (from database/streams/):
    ../.venv/Scripts/python tools/build_manifest.py                 # rebuild, report, write
    ../.venv/Scripts/python tools/build_manifest.py --check         # report only, write nothing
    ../.venv/Scripts/python tools/build_manifest.py --top 20        # a deeper selection cut
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
STREAMS = HERE.parent
DB = STREAMS.parent
REGISTER = DB / "register"
REGISTER_JSON = REGISTER / "build" / "streams.json"
SELECT_JS = REGISTER / "tools" / "select_streams.js"
DECISIONS = STREAMS / "crosswalks" / "object_decisions.csv"
MANIFEST = STREAMS / "crosswalks" / "register_streams.csv"

HDR = ["code", "canonical_name", "commodity_l2", "commodity_l3", "register_l4", "fractie",
       "l4_rank", "l4_t_per_jaar", "grootste_claim_t", "grootste_claim", "geografie",
       "n_claims", "claim_ids", "omschrijving", "DECISION"]

# The register uses two names for one L3 -- MONBIO says "Groenten", ILVO/GeNeSys say
# "Groenten openlucht". select_streams.js drops L3 from its own key for the same reason.
L3_ALIAS = {"Groenten": "Groenten openlucht"}


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return "-".join(p for p in re.split(r"[^a-z0-9]+", s.lower()) if p)


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="\r\n") as f:
        w = csv.DictWriter(f, HDR, delimiter=";", lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


def selection(top: int) -> dict[str, dict]:
    """Run the register's own selection. Never re-derive its numbers here."""
    tmp = REGISTER / "build" / "_selection.json"
    r = subprocess.run(["node", str(SELECT_JS), str(max(top, 24)), "--json", str(tmp)],
                       capture_output=True, text=True, cwd=REGISTER)
    if r.returncode != 0 or not tmp.exists():
        sys.exit(f"select_streams.js failed:\n{r.stderr or r.stdout}")
    sel = json.loads(tmp.read_text(encoding="utf-8"))
    tmp.unlink(missing_ok=True)
    return {it["l4"]: {"rank": i + 1, "M": round(it["M"])}
            for i, it in enumerate(sel["items"]) if i < top}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=13,
                    help="how many ranked commodities to take (default 13 = the 80%% line)")
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    if not REGISTER_JSON.exists():
        sys.exit(f"{REGISTER_JSON} missing -- run register/tools/build_overview.py first.")
    claims = json.loads(REGISTER_JSON.read_text(encoding="utf-8"))["claims"]
    sel = selection(args.top)

    # --- decisions -----------------------------------------------------------------
    merges, codes, names, unused = {}, {}, {}, []
    for d in read_csv(DECISIONS):
        key = (d["register_l4"].strip(), d["fractie"].strip())
        unused.append(key)          # every decision must earn its keep; see the stale check
        if d["merge_naar"].strip():
            merges[key] = d["merge_naar"].strip()
        if d["code"].strip():
            codes[key] = d["code"].strip()
        if d["canonical_name"].strip():
            names[key] = d["canonical_name"].strip()

    # --- group the corpus into objects ---------------------------------------------
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    applied_merges: set[tuple[str, str]] = set()
    for c in claims:
        if c.get("role") != "Reststroom" or c["l4"] not in sel:
            continue
        if str(c.get("name", "")).startswith("AGGREGAAT"):
            continue
        frac = (c.get("l5") or "").strip()
        if (c["l4"], frac) in merges:      # a merged fraction vanishes into its target, so its
            applied_merges.add((c["l4"], frac))   # decision row is used here, not matched below
            frac = merges[(c["l4"], frac)]
        groups[(c["l4"], frac)].append(c)

    problems, rows = [], []
    # Keyed by code: it is the stable identity of an object across a rebuild, whereas its
    # fraction label moves when a synonym is merged.
    prev = {r["code"]: r for r in read_csv(MANIFEST)}

    for (l4, frac), cs in sorted(groups.items(), key=lambda kv: (sel[kv[0][0]]["rank"], kv[0][1])):
        key = (l4, frac)
        if key in unused:
            unused.remove(key)
        l2s = {c["l2"] for c in cs}
        l3s = {L3_ALIAS.get(c["l3"], c["l3"]) for c in cs}
        if len(l2s) != 1 or len(l3s) != 1:
            problems.append(f"{l4} / {frac or '(no fraction)'}: spans several commodity levels "
                            f"(L2 {sorted(l2s)}, L3 {sorted(l3s)})")
            continue

        top = max(cs, key=lambda c: c.get("v") or 0)
        claim_names = sorted({c["name"] for c in cs}, key=len)

        code = codes.get(key) or (f"{slug(l4)}-{slug(frac)}" if frac else slug(l4))
        p = prev.get(code, {})

        # Proposed name: a fraction takes the source's own shortest name for it (those read
        # like material names -- "Maisstro", "Bietenpulp"); a no-fraction group takes the
        # commodity, because its claims are named after losses, not after the thing.
        proposed = claim_names[0] if frac else l4
        name = names.get(key) or p.get("canonical_name") or proposed

        # The gate: a no-fraction group whose claims never mention the commodity is probably
        # a specific product wearing the commodity's name (schroot, fabrieksafval, ...).
        if not frac and key not in names and code not in prev:
            if not any(slug(l4).split("-")[0] in slug(n) for n in claim_names):
                problems.append(
                    f"{l4} / (no fraction): cannot name this safely. Claims are "
                    f"{claim_names[0][:60]!r}; the commodity name may not describe the object. "
                    f"Add a `canonical_name` (and probably a `code`) to {DECISIONS.name}.")

        rows.append({
            "code": code, "canonical_name": name,
            "commodity_l2": l2s.pop(), "commodity_l3": l3s.pop(),
            "register_l4": l4, "fractie": frac,
            "l4_rank": sel[l4]["rank"], "l4_t_per_jaar": sel[l4]["M"],
            "grootste_claim_t": round(top.get("v") or 0),
            "grootste_claim": f"{top['id']} / {top['ed']}",
            "geografie": " | ".join(sorted({c["geo"] for c in cs})),
            "n_claims": len(cs),
            "claim_ids": " ".join(c["id"] for c in cs),
            # Prose is the human's. Proposed once from the source's own label, never overwritten.
            "omschrijving": p.get("omschrijving") or (top.get("label") or ""),
            "DECISION": p.get("DECISION", ""),
        })

    for key in (k for k in unused if k not in applied_merges):
        problems.append(f"{DECISIONS.name}: no group matches {key[0]} / "
                        f"{key[1] or '(no fraction)'} -- stale decision row?")

    # --- report --------------------------------------------------------------------
    now, before = {r["code"] for r in rows}, set(prev)
    print(f"\n{len(groups)} groups over {len(sel)} commodities -> {len(rows)} objects")
    for tag, s in (("new", now - before), ("gone", before - now)):
        if s:
            print(f"  {tag}: {', '.join(sorted(s))}")
    blank = [r["code"] for r in rows if not r["DECISION"].strip()]
    if blank:
        print(f"  undecided ({len(blank)}): {', '.join(blank)}")

    if problems:
        print("\nCannot build -- settle these in crosswalks/object_decisions.csv:\n",
              file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(1)

    if args.check:
        print("\n--check: nothing written.")
        return
    write_csv(MANIFEST, rows)
    print(f"\nwrote {MANIFEST.relative_to(DB)}"
          + (f" -- {len(blank)} row(s) need a DECISION before the loader will run." if blank
             else ""))


if __name__ == "__main__":
    main()
