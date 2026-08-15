# BIOLOOP (UGent workstream) — Project State

*The project dashboard. Read this at the start of a session; update it at the end (project-grain only). Companion to `charter.md`; mechanics defined in `protocol.md`.*
*This file holds project-level state only. Workstream detail lives in `<workstream>/hub.md`; cross-workstream items live in `flags.md`. Route each item by significance — see `protocol.md` §4.*
*Last updated: 2026-08-15 (second entry that day).*

## Current phase
**Foundational.** Database phase 1 done (schema baselined + verified); phase 2 **in progress** — the legacy-Excel loader is built and tested but has loaded nothing yet, pending human curation. Literature and model work not started.

## Workstream rollup
*(one line per workstream — compressed from each hub's Status header; "—" until the workstream's first session runs)*
- **Database:** phase 2 in progress — idempotent loader for the legacy Excel built and verified against the local stack; **paused awaiting the human `DECISION` columns in `database/crosswalks/`**. No data loaded anywhere yet; no schema change needed. In parallel, the candidate stream register (2b) is in-repo with its extraction protocol settled at v2; first source extracted and verified (S080, 114 claims), 11 source PDFs still queued.
- **Literature:** not started. One open flag inherited (F-001, non-blocking).
- **Modelling:** not started (later phase).

## Status snapshot
- Charter refined; source of truth confirmed.
- Backbone protocol drafted (`protocol.md`): read/write contract + status-block and flag schemas.
- Layered repo structure defined: root backbone (`charter` / `state` / `protocol` / `flags` / root `CLAUDE.md`) + one subfolder per workstream; `flags.md` ledger initialised (empty).
- Execution surface decided: Claude Code on the repo, per-workstream MCPs (Supabase; Zotero + Obsidian).
- BioMobi schema: the 11-table star/reference design is live on Supabase and now baselined into `database/supabase/migrations/` (2026-07-27); local toolchain (Supabase CLI + Docker/WSL2) working.
- Legacy-Excel seed (phase 2): loader committed and verified locally; **no data loaded yet** — gated on human curation. The seed will exercise 6 of the 11 tables (composition side); volumes, geography and classification remain untouched.
- Literature review: not started.
- Model and rule layers (transport, process/application): not started — later phase.

## Decision log
*(decision — rationale)*
- **Project treated as semi-reset; charter is the source of truth, proposal is background only** — first ~18 months drifted, MooV underdelivered, staff turnover; proposal goals valid but methods/timeline unreliable.
- **Build BioMobi from scratch in PostgreSQL (+ PostGIS), not the old Excel** — old internal data was inconsistent in variables, format and sourcing; need standardisation, value-level provenance, extensibility, native spatial support.
- **Three-layer architecture — BioMobi (data) / transport + process-application (rules & transformations) / model (engine)** — keeps the data layer model-independent and reusable; isolates all model-coupling in the rule layers.
- **"Application" = "process" (one database; endpoint vs middle-step framing)** — both are constraint + transformation objects; only the role differs.
- **Model is logistics-first; phase 1 is screening, not chaining** — for a single biomass, screen technically possible applications (apply their criteria), then filter by transport feasibility. Chaining (cascading) and optimisation only enter with multiple applications/biomasses and circularity. Build the individual steps first, layer chaining/optimisation on top later.
- **Composition is one fixed-shape vector, shared by streams and process outputs (SETTLED)** — a process/application takes the composition vector, transforms the values, returns a vector of the same shape; this is what enables cascading. BioMobi's composition schema is the canonical representation for raw streams and intermediates alike.
- **Multiple biomasses and cascading are built in parallel, then joined (SETTLED)** — each is a self-contained extension of the linear baseline; solve them independently, then integrate into a combined model. Cleaner than forcing a sequential order. (Supersedes the earlier streams-vs-applications ordering question.)
- **Variable-resolution capture; resolution/basis recorded per value; model accepts mixed granularity** — available data will be uneven (monthly vs annual); the system adapts to the data rather than demanding uniform resolution.
- **Regulatory, transport-feasibility, processing rules and demand-side specs excluded from BioMobi** — these are rules/transformations, not stream facts.
- **Backbone = one git repo, layered (charter / state / protocol / flags + per-workstream hubs); sessions run in Claude Code and write back directly** — durable, portable single source of truth; memory lives in the repo, sessions are disposable surfaces onto it; hand-offs are automated commits, not manual paste. (Supersedes the earlier "manual vs pipeline hand-off — deferred" open question.)
- **Database hosted on Supabase; the committed migration set is canonical — there is no separate `schema.sql` (REFINED 2026-07-27)** — phase 1 baselined the existing live structure as the first migration under `database/supabase/migrations/`, and a local `db reset` reproduced it schema-identically. A parallel `schema.sql` would be a second source of truth needing manual sync, so it is deliberately not kept: to read the schema, read the migrations or rebuild locally. The live instance stays downstream — evolve it forward via committed migrations, never by editing it directly. (Supersedes the earlier "baseline it into `schema.sql`" formulation; the charter's "schema as version-controlled SQL" still holds, the SQL just lives in migrations.)
- **Raw source data is not versioned (2026-07-28)** — `**/data/raw/` is gitignored across the repo. Inputs stay out of git; the committed ingestion script plus the human-verified curation manifests carry the audit trail instead. Applies to the coming OVAM/MONBIO PDFs and literature exports too, not just the database workstream. Trade-off accepted: a fresh clone cannot re-run an ingestion without separately obtaining the input.
- **Ingestion is gated on explicit human curation, not model judgement (2026-07-28)** — each source's crosswalk CSV carries an LLM proposal beside a human `include`/`exclude` decision, per stream *and* per source; the loader refuses to run while any decision is blank. Extends the existing "LLM-proposed, human-verified" crosswalk rule from name-mapping to inclusion.
- **The 80/20 rule applies to prospective harvesting, not to data already in hand (2026-07-28)** — for small, already-collected datasets, selection is manual per stream: check the name (to exclude out-of-scope material) and the source (to validate the entry). Refines, and bounds, the charter's "stream selection guided by the 80/20 principle". Partially answers the "salvageable existing data" open question below.
- **The candidate register covers the supply side of the agri-food chain only (2026-08-15)** — in: primary production (land + sea), auctions / producer organisations, processing industry, retail & wholesale. Out: horeca, catering, households, and anything downstream of retail. An aggregate figure is usable only if every chain stage it spans is in scope, which is why no whole-chain grand total is captured. This bounds what BioMobi's volume side will eventually hold, so it refines the charter's scope rather than merely implementing it. Enforced in `database/register/dictionaries/chain_L2.csv` (`in_scope` column).
- **A single crop is never a commodity subgroup (L3) in the register hierarchy (2026-08-15)** — the seed tree had put `Aardappelen` and `Suikerbieten` at L3 while the same dictionary listed `Aardappel` as an L4 example. Akkerbouw now carries genuine subgroups (`Granen`, `Aardappelen en knolgewassen`, `Suikerbieten en nijverheidsgewassen`, `Peulvruchten en eiwitgewassen`, `Voedergewassen`) with the crop at L4, so the L3 pivot means the same thing on every branch. Recorded here because `commodity_hierarchy.md` requires rule changes to be logged at project level; the member lists themselves stay in the dictionary.
- **Solo for now; do not design for future collaborators** — keep overhead low; revisit if the team grows.
- **Tooling** — PostgreSQL + PostGIS on Supabase, version-controlled SQL, Python/pandas ingestion; Zotero (refs) + Obsidian (notes, linked by citation key); literature-derived values flow into BioMobi carrying their citation key as provenance.

## Open questions
*(project-level only; workstream-local questions live in the relevant hub, cross-workstream ones become flags)*
- **Model resolution & relational structure** — what spatial/temporal granularity will the model reason at, and what entities does it connect? Needed to keep BioMobi's resolution adequate without over-collecting. To be informed by the modelling literature. (Mainly affects the rule layers and harvesting granularity, not BioMobi's parameter list.)
- **Controlled vocabulary / classification of streams** — which scheme to name and aggregate streams by (e.g. EWC waste codes, a sectoral classification, Moerman's ladder)? Decide before bulk data entry.
- **Salvageable existing data** — largely answered for the old Excel (2026-07-30): of 631 rows, ~271 are loadable — those with both a value and a source, on in-scope streams. Its composition data survives scrutiny; its volume figures do not (fabricated placeholders, flagged as such in the file itself). Remaining question is the canonical grain of two streams — see `database/hub.md`.

## Cross-workstream flags
See `flags.md` — the live ledger. **F-001** raised (db→lit, non-blocking): the legacy Excel's ~20 literature sources need Zotero verification and real BBT keys.

## Next actions
1. **Finish database phase 2** (in progress, paused): fill the `DECISION` columns in `database/crosswalks/`, resolve the `Sugar_beet` naming blocker, run `database/ingest/load_biomobi_excel.py`, verify, commit. Full instructions in `database/hub.md` → "Where we are / what's next".
2. Within that workstream, hold the open questions in mind: controlled-vocabulary choice (before bulk entry), variable-resolution capture, and the composition-vector interface.
3. In parallel (later session), a short literature scan: confirm standard units/basis and characterisation parameters, and identify which public inventories (OVAM biomass inventory, ILVO Monbio, voedselverlies.be, Noshan, Food Waste Explorer, Agrocycle) to harvest. Flag F-001 can be folded into that session.
