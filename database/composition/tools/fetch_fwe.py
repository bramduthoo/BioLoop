"""Harvest FoodWasteEXplorer (EuroFIR / REFRESH) for one food + side stream.

    ../.venv/Scripts/python tools/fetch_fwe.py "Sugar beet" "Sugar beet pulp"
    ../.venv/Scripts/python tools/fetch_fwe.py --list

Writes ../extraction/fwe_raw/<slug>.csv -- one row per reported value, exactly as the
site prints it, with the site's own per-value literature reference preserved.

WHY THIS IS ITS OWN TOOL. FoodWasteEXplorer is the one source in this harvest that gives
a REFERENCE PER VALUE rather than per table, and it routinely reports the same parameter
several times from different studies. That is the shape BioMobi wants -- contradictions
kept as separate rows, never averaged -- so it is worth reading properly rather than by
hand. It is also the reason the harvest must NOT be done by eye: `sugar beet pulp` alone
returns roughly fifty rows over five pages.

READ THE `reference` COLUMN BEFORE USING A ROW. A good part of FoodWasteEXplorer's content
is itself compiled from Feedipedia and from FAO's fruit-and-vegetable-waste report, so a
value can arrive here that is already in the dataset from its own source. Two rows citing
the same study are one measurement, not two, and the reference column is what makes that
visible. Rows whose reference is a named primary study are the ones this source adds.

The site paginates at 10 rows; `page=N` walks it. Politeness: one request per page,
sequentially, no concurrency.
"""

from __future__ import annotations

import csv
import io
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "extraction" / "fwe_raw"
BASE = "https://foodwasteexplorer.eu/byWasteStream"
UA = {"User-Agent": "BIOLOOP-BioMobi/1.0 (research; contact via UGent)"}


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read().decode("utf-8", "replace")


def strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def parse_rows(html: str) -> tuple[list[str], list[list[str]]]:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S)
    table = re.search(r"<table.*?</table>", html, flags=re.S)
    if not table:
        return [], []
    out, header = [], []
    for tr in re.findall(r"<tr.*?</tr>", table.group(0), flags=re.S):
        cells = [strip_tags(c) for c in re.findall(r"<t[dh].*?</t[dh]>", tr, flags=re.S)]
        if not any(cells):
            continue
        if not header:
            header = cells
        else:
            out.append(cells)
    return header, out


def max_page(html: str) -> int:
    pages = [int(m) for m in re.findall(r"page=(\d+)", html)]
    return max(pages) if pages else 1


def harvest(food: str, stream: str) -> None:
    q = {"foodname": food, "wastestream": stream, "compgroup": "", "ftc": ""}
    first = fetch(f"{BASE}?{urllib.parse.urlencode(q)}")
    header, rows = parse_rows(first)
    if not header:
        print(f"no table for {food!r} / {stream!r}")
        return
    last = max_page(first)
    for p in range(2, last + 1):
        _, more = parse_rows(fetch(f"{BASE}?{urllib.parse.urlencode(dict(q, page=p))}"))
        rows += more

    # the site can repeat a row across pages; keep one of each
    seen, unique = set(), []
    for r in rows:
        key = tuple(r)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{slug(food)}__{slug(stream)}.csv"
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\n")
    w.writerow(header)
    w.writerows(unique)
    path.write_text(buf.getvalue(), encoding="utf-8-sig")

    refs: dict[str, int] = {}
    comps: dict[str, int] = {}
    for r in unique:
        if len(r) >= 8:
            refs[r[7]] = refs.get(r[7], 0) + 1
            comps[r[3]] = comps.get(r[3], 0) + 1
    print(f"{path.name}: {len(unique)} rows over {last} page(s), "
          f"{len(comps)} components, {len(refs)} references")
    for ref, n in sorted(refs.items(), key=lambda kv: -kv[1]):
        print(f"    {n:>3}  {ref[:80]}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "--list":
        html = fetch(BASE)
        text = strip_tags(html)
        i, j = text.find("Side stream"), text.find("Component group")
        print(text[i:j][:4000] if i >= 0 else text[:2000])
        return
    if len(args) != 2:
        sys.exit(__doc__)
    harvest(args[0], args[1])


if __name__ == "__main__":
    main()
