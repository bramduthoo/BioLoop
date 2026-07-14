# BIOLOOP — Cross-workstream flags

*The shared ledger. The single place cross-workstream items are born, tracked, and closed. A flag is a stateful object with a lifecycle, not a note — see `protocol.md` §5 for the full schema.*
*No workstream reaches into another; it leaves a flag here, and the ledger routes it.*
*Last updated: 2026-07-14.*

## How to use this file
- **Raise** a flag when your session produces something *another specific workstream* must act on. Append a row; take the next free `id`.
- **Inherit** flags by filtering the table to `To: <your workstream>`, `Status: open`/`acked`. Handle **blocking** flags first.
- **Close** a flag by setting `Status: resolved` and filling `Detail / Resolution` with a one-line note + date. Resolved flags stay here as history — never delete them.

Routing shorthand: `lit` = literature, `db` = database, `mod` = modelling.

## Ledger

| ID | Date | From→To | Blocking | Status | Summary | Detail / Resolution |
|----|------|---------|----------|--------|---------|---------------------|
| — | — | — | — | — | *(no flags raised yet)* | — |

<!-- Example of a live and a closed row (delete this comment once real rows exist):
| F-001 | 2026-07-18 | lit→db | no  | open     | brewer's spent grain missing from controlled vocab | literature/hub.md#vocab-gaps |
| F-002 | 2026-07-20 | mod→db | yes | resolved | model needs monthly seasonality for stream X       | resolved 2026-07-28: added monthly resolution field to schema |
-->
