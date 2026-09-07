# `streams/` — conventions and decisions for the selection → SQL transfer

*Local rules for this folder only. Read with, not instead of, `database/CLAUDE.md` and the root
`protocol.md`. Anything here that turns out to bind **every** database session belongs one level
up; anything that binds only this transfer stays here.*
*Last updated: 2026-09-07.*

## The one rule that governs this folder

**The register is the truth; this folder is a transfer.** Its input is the selection the register
already produced and a human already reviewed. This folder does not re-open that selection, does
not re-rank it, and — above all — **does not recompute its numbers**.

A first version of the loader did compute per-material tonnages of its own. It disagreed with
`register/tools/derive.js` on Aardappel — 429.871 t against the pipeline's 548.305 t, because
OVAM's *voedselverlies* and *nevenstroom* are additive components there, not alternatives. The
rival derivation was deleted rather than reconciled. **One derivation, and it lives in the
register.** Carry its figure, cite the claim, compute nothing.

## The grain decision — why 21 streams and not 13

The selection ranks **commodities**; BioMobi stores **materials**. Four of the 13 selected
commodities bundle materials with nothing in common but a crop name, and the register already
measures those halves as separate claims, so they enter as separate streams:

| commodity (rank) | registered as |
|---|---|
| Aardappel (3) | `aardappel-loof` · `aardappel-primair` (the tuber) · `aardappel-industrie` (Prodcom 103113) |
| Suikerbiet (4) | `suikerbiet-loof` · `suikerbiet-pulp` · `suikerbiet-primair` (the beet) |
| Kool- en raapzaad (2) | `raapzaad-stro` (VL) · `raapzaad-schroot` (BE crush) |
| Bloemkool (9) | `bloemkool-loof` · `bloemkool-harten` · `bloemkool-primair` |
| Spruiten (13) | `spruiten-stengelmassa` · `spruiten-primair` |

Two corollaries, both load-bearing:

- **Identity is the material, never the chain stage.** Rejected cauliflower at the auction and at
  the processor is *one* stream carrying two `bioloop-keten` terms — that is what the faceted
  bridge table is for. Do not split a stream because a source reports it at two stages.
- **The split figures are not summable.** The register's 80/20 arithmetic runs at commodity level
  (the largest figure any one source gives a commodity), so adding up split rows produces a
  quantity no source supports. Each manifest row therefore carries its commodity's authoritative
  rank and figure *beside* its own largest single claim, and the loader totals nothing.

A side effect worth knowing: this dissolves the register's **G-08** "incompatible quantities"
problem. *Oogstresten* and *voedselreststromen* of one crop, with spreads up to 50,5×, were never
contradictory measurements — they were measurements of **different materials**, and they now sit
in different rows.

## What is judgement here, and therefore open to challenge

**Four streams rest on a reading, not on a source's own wording:** `aardappel-primair`,
`suikerbiet-primair`, `bloemkool-primair`, `spruiten-primair`. Their claims are OVAM/ILVO figures
for a crop's *voedselverliezen* and *nevenstromen*, read here as "the crop itself, rejected or
unharvested" — a distinct material from that crop's field residue. The reading is what makes the
G-08 spreads resolve, but no source says it in those words. **Worth a reviewer's eye before any
volume attaches to these four.**

The other 17 rows track a name a source actually used: 9 rest on claims the source itself marked
as a fraction (L5 — `stro`, `loof`, `pulp`, `harten`, `stengelmassa`), 8 on L4 claims that already
name a material (`Sojaschroot`, `Zemelen`, `Dierlijk vet`, …).

**Names are cheap to change now and expensive later.** `stream.code` is the primary key every fact
row will reference. The FKs are `ON UPDATE CASCADE`, so a rename is mechanically safe while no
measurements exist — that stops being comfortable once phase 3 hangs composition off these codes.

## The manifest and its gate

`crosswalks/register_streams.csv` — `;`-delimited, UTF-8 BOM (Belgian Excel). One row per stream,
carrying the register claim ids it rests on, its commodity's rank and figure, its own largest
claim, the facet values, and a human `DECISION`.

- **The loader exits non-zero, naming every offending row, while any `DECISION` is blank or is not
  `include`/`exclude`.** It did refuse the first dry run with 21 blanks.
- **The gate is about the *split*, not about the selection.** The selection was reviewed and closed
  when 2b closed; re-approving it here would be ceremony. What is new — and what the column
  actually gates — is the 13 → 21 material split and the four judgement rows above.
- **On 2026-09-07 the session filled all 21 cells with `include`**, on the reviewer's instruction
  in conversation, not by the reviewer typing them. Recorded here because the difference matters
  if anyone later reads the file as evidence of a per-row human review.

**The manifest is authored, not generated**, so the loader re-checks it against
`../register/build/streams.json` on every run: each claim must exist, sit under the L4 the manifest
names, be used by exactly one stream, and match the recorded largest figure. A retired or
re-levelled claim fails the load instead of drifting silently. `--skip-register-check` exists for
the case where the register's `build/` has not been generated; do not use it to get past a real
disagreement.

## Idempotency — what this loader owns

Its namespace is **the set of stream codes the manifest names, inside the two schemes it declares**
(`bioloop-tak`, `bioloop-keten`). Each run rebuilds exactly those `stream_classification` links in
one transaction, so flipping a `DECISION` to `exclude` withdraws that stream's classifications
rather than orphaning them.

**It never deletes a `stream` row**, even one flipped to `exclude` — `stream_classification`
cascades on stream delete, and an ingestion script must not be able to destroy classification work.
An excluded stream keeps its row, loses its links, and is reported.

Verified 2026-09-07 on the local stack: rebuild from migrations, then three consecutive loads
holding at 21 / 7 / 44; `spruiten-primair` flipped to `exclude` dropped 2 links and kept its row.

## The facets

Both are the register's own binding vocabularies, not schemes invented here:

- `bioloop-tak` — commodity branch, the register's L2 (`../register/dictionaries/commodity_hierarchy.md`).
  akkerbouw 13 · tuinbouw 5 · vee 2 · Varia 1.
- `bioloop-keten` — chain stage (`../register/dictionaries/chain_L2.csv`).
  primaire productie 12 · voedingsindustrie 10 · PO's/veilingen 1.

**EWC is untouched** and remains the phase-4 question. These two are a commodity ladder plus a
chain-stage axis; whatever waste-code scheme is eventually chosen must reconcile with them, and
adding it is `INSERT`s into `classification_scheme` / `classification_term`, not a migration.

## What deliberately does not load here

`supply_observation`. A volume row needs `source_key NOT NULL`, and all eight archived register
PDFs still carry a blank `citation_key` (**F-002**); 687 of the register's 801 claims are also
still `awaiting verification`. The claim → stream mapping that load will need is already in the
manifest's `claim_ids` column, so this folder is where that work continues — but it is a separate
loader against `supply_observation`, not an extension of this one.
