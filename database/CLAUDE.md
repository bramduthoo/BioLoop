# Database workstream — Claude Code conventions (BioMobi)

*Local enforcement glue for the database workstream. Read this **with**, not instead of, the root `CLAUDE.md` and `protocol.md`. Detail lives here; only what the project needs rises to `state.md`/`flags.md`.*
*Last updated: 2026-09-07.*

## Session contract (this workstream)
- **At start**, read in order: root `charter.md` → `state.md` → `flags.md` (filtered to `to: db`, status `open`/`acked`) → this folder's `hub.md` (status header first) → this file. The session objective is set when the session is opened.
- **At end**: update `hub.md`'s status block (mechanical, per `protocol.md` §3); route every decision/question by significance (`protocol.md` §4 — local→hub, project→`state.md`, cross-workstream→`flags.md`); update `flags.md`; commit with a message naming workstream + objective.

## Where things are written — read this before adding to this file

**This file holds only what binds *every* database session.** A bounded piece of work gets its own
folder with its own `README.md` (what it is, how to run it) and `CLAUDE.md` (its rules, its
decisions, its judgement calls). The sub-project folders are the detail layer; this file is the
thin layer above them.

| Folder | What it is | Its own docs |
|---|---|---|
| `register/` | the candidate stream register — the claim-level corpus and its selection | `README.md` · `CLAUDE.md` (extraction protocol v2.6) · `log.md` · `OPEN_GAPS.md` |
| `streams/` | the register's selection → BioMobi `stream` rows + classification facets | `README.md` · `CLAUDE.md` |
| `ingest/` | loaders that are not part of a sub-project (shared `requirements.txt`) | — |
| `supabase/migrations/` | the schema of record | — |

**If you are about to add a worked example, a per-source decision, a verification run or a bug
story to this file — it belongs one level down.** What rises to here is the rule the episode
taught, stated in one line, with no case attached. What rises further, to `state.md`, is only what
the *project* needs (`protocol.md` §4). This rule exists because it was broken on 2026-09-07: the
`streams/` transfer wrote its grain rationale and a tonnage-discrepancy anecdote straight into this
file, where no other database session needed them.

## What this workstream owns
BioMobi — a **facts-only** data layer in PostgreSQL/PostGIS on Supabase (project ref `bljaqfeqkjaqvdxwbpkx`). Facts about streams and their characterisation **only**. No regulatory/transport/processing rules, constraints, or transformations — those belong to the model's rule layers, never here.

## Schema lifecycle — git is canonical
- The **schema of record is the migration set** under `database/supabase/migrations/`. The live Supabase instance is downstream of those files, never the source of truth.
- **Never change the remote schema directly** — not via the dashboard, SQL/Table editor, or an ad-hoc MCP DDL call. Every schema change is a committed migration applied with the CLI (`supabase db push`). Direct edits break migration sync.
- **Baseline: done (phase 1, 2026-07-27)** — `database/supabase/migrations/20260727114134_remote_schema.sql`. Do not re-baseline; evolve forward from here.
- **Generating migrations from live drift — read this first.** `supabase db pull` and `db diff` are **not trustworthy on CLI 2.109.x**: the `pg-delta` diff engine returned an empty diff against the full 11-table schema and exited claiming "No schema changes found". The baseline was taken with `supabase db dump --linked --schema public` (pg_dump) instead. If you ever diff against live, **check the output is non-empty before believing it**. Note also that `db dump --schema public` omits extension DDL — PostGIS must be declared explicitly (the baseline does this).
- **Verifying a migration:** `supabase start` then `supabase db reset` rebuilds the local DB from migrations alone. Cross-check against live read-only via the MCP — comparing md5 over column signatures, constraint definitions and index definitions catches far more than a table count. The full local stack is unnecessary; `supabase start -x studio,imgproxy,vector,logflare,mailpit,edge-runtime,realtime,storage-api,supavisor` is enough and avoids ~1 GB of image pulls. Do not exclude `kong` — the CLI health-checks through it and will tear the stack down.
- Use the **project-scoped** Supabase MCP (`project_ref=bljaqfeqkjaqvdxwbpkx`) for inspection and read-only queries during dev. Do **not** use the account-wide MCP for changes, and never touch the unrelated `Financieel` project in the same org.

## Data & ingestion rules
- **Provenance is non-negotiable.** Every `property_measurement` / `supply_observation` row carries a resolvable `source_key` (the schema enforces `NOT NULL` — never work around it). Literature values use their Better BibTeX key; dataset values use a `source` row of type `dataset`.
- **Absence means "not measured."** Never insert fabricated or zero-filled rows to "complete" a composition vector. BioMobi stays sparse; the fixed-shape composition vector is a **model-layer projection**, not represented or padded here.
- **Register vocabulary once, then map.** A parameter is registered a single time (`code`, `name`, `category`, `default_unit_code`, `definition`); every later value **maps** to it — never spawn a near-duplicate. Keep `basis` separate from `unit` (no "%DS"-style compound units). Same discipline for streams.
- **Stream grain guardrail — a stream is a MATERIAL** (settled 2026-09-07, see `state.md`). Define each canonical stream at the **finest grain any target source distinguishes**, and let the *material* decide identity: never a commodity standing in for its fractions, never a chain stage. Volumes attach **upward** (coarse inventory figure → fine stream, via conversion factors, e.g. AgroCycle). Never average composition **down** onto a coarse stream.
- **A sub-project owns one derivation, and consumers read it.** Where a folder computes figures (`register/`), a downstream consumer carries and cites them — it does not re-derive them, because a second implementation drifts.
- **Ingestion = committed scripts.** One idempotent Python script per source (openpyxl/pandas + psycopg), not notebooks — under its sub-project's `tools/`, or `database/ingest/` if it belongs to none. Its crosswalk/manifest CSVs sit beside it in that sub-project's `crosswalks/`, LLM-proposed and **human-verified** (expect NL↔EN semantic mapping — peel/pomace/pulp — not string similarity).
- **Curation is a human gate, not a model judgement.** Each source's crosswalk CSV carries the proposal beside a human `DECISION` column (`include`/`exclude`), per stream *and* per source. **A loader must exit non-zero, naming every unreviewed row, while any decision is blank.** Write these CSVs `;`-delimited with a UTF-8 BOM — the user's Excel is Belgian-locale and will otherwise cram every row into one column.
- **Idempotency via a source-key namespace.** Both fact tables use identity PKs with no natural unique key, so a re-run duplicates silently. Each loader prefixes every `source.citation_key` it creates (e.g. `xls-`), then per run deletes fact rows in that namespace and reloads, in **one transaction**. This converges on removals as well as additions. Do not add UNIQUE constraints for this — legacy sources contain legitimately identical rows. **Never delete reference vocabulary** (`unit`/`basis`/`parameter`/`stream`): `stream_classification` cascades on stream delete, so an ingestion script must not be able to destroy classification work.
- **Record what the source said.** Never silently harmonise units, fix errors, or drop duplicates — load as recorded and *report* the anomaly. A missing unit/basis is `unknown`; an inapplicable one is `n.a.`/`not_applicable`. Those are different claims and must not be collapsed.
- **Raw inputs are not versioned.** `**/data/raw/` is gitignored (project decision, 2026-07-28). The committed script plus the human-verified manifests are the audit trail; a loader must fail with a clear message when its input is absent.
- **Test against the local stack only.** A loader should refuse a non-local DSN unless explicitly overridden.

## Tooling roles (quick map)
- **Schema:** Supabase CLI (authoring/lifecycle; files are truth) · Supabase MCP (read/inspect only).
- **PDF (OVAM / MONBIO / AgroCycle):** `camelot` (bordered tables; confidence reports) + `pdfplumber` (borderless tables + surrounding context); escalate messy/merged tables to a Claude rasterize-and-read pass. Low volume → favour accuracy over automation.
- **Provenance:** Zotero + Better BibTeX; `source.citation_key` = BBT key.
- **Subagents:** run each source's extraction as a bounded `general-purpose` subagent to keep the main session's context clean; run `verify` and `code-review` on migration and ingestion diffs before commit.

## Ignore rules (settled in phase 1)
- The root ignore file was renamed `gitignore` → `.gitignore` (it was inert before). `supabase init` additionally generated `database/supabase/.gitignore`, which covers `.temp/` (holds the linked project ref and pooler URL) and `.branches/`, plus `.env.keys` / `.env.local`. Both are committed; leave them in place.

*See `hub.md` for current status, the phased build plan, the source register, and local open questions.*
