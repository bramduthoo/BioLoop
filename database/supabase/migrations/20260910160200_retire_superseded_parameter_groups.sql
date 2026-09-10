-- Retire the invented parameter groups that 20260910160100 (vocabulary v4) replaced.
--
-- HAND-WRITTEN, and it is a SEPARATE migration for a reason worth recording: the
-- delete was first written into 20260910160000, ahead of the vocabulary insert, and
-- it silently did nothing. Its guard asks whether any parameter still points at the
-- group -- and at that point in the sequence they all still did, because the
-- re-pointing happens in the vocabulary migration that runs afterwards. The guard
-- worked exactly as designed; the ORDER was wrong.
--
-- Generalises: a guarded cleanup must run after the thing whose absence it checks
-- for, not beside it.
--
-- These eight codes are the analytical-tradition buckets fitted to the first two
-- sources read on 2026-09-09, superseded the next day by the adopted FAO/INFOODS
-- tree. The guard stays: a group still carrying a parameter survives and shows up
-- as a leftover, rather than silently taking its parameters' classification with it.

DELETE FROM "public"."parameter_group"
 WHERE "code" IN ('proximate-weende', 'fibre', 'carbohydrate', 'elemental',
                  'minerals', 'heavy-metals', 'other-chemical', 'physical')
   AND NOT EXISTS (
     SELECT 1 FROM "public"."parameter" p WHERE p."group_code" = "parameter_group"."code"
   );
