-- BioMobi schema change: a METHOD axis on measurements, a nested parameter
-- hierarchy, and the permanent removal of microbiological characterisation.
--
-- HAND-WRITTEN. Second DDL since the 2026-07-27 baseline, and it supersedes part
-- of 20260910100000 the same day, on reviewer challenge.
--
-- 1. METHOD BELONGS TO THE MEASUREMENT, NOT TO THE ANALYTE.
--    The catalogue had been resolving method differences by splitting the
--    parameter: `adl` beside `lignin`, `crude_fat` meaning specifically the ether
--    extract, the polarimetric and enzymatic starch determinations sharing one
--    parameter with the method buried in free-text notes. Reviewer challenge,
--    2026-09-10, with the decisive example: dry matter determined at 60 C and at
--    105 C is the SAME analyte and a different number. Splitting the parameter for
--    that gives `dry_matter_105`, `dry_matter_60`, and no way to ask for dry matter.
--
--    This is the same rule the stream layer already runs on. A stream is an object
--    and where it arose belongs to the OBSERVATION; a parameter is an analyte and
--    how it was determined belongs to the MEASUREMENT. If a name only makes sense
--    by saying how it was measured, it is not the analyte.
--
--    The split rule that survives: a method that changes the NUMBER for one analyte
--    is a method (ADL vs Klason lignin, 105 C vs 60 C drying, polarimetric vs
--    enzymatic starch). A method that DEFINES A DIFFERENT FRACTION stays its own
--    parameter, because there is no method-independent thing it could mean --
--    crude fibre, NDF and ADF are three fractions, not three ways of measuring one.
--
--    `method_code` is NULLABLE and that is a real state: a source that prints a
--    column headed only "Lignin" has not told us which determination it used, and
--    recording that as unknown is honest where guessing is not.
--
-- 2. VALUE_ORIGIN. A predicted value must never enter silently. Feedipedia marks
--    equation-derived values with an asterisk and does not publish which equation;
--    the Weende nitrogen-free extract is a by-difference calculation, not a
--    determination at all. Both were being carried in a CSV column and prose. They
--    are now a column with a CHECK, so the database itself cannot hold a predicted
--    value that looks measured.
--
-- 3. NESTED PARAMETER GROUPS. The groups added earlier today were an invented set
--    of analytical-tradition buckets fitted to the two sources read so far
--    ("Weende proximate", "Elemental analysis", "other chemical"). Reviewer
--    challenge: adopt an existing hierarchy instead. The tree is now FAO/INFOODS's
--    own component families, taken from the FAO/INFOODS BioFoodComp documentation,
--    with a second branch adopted from the solid-biofuel standards for the
--    combustion parameters INFOODS has no place for. `parent_code` gives the
--    family/subfamily nesting those standards use, exactly as
--    `classification_term.parent_term_id` does for streams.
--
-- 4. MICROBIOLOGICAL IS OUT PERMANENTLY. Retired 2026-09-10 and confirmed the same
--    day as definitive, so the CHECK constraints are narrowed rather than left
--    admitting a category that must not come back. `charter.md` was narrowed with it.

-- 1. the method axis -------------------------------------------------------

CREATE TABLE IF NOT EXISTS "public"."method" (
    "code" "text" NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    CONSTRAINT "method_pkey" PRIMARY KEY ("code")
);

COMMENT ON TABLE "public"."method" IS
  'How a value was determined. A method changes the NUMBER for one analyte (ADL vs Klason lignin, drying at 105 C vs 60 C, polarimetric vs enzymatic starch); a determination that defines a DIFFERENT FRACTION is its own parameter instead (crude fibre vs NDF vs ADF). Deliberately not constrained per parameter: a method code such as an AOAC number spans several analytes, and the pairing is checked at the crosswalk gate.';

ALTER TABLE "public"."property_measurement"
    ADD COLUMN IF NOT EXISTS "method_code" "text",
    ADD COLUMN IF NOT EXISTS "value_origin" "text" NOT NULL DEFAULT 'measured';

COMMENT ON COLUMN "public"."property_measurement"."method_code" IS
  'NULL is a real state, not a gap to fill: a source printing a column headed only "Lignin" has not said which determination it used. Recording that as unknown is honest; guessing is not.';
COMMENT ON COLUMN "public"."property_measurement"."value_origin" IS
  'measured = a determination. predicted = the output of a regression equation (Feedipedia''s asterisk). calculated = arithmetic by the source (Weende nitrogen-free extract, fixed carbon). unknown = the source did not say. This exists so a predicted value cannot enter looking measured.';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'property_measurement_method_code_fkey') THEN
    ALTER TABLE "public"."property_measurement"
      ADD CONSTRAINT "property_measurement_method_code_fkey"
      FOREIGN KEY ("method_code") REFERENCES "public"."method"("code") ON UPDATE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'property_measurement_value_origin_check') THEN
    ALTER TABLE "public"."property_measurement"
      ADD CONSTRAINT "property_measurement_value_origin_check"
      CHECK ("value_origin" = ANY (ARRAY['measured'::"text", 'predicted'::"text",
                                         'calculated'::"text", 'unknown'::"text"]));
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS "property_measurement_method_code_idx"
    ON "public"."property_measurement" USING "btree" ("method_code");

ALTER TABLE "public"."method" ENABLE ROW LEVEL SECURITY;

-- 2. nested parameter groups -----------------------------------------------

ALTER TABLE "public"."parameter_group"
    ADD COLUMN IF NOT EXISTS "parent_code" "text",
    ADD COLUMN IF NOT EXISTS "external_ref" "text";

COMMENT ON COLUMN "public"."parameter_group"."parent_code" IS
  'Family / subfamily nesting, as classification_term.parent_term_id does for streams. A parameter attaches to its DEEPEST group; the ancestors are reached by walking up.';
COMMENT ON COLUMN "public"."parameter_group"."external_ref" IS
  'The standard this group is adopted from -- FAO/INFOODS for everything a food-composition standard covers, ISO 17225 / CEN-TS for the combustion branch. A group marked "neither standard" is ours and is labelled so on purpose.';

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'parameter_group_parent_code_fkey') THEN
    ALTER TABLE "public"."parameter_group"
      ADD CONSTRAINT "parameter_group_parent_code_fkey"
      FOREIGN KEY ("parent_code") REFERENCES "public"."parameter_group"("code") ON UPDATE CASCADE;
  END IF;
END $$;

-- 3. retire the parameters the method axis makes redundant -----------------
-- `adl` becomes `lignin` + method 'lignin-adl'; `crude_fat` becomes `fat_total`
-- + the extraction as a method. Guarded, so neither can orphan a measurement.

UPDATE "public"."parameter" SET "code" = 'fat_total'
 WHERE "code" = 'crude_fat'
   AND NOT EXISTS (SELECT 1 FROM "public"."parameter" WHERE "code" = 'fat_total');

DELETE FROM "public"."parameter"
 WHERE "code" = 'adl'
   AND NOT EXISTS (
     SELECT 1 FROM "public"."property_measurement" m WHERE m."parameter_code" = 'adl'
   );

-- 4. microbiological, permanently ------------------------------------------

DELETE FROM "public"."parameter"
 WHERE "category" = 'microbiological'
   AND NOT EXISTS (
     SELECT 1 FROM "public"."property_measurement" m
      WHERE m."parameter_code" = "parameter"."code"
   );

ALTER TABLE "public"."parameter" DROP CONSTRAINT IF EXISTS "parameter_category_check";
ALTER TABLE "public"."parameter"
    ADD CONSTRAINT "parameter_category_check"
    CHECK (("category" = ANY (ARRAY['chemical'::"text", 'physical'::"text"])));

ALTER TABLE "public"."parameter_group" DROP CONSTRAINT IF EXISTS "parameter_group_category_check";
ALTER TABLE "public"."parameter_group"
    ADD CONSTRAINT "parameter_group_category_check"
    CHECK (("category" = ANY (ARRAY['chemical'::"text", 'physical'::"text"])));
