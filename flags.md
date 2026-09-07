# BIOLOOP — Cross-workstream flags

*The shared ledger. The single place cross-workstream items are born, tracked, and closed. A flag is a stateful object with a lifecycle, not a note — see `protocol.md` §5 for the full schema.*
*No workstream reaches into another; it leaves a flag here, and the ledger routes it.*
*Last updated: 2026-09-07.*

## How to use this file
- **Raise** a flag when your session produces something *another specific workstream* must act on. Append a row; take the next free `id`.
- **Inherit** flags by filtering the table to `To: <your workstream>`, `Status: open`/`acked`. Handle **blocking** flags first.
- **Close** a flag by setting `Status: resolved` and filling `Detail / Resolution` with a one-line note + date. Resolved flags stay here as history — never delete them.

Routing shorthand: `lit` = literature, `db` = database, `mod` = modelling.

## Ledger

| ID | Date | From→To | Blocking | Status | Summary | Detail / Resolution |
|----|------|---------|----------|--------|---------|---------------------|
| F-001 | 2026-07-30 | db→lit | no | **resolved** | ~20 legacy sources need Zotero entries + real BBT keys | **Withdrawn 2026-09-07 — the need disappeared, the work was not done.** The flag existed only to give the legacy Excel's secondhand sources real BBT keys before that workbook loaded. The database workstream abandoned that load (2a, 2026-09-07): the workbook is not a BioMobi input, nothing was ever loaded from it, and `crosswalks/biomobi_excel_sources.csv` is deleted. **Nothing for literature to do.** If those ~20 references are ever wanted for their own sake, that is a new flag, not this one. |
| F-002 | 2026-08-14 | db→lit | no | open | No Zotero MCP is wired — the register's 8 archived source PDFs all have a blank `citation_key` — **now the only gate on BioMobi's volume side** | `database/register/CLAUDE.md` step 2 assumes a Zotero MCP "wired at repo root `.mcp`", but `.mcp.json` holds only Supabase. **Update 2026-09-06, register closed:** all **eight** archived sources (S080, S002, S091, S007, S066, S065, S087, S010) carry a blank `citation_key`, and the Zotero server timed out again on connect this session. A Zotero MCP *did* connect during the S002 session, so the tool is reachable — but it comes from user/global config, not the repo, so it is not reproducible for another clone. **This now gates real work, not just tidiness:** BioMobi's `source.citation_key` is `NOT NULL` and `source_key` is the provenance spine, so no register claim can become a `supply_observation` row until these keys exist. Fix: declare the Zotero server in `.mcp.json`, create the items from the register's `Sources`-sheet metadata (**not** from PDF DOI extraction — ILVO/OVAM grey literature has no DOI), then backfill the keys. Source FKs are `ON UPDATE CASCADE`, so placeholder keys can be renamed safely later. **Update 2026-09-07:** the register's stream *selection* is now loaded into BioMobi (21 `stream` rows) — that needed no source, because `stream` carries no source FK. Everything downstream of it does. This flag is therefore the single remaining blocker on the volume side, and its priority has risen accordingly. A Zotero MCP connected again this session. |
| F-003 | 2026-09-06 | db→lit | no | open | The source hunt — 15 gaps no further extraction can close | `database/register/OPEN_GAPS.md`; worklist in `database/register/crosswalks/GAP_LIST.csv` (one row per gap: claim ids, the total that exists, the detail that does not, the candidate or an explicit *none*). The register is closed at 801 claims and its remaining gaps are **class B — nothing in the corpus measures them**. Priority: **aardappelverwerking** (621.063 t, zero components, no candidate) → **zuivel/wei** (absent from all 801 claims, would likely enter the top ten on its own, no candidate) → **vlees per diersoort** → **retail + bakkerij** (S067, S025 — named but no PDF) → **cacao** and **Flemish oilseed crush**. **Fact-check G-02 first** (PO's/veilingen at 15.189 t looks too small to be true; an afternoon against VBT or one auction's jaarverslag decides it) — do not commission for that stage before it. **Screening rule: does the candidate carve by *process*?** A source carving by NACE class, Prodcom code, or a monitor's own loss definition will reproduce the gaps we already have — that is exactly how they arose. Sources marked `_RETIRED` in `register/inbox/` are **excluded from every candidate and must not be proposed** (reviewer, 2026-09-04). |

<!-- Example of a live and a closed row (delete this comment once real rows exist):
| F-001 | 2026-07-18 | lit→db | no  | open     | brewer's spent grain missing from controlled vocab | literature/hub.md#vocab-gaps |
| F-002 | 2026-07-20 | mod→db | yes | resolved | model needs monthly seasonality for stream X       | resolved 2026-07-28: added monthly resolution field to schema |
-->
