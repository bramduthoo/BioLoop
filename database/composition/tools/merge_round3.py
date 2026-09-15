"""Merge round 3 into review CSVs: per-item JSONs plus the FoodWasteEXplorer rows.

    ../.venv/Scripts/python tools/merge_round3.py

Round 3 has two shapes of input and both end up in the same two files:

  extraction/round3/<code>.json   one file per stream, written the moment that stream is
                                  finished -- the S2BIOM tables and every literature
                                  source read per stream
  extraction/fwe_rows.csv         the FoodWasteEXplorer harvest, produced by
                                  tools/map_fwe.py from the raw per-stream CSVs through a
                                  committed crosswalk

Nothing here is loaded. Every row carries a blank DECISION.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXTRACT = ROOT / "extraction"
ITEMS = EXTRACT / "round3"
ITEMS4 = EXTRACT / "round4"

ROW_FIELDS = ["stream_code", "parameter_code", "value_type", "value_num", "value_min",
              "value_max", "sd", "n_samples", "unit_code", "basis_code", "method_code",
              "value_origin", "source_key", "source_ref", "year", "reported_label",
              "variant", "restatement", "flag", "transcription", "DECISION", "notes"]
SRC_FIELDS = ["citation_key", "source_type", "title", "url", "year", "kind", "country", "notes"]

FWE_SOURCE = dict(
    citation_key="foodwasteexplorer-eurofir", source_type="dataset", year=2019,
    kind="curated-database", country="EU",
    title="FoodWasteEXplorer (EuroFIR / REFRESH) - food side-stream composition database",
    url="https://foodwasteexplorer.eu/",
    notes="The second of the three composition databases the field has, and the only one that "
          "carries a LITERATURE REFERENCE PER VALUE rather than per table - which is why it "
          "routinely reports one parameter several times from different studies, exactly the "
          "shape BioMobi wants. Built on CEN EN 16104:2012. Part of its content is itself "
          "compiled from Feedipedia and ECN Phyllis 2; those rows are dropped here because this "
          "harvest already reads both directly, and two rows citing one study are one "
          "measurement. What survives is what this source actually adds.")


CVB_SOURCE = dict(
    citation_key="cvb-veevoedertabel-2023", source_type="dataset", year=2023,
    kind="sector-institutional", country="NL",
    title="CVB Veevoedertabel 2023 - Chemische samenstellingen en nutritionele waarden "
          "van voedermiddelen (Stichting CVB)",
    url="https://www.cvbdiervoeding.nl/bestand/10900/cvb-veevoedertabel-20232.pdf.ashx",
    notes="The source our own source points at: GeNeSys (S065), which supplies several of "
          "these tonnages, cites CVB for the dry matter of exactly these horticultural streams "
          "and carries no composition table itself. Dutch rather than tropical or "
          "Mediterranean, free, 708 pages, one sheet per material, every value in g/kg dry "
          "matter with a standard deviation where CVB has one - and over 16.000 sample "
          "analyses behind the 2019-2023 editions. Everything below the digestibility line "
          "(VEM, DVE, OEB, the amino-acid and fatty-acid blocks) is deliberately NOT taken: "
          "feed-value figures are facts about a material AND an animal.")


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "") for k, v in r.items()} for r in csv.DictReader(fh, delimiter=";")]


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
    rows: list[dict] = []
    sources: dict[str, dict] = {}

    ITEMS4.mkdir(parents=True, exist_ok=True)
    for path in sorted(ITEMS.glob("*.json")) + sorted(ITEMS4.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        for s in item.get("sources", []):
            sources.setdefault(s["citation_key"], s)
        rows += item.get("rows", [])

    fwe = read_csv(EXTRACT / "fwe_rows.csv")
    if fwe:
        sources.setdefault(FWE_SOURCE["citation_key"], FWE_SOURCE)
        rows += fwe

    cvb = read_csv(EXTRACT / "cvb_rows.csv")
    if cvb:
        sources.setdefault(CVB_SOURCE["citation_key"], CVB_SOURCE)
        rows += cvb

    write_csv(EXTRACT / "round3_measurements.csv", ROW_FIELDS, rows)
    write_csv(EXTRACT / "round3_sources.csv", SRC_FIELDS, list(sources.values()))

    per: dict[str, int] = {}
    for r in rows:
        per[r["stream_code"]] = per.get(r["stream_code"], 0) + 1
    print(f"rounds 3+4: {len(rows)} rows over {len(per)} streams, {len(sources)} sources")
    for c, n in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>4}  {c}")


if __name__ == "__main__":
    main()
