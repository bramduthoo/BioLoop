# BIOLOOP (UGent workstream) — Project State

*The project dashboard. Read this at the start of a session; update it at the end (project-grain only). Companion to `charter.md`; mechanics defined in `protocol.md`.*
*This file holds project-level state only. Workstream detail lives in `<workstream>/hub.md`; cross-workstream items live in `flags.md`. Route each item by significance — see `protocol.md` §4.*
*Last updated: 2026-07-27.*

## Current phase
**Foundational.** Database workstream phase 1 done — the live BioMobi schema is baselined into version control and verified. Ingestion not started; literature and model work not started.

## Workstream rollup
*(one line per workstream — compressed from each hub's Status header; "—" until the workstream's first session runs)*
- **Database:** phase 1 complete — live schema baselined as a committed migration, verified schema-identical by a local `db reset`; next session opens phase 2 (seed the old internal Excel).
- **Literature:** not started.
- **Modelling:** not started (later phase).

## Status snapshot
- Charter refined; source of truth confirmed.
- Backbone protocol drafted (`protocol.md`): read/write contract + status-block and flag schemas.
- Layered repo structure defined: root backbone (`charter` / `state` / `protocol` / `flags` / root `CLAUDE.md`) + one subfolder per workstream; `flags.md` ledger initialised (empty).
- Execution surface decided: Claude Code on the repo, per-workstream MCPs (Supabase; Zotero + Obsidian).
- BioMobi schema: the 11-table star/reference design is live on Supabase and now baselined into `database/supabase/migrations/` (2026-07-27); local toolchain (Supabase CLI + Docker/WSL2) working.
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
- **Solo for now; do not design for future collaborators** — keep overhead low; revisit if the team grows.
- **Tooling** — PostgreSQL + PostGIS on Supabase, version-controlled SQL, Python/pandas ingestion; Zotero (refs) + Obsidian (notes, linked by citation key); literature-derived values flow into BioMobi carrying their citation key as provenance.

## Open questions
*(project-level only; workstream-local questions live in the relevant hub, cross-workstream ones become flags)*
- **Model resolution & relational structure** — what spatial/temporal granularity will the model reason at, and what entities does it connect? Needed to keep BioMobi's resolution adequate without over-collecting. To be informed by the modelling literature. (Mainly affects the rule layers and harvesting granularity, not BioMobi's parameter list.)
- **Controlled vocabulary / classification of streams** — which scheme to name and aggregate streams by (e.g. EWC waste codes, a sectoral classification, Moerman's ladder)? Decide before bulk data entry.
- **Salvageable existing data** — which of the old internal data survives scrutiny and can seed BioMobi? Assess against the new schema.

## Cross-workstream flags
See `flags.md` — the live ledger. None raised. Database phase 1 produced nothing another workstream must act on.

## Next actions
1. Open the next **database session**: phase 2 — seed the old internal Excel into the schema via a committed `database/ingest/` script, validating the schema end-to-end before heavier harvesting.
2. Within that workstream, hold the open questions in mind: controlled-vocabulary choice (before bulk entry), variable-resolution capture, and the composition-vector interface.
3. In parallel (later session), a short literature scan: confirm standard units/basis and characterisation parameters, and identify which public inventories (OVAM biomass inventory, ILVO Monbio, voedselverlies.be, Noshan, Food Waste Explorer, Agrocycle) to harvest.
