"""Propose the three structural fixes found by the 2026-09-01 integrity audit.

Companion to `crosswalks/REVIEW_2026-08-31.csv`. That sheet reviews the *decisions* Claude took
while the reviewer was away; this one lists the *structural defects* in the register itself, so
that between the two every row in the stream overview is accounted for.

Three fix classes, kept separate because their evidence is different:

  A  prodcom-level    A Prodcom row names a PRODUCT, so it belongs at L4 under its subgroup. 75
                      rows sit at L3 with no L4. Pre-existing (S091/S007 extractions); the same
                      rule was applied to the Prodcom rows that went through varia_reclass and
                      never to those under real commodity groups.
  B  level-mismatch   14 aggregate rows whose `level_1to5` does not match the columns actually
                      filled. Introduced by Claude on 2026-08-31: `level` was set to the level the
                      aggregate TOTALS, which belongs in aggregate_coverage.totals_level, not to
                      the row's own commodity depth.
  C  unmarked-total   14 "Nevenstromen en productieresiduen <gewasgroep>" rows that are exact
                      totals of the fraction rows beneath them but carry no `AGGREGAAT - ` prefix,
                      so they sum with their own parts. Missed by promote_totals.py because their
                      name never says "totaal". Together they are ~2.8 Mt of double counting.

Writes proposals to

    register/crosswalks/FIXES_2026-09-01.csv     DECISION_fix: ok | skip | (blank = unreviewed)

Nothing is applied here. Idempotent; re-running preserves any DECISION_fix already entered.

    database/.venv/Scripts/python.exe database/register/make_fixes.py
"""
import csv, io, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "streams.json"
OUT = HERE / "crosswalks" / "FIXES_2026-09-01.csv"
AGG_PREFIX = "AGGREGAAT - "

COLUMNS = ["fix_id", "fix_class", "claim_id", "source_short", "L1_role", "chain_L2",
           "volume_t_per_yr", "current_path", "current_level", "current_name",
           "SET_level_1to5", "SET_L4_ingredient", "SET_stream_name_NL",
           "why", "evidence", "DECISION_fix"]

PRODCOM_RE = re.compile(r"Prodcom", re.I)
CODE_RE = re.compile(r"\s*\(Prodcom[^)]*\)\s*$")
GROUP_RE = re.compile(r"^Nevenstromen en productieresiduen\b", re.I)


def path_of(c):
    return " > ".join(x for x in (c.get("l2"), c.get("l3"), c.get("l4"), c.get("l5")) if x)


def depth_of(c):
    return 5 if c.get("l5") else 4 if c.get("l4") else 3 if c.get("l3") else 2


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC.name} - run prep_data.py first")
    claims = json.load(io.open(SRC, encoding="utf-8"))["claims"]
    by_id = {c["id"]: c for c in claims}

    prior = {}
    if OUT.exists():
        for r in csv.DictReader(io.open(OUT, encoding="utf-8-sig"), delimiter=";"):
            prior[(r["fix_class"], r["claim_id"])] = r.get("DECISION_fix", "")

    rows = []

    def add(cls, c, **kw):
        row = dict(
            fix_class=cls, claim_id=c["id"], source_short=c.get("ed") or "",
            L1_role=c.get("role") or "", chain_L2=c.get("st") or "",
            volume_t_per_yr=c.get("v") or 0, current_path=path_of(c),
            current_level=c.get("lvl"), current_name=c.get("name") or "",
            SET_level_1to5="", SET_L4_ingredient="", SET_stream_name_NL="",
            DECISION_fix=prior.get((cls, c["id"]), ""))
        row.update(kw)                      # the SET_* columns this fix class actually changes
        rows.append(row)

    # --- A: Prodcom products parked at L3 -------------------------------------------------
    for c in claims:
        name = c.get("name") or ""
        if (PRODCOM_RE.search(name) and c.get("lvl") == 3 and not c.get("l4")
                and not name.upper().startswith("AGGREGAAT")):
            add("A-prodcom-level", c,
                SET_level_1to5=4, SET_L4_ingredient=CODE_RE.sub("", name).strip(),
                why="a Prodcom row names a product, which sits at L4 under its subgroup",
                evidence="same rule already applied to the Prodcom rows under Varia")

    # --- B: level_1to5 disagrees with the filled columns ----------------------------------
    for c in claims:
        d = depth_of(c)
        if c.get("lvl") != d:
            add("B-level-mismatch", c,
                SET_level_1to5=d,
                why="level_1to5 must be the row's own commodity depth, not the level it totals",
                evidence=f"deepest filled column is L{d}; the totalled level lives in "
                         f"aggregate_coverage.totals_level")

    # --- C: exact totals carrying no AGGREGAAT prefix -------------------------------------
    groups = [c for c in claims if GROUP_RE.match(c.get("name") or "")
              and not (c.get("name") or "").upper().startswith("AGGREGAAT")]
    for c in groups:
        kids = [k for k in claims
                if k.get("ed") == c.get("ed") and k.get("role") == c.get("role")
                and k.get("l3") == c.get("l3") and (k.get("lvl") or 0) >= 4
                and k.get("st") == c.get("st")]
        ks = sum(k.get("v") or 0 for k in kids)
        v = c.get("v") or 0
        exact = ks > 0 and abs(ks - v) <= max(2, v * 0.001)
        ev = (f"fractions beneath sum to {ks:,.0f} against {v:,.0f}"
              + (" - EXACT" if exact else " - partial, the rest is not captured"))
        if not kids:
            # MONBIO's gewasgroepen cut across the OVAM-derived subgroups, so a group total's own
            # fractions can sit under a DIFFERENT L3. Look for a matching set across the partition
            # before concluding nothing was captured.
            pool = [k for k in claims
                    if k.get("ed") == c.get("ed") and k.get("role") == c.get("role")
                    and k.get("st") == c.get("st") and (k.get("lvl") or 0) >= 4
                    and k.get("l3") != c.get("l3") and (k.get("v") or 0) > 0
                    and not (k.get("name") or "").upper().startswith("AGGREGAAT")]
            hit = None
            n = len(pool)
            if 0 < n <= 16:
                for mask in range(1, 1 << n):
                    members = [pool[i] for i in range(n) if mask & (1 << i)]
                    if len(members) < 2:
                        continue
                    s = sum(m["v"] for m in members)
                    if abs(s - v) <= max(2, v * 0.001):
                        hit = members
                        break
            if hit:
                ev = ("fractions live under a DIFFERENT L3 (MONBIO's gewasgroepen cut across the "
                      "OVAM subgroups): " + " + ".join(f"{m['id']} {m['v']:,.0f}" for m in hit)
                      + f" = {v:,.0f} - EXACT")
            else:
                ev = ("no fractions captured beneath it, under this L3 or any other; it is still a "
                      "group total by construction and must not sum with its parent")
        add("C-unmarked-total", c,
            SET_stream_name_NL=AGG_PREFIX + (c.get("name") or ""),
            why="a per-gewasgroep total of the fraction rows beneath it, so it must not sum "
                "with them",
            evidence=ev)

    for i, r in enumerate(sorted(rows, key=lambda x: (x["fix_class"], -(x["volume_t_per_yr"] or 0))), 1):
        r["fix_id"] = f"F-{i:03d}"

    rows.sort(key=lambda r: r["fix_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    import collections
    cnt = collections.Counter(r["fix_class"] for r in rows)
    vol = collections.defaultdict(float)
    for r in rows:
        vol[r["fix_class"]] += r["volume_t_per_yr"] or 0
    print(f"{OUT.relative_to(HERE.parent)}: {len(rows)} fixes proposed")
    for k in sorted(cnt):
        print(f"   {k:20} {cnt[k]:>4} rows   {vol[k]:>14,.0f} t/yr")
    blank = [r["fix_id"] for r in rows if not (r["DECISION_fix"] or "").strip()]
    print(f"awaiting DECISION_fix: {len(blank)}")


if __name__ == "__main__":
    main()
