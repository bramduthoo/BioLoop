# CLAUDE.md — BIOLOOP repo (root)

This repo is the durable backbone and working record of the BIOLOOP UGent workstream. It is the source of truth — the memory lives here, not in any chat. You (a Claude Code session) are a disposable reasoning surface: orient from the backbone at the start, write back to it at the end.

**Read `protocol.md` once — it is the rulebook.** This file only makes that rulebook automatic.

## What this repo is
- A single git repo. Project-level backbone at root; one subfolder per workstream (`database/`, `literature/`, `modelling/`).
- Git is canonical. The version history is the record. Prefer forward-moving, committed changes over ad-hoc edits to any live external store (e.g. the Supabase instance — evolve it via committed migrations, never let the live DB drift as the sole truth).

## Which workstream am I in?
Determined by the subfolder in focus / the objective you were given. Attach the right tools for that workstream (the per-folder `CLAUDE.md` says which):
- `database/` — Supabase MCP; schema + migrations + ingestion here.
- `literature/` — Zotero + Obsidian MCPs. The Obsidian vault is project-wide at root `vault/` (cross-cutting notes; literature's own live in `vault/Literature/`), not under `literature/`. Since the vault is in-repo markdown, any session can read its notes as plain files; the Obsidian MCP is only needed for richer operations (backlinks, tags, graph).
- `modelling/` — repo only; model code + design notes here.

## Session start (do this before working)
1. Read `charter.md` — scope and binding constraints (skim if already familiar).
2. Read `state.md` — current phase and project-level state.
3. Read `flags.md` — filter to `to: <this workstream>`, `status: open`/`acked`. Blocking flags first.
4. Read `<this workstream>/hub.md` — start with its Status header.
5. Read `<this workstream>/CLAUDE.md` — local conventions.
Then confirm the session's single objective with the user before executing.

## Session end (do this before the session closes)
Per `protocol.md`:
1. Update the hub's **Status block** (mechanical — §3 of protocol).
2. Route each decision / open question / artifact by the **routing rule** (§4): local → hub body; project-level or interface → `state.md`; needs another workstream to act → a **flag** in `flags.md`; scope-reshaping → `charter.md`.
3. Update `flags.md` — raise new flags; flip resolved ones with a note (§5).
4. `git add` + commit. Message format: `<workstream>: <objective> — <one-line outcome>`.

## Session hygiene
- When a session starts feeling long, or the objective shifts, **stop**: write the report (above), commit, and have the user open a fresh session seeded from the updated backbone. Long chats degrade; short well-briefed ones don't.
- Keep detail *low*. Only what other workstreams or the project need rises to `state.md` or `flags.md`. Do not bloat the project dashboard with workstream internals.
- Do not invent structure speculatively — especially not hub bodies for workstreams that haven't started.
