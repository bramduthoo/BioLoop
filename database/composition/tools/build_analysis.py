"""Build the exploratory-analysis page from eda.py and qc_values.py.

    ../.venv/Scripts/python tools/build_analysis.py   ->  ../build/analysis.html

A pure function of the extraction CSVs and the vocabulary, like every other page in this
folder: re-run it after a harvest round and the picture updates with nothing to edit.
"""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = ROOT / "build"
PY = sys.executable


def run(script: str) -> dict:
    # the child prints UTF-8 (the QC messages carry middots and arrows); Windows would
    # otherwise hand back cp1252 and the JSON would not decode
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    out = subprocess.run([PY, str(HERE / script), "--json"], capture_output=True,
                         text=True, encoding="utf-8", env=env)
    if out.returncode:
        sys.exit(f"FAIL: {script}\n{out.stderr}")
    return json.loads(out.stdout)


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def main() -> None:
    d = run("eda.py")
    qc = run("qc_values.py")

    pars = [p for p in d["parameters"] if p["values"]]
    streams = d["streams"]
    codes = [s["code"] for s in streams]
    cover = {(p["code"], s): 0 for p in pars for s in codes}
    for p in pars:
        for s in p["stream_list"]:
            cover[(p["code"], s)] = 1
    # value counts per cell
    counts = {}
    for s in streams:
        for p in s["parameter_list"]:
            counts[(p, s["code"])] = counts.get((p, s["code"]), 0) + 1

    payload = dict(eda=d, qc={
        "wellformed": len(qc["wellformed"]),
        "identities": len(qc["identities"]),
        "spreads": qc["spreads"],
    })

    BUILD.mkdir(parents=True, exist_ok=True)
    tpl = (HERE / "analysis_template.html").read_text(encoding="utf-8")
    (BUILD / "analysis.html").write_text(
        tpl.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":"))),
        encoding="utf-8")
    # render-check before anyone publishes it: node tools/check_page.js on the extracted
    # script. A page that throws in its first section arrives EMPTY, which reads as a data
    # problem when it is a code problem.
    import re
    m = re.search(r"<script>(.*)</script>", (BUILD / "analysis.html").read_text(encoding="utf-8"), re.S)
    (BUILD / "analysis.js").write_text(m.group(1), encoding="utf-8")
    chk = subprocess.run(["node", str(HERE / "check_page.js"), str(BUILD / "analysis.js")],
                         capture_output=True, text=True, encoding="utf-8")
    print(chk.stdout.rstrip())
    if "THREW" in chk.stdout or "reported a build error" in chk.stdout:
        sys.exit("FAIL: the page does not render - fix it before publishing")

    print(f"wrote {BUILD / 'analysis.html'} "
          f"({(BUILD / 'analysis.html').stat().st_size / 1024:.0f} KB)")
    print(f"  {d['n_values']} values, {len(pars)} parameters used, "
          f"{d['n_streams_with_data']}/{d['n_streams_in_scope']} streams")
    print(f"  QC: {len(qc['wellformed'])} well-formedness, {len(qc['identities'])} identity, "
          f"{len(qc['spreads'])} spread findings")


if __name__ == "__main__":
    main()
