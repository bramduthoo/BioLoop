# BIOLOOP — Backbone Protocol

*The rulebook. Defines how the backbone is read and written, and the two schemas that are standardised across all workstreams. Tool-agnostic and durable: this survives unchanged even if the execution surface (Claude Code, MCPs) is ever replaced.*
*Companion documents: `charter.md` (what/why), `state.md` (project dashboard), `flags.md` (cross-workstream ledger).*
*Last updated: 2026-07-14.*

---

## 1. What the backbone is

The project's memory lives in a durable, version-controlled git repo — **not** in any chat. A chat/session is a disposable reasoning surface: it reads the backbone to orient itself at the start and writes back to it at the end. The repo is the source of truth, the version history, and the backup, all at once.

The backbone is layered by *rate of change* and *reader*:

| File | Job | Changes | Read by |
|------|-----|---------|---------|
| `charter.md` | The constitution — scope, architecture, binding constraints | Rarely | Anyone orienting to the project |
| `state.md` | The project dashboard — phase, per-workstream rollup, project-level decisions & open questions | Every session (project-grain) | You (router), any session |
| `flags.md` | The cross-workstream ledger — routed items with a lifecycle | When a session raises/closes a flag | The workstream a flag is routed *to* |
| `protocol.md` (this file) | The rulebook — read/write contract + schemas | Rarely | Any session, once |
| `<workstream>/hub.md` | A workstream's working memory — standard status header + **local** body | Every session in that workstream | Sessions in that workstream |
| `CLAUDE.md` (root + per-folder) | Enforcement glue — makes this contract automatic in Claude Code | Rarely | Claude Code, automatically |

The flow: **charter orients · state dashboards · flags route · protocol governs · CLAUDE enforces · hubs hold the detail.**

Design tenet: detail lives *low* (in hubs and deliverables); only what other workstreams or the project need rises. Nothing rises automatically except the status rollup (§3). Everything else is *routed by significance* (§4).

---

## 2. The read/write contract

Every session, in every workstream, follows the same contract.

**At session start (brief down) — read:**
1. `charter.md` — orient to scope and constraints (cheap; skim if already known).
2. `state.md` — current phase and project-level state.
3. `flags.md`, filtered to `to: <this workstream>` and `status: open` or `acked` — inherited work.
4. `<this workstream>/hub.md` — the local working memory, starting with its status header.
5. `<this workstream>/CLAUDE.md` — local conventions, if present.

The session's objective is set by you when you open it (often "resolve the open flag" or "the next-action from the hub").

**At session end (report up) — write:**
1. Update the hub's **status header** (mechanical — see §3).
2. For each decision made, question opened, or artifact produced, apply the **routing rule** (§4) and write it to the correct file.
3. Update `flags.md`: raise any new cross-workstream flags; flip any you resolved to `resolved` with a note (§5).
4. Commit, with a message naming the workstream and objective.

**Your role (the router):** review the git diff of a session's report. The diff *is* the curation step — it's where you catch a decision that was filed locally but should have graduated to `state.md`, or a flag that should have been raised. The heavy manual transfer is gone; the judgment stays, applied to a diff rather than by retyping.

---

## 3. Standardised schema #1 — the status block

Every `hub.md` begins with this exact header. It is the only standardised part of a hub; everything below it is local. Because the fields are identical everywhere, `state.md`'s per-workstream rollup is just each hub's top line, compressed.

**Copy this block into `<workstream>/hub.md` when a phase starts, then fill it in:**

```markdown
## Status
- **Workstream:** <name>
- **Current objective:** <one line — or "between sessions">
- **Last session:** <YYYY-MM-DD> — <one-line outcome>
- **Progress:**
  - done: <…>
  - in progress: <…>
  - not started: <…>
- **Key artifacts:** <path — one line each of what it is>
- **Next action:** <one line>

<!-- Everything below this line is LOCAL to this workstream.
     Design the body when the phase starts, against real work — do not pre-structure it. -->
```

Field notes:
- **Current objective** — the single objective of the session in progress, or "between sessions" when idle. A workstream is never chasing a vague finish line; each session has one crisp objective.
- **Progress** — deliberately coarse (done / in-progress / not-started). Fine detail belongs in the local body, not here.
- **Next action** — what the *next* session should open on. This is what makes a cold restart instant.

The body beneath is intentionally unspecified. It is shaped per workstream, in-phase (e.g. the database's is a schema changelog + per-source load status; literature's is a reading log + synthesis index + gap list; modelling's is architecture-decision records + module status). Do not template the body here.

---

## 4. The routing rule — where does a decision or open question go?

Status rolls up mechanically (§3). Decisions and open questions do **not** auto-roll — at session end, ask one question per item: **who needs this?**

- **Only this workstream needs it** (e.g. "harvest OVAM before ILVO") → stays in the hub body. Never rises.
- **The whole project needs it, or it defines an interface others depend on** (e.g. "composition is one fixed-shape vector") → `state.md` (decision log or open-questions list).
- **Another *specific* workstream needs to act on it** → it is a **flag**, not a note. Raise it in `flags.md` (§5). A cross-workstream open question that blocks someone is a flag, not a `state.md` line.
- **A permanent constraint that reshapes scope** → `charter.md`. Rare and deliberate.

This routing is the one piece of judgment the system deliberately keeps human-in-the-loop (via your diff review).

---

## 5. Standardised schema #2 — the flag object

A flag is not a note; it is a small stateful object with a lifecycle. That lifecycle is what makes cross-workstream coupling actually work: no workstream reaches into another — it leaves a flag, and the ledger routes it.

**Fields:**
- `id` — F-001, F-002, … (monotonic, never reused)
- `date` — when raised
- `from → to` — source workstream → target workstream (the routing)
- `summary` — one line
- `detail` — a pointer to where full context lives (e.g. `literature/hub.md#vocab-gaps`), not the context itself
- `blocking?` — yes / no (does the target's next objective depend on it?)
- `status` — `open` → `acked` → `resolved`
- `resolution` — one line + date, filled when closed

**Lifecycle:**
1. A session in the *source* workstream raises the flag (appends a row to `flags.md`).
2. The *target* workstream's next brief filters `flags.md` for `to: <target>, status: open/acked`. Blocking flags surface first.
3. A target session acts on it and flips it to `resolved` with a note. It stays in the ledger as history — resolved, not deleted.

**Example:** literature finds a high-volume stream missing from the controlled vocabulary →
`F-003 · 2026-07-18 · lit→db · brewer's spent grain missing from controlled vocab · literature/hub.md#vocab-gaps · blocking: no · open`
The next database session picks it up, adds the category, and closes it:
`… · resolved (2026-07-25): added to vocab under EWC 02 07 04`.

See `flags.md` for the live ledger and its exact table format.

---

## 6. What is deliberately *not* here

- **No standardised decision record.** Project-level decisions live in `state.md`; local ones stay in each hub. If cross-workstream decision-tracking ever becomes a real friction, revisit — but do not build the channel speculatively.
- **No standardised hub body.** See §3. Locality is the point.
- **No hand-off automation spec beyond "the session writes files and commits."** The execution glue is in `CLAUDE.md`, kept separate so this protocol stays portable.
