# BIOLOOP — Cross-workstream flags

*The shared ledger. The single place cross-workstream items are born, tracked, and closed. A flag is a stateful object with a lifecycle, not a note — see `protocol.md` §5 for the full schema.*
*No workstream reaches into another; it leaves a flag here, and the ledger routes it.*
*Last updated: 2026-08-15.*

## How to use this file
- **Raise** a flag when your session produces something *another specific workstream* must act on. Append a row; take the next free `id`.
- **Inherit** flags by filtering the table to `To: <your workstream>`, `Status: open`/`acked`. Handle **blocking** flags first.
- **Close** a flag by setting `Status: resolved` and filling `Detail / Resolution` with a one-line note + date. Resolved flags stay here as history — never delete them.

Routing shorthand: `lit` = literature, `db` = database, `mod` = modelling.

## Ledger

| ID | Date | From→To | Blocking | Status | Summary | Detail / Resolution |
|----|------|---------|----------|--------|---------|---------------------|
| F-001 | 2026-07-30 | db→lit | no | open | ~20 legacy sources need Zotero entries + real BBT keys | `database/crosswalks/biomobi_excel_sources.csv`. Sources transcribed secondhand out of the old Excel; 8 carry DOIs, the rest are bare titles or database names. They load as `source_type='internal'` under placeholder keys (`xls-*`). Renaming to real BBT keys is safe — all source FKs are `ON UPDATE CASCADE`. |
| F-002 | 2026-08-14 | db→lit | no | open | No Zotero MCP is wired — register sources cannot be archived or given BBT keys | `database/register/CLAUDE.md` step 2 assumes a Zotero MCP "wired at repo root `.mcp`", but `.mcp.json` holds only the Supabase server. S080 (114 claims) and S002 (100 claims) have now been extracted with their PDFs archived, but no Zotero item exists for either and both `citation_key` cells are blank. Every later register source hits the same wall. **Update 2026-08-15: a Zotero MCP server did connect in the S002 session, so the tool is reachable — but it is not declared in the repo's `.mcp.json` (still Supabase-only), so it is coming from user/global config and is not reproducible for another clone.** Fix: declare the Zotero server in `.mcp.json`, then backfill the items + BBT keys for every extracted source (S080, S002, …). |

<!-- Example of a live and a closed row (delete this comment once real rows exist):
| F-001 | 2026-07-18 | lit→db | no  | open     | brewer's spent grain missing from controlled vocab | literature/hub.md#vocab-gaps |
| F-002 | 2026-07-20 | mod→db | yes | resolved | model needs monthly seasonality for stream X       | resolved 2026-07-28: added monthly resolution field to schema |
-->
