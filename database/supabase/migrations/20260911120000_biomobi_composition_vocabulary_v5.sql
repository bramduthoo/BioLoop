-- BioMobi vocabulary: units, reporting bases and the composition parameter catalogue.
--
-- GENERATED -- do not hand-edit. Regenerate with, from database/composition/:
--   ../.venv/Scripts/python tools/emit_vocabulary.py --emit-migration <path>
-- The source of truth is vocabulary/{units,bases,parameters}.csv.
--
-- The parameter catalogue is DELIBERATELY NOT A REQUIRED VECTOR. BioMobi stays sparse:
-- absence of a row means 'not measured', never zero. The fixed-shape composition vector
-- the charter describes is a projection built in the model layer over this catalogue.
--
-- The catalogue GROWS. When a source reports a parameter that is not here, add a row to
-- parameters.csv and emit a NEW migration -- never map it onto a near-neighbour, and
-- never edit an applied migration. Every statement below is ON CONFLICT-guarded.
--
-- 29 units, 6 bases, 16 parameter groups, 17 methods, 65 parameters.

-- 1. units. Basis is NEVER folded into a unit string -- that is what basis is for.
INSERT INTO unit (code, description) VALUES ('%', 'Percentage (massafractie x 100), tenzij de parameter anders bepaalt')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('g/kg', 'Gram per kilogram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mg/kg', 'Milligram per kilogram (ppm)')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('ug/kg', 'Microgram per kilogram (ppb)')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('g/100g', 'Gram per 100 gram - de gebruikelijke eenheid van voedingsmiddelentabellen')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mg/100g', 'Milligram per 100 gram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('g/L', 'Gram per liter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mg/L', 'Milligram per liter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('MJ/kg', 'Megajoule per kilogram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('kJ/kg', 'Kilojoule per kilogram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('kcal/kg', 'Kilocalorie per kilogram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('kg/m3', 'Kilogram per kubieke meter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('g/cm3', 'Gram per kubieke centimeter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mm', 'Millimeter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('um', 'Micrometer')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mS/cm', 'Millisiemens per centimeter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('degC', 'Graden Celsius')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('g/g', 'Gram per gram - dimensieloze massaverhouding, gebruikt voor bv. waterbindend vermogen')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('mL/g', 'Milliliter per gram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('ratio', 'Dimensieloze verhouding (bv. C/N)')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('pH', 'pH-eenheid - dimensieloze logaritmische schaal')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('cfu/g', 'Kolonievormende eenheden per gram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('cfu/mL', 'Kolonievormende eenheden per milliliter')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('log10 cfu/g', 'Log10 kolonievormende eenheden per gram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('t', 'Ton (metrische ton, 1000 kg)')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('kg', 'Kilogram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('unknown', 'De bron vermeldt geen eenheid - een ONTBREKENDE claim, niet hetzelfde als n.a.')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('n.a.', 'Geen eenheid van toepassing - een ONTBREKENDE eenheid is unknown, niet n.a.')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO unit (code, description) VALUES ('umol/g', 'Micromol per gram')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;

-- 2. reporting bases. 'unknown' (the source did not say) and 'n.a.' (no basis applies)
--    are DIFFERENT CLAIMS and must never be collapsed into one another.
INSERT INTO basis (code, description) VALUES ('fresh', 'Verse stof - de stof zoals ze aankomt (FM, wet basis, as received, as fed). Bronnen die "as is" of "vers gewicht" zeggen vallen hier')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO basis (code, description) VALUES ('dry', 'Droge stof - na drogen tot constant gewicht (DM). Bronnen die "total solids" of "TS" zeggen vallen hier - leg de term van de bron vast in notes')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO basis (code, description) VALUES ('dry_ash_free', 'Droge asvrije stof (DAF) - droge stof minus as, ook wel organische-stofbasis')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO basis (code, description) VALUES ('volatile_solids', 'Vluchtige stof (VS) - basis die anaerobe-vergistingsbronnen gebruiken. Niet gelijkstellen aan DAF zonder dat de bron dat zegt')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO basis (code, description) VALUES ('unknown', 'De bron vermeldt geen basis - een ONTBREKENDE claim, niet hetzelfde als n.a.')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;
INSERT INTO basis (code, description) VALUES ('n.a.', 'Geen basis van toepassing (pH, temperatuur, C/N-verhouding, bulkdichtheid). Een ONTBREKENDE basis is unknown, niet n.a.')
  ON CONFLICT (code) DO UPDATE SET description = EXCLUDED.description;

-- 3. the parameter hierarchy, adopted rather than invented: FAO/INFOODS component
--    families, plus a solid-biofuel branch for the combustion parameters INFOODS has
--    no place for. Parents first, then children. A parameter attaches to a LEAF.
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'macronutrients-energy', 'Macronutrients including energy', NULL, 'chemical',
  10, 'FAO/INFOODS',
  'Top-level INFOODS family. Carries no parameters itself - a parameter attaches to the deepest group, as a stream attaches to its deepest classification term')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'minerals-trace', 'Minerals and trace elements', NULL, 'chemical',
  20, 'FAO/INFOODS',
  'Mineral elements as nutrients, including the agronomic oxide forms P2O5 and K2O')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'heavy-metals-contaminants', 'Heavy metals and contaminants', NULL, 'chemical',
  30, 'FAO/INFOODS',
  'Elements that decide which applications a stream is admissible for')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'bioactive', 'Bioactive constituents', NULL, 'chemical',
  40, 'FAO/INFOODS',
  'INFOODS nests flavonoids, tannins, phenolic acids and other bioactives here. Only a total-polyphenol figure is registered so far - the subfamilies enter when a source reports them')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'fuel-characterisation', 'Solid-biofuel characterisation', NULL, 'chemical',
  50, 'ISO 17225 / CEN-TS',
  'THE SEAM. INFOODS has no place for combustion characterisation, so this branch is adopted from the solid-biofuel standards instead - the same CEN/TS methods Phyllis2 records cite. Carries no parameters itself')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'physical-properties', 'Physical properties', NULL, 'physical',
  60, 'neither standard',
  'Bulk, particle and water-relation properties. Neither INFOODS nor ISO 17225 carries these as a family, so this branch is ours and is labelled as such. Feeds the transport and handling side of the model')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'miscellaneous', 'Miscellaneous', NULL, 'chemical',
  70, 'FAO/INFOODS',
  'INFOODS closes its list with this family and so do we. pH and the effluent-load parameters are not food components in any tradition')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'water', 'Water', 'macronutrients-energy', 'chemical',
  11, 'FAO/INFOODS',
  'Water and its complement. Dry matter is registered here rather than under ash because INFOODS treats the water axis as one family')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'protein', 'Protein', 'macronutrients-energy', 'chemical',
  12, 'FAO/INFOODS',
  'Nitrogen and the protein figures derived from it')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'fat', 'Fat components', 'macronutrients-energy', 'chemical',
  13, 'FAO/INFOODS',
  'Total fat and lipid fractions. The extraction used is a METHOD, not a separate parameter')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'carbohydrates', 'Carbohydrates and carbohydrate fractions', 'macronutrients-energy', 'chemical',
  14, 'FAO/INFOODS',
  'Starch, sugars and the by-difference carbohydrate figures')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'dietary-fibre', 'Dietary fibre and dietary fibre fractions', 'macronutrients-energy', 'chemical',
  15, 'FAO/INFOODS',
  'Every fibre fraction, whichever tradition defined it - AOAC dietary fibre, Weende crude fibre and the Van Soest detergent fractions all live here. They are DIFFERENT FRACTIONS, not one fraction measured differently')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'ash-solids', 'Ash and other solids', 'macronutrients-energy', 'chemical',
  16, 'FAO/INFOODS',
  'Mineral residue and the organic complement')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'energy', 'Energy', 'macronutrients-energy', 'chemical',
  17, 'FAO/INFOODS',
  'Calorific value. Feed sources call it gross energy, fuel sources call it HHV - one quantity, one group')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'proximate-fuel', 'Proximate analysis', 'fuel-characterisation', 'chemical',
  51, 'ISO 17225 / CEN-TS',
  'Volatile matter and fixed carbon. Not the Weende proximate partition and not to be confused with it')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;
INSERT INTO parameter_group (code, name, parent_code, category, sort_order,
    external_ref, definition) VALUES (
  'ultimate', 'Ultimate (elemental) analysis', 'fuel-characterisation', 'chemical',
  52, 'ISO 17225 / CEN-TS',
  'The CHNOS plus chlorine set, and the C/N ratio derived from it. Sulphur and chlorine sit here rather than with the minerals because the ultimate analysis is a defined standard set that includes them - not because our sources happen to report them that way')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    parent_code = EXCLUDED.parent_code, category = EXCLUDED.category,
    sort_order = EXCLUDED.sort_order, external_ref = EXCLUDED.external_ref,
    definition = EXCLUDED.definition;

-- 4. methods. A method changes the NUMBER for one analyte; a determination that
--    defines a DIFFERENT FRACTION is its own parameter instead.
INSERT INTO method (code, name, description) VALUES (
  'dm-oven-105', 'Oven drying at 103-105 C', 'Drying to constant mass at 103-105 C. The temperature matters - a lower-temperature or vacuum drying gives a different figure for the same material, which is exactly why the method is recorded beside the value and not inside the parameter')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'dm-oven-60', 'Oven drying at 60 C', 'Low-temperature drying, common where volatiles would be lost at 105 C')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ash-550', 'Ashing at 550 C', 'Incineration to constant mass at 550 C')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ash-600', 'Ashing at 600 C', 'Incineration to constant mass at 600 C')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ee-diethyl', 'Ether extraction (diethyl ether)', 'Continuous or Soxhlet extraction with diethyl ether. This is what the Weende scheme calls crude fat - a method of determining total fat, not a different analyte')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ee-petroleum', 'Ether extraction (petroleum ether)', 'Extraction with petroleum ether. Recovers a slightly different lipid set than diethyl ether')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ee-hcl', 'Acid hydrolysis then ether extraction', 'HCl hydrolysis before extraction, which releases bound lipids the plain ether extract leaves behind. Systematically higher than ee-diethyl on the same material')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'lignin-adl', 'Acid detergent lignin (Van Soest)', 'Lignin as the residue of the acid-detergent sequence. feedtables.com defines its Lignin column as usually this method - note the hedge, which is why a value from a column headed only Lignin is recorded as method unknown rather than as this one')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'lignin-klason', 'Klason lignin', 'Lignin as the residue after 72 percent sulphuric acid hydrolysis. Reads systematically higher than ADL')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'lignin-permanganate', 'Permanganate lignin (Van Soest)', 'The permanganate variant of the Van Soest lignin determination')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ndf-amylase', 'NDF with amylase (aNDF)', 'Neutral detergent fibre run with heat-stable amylase, so residual starch does not inflate the figure')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'ndf-ash-corrected', 'NDF corrected for ash (aNDFom)', 'Neutral detergent fibre expressed free of residual ash')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'starch-polarimetric', 'Starch by polarimetry (Ewers)', 'The polarimetric determination. Reads higher than the enzymatic method on the same material - Feedipedia prints both for several feeds')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'starch-enzymatic', 'Starch by enzymatic assay', 'Enzymatic determination')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'kjeldahl', 'Kjeldahl nitrogen', 'Wet digestion nitrogen determination')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'dumas', 'Dumas combustion nitrogen', 'Combustion nitrogen determination')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;
INSERT INTO method (code, name, description) VALUES (
  'prediction-equation', 'Predicted from a regression equation', 'NOT A MEASUREMENT. The value is the output of an equation fitted to other constituents. Record it on value_origin as predicted - this method row exists for the case where the source names the equation')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    description = EXCLUDED.description;

-- 5. the parameter catalogue. default_unit_code is a HINT ONLY -- every measurement
--    records its own unit, and units may differ between measurements of one parameter.
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'dry_matter',
  'Dry matter',
  'chemical',
  'water',
  '%',
  'Mass fraction remaining after drying to constant mass. The drying TEMPERATURE is a method, recorded on the measurement - 105 C and 60 C give different figures for the same material. Sources write DM, TS or DS. Reported on fresh basis')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'moisture',
  'Moisture',
  'chemical',
  'water',
  '%',
  'Watergehalte zoals de bron het rapporteert. Apart geregistreerd van droge stof omdat bronnen het zo geven - niet afleiden, alleen vastleggen wat er staat')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'ash',
  'Ash',
  'chemical',
  'ash-solids',
  '%',
  'Mineral residue after incineration. The ashing TEMPERATURE is a method, recorded on the measurement')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'organic_matter',
  'Organic matter',
  'chemical',
  'ash-solids',
  '%',
  'Droge stof min as. Bronnen over anaerobe vergisting schrijven hier vaak VS - leg de term van de bron vast in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'crude_protein',
  'Crude protein',
  'chemical',
  'protein',
  '%',
  'Total nitrogen multiplied by a protein factor, usually 6,25. INFOODS calls this PROCNT, protein calculated from total nitrogen. The FACTOR is an expression rather than a method - record it in the measurement notes until an expression axis exists')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'total_nitrogen',
  'Total nitrogen',
  'chemical',
  'protein',
  '%',
  'Kjeldahl- of Dumas-stikstof zelf, zonder eiwitfactor. Registreer dit wanneer de bron N geeft en niet het eiwit')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'true_protein',
  'True protein',
  'chemical',
  'protein',
  '%',
  'Eiwit bepaald als som van aminozuren of na aftrek van niet-eiwitstikstof. Een ander object dan ruw eiwit, niet een betere meting ervan')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'fat_total',
  'Total fat',
  'chemical',
  'fat',
  '%',
  'Total lipid. WHICH EXTRACTION was used is a METHOD, recorded on the measurement - diethyl ether (what the Weende scheme calls crude fat), petroleum ether, or acid hydrolysis, which recovers bound lipids the plain ether extract leaves behind and reads systematically higher. INFOODS separates FAT from FATCE on the same grounds')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'crude_fibre',
  'Crude fibre',
  'chemical',
  'dietary-fibre',
  '%',
  'The Weende crude-fibre fraction, and it is genuinely Weende-specific: there is no method-independent thing it could mean. It is NOT a worse measurement of fibre than NDF - it is a DIFFERENT fraction, losing most hemicellulose and part of the lignin. INFOODS carries it as FIBC')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'nfe',
  'Nitrogen-free extract',
  'chemical',
  'carbohydrates',
  '%',
  'The by-difference carbohydrate remainder of the Weende partition. A calculation by the source, not a determination - record it with value_origin = calculated. INFOODS has the same concept as CHOAVLDF')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'ndf',
  'Neutral detergent fibre (NDF)',
  'chemical',
  'dietary-fibre',
  '%',
  'Van Soest-celwand - cellulose plus hemicellulose plus lignine. Vermeld in notes of de bron aNDF of aNDFom bedoelt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'adf',
  'Acid detergent fibre (ADF)',
  'chemical',
  'dietary-fibre',
  '%',
  'Van Soest - cellulose plus lignine')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'cellulose',
  'Cellulose',
  'chemical',
  'dietary-fibre',
  '%',
  'Alleen wanneer de bron cellulose zelf rapporteert. Niet afleiden uit ADF min ADL - dat is een berekening en hoort in de modellaag')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'hemicellulose',
  'Hemicellulose',
  'chemical',
  'dietary-fibre',
  '%',
  'Alleen wanneer de bron hemicellulose zelf rapporteert. Niet afleiden uit NDF min ADF')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'lignin',
  'Lignin',
  'chemical',
  'dietary-fibre',
  '%',
  'Lignin. WHICH DETERMINATION was used is a METHOD, recorded on the measurement - acid detergent lignin (Van Soest), Klason, or permanganate. They give different numbers for the same analyte, so a value from a table headed only Lignin is recorded with method unknown rather than assigned to one')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'pectin',
  'Pectin',
  'chemical',
  'dietary-fibre',
  '%',
  'Pectinegehalte zoals de bron het bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'total_dietary_fibre',
  'Total dietary fibre',
  'chemical',
  'dietary-fibre',
  '%',
  'AOAC-voedingsvezel. Niet uitwisselbaar met NDF of ruwe celstof')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'starch',
  'Starch',
  'chemical',
  'carbohydrates',
  '%',
  'Zetmeelgehalte zoals de bron het bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'total_sugars',
  'Total sugars',
  'chemical',
  'carbohydrates',
  '%',
  'Som van vrije mono- en disachariden zoals de bron ze bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'glucose',
  'Glucose',
  'chemical',
  'carbohydrates',
  '%',
  'Vrije glucose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'fructose',
  'Fructose',
  'chemical',
  'carbohydrates',
  '%',
  'Vrije fructose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'sucrose',
  'Sucrose',
  'chemical',
  'carbohydrates',
  '%',
  'Sacharose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'lactose',
  'Lactose',
  'chemical',
  'carbohydrates',
  '%',
  'Lactose - relevant voor zuivel- en weistromen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'hhv',
  'Gross calorific value (HHV)',
  'chemical',
  'energy',
  'MJ/kg',
  'Higher heating value (HHV), ook bruto-energie (GE) in voederwaardebronnen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'lhv',
  'Net calorific value (LHV)',
  'chemical',
  'energy',
  'MJ/kg',
  'Lower heating value (LHV), netto verbrandingswaarde')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'total_carbon',
  'Total carbon (C)',
  'chemical',
  'ultimate',
  '%',
  'Totale koolstof, doorgaans elementair bepaald')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'c_n_ratio',
  'Carbon-to-nitrogen ratio (C/N)',
  'chemical',
  'ultimate',
  'ratio',
  'Verhouding totale koolstof tot totale stikstof zoals de bron ze geeft. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'phosphorus',
  'Phosphorus (P)',
  'chemical',
  'minerals-trace',
  '%',
  'Fosfor uitgedrukt als element P. Wordt de waarde als P2O5 gerapporteerd, gebruik phosphorus_p2o5')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'phosphorus_p2o5',
  'Phosphorus (as P2O5)',
  'chemical',
  'minerals-trace',
  '%',
  'Fosfor uitgedrukt als fosforpentoxide, de gangbare agronomische vorm. Een andere gerapporteerde grootheid dan P, niet een andere eenheid')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'potassium',
  'Potassium (K)',
  'chemical',
  'minerals-trace',
  '%',
  'Kalium uitgedrukt als element K')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'potassium_k2o',
  'Potassium (as K2O)',
  'chemical',
  'minerals-trace',
  '%',
  'Kalium uitgedrukt als kaliumoxide, de gangbare agronomische vorm')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'calcium',
  'Calcium (Ca)',
  'chemical',
  'minerals-trace',
  '%',
  'Calcium als element Ca')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'magnesium',
  'Magnesium (Mg)',
  'chemical',
  'minerals-trace',
  '%',
  'Magnesium als element Mg')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'sodium',
  'Sodium (Na)',
  'chemical',
  'minerals-trace',
  '%',
  'Natrium als element Na')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'sulphur',
  'Sulphur (S)',
  'chemical',
  'ultimate',
  '%',
  'Zwavel als element S')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'chloride',
  'Chloride (water-soluble)',
  'chemical',
  'minerals-trace',
  '%',
  'Chloride')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'iron',
  'Iron (Fe)',
  'chemical',
  'minerals-trace',
  'mg/kg',
  'IJzer als element Fe')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'zinc',
  'Zinc (Zn)',
  'chemical',
  'minerals-trace',
  'mg/kg',
  'Zink als element Zn')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'copper',
  'Copper (Cu)',
  'chemical',
  'minerals-trace',
  'mg/kg',
  'Koper als element Cu')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'manganese',
  'Manganese (Mn)',
  'chemical',
  'minerals-trace',
  'mg/kg',
  'Mangaan als element Mn')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'cadmium',
  'Cadmium (Cd)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Cadmium - zwaar metaal, bepalend voor toelaatbare toepassingen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'lead',
  'Lead (Pb)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Lood - zwaar metaal')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'mercury',
  'Mercury (Hg)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Kwik - zwaar metaal')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'arsenic',
  'Arsenic (As)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Arseen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'chromium',
  'Chromium (Cr)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Chroom, totaal tenzij de bron een species noemt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'nickel',
  'Nickel (Ni)',
  'chemical',
  'heavy-metals-contaminants',
  'mg/kg',
  'Nikkel')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'ph',
  'pH',
  'chemical',
  'miscellaneous',
  'pH',
  'pH van de stof of van een gestandaardiseerd extract. De extractiemethode van de bron hoort in notes. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'total_polyphenols',
  'Total polyphenols',
  'chemical',
  'bioactive',
  'mg/100g',
  'Totale fenolen, doorgaans als gallinezuurequivalent (GAE). Het equivalent van de bron hoort in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'cod',
  'Chemical oxygen demand (COD)',
  'chemical',
  'miscellaneous',
  'mg/L',
  'CZV of COD - relevant voor vloeibare stromen zoals wei en proceswater')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'bod',
  'Biochemical oxygen demand (BOD5)',
  'chemical',
  'miscellaneous',
  'mg/L',
  'BZV of BOD5')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'bulk_density',
  'Bulk density',
  'physical',
  'physical-properties',
  'kg/m3',
  'Stortgewicht van het materiaal zoals gemeten. Bepalend voor de transportlaag van het model')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'particle_size_d50',
  'Median particle size (d50)',
  'physical',
  'physical-properties',
  'mm',
  'Mediane deeltjesgrootte')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'water_holding_capacity',
  'Water-holding capacity',
  'physical',
  'physical-properties',
  'g/g',
  'Gram water per gram droge stof die het materiaal vasthoudt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'electrical_conductivity',
  'Electrical conductivity',
  'physical',
  'physical-properties',
  'mS/cm',
  'EC van een gestandaardiseerd extract. Extractiemethode in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'water_activity',
  'Water activity (aw)',
  'physical',
  'physical-properties',
  'ratio',
  'aw-waarde. Bepalend voor houdbaarheid en microbiologische stabiliteit. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'hydrogen',
  'Hydrogen (H)',
  'chemical',
  'ultimate',
  '%',
  'Elementaire waterstof uit de ultieme analyse. Standaard gerapporteerd naast C, N, O en S door verbrandingsgerichte bronnen zoals Phyllis2')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'oxygen',
  'Oxygen (O)',
  'chemical',
  'ultimate',
  '%',
  'Elementaire zuurstof uit de ultieme analyse. Doorgaans als verschil bepaald in plaats van gemeten - leg vast wat de bron zegt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'volatile_matter',
  'Volatile matter',
  'chemical',
  'proximate-fuel',
  '%',
  'Proximate-analyse - massaverlies bij verhitten zonder zuurstof, doorgaans bij 900 graden C. NIET de basis volatile_solids en NIET organische stof')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'fixed_carbon',
  'Fixed carbon',
  'chemical',
  'proximate-fuel',
  '%',
  'Proximate-analyse-restpost - 100 min vocht min as min vluchtige bestanddelen. Een verschilberekening van de bron, geen meting')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'chlorine',
  'Chlorine (total Cl)',
  'chemical',
  'ultimate',
  'mg/kg',
  'Totaal chloor uit elementaire analyse. Een andere bepaling dan chloride, dat de wateroplosbare Cl-ionen meet - beide bestaan naast elkaar')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'insoluble_ash',
  'Insoluble ash',
  'chemical',
  'ash-solids',
  '%',
  'Zoutzuur-onoplosbaar asresidu, een maat voor grond- en zandinsleep. Voederwaardetabellen rapporteren dit naast ruw as')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'tannins',
  'Tannins',
  'chemical',
  'bioactive',
  'g/kg',
  'Condensed and hydrolysable tannins. Sources usually express them as a tannic acid equivalent - record the equivalent in the measurement notes. INFOODS nests Tannins under Bioactive constituents')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'glucosinolates',
  'Glucosinolates',
  'chemical',
  'bioactive',
  'umol/g',
  'Total glucosinolates. The characteristic secondary metabolite of brassica and of rapeseed meal, and a constraint on feed use - which is why it belongs in the catalogue rather than in prose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'selenium',
  'Selenium (Se)',
  'chemical',
  'minerals-trace',
  'mg/kg',
  'Selenium as element Se')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, group_code, default_unit_code, definition)
  VALUES (
  'condensed_tannins',
  'Condensed tannins',
  'chemical',
  'bioactive',
  'g/kg',
  'Condensed tannins (proanthocyanidins), usually as a catechin equivalent. A DIFFERENT FRACTION from total tannins, not another way of measuring them - so its own parameter')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, group_code = EXCLUDED.group_code,
    default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
