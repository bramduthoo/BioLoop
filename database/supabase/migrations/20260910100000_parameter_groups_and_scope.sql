-- BioMobi schema change: a middle level for the parameter catalogue, and the
-- retirement of the microbiological parameters.
--
-- HAND-WRITTEN. This is the first DDL since the 2026-07-27 baseline, and both
-- halves are deliberate acts a generator must not be able to perform.
--
-- 1. `parameter.category` was the only classification a parameter carried, and it
--    has three values, so 62 parameters sat in two flat buckets. Reviewer request,
--    2026-09-10: the catalogue needs its hierarchical level. The shape follows the
--    one the schema already uses for streams -- a reference table naming the axis's
--    vocabulary, and an FK from the thing being classified:
--
--        category (chemical | physical)  ->  parameter_group  ->  parameter
--
--    A group implies exactly one category; `composition/tools/emit_vocabulary.py`
--    refuses to emit when a parameter's category disagrees with its group's.
--    `group_code` is NULLABLE so a parameter can exist before its group is decided,
--    which is what "the catalogue grows" needs.
--
-- 2. The six microbiological parameters are retired. Reviewer decision, 2026-09-10:
--    microbiological characterisation is out of scope for the project. NOTE that
--    `charter.md` lists it as IN scope, so the charter is amended alongside this
--    migration -- the scope statement moved, the schema followed.
--
--    The CHECK on `parameter.category` still admits 'microbiological', deliberately:
--    narrowing it would make the decision expensive to reverse, and an empty
--    category costs nothing.
--
--    The DELETE is guarded on `property_measurement`, so it cannot destroy a
--    measurement's parameter. If any of the six is ever referenced, the guard
--    silently keeps it and the row must then be retired by hand.

-- 1. the middle level ------------------------------------------------------

CREATE TABLE IF NOT EXISTS "public"."parameter_group" (
    "code" "text" NOT NULL,
    "name" "text" NOT NULL,
    "category" "text" NOT NULL,
    "sort_order" integer NOT NULL DEFAULT 0,
    "definition" "text",
    CONSTRAINT "parameter_group_pkey" PRIMARY KEY ("code"),
    CONSTRAINT "parameter_group_category_check"
        CHECK (("category" = ANY (ARRAY['chemical'::"text", 'physical'::"text",
                                       'microbiological'::"text"])))
);

COMMENT ON TABLE "public"."parameter_group" IS
  'The middle level of the parameter hierarchy: category -> group -> parameter. A group is an analytical partition (Weende proximate, Van Soest fibre, elemental analysis, heavy metals), not a chemical family -- which is the point, because a parameter''s identity here is method-defined.';
COMMENT ON COLUMN "public"."parameter_group"."sort_order" IS
  'Presentation order, so a composition table reads in the order an analyst expects rather than alphabetically.';

ALTER TABLE "public"."parameter"
    ADD COLUMN IF NOT EXISTS "group_code" "text";

COMMENT ON COLUMN "public"."parameter"."group_code" IS
  'Nullable on purpose: a parameter may be registered before its group is settled. The group implies the category -- see composition/tools/emit_vocabulary.py, which refuses a disagreement.';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'parameter_group_code_fkey') THEN
    ALTER TABLE "public"."parameter"
      ADD CONSTRAINT "parameter_group_code_fkey"
      FOREIGN KEY ("group_code") REFERENCES "public"."parameter_group"("code")
      ON UPDATE CASCADE;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS "parameter_group_code_idx"
    ON "public"."parameter" USING "btree" ("group_code");

ALTER TABLE "public"."parameter_group" ENABLE ROW LEVEL SECURITY;

-- 2. retire the microbiological parameters ---------------------------------

DELETE FROM "public"."parameter"
 WHERE "category" = 'microbiological'
   AND NOT EXISTS (
     SELECT 1 FROM "public"."property_measurement" m
      WHERE m."parameter_code" = "parameter"."code"
   );
