"""Propose (and maintain) the aggregate-coverage registry for the stream overview.

An AGGREGAAT row is not a commodity: it claims "the total of <these rows> is X". The overview
needs to know *which* rows, so it can use the figure as a denominator instead of a summand.
This script writes one proposal per aggregate claim into

    register/crosswalks/aggregate_coverage.csv

which is a HUMAN-GATED file: nothing is used until its `DECISION` column says so.

Idempotent. Re-running preserves every existing row verbatim (your edits and decisions) and
only appends proposals for aggregate claims not yet listed, so it stays usable as new sources
are extracted.

    database/.venv/Scripts/python.exe database/register/make_aggregate_coverage.py
"""
import csv, io, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "streams_export.csv"
OUT = HERE / "crosswalks" / "aggregate_coverage.csv"
SEP = " ¦ "                                    # the path separator derive.js builds
PREFIX = "AGGREGAAT"

COLUMNS = ["claim_id", "source_short", "reference_year", "chain_L2", "quantity_type",
           "volume_t_per_yr", "name", "totals_level", "parent_row", "commodity_coverage",
           "stage_coverage", "treatment", "allocatable", "note", "DECISION"]

# the four stages OVAM's "primaire sector" spans (4 of the 6 in-scope stages)
PRIM4 = "Primaire productie,Producentenorganisaties/veilingen,Visserij,Visveilingen"
LEVEL_BELOW = {"role": "L2", "L2": "L3", "L3": "L4", "L4": "L5"}

# --- per-claim judgement -----------------------------------------------------------------
# Only the rows the default rule below cannot get right. Everything else is derived from the
# row's own placement. `parent_row` values naming Varia are created by varia_reclass.csv; until
# that lands the parent row does not exist and the overview shows the aggregate as unallocated.
VARIA = "Varia"
VARIA_OILS = "Varia" + SEP + "Olien, vetten"
VARIA_DRINK = "Varia" + SEP + "Dranken"
VARIA_CHOCO = "Varia" + SEP + "Chocolade"
FEDIOL = "Belgisch FEDIOL-cijfer; same figure as {} recorded under Oliehoudende gewassen"

# --- coverage lists after the 2026-08-31 L3 split -----------------------------------------
# Only Chocolade and Zetmeel hold captured rows. The other halves of the two NACE lumps are
# named here so a reviewer can see what an aggregate includes but the register does not hold
# (protocol v2.3: an aggregate that includes an uncaptured component must say so).
SUGAR_SET = "Chocolade,Suiker"
SUGAR_OVAM = "Chocolade,Suiker,Bereide maaltijden"
MILL_SET = "Bakkerij,Zetmeel en zetmeelproducten,Deegwaren,Maalderijproducten"
MILL_OVAM = "Zetmeel en zetmeelproducten,Deegwaren,Maalderijproducten,Dieetvoeding"
UNCAP = "; includes components the register does not capture ({}) - the coverage % is a floor"

# The retail channel halves. They are the retail chain stage split by collection channel, not
# a commodity, and each pair sums exactly to a stage total the source ALSO prints standalone.
# They keep `full` coverage so they stay allocatable; derive.js marks the merged pair as a
# RESTATEMENT of that total and leaves it out of the mean, so the decomposition stays visible
# without being weighted twice against a genuine variant.
CHAN = ("retail chain stage split by collection channel; sums with {} to {} ({:,} t), which the "
        "source also prints standalone - derive.js marks the merged pair as a restatement of it "
        "rather than a rival measurement")

OVERRIDE = {
    # --- OVAM, aggregates spanning several chain stages: never eligible for the Total column
    "C-002": dict(stage_coverage="Primaire productie,Producentenorganisaties/veilingen",
                  note="EU-definitie; 2 of 6 in-scope stages"),
    "C-004": dict(stage_coverage=PRIM4, note="primaire sector = 4 of 6 in-scope stages"),
    "C-210": dict(stage_coverage=PRIM4, note="primaire sector = 4 of 6 in-scope stages"),
    "C-217": dict(stage_coverage="Primaire productie,Visserij",
                  note="landbouw + visserij = 2 of 6 in-scope stages"),
    # --- collection-route halves: these DO sum (to C-004), so they are not competing variants
    "C-111": dict(stage_coverage=PRIM4, treatment="component_set",
                  note="route half (ingezameld); sums with C-112 - together they make C-004's voedselverlies part"),
    "C-112": dict(stage_coverage=PRIM4, treatment="component_set",
                  note="route half (andere bestemming); sums with C-111"),
    "C-113": dict(stage_coverage=PRIM4, treatment="component_set",
                  note="route half (ingezameld); sums with C-114"),
    "C-114": dict(stage_coverage=PRIM4, treatment="component_set",
                  note="route half (andere bestemming); sums with C-113"),
    # --- MONBIO, commodity subsets at role level: plantaardig = 2 of the L2 groups
    "C-218": dict(commodity_coverage="Plantaardig - akkerbouw,Plantaardig - tuinbouw",
                  note="plantaardige landbouw spans 2 L2 groups - subset, not a full L2 total"),
    "C-238": dict(commodity_coverage="Plantaardig - akkerbouw,Plantaardig - tuinbouw",
                  note="plantaardige landbouw spans 2 L2 groups - subset, not a full L2 total"),
    "C-399": dict(commodity_coverage="Plantaardig - akkerbouw,Plantaardig - tuinbouw",
                  note="plantaardige landbouw spans 2 L2 groups - subset, not a full L2 total"),
    "C-419": dict(commodity_coverage="Plantaardig - akkerbouw,Plantaardig - tuinbouw",
                  note="plantaardige landbouw spans 2 L2 groups - subset, not a full L2 total"),
    # --- the PO's aanvoer total covers only the 10 biggest crops, so it is a subset, not a full
    # L3 total. The source names them in Figuur 6; two of the ten (komkommer, kropsla) are printed
    # in pieces and were not convertible, so the captured children can never reach 100%.
    "C-086": dict(commodity_coverage="de 10 belangrijkste groenten en fruit (Figuur 6)",
                  note="subset: 'som van de 10 belangrijkste', not every crop in the L3 group; "
                       "komkommer and kropsla are reported in pieces and are not captured"),
    # --- MONBIO's per-gewasgroep residue totals (promoted 2026-09-01). Most total the L4 rows
    # under their own L3. Two do not: "Suiker- en zetmeelgewassen" is MONBIO's own crop group and
    # its fractions sit under the OVAM-derived subgroups, so it is a cross-partition SUBSET at L3.
    "C-240": dict(totals_level="L3", parent_row="Plantaardig - akkerbouw",
                  commodity_coverage="Aardappelen en knolgewassen,Suikerbieten en nijverheidsgewassen",
                  note="= C-247 aardappelloof + C-248 suikerbietenloof, exactly; MONBIO's gewasgroep "
                       "cuts across the OVAM subgroups so this is a subset, not a full L3 total"),
    "C-421": dict(totals_level="L3", parent_row="Plantaardig - akkerbouw",
                  commodity_coverage="Aardappelen en knolgewassen,Suikerbieten en nijverheidsgewassen",
                  note="as C-240, MONBIO 3.0 edition"),
    # --- placements the reviewer set by hand in the round-2 review (2026-09-01)
    "C-355": dict(parent_row=VARIA + SEP + "Zetmeel en zetmeelproducten", totals_level="L4",
                  note="totals the L4 starch products beneath (reviewer, round 2)"),
    "C-546": dict(parent_row=VARIA + SEP + "Zetmeel en zetmeelproducten", totals_level="L4",
                  note="as C-355, MONBIO 3.0 edition"),
    "C-356": dict(parent_row=VARIA + SEP + "Suiker", totals_level="L4",
                  note="glucose/fructose/invertsuiker are sugars, not starch (reviewer, round 2)"),
    "C-547": dict(parent_row=VARIA + SEP + "Suiker", totals_level="L4",
                  note="as C-356, MONBIO 3.0 edition"),
    "C-365": dict(parent_row=VARIA_CHOCO, totals_level="L4",
                  note="aggregate within L3 Chocolade over the cacao products (reviewer, round 2)"),
    "C-558": dict(parent_row=VARIA_CHOCO, totals_level="L4",
                  note="as C-365, MONBIO 3.0 edition"),
    # --- MONBIO, definition variants of the same veeteelt total
    "C-216": dict(note="variant of C-264: excl. geiten- en schapenmelk, incl. paarden-, schapen- en geitenvlees"),
    "C-264": dict(note="variant of C-216: incl. geiten- en schapenmelk"),
    # --- MONBIO NACE processing subsectors: parents that varia_reclass.csv creates
    "C-279": dict(parent_row=VARIA_OILS, totals_level="L4", note=FEDIOL.format("C-329")),
    "C-280": dict(parent_row=VARIA_OILS, totals_level="L4", note=FEDIOL.format("C-335")),
    "C-464": dict(parent_row=VARIA_OILS, totals_level="L4", note=FEDIOL.format("C-518")),
    "C-465": dict(parent_row=VARIA_OILS, totals_level="L4", note=FEDIOL.format("C-524")),
    # --- NACE 10.6/10.7: spans Bakkerij + Zetmeel (captured) and Deegwaren + Maalderij (not)
    "C-283": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_SET,
                  note="NACE 10.6/10.7 spans 4 Varia subgroups - subset"
                       + UNCAP.format("Deegwaren, Maalderijproducten")),
    "C-284": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_SET,
                  note="NACE 10.6/10.7 spans 4 Varia subgroups - subset"
                       + UNCAP.format("Deegwaren, Maalderijproducten")),
    "C-468": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_SET,
                  note="NACE 10.6/10.7 spans 4 Varia subgroups - subset"
                       + UNCAP.format("Deegwaren, Maalderijproducten")),
    "C-469": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_SET,
                  note="NACE 10.6/10.7 spans 4 Varia subgroups - subset"
                       + UNCAP.format("Deegwaren, Maalderijproducten")),
    # --- NACE 10.8 suiker en chocolade: only Chocolade is captured
    "C-285": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_SET,
                  note="NACE 10.8 covers sugar and chocolate" + UNCAP.format("Suiker")),
    "C-286": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_SET,
                  note="NACE 10.8 covers sugar and chocolate" + UNCAP.format("Suiker")),
    "C-470": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_SET,
                  note="NACE 10.8 covers sugar and chocolate" + UNCAP.format("Suiker")),
    "C-471": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_SET,
                  note="NACE 10.8 covers sugar and chocolate" + UNCAP.format("Suiker")),
    # --- the OVAM subsector lumps, promoted to aggregates on the reviewer's instruction
    "C-097": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_OVAM,
                  note="OVAM subsector lump" + UNCAP.format("Suiker, Bereide maaltijden")),
    "C-198": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=SUGAR_OVAM,
                  note="OVAM subsector lump" + UNCAP.format("Suiker, Bereide maaltijden")),
    "C-099": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_OVAM,
                  note="OVAM subsector lump"
                       + UNCAP.format("Deegwaren, Maalderijproducten, Dieetvoeding")),
    "C-199": dict(parent_row=VARIA, totals_level="L3", commodity_coverage=MILL_OVAM,
                  note="OVAM subsector lump"
                       + UNCAP.format("Deegwaren, Maalderijproducten, Dieetvoeding")),
    # --- the Flemish chocolate estimate totals the Prodcom chocolate rows beneath it
    "C-383": dict(parent_row=VARIA_CHOCO, totals_level="L4",
                  note="Vlaamse chocoladeproductie (schatting); totals the L4 chocolate rows"),
    "C-576": dict(parent_row=VARIA_CHOCO, totals_level="L4",
                  note="Vlaamse chocoladeproductie (schatting); totals the L4 chocolate rows"),
    "C-287": dict(parent_row=VARIA_DRINK, totals_level="L4", note="totals the Prodcom products beneath"),
    "C-472": dict(parent_row=VARIA_DRINK, totals_level="L4", note="totals the Prodcom products beneath"),
    # --- retail collection channels: each pair sums to the stage total already registered
    "C-103": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-104", "C-105", 132082)),
    "C-104": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-103", "C-105", 132082)),
    "C-106": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-107", "C-108", 59849)),
    "C-107": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-106", "C-108", 59849)),
    "C-203": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-204", "C-205", 85802)),
    "C-204": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-203", "C-205", 85802)),
    "C-208": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-209", "C-206", 37381)),
    "C-209": dict(totals_level="L2", parent_row="Reststroom", treatment="component_set", note=CHAN.format("C-208", "C-206", 37381)),
    # --- OVAM's processing-subsector rows that are really a total of commodity groups the tree
    # already holds (promoted to aggregates by varia_reclass.csv). Their entries live under two
    # different L2 parents, so no single row covers them: the allocation rule sends them to the
    # unallocated part, which is where they belong.
    "C-094": dict(totals_level="L3", parent_row="Reststroom",
                  commodity_coverage="Aardappelen en knolgewassen,Groenten openlucht,Groenten beschut,Groenten,Fruit",
                  note="totals 3 L3 entries under 2 different L2 parents - unallocatable by design"),
    "C-195": dict(totals_level="L3", parent_row="Reststroom",
                  commodity_coverage="Aardappelen en knolgewassen,Groenten openlucht,Groenten beschut,Groenten,Fruit",
                  note="totals 3 L3 entries under 2 different L2 parents - unallocatable by design"),
    "C-098": dict(totals_level="L3", parent_row="Reststroom", commodity_coverage="Vlees,Vis",
                  note="totals meat + fish, which sit under 2 different L2 parents - unallocatable by design"),
    "C-201": dict(totals_level="L3", parent_row="Reststroom", commodity_coverage="Vlees,Vis",
                  note="totals meat + fish, which sit under 2 different L2 parents - unallocatable by design"),
    # --- the Belgian oil figures recorded a second time under the crop subgroup
    "C-329": dict(note="Belgian FEDIOL figure; same value as C-279 - excluding one of the pair avoids double counting"),
    "C-335": dict(note="Belgian FEDIOL figure; same value as C-280 - excluding one of the pair avoids double counting"),
    "C-518": dict(note="Belgian FEDIOL figure; same value as C-464 - excluding one of the pair avoids double counting"),
    "C-524": dict(note="Belgian FEDIOL figure; same value as C-465 - excluding one of the pair avoids double counting"),
}


# --- residual nomenclature buckets ---------------------------------------------------------
# A statistical nomenclature always ends its branches with a leftover class: "Andere ...",
# "... en andere ...", "van alle soorten", "n.e.g.". Such a row is a real volume but it is not a
# named stream and it is not the total of its siblings either - it is whatever the nomenclature
# did not name. It therefore cannot be placed under one parent at one level, which is exactly the
# condition the allocation rule uses: it goes to the UNALLOCATED band, where it stays visible and
# usable for interpretation but is never compared and never summed.
#
# This is a rule rather than a claim list on purpose: every new Prodcom/NACE source brings its own
# residual classes, and they should be caught without another review round.
# Assembled from named signals so each one can be read, tested and extended on its own.
COLLECTION_SIGNALS = [
    r"\ben andere\b",                                     # en andere ...
    r"\bof andere\b",                                     # of andere ...
    r"\bvan andere\b",                                    # van andere ...
    r"\buit andere\b",                                    # uit andere ... (added 2026-09-03: the
    #   missing preposition let 'Meel/schroot uit ANDERE oliehoudende zaden' (C-334, C-523,
    #   68.000 t each) sit as a plain L3 component - neither selectable nor an aggregate, so its
    #   mass appeared nowhere at all. Prepositions are cheap; enumerate them.)
    r"^\s*(?:AGGREGAAT\s*-\s*)?ander(?:e)?\b",            # the name starts with 'Andere'
    r"\balle soorten\b",                                  # van alle soorten
    r"n\.e\.g\.",                                         # n.e.g.
    r"\bop andere wijze\b",                               # op andere wijze
    r"enz\.",                                             # ..., enz.
    r"\ben ander \w+",                                    # en ander <woord>
    r"(?:\w+, ){2,}",                                     # three or more comma-separated items
    r"\w+-, \w+-,",                                       # 'Rund-, schapen-, geiten- of varkensvet'
    r"\ben (?:noten|eigeel|afvallen|wrongel)\b",          # 'X en noten/eigeel/afvallen/wrongel'
    r"\b(?:niet-)?eetbare (?:ruwe )?slachtafvallen\b",    # a whole offal category
    r"\ben afvallen van\b",                               # 'X en afvallen van Y'
]
COLLECTION_RE = re.compile("|".join(COLLECTION_SIGNALS), re.I)

# An explicit per-claim placement in OVERRIDE always beats the pattern below: a name can look
# like a residual class and still be a genuine, placeable aggregate ("Zetmeel, inuline, tarwegluten,
# dextrine en ander gewijzigd zetmeel" totals real L4 rows under Zetmeel). Keeping that as a
# property of OVERRIDE rather than a second list means there is one place to record a judgement.


# A row that calls itself a *totaal* is a real total of its siblings, whatever else its name
# contains - "Eetbare slachtafvallen, totaal" is the offal total, not a leftover class.
TOTAL_RE = re.compile(r"\btotaal\b|\btotale\b", re.I)


# A bundled label does not always mean a residual class. Reviewer rule, 2026-09-03:
# where the bundled items ARISE TOGETHER and cannot be separated in practice, the row is one real
# stream and belongs at L4 - even though the label reads like a leftover class. That is a physical
# fact about the material, not something derivable from the string, so it is recorded per claim.
# Rule 2 still holds where the bundle is a STATISTICAL leftover ("Andere ...", "van alle soorten").
#
# This is deliberately NOT the `PLACED_BY_REVIEWER` list removed on 2026-09-01. That one was
# redundant, because an explicit OVERRIDE entry already said the same thing for an aggregate.
# These claims are COMPONENTS: they have no registry line, so OVERRIDE cannot carry the judgement
# and there is nowhere else to put it. Do not delete it as overfitting without reading
# crosswalks/GAP_DECISIONS.csv first.
PHYSICAL_BUNDLE = {
    "C-297": "Prodcom 101150 is a named product - animal fat - not a species leftover (GAP-2)",
    "C-482": "Prodcom 101150 is a named product - animal fat - not a species leftover (GAP-2)",
    "C-358": "zemelen en slijpsel leave the mill together (GAP-4)",
    "C-549": "zemelen en slijpsel leave the mill together (GAP-4)",
    "C-357": "gries en griesmeel are one milling fraction (GAP-4)",
    "C-548": "gries en griesmeel are one milling fraction (GAP-4)",
    "C-397": "bostel en branderijafval are collected as one stream (GAP-5)",
    "C-590": "bostel en branderijafval are collected as one stream (GAP-5)",
    # FIX_LIST F1/F2, reviewer 2026-09-04. Both are collected and sold as one material even though
    # the Prodcom label enumerates species; the per-species split is a DATA gap (G-04), not a
    # placement one, so the bundles are streams and the split stays open.
    "C-298": "Prodcom 101160 - non-edible raw offal is rendered as one stream (F1)",
    "C-483": "Prodcom 101160 - non-edible raw offal is rendered as one stream (F1)",
    "C-295": "edible red-meat offal is traded as one stream; the species split is G-04 (F2)",
    "C-480": "edible red-meat offal is traded as one stream; the species split is G-04 (F2)",
}


def is_collection(name, claim_id=None):
    """True when the name is a residual class of the nomenclature rather than a named stream."""
    if claim_id and claim_id in PHYSICAL_BUNDLE:
        return False
    name = name or ""
    if TOTAL_RE.search(name):
        return False
    return bool(COLLECTION_RE.search(name))


def propose(r):
    """Default rule: an aggregate totals the level below the deepest level it names itself."""
    role = r["L1_role"].strip()
    if r["L2_commodity_group"].strip() == "Aggregaat":       # a whole-stage total, all commodities
        parent, anchor_level = role, "role"
    else:
        parts = [role]
        anchor_level = "role"
        for col, lvl in (("L2_commodity_group", "L2"), ("L3_commodity_subgroup", "L3"),
                         ("L4_ingredient", "L4")):
            if r[col].strip():
                parts.append(r[col].strip())
                anchor_level = lvl
        parent = SEP.join(parts)
    row = dict(
        claim_id=r["claim_id"], source_short=r["source_short"], reference_year=r["reference_year"],
        chain_L2=r["chain_L2"], quantity_type=r["quantity_type"],
        volume_t_per_yr=r["volume_t_per_yr"], name=r["stream_name_NL"],
        totals_level=LEVEL_BELOW[anchor_level], parent_row=parent,
        commodity_coverage="full", stage_coverage=r["chain_L2"],
        treatment="variant", allocatable="yes", note="", DECISION="",
    )
    if is_collection(r["stream_name_NL"], r["claim_id"]) and r["claim_id"] not in OVERRIDE:
        row.update(allocatable="no", commodity_coverage="residual nomenclature class",
                   note="a leftover class of the nomenclature ('Andere ...', 'n.e.g.', "
                        "'van alle soorten'): a real volume, but not a named stream and not the "
                        "total of its siblings - it cannot be placed under one parent at one "
                        "level, so it goes to the unallocated band")
    row.update(OVERRIDE.get(r["claim_id"], {}))
    # an override may name the parent from L2 down ("Varia ¦ Dranken"); paths start at the role
    if not row["parent_row"].split(SEP)[0] in ("Reststroom", "Productievolume"):
        row["parent_row"] = role + SEP + row["parent_row"]
    return row


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC.name} - run prep/export first")
    rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig"), delimiter=";"))
    aggregates = [r for r in rows if r["stream_name_NL"].strip().upper().startswith(PREFIX)]

    existing, order = {}, []
    if OUT.exists():
        for r in csv.DictReader(io.open(OUT, encoding="utf-8-sig"), delimiter=";"):
            existing[r["claim_id"]] = r
            order.append(r["claim_id"])

    # --refresh re-proposes the PLACEMENT of every row (levels, parents, coverage, notes) while
    # carrying each reviewer's DECISION forward untouched. Needed whenever the commodity tree
    # moves under the registry - a reclassification renames the very parent rows it points at,
    # and a silently stale parent_row sends a good aggregate to the unallocated band.
    refresh = "--refresh" in sys.argv
    added = []
    if refresh:
        out = []
        for r in aggregates:
            row = propose(r)
            old = existing.get(r["claim_id"])
            if old:
                row["DECISION"] = old.get("DECISION", "")
                for extra in old:                       # keep any column the reviewer added
                    if extra not in row and extra:
                        row[extra] = old[extra]
            out.append(row)
    else:
        added = [propose(r) for r in aggregates if r["claim_id"] not in existing]
        out = [existing[c] for c in order] + added

    # Write COLUMNS plus any column the reviewer added to the file, in the order the file had them.
    # FIXED 2026-09-04: fieldnames was hard-wired to COLUMNS and the writer used
    # extrasaction="ignore", so a reviewer-added column was silently DROPPED on every run - the
    # --refresh branch above carries extras forward into the row dict and the writer then threw
    # them away. Running the script during the close-out erased RATIONALE_claude from 45 rows.
    extras = [c for c in (order and next(iter(existing.values())) or {}) if c and c not in COLUMNS]
    fields = COLUMNS + extras

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=";", extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    blank = [r["claim_id"] for r in out if not (r.get("DECISION") or "").strip()]
    how = (f"{len(out)} re-proposed, decisions carried forward" if refresh
           else f"{len(added)} newly proposed, {len(existing)} preserved")
    print(f"{OUT.relative_to(HERE.parent)}: {len(out)} aggregates ({how})")
    print(f"awaiting DECISION: {len(blank)}" + (f"  e.g. {', '.join(blank[:6])}" if blank else ""))


if __name__ == "__main__":
    main()
