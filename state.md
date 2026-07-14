# BIOLOOP (UGent workstream) — Project State

*The project dashboard. Read this at the start of a session; update it at the end (project-grain only). Companion to `charter.md`; mechanics defined in `protocol.md`.*
*This file holds project-level state only. Workstream detail lives in `<workstream>/hub.md`; cross-workstream items live in `flags.md`. Route each item by significance — see `protocol.md` §4.*
*Last updated: 2026-07-14.*

## Current phase
**Foundational.** Backbone restructured into the layered git repo. Preparing to open the first database workstream session. No schema, literature, or model work started yet.

## Workstream rollup
*(one line per workstream — compressed from each hub's Status header; "—" until the workstream's first session runs)*
- **Database:** not started — first session will design the schema + `database/hub.md`.
- **Literature:** not started.
- **Modelling:** not started (later phase).

## Status snapshot
- Charter refined; source of truth confirmed.
- Backbone protocol drafted (`protocol.md`): read/write contract + status-block and flag schemas.
- Layered repo structure defined: root backbone (`charter` / `state` / `protocol` / `flags` / root `CLAUDE.md`) + one subfolder per workstream; `flags.md` ledger initialised (empty).
- Execution surface decided: Claude Code on the repo, per-workstream MCPs (Supabase; Zotero + Obsidian).
- BioMobi schema / data dictionary: not started.
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
- **Database hosted on Supabase; git canonical via schema.sql + committed migrations** — structure already exists in Supabase; baseline it into `schema.sql`, then evolve forward through migrations rather than editing the live instance, to preserve diffable history.
- **Solo for now; do not design for future collaborators** — keep overhead low; revisit if the team grows.
- **Tooling** — PostgreSQL + PostGIS on Supabase, version-controlled SQL, Python/pandas ingestion; Zotero (refs) + Obsidian (notes, linked by citation key); literature-derived values flow into BioMobi carrying their citation key as provenance.

## Open questions
*(project-level only; workstream-local questions live in the relevant hub, cross-workstream ones become flags)*
- **Model resolution & relational structure** — what spatial/temporal granularity will the model reason at, and what entities does it connect? Needed to keep BioMobi's resolution adequate without over-collecting. To be informed by the modelling literature. (Mainly affects the rule layers and harvesting granularity, not BioMobi's parameter list.)
- **Controlled vocabulary / classification of streams** — which scheme to name and aggregate streams by (e.g. EWC waste codes, a sectoral classification, Moerman's ladder)? Decide before bulk data entry.
- **Salvageable existing data** — which of the old internal data survives scrutiny and can seed BioMobi? Assess against the new schema.

## Cross-workstream flags
See `flags.md` — the live ledger. None raised yet (no workstream sessions run).

## Next actions
1. Stand up the git repo from the drafted backbone files (charter / state / protocol / flags / root CLAUDE), plus empty `database/`, `literature/`, `modelling/` subfolders.
2. Open the first **database workstream session** in Claude Code (Supabase MCP attached). Its first acts: baseline the existing Supabase schema into `schema.sql`; then design `database/hub.md` (status header from `protocol.md` §3 + a local body) and `database/CLAUDE.md`, live against the real work.
3. Within that workstream, hold the open questions in mind: controlled-vocabulary choice (before bulk entry), variable-resolution capture, and the composition-vector interface.
4. In parallel (later session), a short literature scan: confirm standard units/basis and characterisation parameters, and identify which public inventories (OVAM biomass inventory, ILVO Monbio, voedselverlies.be, Noshan, Food Waste Explorer, Agrocycle) to harvest.
