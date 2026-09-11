"""Merge the per-item round-2 extraction files into the review CSVs.

    ../.venv/Scripts/python tools/merge_round2.py

Each target is extracted into its OWN file, `../extraction/round2/<stream_code>.json`,
and written the moment that item is finished. That is the whole point of the layout:
a session that runs out of budget half-way leaves every completed item intact on disk,
and the next session picks up the targets whose file does not exist yet.

This script concatenates them into `round2_measurements.csv` / `round2_sources.csv`,
and writes the per-item status back into `round2_targets.csv` so the worklist always
shows what is done, what yielded nothing, and what has not been looked at.

Nothing here is loaded into the database. Every row carries a blank `DECISION`.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ITEMS = ROOT / "extraction" / "round2"
TARGETS = ROOT / "extraction" / "round2_targets.csv"

ROW_FIELDS = ["stream_code", "parameter_code", "value_type", "value_num", "value_min",
              "value_max", "sd", "n_samples", "unit_code", "basis_code", "method_code",
              "value_origin", "source_key", "source_ref", "year", "reported_label",
              "variant", "restatement", "flag", "transcription", "DECISION", "notes"]

SRC_FIELDS = ["citation_key", "source_type", "title", "url", "year", "kind", "notes"]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "") for k, v in r.items()}
                for r in csv.DictReader(fh, delimiter=";")]


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n",
                       extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    path.write_text(buf.getvalue(), encoding="utf-8-sig")


def main() -> None:
    ITEMS.mkdir(parents=True, exist_ok=True)
    targets = read_csv(TARGETS)

    all_rows: list[dict] = []
    sources: dict[str, dict] = {}
    status: dict[str, dict] = {}

    for path in sorted(ITEMS.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        code = item["stream_code"]
        for s in item.get("sources", []):
            sources.setdefault(s["citation_key"], s)
        rows = item.get("rows", [])
        for r in rows:
            r.setdefault("stream_code", code)
            r.setdefault("value_type", "point")
            r.setdefault("transcription", "machine")
            r.setdefault("DECISION", "")
            r.setdefault("restatement", "no")
            r.setdefault("value_origin", "measured")
            all_rows.append(r)
        status[code] = {
            "status": item.get("status", "done"),
            "sources_found": len(item.get("sources", [])),
            "rows_extracted": len(rows),
            "note": item.get("note", ""),
        }

    for t in targets:
        st = status.get(t["stream_code"])
        if st:
            t["status"] = st["status"]
            t["sources_found"] = st["sources_found"]
            t["rows_extracted"] = st["rows_extracted"]
            if st["note"]:
                t["note"] = st["note"]

    write_csv(TARGETS, list(targets[0].keys()) if targets else [], targets)
    write_csv(ROOT / "extraction" / "round2_measurements.csv", ROW_FIELDS, all_rows)
    write_csv(ROOT / "extraction" / "round2_sources.csv", SRC_FIELDS, list(sources.values()))

    done = [t for t in targets if t["status"] == "done"]
    empty = [t for t in targets if t["status"] == "no-source"]
    todo = [t for t in targets if t["status"] == "todo"]
    mass_done = sum(int(t["tonnes"]) for t in done)
    mass_todo = sum(int(t["tonnes"]) for t in todo)
    print(f"{len(all_rows)} rows from {len(list(ITEMS.glob('*.json')))} items, "
          f"{len(sources)} distinct sources")
    print(f"  done   {len(done):>3}  ({mass_done:>10,} t/yr)")
    print(f"  empty  {len(empty):>3}  (checked, nothing usable)")
    print(f"  todo   {len(todo):>3}  ({mass_todo:>10,} t/yr still to look at)")


if __name__ == "__main__":
    main()
