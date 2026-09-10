# BIOLOOP — Project Charter (UGent workstream)

*Living scope document. Last updated: 2026-09-10.*
*For matters of current scope this supersedes the 2-year-old VLAIO proposal; the proposal is retained as background reference only.*
*Companion documents: `state.md` (current phase, decisions, open questions), `protocol.md` (how the backbone is read/written), `flags.md` (cross-workstream ledger).*

## What this project is
BIOLOOP is a 3-year cSBO (started 01/02/2024; UGent-coordinated, with VITO and AMS) building a decision-support framework to design and optimise biobased supply chains in Flanders — better matching fragmented biomass side streams to higher-value uses. The intended core is a model fed by a data layer characterising Flemish biomass streams (the "BioMobi" dataset).

## Why this charter exists — the reset
After ~18 months, founding assumptions did not hold, VITO's MooV platform did not deliver what the proposal promised, and staff turned over. The project has effectively semi-restarted. On the UGent side, prior work is treated as *salvageable input, not foundation*: almost everything is being revisited and rebuilt. The proposal's broad *goals* remain valid; its *methods, task breakdown, and timeline* are unreliable and not binding. **This charter, not the proposal, is the source of truth for what is being done now.**

## Goal
Produce, on the UGent side: (1) a clean, rigorously-sourced, extensible **data layer** (BioMobi) of the relevant biomass waste streams in Flanders and their characterisation; and (2) an in-house decision-support **model** — with its transport and process/application rule layers — built on that data, replacing reliance on MooV.

## Remit
Owner: you (solo for now).
- Build the BioMobi database from scratch (the data layer).
- Subsequently build the BIOLOOP model in-house — including its transport and process/application rule layers — with full design freedom over its structure.
- Solo for now; possible future collaborators are deliberately *not* designed for at this stage.
- Proposal tasks/deliverables (e.g. WP1 D1.x) are loose reference, not commitments; scope may evolve.

## Scope

**BioMobi — the database built first (a pure data layer)**
- In: the relevant Flemish biomass waste streams **plus their intrinsic characterisation** — chemical composition, volumes, physical characteristics, seasonality, and geographic location of supply.
- **Out: microbiological characterisation** (narrowed 2026-09-10). It was listed as in scope from the first draft of this charter and never acted on; the six microbiological parameters registered in the composition catalogue on 2026-09-09 were retired the next day, before any measurement referenced them. The `parameter.category` CHECK still admits `microbiological`, so reversing this is an `INSERT`, not a migration.
- Stream selection guided by the 80/20 principle (streams accounting for ~80% of volume). It is a **prioritisation sort, not a hard gate** — a stream below the line is not excluded, only not first.
- **Supply side of the agri-food chain only** (settled 2026-08-15, on the evidence of the candidate stream register). In: primary production (land and sea), the auction / producer-organisation layer, the processing industry, and retail & wholesale distribution. **Out: horeca, catering, and households**, and anything downstream of retail. The consequence is binding and not obvious: **a whole-chain total for Flanders is never usable**, because every one of them swallows an excluded stage — so BioMobi's volume side is built from stage-resolved figures upward, never from a national total downward. Enforced in `database/register/dictionaries/chain_L2.csv` (`in_scope` column).
- **Manure and OFMSW are excluded**, and that exclusion binds source extraction as well as the database — it removed ~23,4 Mton of 2021 animal side stream from the register in one stroke.
- BioMobi holds **facts only** — no constraints, rules, or transformations.
- Explicitly excluded (these are rules/transformations, not stream facts, and live in the model's rule layers): regulatory constraints (permitting, low-emission zones), transport feasibility, processing rules, demand-side specifications.

**The model and its rule layers — also your remit (later phase), separate from BioMobi**
- See "Model" below. The transport and process/application databases consume BioMobi data and form the basis of the model.

**Literature review (supporting, current phase)**
- (a) contextual understanding of comparable / partial prior work; (b) targeted gap-filling of BioMobi characterisation data not covered by existing databases.

**Out of scope**
- VITO's MooV platform.
- Other consortium work packages and partner-led (VITO / AMS) tasks, except where they hand off to or receive from this workstream.

## Model — intended architecture and progression
The model is **logistics-first**: transport feasibility is its primary concern. Three layers — a data layer, a rule/transformation layer, and the engine:
- **BioMobi (data).** Facts about streams and their characterisation; model-independent.
- **Transport + process/application (rules & transformations).** Separate databases that consume BioMobi data and form the basis of the model:
  - *Process / application* — one database of requirements/criteria and composition transformations. Applied to a biomass, it determines what is *technically* possible to make from it. A "process" is a middle step; an "application" is an endpoint — same object, different role.
  - *Transport* — screening rules: which streams/products satisfy the criteria of each transport mode, determining what is *logistically* possible.
- **The model (engine).** Its job grows in stages:
  - *Phase 1 — screening, no chaining.* For a single biomass: first screen all **technically** possible applications (apply each application's criteria to the biomass), then apply the **transport** check to see which of those are also **logistically** possible. Output: the applications that are both technically and logistically feasible for that biomass.
  - *Later — chaining & optimisation.* Cascading (one application's output feeding another) only becomes necessary with multiple applications and circularity. Once multiple biomasses, applications and circularity coincide, the model chains the individual steps and optimises across them.

Build philosophy: set up the individual steps (criteria, transformations, transport rules, single-biomass screening) first; layer chaining and optimisation on top once the system scales.

This factoring is deliberate: BioMobi stays a pure, reusable data layer (genuinely model-independent), while everything model-coupled lives in the rule layers.

*Key interface (settled):* BioMobi defines a single, fixed-shape **composition vector**. A process/application takes that vector, transforms the values, and returns a vector of the **same shape** — which is exactly what lets applications chain in a cascade. So BioMobi's composition schema is the canonical representation for both raw streams and process outputs/intermediates.

Progression (staged build):
1. Single biomass → single application, linear baseline (screen technically possible applications, then filter by transport feasibility).
2. In parallel, two self-contained extensions solved independently:
   a. Multiple biomasses — added logistical complexity.
   b. Multiple applications via cascading — added logistical + operational complexity; relies on the shared composition vector.
3. Join the two extensions into a combined model.
4. Circularity.
5. Collaboration.

*Note:* this re-bundles the proposal's feature-based shells (1.0 base → 1.1 circularity, where the proposal places cascading → 1.2 collaboration → 2.0 combined + multi-feedstock). The proposal is not binding; this build order is ours.

## Design principles & binding constraints
- **Clean separation of data and rules.** BioMobi captures facts; constraints, rules and transformations live only in the transport and process/application layers. This keeps BioMobi a reusable, model-independent asset.
- **Variable-resolution by design.** Available data will be uneven (e.g. monthly vs single-annual seasonality). The schema stores values at whatever resolution exists and records that resolution / basis explicitly per value; the model is built to accept heterogeneous granularity.
- **Rigour over completeness.** Standardised units and basis (e.g. fresh vs dry matter, moisture-corrected); a source recorded for every value; a deliberate controlled vocabulary for naming and aggregating streams.
- **Built to extend.** A relational structure designed so later phases and the separate rule layers link in without redesign.
- **Portable source of truth.** Project knowledge lives in one version-controlled git repo as a layered backbone: charter, state, protocol, and flags at root (tool-agnostic Markdown); schema as version-controlled SQL; one subfolder per workstream holding its own detailed, tool-flavoured record; and a single Obsidian vault at root (`vault/`) for cross-cutting prose notes. The record outlives any chat or app. See `protocol.md` for how the layers are read and written.

## Tooling (current decisions)
- **Database:** PostgreSQL with PostGIS (handles supply-side geography natively), hosted on **Supabase**; schema / data dictionary as version-controlled SQL, evolved forward via committed migrations (git is canonical, not the live instance); ingestion from public inventories via Python / pandas scripts.
- **Literature & notes:** Zotero (reference spine); Obsidian as the project notebook — a single, cross-cutting vault kept in-repo at root as `vault/` (it spans all workstreams, e.g. `vault/Database/`, `vault/Literature/`), with notes linked by citation key; literature-derived data values flow into the database carrying their citation key as provenance.
- **Backbone:** one git repo with a layered structure — `charter.md` / `state.md` / `protocol.md` / `flags.md` at root, plus `<workstream>/hub.md` per workstream and a root-level `vault/` (Obsidian) for cross-cutting prose notes (see `protocol.md`).
- **Execution surface & hand-offs:** sessions run in **Claude Code** on the repo, attaching the relevant MCP servers per workstream (Supabase for database; Zotero + Obsidian for literature). Each session reads the backbone at start and writes it back at end, committing directly — so hand-offs are automated file writes, not manual paste. *(This resolves the earlier open question of manual-vs-pipeline hand-off automation.)*

## Phases (high level)
1. **Foundational (current):** background literature review + build BioMobi (schema / data dictionary → harvest existing public inventories → gap-fill from literature).
2. **Model:** build the in-house model and its transport and process/application rule layers, following the staged progression above.
3. *Later (circularity, collaboration, case validation): to be scoped if/when they enter this workstream.*

## Success criteria
- A BioMobi data layer covering the ~80/20 of relevant Flemish streams — properly structured, standardised, fully sourced, extensible, and pure (facts only).
- An in-house model (with transport and process/application rule layers) that runs on BioMobi and supports the project's supply-chain design questions.
- A maintained backbone (charter + state + protocol + flags + per-workstream hubs) that lets separate sessions, and any future collaborator, orient quickly.
