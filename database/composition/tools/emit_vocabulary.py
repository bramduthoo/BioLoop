"""Emit BioMobi's composition vocabulary as a generated data migration.

The source of truth is the three CSVs in ../vocabulary/ (unit, basis, parameter).
This script validates them and writes an ON CONFLICT-guarded migration, per the
workstream rule that reference vocabulary ships as a generated data migration so
`supabase db reset` reproduces the whole database from git.

    ../../.venv/Scripts/python tools/emit_vocabulary.py \
        --emit-migration ../supabase/migrations/<ts>_biomobi_composition_vocabulary.sql

Never hand-edit the emitted file, and never re-edit one that has been applied:
change a CSV and emit a NEW migration. Every statement is ON CONFLICT-guarded,
so migrations stack and a later one supersedes an earlier value harmlessly.

The script refuses rather than guesses: it exits non-zero on a duplicate code, a
parameter category the schema's CHECK constraint would reject, or a
default_unit_code that names no unit.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VOCAB = HERE.parent / "vocabulary"

# parameter_category_check in the baseline migration
VALID_CATEGORIES = {"chemical", "physical", "microbiological"}


def read(name: str) -> list[dict[str, str]]:
    path = VOCAB / name
    if not path.exists():
        sys.exit(f"FAIL: {path} is missing")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = [
            {k: (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(fh, delimiter=";")
        ]
    if not rows:
        sys.exit(f"FAIL: {path} has no rows")
    return rows


def check_unique(rows: list[dict[str, str]], name: str) -> None:
    seen: dict[str, int] = {}
    for i, row in enumerate(rows, start=2):
        code = row["code"]
        if not code:
            sys.exit(f"FAIL: {name} line {i} has an empty code")
        if code in seen:
            sys.exit(f"FAIL: {name} code {code!r} appears twice (lines {seen[code]} and {i})")
        seen[code] = i


def q(value: str) -> str:
    """Single-quoted SQL literal."""
    return "'" + value.replace("'", "''") + "'"


def qn(value: str) -> str:
    """Single-quoted SQL literal, or NULL when empty."""
    return q(value) if value else "NULL"


def validate() -> tuple[list[dict], list[dict], list[dict]]:
    units = read("units.csv")
    bases = read("bases.csv")
    params = read("parameters.csv")

    check_unique(units, "units.csv")
    check_unique(bases, "bases.csv")
    check_unique(params, "parameters.csv")

    unit_codes = {u["code"] for u in units}
    problems: list[str] = []

    for p in params:
        if not p["name"]:
            problems.append(f"parameter {p['code']}: empty name")
        if p["category"] not in VALID_CATEGORIES:
            problems.append(
                f"parameter {p['code']}: category {p['category']!r} is not one of "
                f"{sorted(VALID_CATEGORIES)} - the schema CHECK would reject it"
            )
        du = p["default_unit_code"]
        if du and du not in unit_codes:
            problems.append(
                f"parameter {p['code']}: default_unit_code {du!r} is in no row of units.csv"
            )
        if not p["definition"]:
            problems.append(
                f"parameter {p['code']}: empty definition - a parameter is registered once and "
                f"every later value maps to it, so what it means must be written down"
            )

    for table, rows in (("units.csv", units), ("bases.csv", bases)):
        for row in rows:
            if not row["description"]:
                problems.append(f"{table} {row['code']}: empty description")

    for code in ("unknown", "n.a."):
        if code not in unit_codes:
            problems.append(f"units.csv is missing {code!r} - absence and inapplicability differ")
        if code not in {b["code"] for b in bases}:
            problems.append(f"bases.csv is missing {code!r} - absence and inapplicability differ")

    if problems:
        for p in problems:
            print("FAIL:", p, file=sys.stderr)
        sys.exit(1)

    return units, bases, params


def emit(units, bases, params, path: Path) -> None:
    out: list[str] = []
    w = out.append

    w("-- BioMobi vocabulary: units, reporting bases and the composition parameter catalogue.")
    w("--")
    w("-- GENERATED -- do not hand-edit. Regenerate with, from database/composition/:")
    w("--   ../.venv/Scripts/python tools/emit_vocabulary.py --emit-migration <path>")
    w("-- The source of truth is vocabulary/{units,bases,parameters}.csv.")
    w("--")
    w("-- The parameter catalogue is DELIBERATELY NOT A REQUIRED VECTOR. BioMobi stays sparse:")
    w("-- absence of a row means 'not measured', never zero. The fixed-shape composition vector")
    w("-- the charter describes is a projection built in the model layer over this catalogue.")
    w("--")
    w("-- The catalogue GROWS. When a source reports a parameter that is not here, add a row to")
    w("-- parameters.csv and emit a NEW migration -- never map it onto a near-neighbour, and")
    w("-- never edit an applied migration. Every statement below is ON CONFLICT-guarded.")
    w("--")
    w(f"-- {len(units)} units, {len(bases)} bases, {len(params)} parameters.")
    w("")

    w("-- 1. units. Basis is NEVER folded into a unit string -- that is what basis is for.")
    for u in units:
        w(
            f"INSERT INTO unit (code, description) VALUES ({q(u['code'])}, {q(u['description'])})"
        )
        w("  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;")
    w("")

    w("-- 2. reporting bases. 'unknown' (the source did not say) and 'n.a.' (no basis applies)")
    w("--    are DIFFERENT CLAIMS and must never be collapsed into one another.")
    for b in bases:
        w(
            f"INSERT INTO basis (code, description) VALUES ({q(b['code'])}, {q(b['description'])})"
        )
        w("  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;")
    w("")

    w("-- 3. the parameter catalogue. default_unit_code is a HINT ONLY -- every measurement")
    w("--    records its own unit, and units may differ between measurements of one parameter.")
    for p in params:
        w("INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (")
        w(f"  {q(p['code'])},")
        w(f"  {q(p['name'])},")
        w(f"  {q(p['category'])},")
        w(f"  {qn(p['default_unit_code'])},")
        w(f"  {q(p['definition'])})")
        w("  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,")
        w("    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,")
        w("    definition = EXCLUDED.definition;")
    w("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--emit-migration",
        metavar="PATH",
        help="write the migration to PATH; without it the script only validates",
    )
    args = ap.parse_args()

    units, bases, params = validate()
    print(
        f"OK: {len(units)} units, {len(bases)} bases, {len(params)} parameters "
        f"({sum(1 for p in params if p['category'] == 'chemical')} chemical, "
        f"{sum(1 for p in params if p['category'] == 'physical')} physical, "
        f"{sum(1 for p in params if p['category'] == 'microbiological')} microbiological)"
    )

    if args.emit_migration:
        out = Path(args.emit_migration)
        if out.exists():
            sys.exit(
                f"FAIL: {out} already exists. An applied migration is frozen -- "
                f"emit a NEW one with a later timestamp instead."
            )
        emit(units, bases, params, out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
