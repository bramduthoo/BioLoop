#!/usr/bin/env python3
"""BIOLOOP stream-overview generator.
Reads the register workbook + the pure derivation, emits ONE self-contained HTML.
Output is a pure function of the `Streams` sheet and regenerates deterministically.

  python3 build_overview.py                       # auto-find the workbook in this folder
  python3 build_overview.py /path/to/workbook.xlsx
"""
import subprocess, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
subprocess.run([sys.executable, str(HERE/"prep_data.py"), *sys.argv[1:]], check=True)
derive = (HERE/"derive.js").read_text(encoding="utf-8")
data   = (HERE/"streams.json").read_text(encoding="utf-8")
html   = (HERE/"template.html").read_text(encoding="utf-8").replace("/*__DERIVE__*/", derive).replace("/*__DATA__*/", data)
out = HERE/"stream_overview.html"; out.write_text(html, encoding="utf-8")
print(f"wrote {out.name}  ({len(html)//1024} KB) — open it in a browser")
