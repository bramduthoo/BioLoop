


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


-- Added during phase-1 baseline review (not emitted by `db dump --schema public`):
-- public.geography.geom is typed extensions.geometry, so PostGIS must exist before
-- this migration's CREATE TABLE statements run on an empty database.
-- Mirrors the live project, where postgis 3.3.7 is installed in schema "extensions".
CREATE SCHEMA IF NOT EXISTS "extensions";

CREATE EXTENSION IF NOT EXISTS "postgis" WITH SCHEMA "extensions";


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."basis" (
    "code" "text" NOT NULL,
    "description" "text" NOT NULL
);


ALTER TABLE "public"."basis" OWNER TO "postgres";


COMMENT ON TABLE "public"."basis" IS 'Reporting basis for a value, split out of unit strings like "%DS". Converting between bases is a transformation and belongs to the model layer, not here.';



CREATE TABLE IF NOT EXISTS "public"."classification_scheme" (
    "code" "text" NOT NULL,
    "name" "text" NOT NULL
);


ALTER TABLE "public"."classification_scheme" OWNER TO "postgres";


COMMENT ON TABLE "public"."classification_scheme" IS 'A facet of classification (e.g. origin sector, material type, EWC). Streams are classified by many schemes at once.';



CREATE TABLE IF NOT EXISTS "public"."classification_term" (
    "term_id" bigint NOT NULL,
    "scheme_code" "text" NOT NULL,
    "code" "text" NOT NULL,
    "label" "text" NOT NULL,
    "parent_term_id" bigint
);


ALTER TABLE "public"."classification_term" OWNER TO "postgres";


COMMENT ON COLUMN "public"."classification_term"."parent_term_id" IS 'Self-reference giving in-scheme hierarchy, e.g. Type -> Klasse -> Subclasse as in the OVAM data.';



ALTER TABLE "public"."classification_term" ALTER COLUMN "term_id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."classification_term_term_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."geography" (
    "geography_id" bigint NOT NULL,
    "name" "text" NOT NULL,
    "level" "text" NOT NULL,
    "geom" "extensions"."geometry"(Geometry,4326),
    "parent_id" bigint,
    CONSTRAINT "geography_level_check" CHECK (("level" = ANY (ARRAY['region'::"text", 'province'::"text", 'municipality'::"text", 'nuts'::"text", 'site'::"text", 'point'::"text"])))
);


ALTER TABLE "public"."geography" OWNER TO "postgres";


COMMENT ON COLUMN "public"."geography"."geom" IS 'PostGIS geometry, SRID 4326 (WGS84). Polygons for administrative areas, points for named sites. Sparse for now; scaffolding for the transport layer.';



ALTER TABLE "public"."geography" ALTER COLUMN "geography_id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."geography_geography_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."parameter" (
    "code" "text" NOT NULL,
    "name" "text" NOT NULL,
    "category" "text" NOT NULL,
    "default_unit_code" "text",
    "definition" "text",
    CONSTRAINT "parameter_category_check" CHECK (("category" = ANY (ARRAY['chemical'::"text", 'physical'::"text", 'microbiological'::"text"])))
);


ALTER TABLE "public"."parameter" OWNER TO "postgres";


COMMENT ON TABLE "public"."parameter" IS 'The controlled catalogue = the fixed-shape composition/property vector. Adding a parameter is one INSERT, not a schema change. default_unit_code is a hint only; each measurement records its own unit.';



CREATE TABLE IF NOT EXISTS "public"."property_measurement" (
    "measurement_id" bigint NOT NULL,
    "stream_code" "text" NOT NULL,
    "parameter_code" "text" NOT NULL,
    "value_type" "text" NOT NULL,
    "value_num" numeric,
    "value_min" numeric,
    "value_max" numeric,
    "value_avg" numeric,
    "value_text" "text",
    "sd" numeric,
    "n_samples" integer,
    "unit_code" "text" NOT NULL,
    "basis_code" "text" NOT NULL,
    "source_key" "text" NOT NULL,
    "year" integer,
    "temporal_resolution" "text" DEFAULT 'unknown'::"text" NOT NULL,
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "property_measurement_temporal_resolution_check" CHECK (("temporal_resolution" = ANY (ARRAY['annual'::"text", 'monthly'::"text", 'seasonal'::"text", 'point'::"text", 'unknown'::"text"]))),
    CONSTRAINT "property_measurement_value_type_check" CHECK (("value_type" = ANY (ARRAY['point'::"text", 'range'::"text", 'qualitative'::"text"]))),
    CONSTRAINT "range_order" CHECK ((("value_min" IS NULL) OR ("value_max" IS NULL) OR ("value_min" <= "value_max"))),
    CONSTRAINT "value_shape" CHECK (((("value_type" = 'point'::"text") AND ("value_num" IS NOT NULL)) OR (("value_type" = 'range'::"text") AND ("value_min" IS NOT NULL) AND ("value_max" IS NOT NULL)) OR (("value_type" = 'qualitative'::"text") AND ("value_text" IS NOT NULL))))
);


ALTER TABLE "public"."property_measurement" OWNER TO "postgres";


COMMENT ON TABLE "public"."property_measurement" IS 'The "what is it like" facts: chemical / physical / microbiological values. One row per reported value, each carrying its own unit, basis, uncertainty and source.';



COMMENT ON COLUMN "public"."property_measurement"."source_key" IS 'NOT NULL by design: a value with no source physically cannot be inserted. This is the constraint the old Excel could not enforce.';



ALTER TABLE "public"."property_measurement" ALTER COLUMN "measurement_id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."property_measurement_measurement_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."source" (
    "citation_key" "text" NOT NULL,
    "source_type" "text" NOT NULL,
    "title" "text",
    "url" "text",
    "year" integer,
    "notes" "text",
    CONSTRAINT "source_source_type_check" CHECK (("source_type" = ANY (ARRAY['zotero'::"text", 'dataset'::"text", 'expert'::"text", 'internal'::"text"])))
);


ALTER TABLE "public"."source" OWNER TO "postgres";


COMMENT ON TABLE "public"."source" IS 'Provenance. Every fact-table value references one source. citation_key aligns with the Zotero key for literature, or a dataset id for inventories.';



CREATE TABLE IF NOT EXISTS "public"."stream" (
    "code" "text" NOT NULL,
    "canonical_name" "text" NOT NULL,
    "description" "text",
    "notes" "text"
);


ALTER TABLE "public"."stream" OWNER TO "postgres";


COMMENT ON TABLE "public"."stream" IS 'A biomass stream TYPE / archetype, not a physical consignment. Seasonal or processed variation is expressed via temporal_resolution on the measurements, not by creating separate streams.';



CREATE TABLE IF NOT EXISTS "public"."stream_classification" (
    "stream_code" "text" NOT NULL,
    "term_id" bigint NOT NULL
);


ALTER TABLE "public"."stream_classification" OWNER TO "postgres";


COMMENT ON TABLE "public"."stream_classification" IS 'Faceted classification bridge: one stream carries many terms across many schemes, so you can roll up by any facet (sector OR material OR EWC).';



CREATE TABLE IF NOT EXISTS "public"."supply_observation" (
    "observation_id" bigint NOT NULL,
    "stream_code" "text" NOT NULL,
    "quantity_num" numeric,
    "quantity_min" numeric,
    "quantity_max" numeric,
    "unit_code" "text" NOT NULL,
    "basis_code" "text" NOT NULL,
    "reported_as" "text",
    "conversion_note" "text",
    "geography_id" bigint,
    "year" integer,
    "temporal_resolution" "text" DEFAULT 'annual'::"text" NOT NULL,
    "source_key" "text" NOT NULL,
    "notes" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "qty_present" CHECK ((("quantity_num" IS NOT NULL) OR (("quantity_min" IS NOT NULL) AND ("quantity_max" IS NOT NULL)))),
    CONSTRAINT "supply_observation_temporal_resolution_check" CHECK (("temporal_resolution" = ANY (ARRAY['annual'::"text", 'monthly'::"text", 'seasonal'::"text", 'point'::"text", 'unknown'::"text"])))
);


ALTER TABLE "public"."supply_observation" OWNER TO "postgres";


COMMENT ON TABLE "public"."supply_observation" IS 'The "how much / where / when" facts: volume & availability. Seasonality lives in temporal_resolution.';



COMMENT ON COLUMN "public"."supply_observation"."reported_as" IS 'Original reporting basis where it differs, e.g. "t N" for manure.';



COMMENT ON COLUMN "public"."supply_observation"."conversion_note" IS 'Provenance of any conversion the source applied, e.g. "assume 4.5 kg N/t fresh". The conversion itself is never baked into the stored value.';



ALTER TABLE "public"."supply_observation" ALTER COLUMN "observation_id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."supply_observation_observation_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."unit" (
    "code" "text" NOT NULL,
    "description" "text" NOT NULL
);


ALTER TABLE "public"."unit" OWNER TO "postgres";


COMMENT ON TABLE "public"."unit" IS 'Controlled units. Basis (dry matter etc.) is recorded separately in "basis", never folded into the unit string — this is what fixes the old "%DS" problem.';



ALTER TABLE ONLY "public"."basis"
    ADD CONSTRAINT "basis_pkey" PRIMARY KEY ("code");



ALTER TABLE ONLY "public"."classification_scheme"
    ADD CONSTRAINT "classification_scheme_pkey" PRIMARY KEY ("code");



ALTER TABLE ONLY "public"."classification_term"
    ADD CONSTRAINT "classification_term_pkey" PRIMARY KEY ("term_id");



ALTER TABLE ONLY "public"."classification_term"
    ADD CONSTRAINT "classification_term_scheme_code_code_key" UNIQUE ("scheme_code", "code");



ALTER TABLE ONLY "public"."geography"
    ADD CONSTRAINT "geography_pkey" PRIMARY KEY ("geography_id");



ALTER TABLE ONLY "public"."parameter"
    ADD CONSTRAINT "parameter_pkey" PRIMARY KEY ("code");



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_pkey" PRIMARY KEY ("measurement_id");



ALTER TABLE ONLY "public"."source"
    ADD CONSTRAINT "source_pkey" PRIMARY KEY ("citation_key");



ALTER TABLE ONLY "public"."stream_classification"
    ADD CONSTRAINT "stream_classification_pkey" PRIMARY KEY ("stream_code", "term_id");



ALTER TABLE ONLY "public"."stream"
    ADD CONSTRAINT "stream_pkey" PRIMARY KEY ("code");



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_pkey" PRIMARY KEY ("observation_id");



ALTER TABLE ONLY "public"."unit"
    ADD CONSTRAINT "unit_pkey" PRIMARY KEY ("code");



CREATE INDEX "classification_term_scheme_code_idx" ON "public"."classification_term" USING "btree" ("scheme_code");



CREATE INDEX "geography_geom_idx" ON "public"."geography" USING "gist" ("geom");



CREATE INDEX "property_measurement_parameter_code_idx" ON "public"."property_measurement" USING "btree" ("parameter_code");



CREATE INDEX "property_measurement_source_key_idx" ON "public"."property_measurement" USING "btree" ("source_key");



CREATE INDEX "property_measurement_stream_code_idx" ON "public"."property_measurement" USING "btree" ("stream_code");



CREATE INDEX "stream_classification_term_id_idx" ON "public"."stream_classification" USING "btree" ("term_id");



CREATE INDEX "supply_observation_geography_id_idx" ON "public"."supply_observation" USING "btree" ("geography_id");



CREATE INDEX "supply_observation_source_key_idx" ON "public"."supply_observation" USING "btree" ("source_key");



CREATE INDEX "supply_observation_stream_code_idx" ON "public"."supply_observation" USING "btree" ("stream_code");



ALTER TABLE ONLY "public"."classification_term"
    ADD CONSTRAINT "classification_term_parent_term_id_fkey" FOREIGN KEY ("parent_term_id") REFERENCES "public"."classification_term"("term_id");



ALTER TABLE ONLY "public"."classification_term"
    ADD CONSTRAINT "classification_term_scheme_code_fkey" FOREIGN KEY ("scheme_code") REFERENCES "public"."classification_scheme"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."geography"
    ADD CONSTRAINT "geography_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."geography"("geography_id");



ALTER TABLE ONLY "public"."parameter"
    ADD CONSTRAINT "parameter_default_unit_code_fkey" FOREIGN KEY ("default_unit_code") REFERENCES "public"."unit"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_basis_code_fkey" FOREIGN KEY ("basis_code") REFERENCES "public"."basis"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_parameter_code_fkey" FOREIGN KEY ("parameter_code") REFERENCES "public"."parameter"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_source_key_fkey" FOREIGN KEY ("source_key") REFERENCES "public"."source"("citation_key") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_stream_code_fkey" FOREIGN KEY ("stream_code") REFERENCES "public"."stream"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."property_measurement"
    ADD CONSTRAINT "property_measurement_unit_code_fkey" FOREIGN KEY ("unit_code") REFERENCES "public"."unit"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."stream_classification"
    ADD CONSTRAINT "stream_classification_stream_code_fkey" FOREIGN KEY ("stream_code") REFERENCES "public"."stream"("code") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."stream_classification"
    ADD CONSTRAINT "stream_classification_term_id_fkey" FOREIGN KEY ("term_id") REFERENCES "public"."classification_term"("term_id");



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_basis_code_fkey" FOREIGN KEY ("basis_code") REFERENCES "public"."basis"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_geography_id_fkey" FOREIGN KEY ("geography_id") REFERENCES "public"."geography"("geography_id");



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_source_key_fkey" FOREIGN KEY ("source_key") REFERENCES "public"."source"("citation_key") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_stream_code_fkey" FOREIGN KEY ("stream_code") REFERENCES "public"."stream"("code") ON UPDATE CASCADE;



ALTER TABLE ONLY "public"."supply_observation"
    ADD CONSTRAINT "supply_observation_unit_code_fkey" FOREIGN KEY ("unit_code") REFERENCES "public"."unit"("code") ON UPDATE CASCADE;



ALTER TABLE "public"."basis" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."classification_scheme" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."classification_term" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."geography" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."parameter" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."property_measurement" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."source" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."stream" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."stream_classification" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."supply_observation" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."unit" ENABLE ROW LEVEL SECURITY;


GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON TABLE "public"."basis" TO "anon";
GRANT ALL ON TABLE "public"."basis" TO "authenticated";
GRANT ALL ON TABLE "public"."basis" TO "service_role";



GRANT ALL ON TABLE "public"."classification_scheme" TO "anon";
GRANT ALL ON TABLE "public"."classification_scheme" TO "authenticated";
GRANT ALL ON TABLE "public"."classification_scheme" TO "service_role";



GRANT ALL ON TABLE "public"."classification_term" TO "anon";
GRANT ALL ON TABLE "public"."classification_term" TO "authenticated";
GRANT ALL ON TABLE "public"."classification_term" TO "service_role";



GRANT ALL ON SEQUENCE "public"."classification_term_term_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."classification_term_term_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."classification_term_term_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."geography" TO "anon";
GRANT ALL ON TABLE "public"."geography" TO "authenticated";
GRANT ALL ON TABLE "public"."geography" TO "service_role";



GRANT ALL ON SEQUENCE "public"."geography_geography_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."geography_geography_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."geography_geography_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."parameter" TO "anon";
GRANT ALL ON TABLE "public"."parameter" TO "authenticated";
GRANT ALL ON TABLE "public"."parameter" TO "service_role";



GRANT ALL ON TABLE "public"."property_measurement" TO "anon";
GRANT ALL ON TABLE "public"."property_measurement" TO "authenticated";
GRANT ALL ON TABLE "public"."property_measurement" TO "service_role";



GRANT ALL ON SEQUENCE "public"."property_measurement_measurement_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."property_measurement_measurement_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."property_measurement_measurement_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."source" TO "anon";
GRANT ALL ON TABLE "public"."source" TO "authenticated";
GRANT ALL ON TABLE "public"."source" TO "service_role";



GRANT ALL ON TABLE "public"."stream" TO "anon";
GRANT ALL ON TABLE "public"."stream" TO "authenticated";
GRANT ALL ON TABLE "public"."stream" TO "service_role";



GRANT ALL ON TABLE "public"."stream_classification" TO "anon";
GRANT ALL ON TABLE "public"."stream_classification" TO "authenticated";
GRANT ALL ON TABLE "public"."stream_classification" TO "service_role";



GRANT ALL ON TABLE "public"."supply_observation" TO "anon";
GRANT ALL ON TABLE "public"."supply_observation" TO "authenticated";
GRANT ALL ON TABLE "public"."supply_observation" TO "service_role";



GRANT ALL ON SEQUENCE "public"."supply_observation_observation_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."supply_observation_observation_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."supply_observation_observation_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."unit" TO "anon";
GRANT ALL ON TABLE "public"."unit" TO "authenticated";
GRANT ALL ON TABLE "public"."unit" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";







