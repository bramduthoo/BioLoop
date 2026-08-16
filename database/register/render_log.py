# -*- coding: utf-8 -*-
"""Render `log.md` to `log.html` — a read-only HTML view of the extraction log.

`log.md` is the source of truth. This script never writes to it. The output
`log.html` is derived, gitignored, and safe to delete: regenerate it any time with

    database/.venv/Scripts/python database/register/render_log.py

The summary figures at the top of the page are computed from the log's own
Sessions table and from `streams_export.csv`, so they cannot drift out of date.

Usage:
    render_log.py [--in LOG.md] [--out LOG.html]
"""
import argparse
import html
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------- markdown

def inline(s):
    """Escape, then apply the inline markdown the log actually uses."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n][^*]*?)\*(?!\*)", r"<em>\1</em>", s, flags=re.S)
    s = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", r'<a href="#\2">\1</a>', s)
    return s


def slug(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"[^\w\s-]", "", t).strip().lower()
    return re.sub(r"[\s_]+", "-", t)


def convert(md):
    """Return (body_html, nav, sessions, section_counts)."""
    lines = md.replace("\r\n", "\n").split("\n")
    out, nav, sessions = [], [], []
    counts = {}
    i, cur_sec = 0, 0

    while i < len(lines):
        ln = lines[i]

        # tables
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if "source_id" in head and "Claims added" in head:
                sessions.extend(body)
            out.append('<div class="tw"><table><thead><tr>'
                       + "".join("<th>%s</th>" % inline(c) for c in head)
                       + "</tr></thead><tbody>")
            for r in body:
                out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r)
                           + "</tr>")
            out.append("</tbody></table></div>")
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            sid = slug(txt)
            if lvl == 1:
                pass  # the masthead carries the document title
            elif lvl == 2:
                out.append('<h2 id="%s">%s</h2>' % (sid, inline(txt)))
                nav.append((2, sid, txt))
            elif lvl == 3:
                cur_sec = 0
                out.append('<h3 id="%s"><span class="src-badge">%s</span></h3>'
                           % (sid, inline(txt)))
                nav.append((3, sid, txt))
            else:
                n = re.match(r"^(\d)\.", txt)
                cur_sec = int(n.group(1)) if n else 0
                out.append('<h4 id="%s" data-sec="%d">%s</h4>'
                           % (sid, cur_sec, inline(txt)))
                nav.append((4, sid, txt))
            i += 1
            continue

        # lists (2-space continuations, one nesting level)
        if re.match(r"^\s*-\s+", ln):
            items, buf, buf_depth = [], None, 0
            while i < len(lines) and (re.match(r"^\s*-\s+", lines[i])
                                      or (lines[i].startswith("  ") and lines[i].strip())):
                m2 = re.match(r"^(\s*)-\s+(.*)$", lines[i])
                if m2:
                    if buf is not None:
                        items.append((buf_depth, buf))
                    buf_depth = 1 if len(m2.group(1)) >= 2 else 0
                    buf = m2.group(2)
                else:
                    buf = (buf or "") + " " + lines[i].strip()
                i += 1
            if buf is not None:
                items.append((buf_depth, buf))
            counts[cur_sec] = counts.get(cur_sec, 0) + sum(1 for d, _ in items if d == 0)
            out.append('<ul class="sec-%d">' % cur_sec)
            open_sub = 0
            for d, txt in items:
                if d == 1 and not open_sub:
                    out.append("<ul class='sub'>")
                    open_sub = 1
                elif d == 0 and open_sub:
                    out.append("</ul>")
                    open_sub = 0
                out.append("<li>%s</li>" % inline(txt))
            if open_sub:
                out.append("</ul>")
            out.append("</ul>")
            continue

        # paragraphs
        if ln.strip():
            para = [ln.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^\s*[-|#]", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append("<p>%s</p>" % inline(" ".join(para)))
            continue
        i += 1

    return "\n".join(out), nav, sessions, counts


# --------------------------------------------------------------- figures

def corpus_claims(register_dir):
    """Authoritative claim count: data rows in streams_export.csv."""
    p = os.path.join(register_dir, "streams_export.csv")
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8-sig") as f:
        return max(sum(1 for ln in f if ln.strip()) - 1, 0)


def head_commit(register_dir):
    try:
        return subprocess.check_output(
            ["git", "-C", register_dir, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def build_stats(sessions, counts, claims, commit):
    unverified = sum(1 for r in sessions
                     if len(r) > 5 and not r[5].lower().lstrip("*").startswith("yes"))
    cells = []
    if claims is not None:
        cells.append((claims, "claims in corpus"))
    cells.append((len(sessions), "sources extracted"))
    cells.append((unverified, "awaiting verification"))
    if counts.get(1):
        cells.append((counts[1], "variant readings"))
    if counts.get(2):
        cells.append((counts[2], "suspected source errors"))
    return "\n".join(
        '  <div class="stat"><b>%s</b><span>%s</span></div>' % (v, l) for v, l in cells)


# --------------------------------------------------------------- template

CSS = """
:root{
  --ground:#F6F7F3; --surface:#FFFFFF; --surface-2:#EFF2EA;
  --ink:#1E241D; --ink-soft:#5A6357; --ink-faint:#828B7D;
  --rule:#DDE2D8; --rule-soft:#E9EDE4;
  --accent:#4A6B3F; --accent-soft:#E4EBDD;
  --flag:#8F5710; --excl:#7E5049;
  --serif:Georgia,"Iowan Old Style","Palatino Linotype",Palatino,serif;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,"Cascadia Mono","SF Mono",Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#15180F; --surface:#1B1F17; --surface-2:#232819;
  --ink:#E7EBDF; --ink-soft:#A0A996; --ink-faint:#7C8573;
  --rule:#2F352A; --rule-soft:#262B21;
  --accent:#A3C48D; --accent-soft:#242E1D;
  --flag:#DCA463; --excl:#C79185;
}}
:root[data-theme="dark"]{
  --ground:#15180F; --surface:#1B1F17; --surface-2:#232819;
  --ink:#E7EBDF; --ink-soft:#A0A996; --ink-faint:#7C8573;
  --rule:#2F352A; --rule-soft:#262B21;
  --accent:#A3C48D; --accent-soft:#242E1D;
  --flag:#DCA463; --excl:#C79185;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:var(--sans);font-size:15.5px;line-height:1.65;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 96px;
  display:grid;grid-template-columns:236px minmax(0,1fr);gap:56px;align-items:start}
header.mast{grid-column:1/-1;padding:52px 0 26px;border-bottom:2px solid var(--ink)}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-faint);margin:0 0 14px}
.mast h1{font-family:var(--serif);font-weight:400;font-size:clamp(30px,4.4vw,46px);
  line-height:1.1;margin:0;text-wrap:balance;letter-spacing:-.015em}
.mast p.sub{margin:14px 0 0;max-width:62ch;color:var(--ink-soft);font-size:15px}
.stats{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:0;
  border-bottom:1px solid var(--rule);margin-bottom:8px}
.stat{padding:18px 30px 18px 0;margin-right:30px;border-right:1px solid var(--rule-soft)}
.stat:last-child{border-right:0;margin-right:0}
.stat b{display:block;font-family:var(--serif);font-size:27px;line-height:1;
  font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.stat span{display:block;margin-top:7px;font-family:var(--mono);font-size:10.5px;
  letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint)}
nav{position:sticky;top:24px;padding-top:30px;font-size:13px;
  max-height:calc(100vh - 48px);overflow-y:auto}
nav a{display:block;text-decoration:none;color:var(--ink-soft);
  padding:4px 0 4px 12px;border-left:2px solid var(--rule-soft);line-height:1.4}
nav a:hover{color:var(--accent);border-left-color:var(--accent)}
nav a:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
nav a.n2{font-family:var(--mono);font-size:10.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--ink-faint);margin-top:20px;
  border-left-color:transparent}
nav a.n3{font-family:var(--serif);font-size:16px;color:var(--ink);margin-top:6px}
nav a.n4{padding-left:24px;font-size:12.5px}
article{padding-top:30px;min-width:0}
h2{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-faint);font-weight:600;margin:64px 0 18px;
  padding-bottom:9px;border-bottom:1px solid var(--rule)}
h3{margin:60px 0 20px}
.src-badge{display:inline-block;font-family:var(--mono);font-size:19px;font-weight:600;
  letter-spacing:.02em;background:var(--accent-soft);color:var(--accent);
  border:1px solid var(--accent);border-radius:3px;padding:5px 14px}
h4{font-family:var(--serif);font-weight:400;font-size:22px;line-height:1.25;
  margin:44px 0 14px;text-wrap:balance;letter-spacing:-.01em;
  padding-left:14px;border-left:3px solid var(--accent)}
h4[data-sec="2"]{border-left-color:var(--flag)}
h4[data-sec="3"]{border-left-color:var(--excl)}
p{margin:0 0 15px;max-width:70ch}
ul{margin:0 0 18px;padding-left:0;list-style:none;max-width:72ch}
li{position:relative;padding-left:20px;margin-bottom:11px}
li::before{content:"";position:absolute;left:2px;top:.68em;width:6px;height:1.5px;
  background:var(--ink-faint)}
ul.sub{margin:11px 0 0;padding-left:20px}
ul.sec-2>li::before{background:var(--flag);height:2px}
ul.sec-3>li::before{background:var(--excl)}
strong{font-weight:650}
em{font-style:italic;color:var(--ink-soft)}
code{font-family:var(--mono);font-size:.865em;background:var(--surface-2);
  padding:1.5px 5px;border-radius:3px;
  font-variant-numeric:tabular-nums;word-break:break-word}
a{color:var(--accent);text-decoration:underline;text-underline-offset:2px}
.tw{overflow-x:auto;margin:0 0 26px;border:1px solid var(--rule);
  border-radius:4px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:520px}
th{text-align:left;font-family:var(--mono);font-size:10px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink-faint);font-weight:600;
  padding:11px 14px;border-bottom:1px solid var(--rule);
  background:var(--surface-2);white-space:nowrap;vertical-align:bottom}
td{padding:11px 14px;border-bottom:1px solid var(--rule-soft);
  vertical-align:top;font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:0}
td code{background:transparent;padding:0}
@media (max-width:940px){
  .wrap{grid-template-columns:1fr;gap:0;padding:0 20px 72px}
  nav{position:static;max-height:none;padding:24px 0 0;
    border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:4px 18px}
  nav a{border-left:0;padding-left:0}
  nav a.n2{margin-top:0}
  nav a.n4{padding-left:0}
  .stat{padding-right:20px;margin-right:20px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

PAGE = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BIOLOOP Extraction Log</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<header class="mast">
  <p class="eyebrow">BIOLOOP &middot; database / register &middot; phase 2b</p>
  <h1>Register extraction log</h1>
  <p class="sub">The running record of every source-extraction session: what was
  extracted, what looked wrong, and whether a human has checked it against the
  archived PDF. Generated from <code>log.md</code>__STAMP__ &mdash; do not edit this
  page; edit the markdown and re-run <code>render_log.py</code>.</p>
</header>
<section class="stats">
__STATS__
</section>
<nav>__NAV__</nav>
<article>__BODY__</article>
</div>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="src", default=os.path.join(HERE, "log.md"))
    ap.add_argument("--out", dest="dst", default=os.path.join(HERE, "log.html"))
    a = ap.parse_args()

    if not os.path.exists(a.src):
        sys.exit("render_log.py: input not found: %s" % a.src)

    md = io.open(a.src, encoding="utf-8").read()
    body, nav, sessions, counts = convert(md)

    nav_html = []
    for lvl, sid, txt in nav:
        label = txt if lvl != 4 else re.sub(r"^\d\.\s*", "", txt).split(" — ")[0]
        nav_html.append('<a class="n%d" href="#%s">%s</a>'
                        % (lvl, sid, html.escape(label)))

    commit = head_commit(HERE)
    stamp = (" at commit <code>%s</code>" % commit) if commit else ""
    stats = build_stats(sessions, counts, corpus_claims(HERE), commit)

    page = (PAGE.replace("__CSS__", CSS)
                .replace("__STATS__", stats)
                .replace("__NAV__", "\n".join(nav_html))
                .replace("__BODY__", body)
                .replace("__STAMP__", stamp))
    io.open(a.dst, "w", encoding="utf-8", newline="\n").write(page)

    print("render_log.py: %s -> %s" % (os.path.basename(a.src), a.dst))
    print("  %d sessions, %d nav entries, %d bytes"
          % (len(sessions), len(nav), len(page)))


if __name__ == "__main__":
    main()
