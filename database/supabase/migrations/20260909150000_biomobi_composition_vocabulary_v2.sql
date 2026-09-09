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
-- 28 units, 6 bases, 68 parameters.

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

-- 3. the parameter catalogue. default_unit_code is a HINT ONLY -- every measurement
--    records its own unit, and units may differ between measurements of one parameter.
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'dry_matter',
  'Droge stof',
  'chemical',
  '%',
  'Massafractie die overblijft na drogen tot constant gewicht, doorgaans bij 103-105 graden C. Bronnen schrijven DM, TS, DS of droge stof. Wordt vrijwel altijd op verse basis gerapporteerd')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'moisture',
  'Vochtgehalte',
  'chemical',
  '%',
  'Watergehalte zoals de bron het rapporteert. Apart geregistreerd van droge stof omdat bronnen het zo geven - niet afleiden, alleen vastleggen wat er staat')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'ash',
  'Ruw as',
  'chemical',
  '%',
  'Anorganisch residu na verassing, doorgaans bij 550 graden C. Weende-parameter')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'organic_matter',
  'Organische stof',
  'chemical',
  '%',
  'Droge stof min as. Bronnen over anaerobe vergisting schrijven hier vaak VS - leg de term van de bron vast in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'crude_protein',
  'Ruw eiwit',
  'chemical',
  '%',
  'Kjeldahl- of Dumas-stikstof maal een omrekeningsfactor, meestal 6,25. METHODE-BEPAALD - de gebruikte factor hoort in notes. Niet uitwisselbaar met zuiver eiwit')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_nitrogen',
  'Totale stikstof',
  'chemical',
  '%',
  'Kjeldahl- of Dumas-stikstof zelf, zonder eiwitfactor. Registreer dit wanneer de bron N geeft en niet het eiwit')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'true_protein',
  'Zuiver eiwit',
  'chemical',
  '%',
  'Eiwit bepaald als som van aminozuren of na aftrek van niet-eiwitstikstof. Een ander object dan ruw eiwit, niet een betere meting ervan')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'crude_fat',
  'Ruw vet',
  'chemical',
  '%',
  'Ether-extract volgens Weende of Soxhlet. Bronnen schrijven EE, ruw vet, lipiden of vetgehalte')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'crude_fibre',
  'Ruwe celstof',
  'chemical',
  '%',
  'Weende-ruwe celstof. METHODE-BEPAALD en niet vergelijkbaar met NDF, ADF of voedingsvezel')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'nfe',
  'Stikstofvrije extractstoffen',
  'chemical',
  '%',
  'Weende-restpost (NFE). Een verschilberekening van de bron, geen meting - alleen vastleggen wanneer de bron hem geeft')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'ndf',
  'Neutral detergent fibre',
  'chemical',
  '%',
  'Van Soest-celwand - cellulose plus hemicellulose plus lignine. Vermeld in notes of de bron aNDF of aNDFom bedoelt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'adf',
  'Acid detergent fibre',
  'chemical',
  '%',
  'Van Soest - cellulose plus lignine')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'adl',
  'Acid detergent lignin',
  'chemical',
  '%',
  'Van Soest-lignine')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'cellulose',
  'Cellulose',
  'chemical',
  '%',
  'Alleen wanneer de bron cellulose zelf rapporteert. Niet afleiden uit ADF min ADL - dat is een berekening en hoort in de modellaag')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'hemicellulose',
  'Hemicellulose',
  'chemical',
  '%',
  'Alleen wanneer de bron hemicellulose zelf rapporteert. Niet afleiden uit NDF min ADF')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'lignin',
  'Lignine',
  'chemical',
  '%',
  'Lignine bepaald langs een andere weg dan ADL, bijvoorbeeld Klason. Methode van de bron in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'pectin',
  'Pectine',
  'chemical',
  '%',
  'Pectinegehalte zoals de bron het bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_dietary_fibre',
  'Totale voedingsvezel',
  'chemical',
  '%',
  'AOAC-voedingsvezel. Niet uitwisselbaar met NDF of ruwe celstof')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'starch',
  'Zetmeel',
  'chemical',
  '%',
  'Zetmeelgehalte zoals de bron het bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_sugars',
  'Totale suikers',
  'chemical',
  '%',
  'Som van vrije mono- en disachariden zoals de bron ze bepaalt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'glucose',
  'Glucose',
  'chemical',
  '%',
  'Vrije glucose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'fructose',
  'Fructose',
  'chemical',
  '%',
  'Vrije fructose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'sucrose',
  'Sucrose',
  'chemical',
  '%',
  'Sacharose')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'lactose',
  'Lactose',
  'chemical',
  '%',
  'Lactose - relevant voor zuivel- en weistromen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'hhv',
  'Bovenste verbrandingswaarde',
  'chemical',
  'MJ/kg',
  'Higher heating value (HHV), ook bruto-energie (GE) in voederwaardebronnen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'lhv',
  'Onderste verbrandingswaarde',
  'chemical',
  'MJ/kg',
  'Lower heating value (LHV), netto verbrandingswaarde')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_carbon',
  'Totale koolstof',
  'chemical',
  '%',
  'Totale koolstof, doorgaans elementair bepaald')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'c_n_ratio',
  'C/N-verhouding',
  'chemical',
  'ratio',
  'Verhouding totale koolstof tot totale stikstof zoals de bron ze geeft. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'phosphorus',
  'Fosfor (P)',
  'chemical',
  '%',
  'Fosfor uitgedrukt als element P. Wordt de waarde als P2O5 gerapporteerd, gebruik phosphorus_p2o5')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'phosphorus_p2o5',
  'Fosfor (P2O5)',
  'chemical',
  '%',
  'Fosfor uitgedrukt als fosforpentoxide, de gangbare agronomische vorm. Een andere gerapporteerde grootheid dan P, niet een andere eenheid')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'potassium',
  'Kalium (K)',
  'chemical',
  '%',
  'Kalium uitgedrukt als element K')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'potassium_k2o',
  'Kalium (K2O)',
  'chemical',
  '%',
  'Kalium uitgedrukt als kaliumoxide, de gangbare agronomische vorm')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'calcium',
  'Calcium',
  'chemical',
  '%',
  'Calcium als element Ca')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'magnesium',
  'Magnesium',
  'chemical',
  '%',
  'Magnesium als element Mg')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'sodium',
  'Natrium',
  'chemical',
  '%',
  'Natrium als element Na')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'sulphur',
  'Zwavel',
  'chemical',
  '%',
  'Zwavel als element S')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'chloride',
  'Chloride',
  'chemical',
  '%',
  'Chloride')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'iron',
  'IJzer',
  'chemical',
  'mg/kg',
  'IJzer als element Fe')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'zinc',
  'Zink',
  'chemical',
  'mg/kg',
  'Zink als element Zn')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'copper',
  'Koper',
  'chemical',
  'mg/kg',
  'Koper als element Cu')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'manganese',
  'Mangaan',
  'chemical',
  'mg/kg',
  'Mangaan als element Mn')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'cadmium',
  'Cadmium',
  'chemical',
  'mg/kg',
  'Cadmium - zwaar metaal, bepalend voor toelaatbare toepassingen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'lead',
  'Lood',
  'chemical',
  'mg/kg',
  'Lood - zwaar metaal')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'mercury',
  'Kwik',
  'chemical',
  'mg/kg',
  'Kwik - zwaar metaal')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'arsenic',
  'Arseen',
  'chemical',
  'mg/kg',
  'Arseen')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'chromium',
  'Chroom',
  'chemical',
  'mg/kg',
  'Chroom, totaal tenzij de bron een species noemt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'nickel',
  'Nikkel',
  'chemical',
  'mg/kg',
  'Nikkel')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'ph',
  'Zuurtegraad',
  'chemical',
  'pH',
  'pH van de stof of van een gestandaardiseerd extract. De extractiemethode van de bron hoort in notes. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_polyphenols',
  'Totale polyfenolen',
  'chemical',
  'mg/100g',
  'Totale fenolen, doorgaans als gallinezuurequivalent (GAE). Het equivalent van de bron hoort in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'cod',
  'Chemisch zuurstofverbruik',
  'chemical',
  'mg/L',
  'CZV of COD - relevant voor vloeibare stromen zoals wei en proceswater')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'bod',
  'Biochemisch zuurstofverbruik',
  'chemical',
  'mg/L',
  'BZV of BOD5')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'bulk_density',
  'Bulkdichtheid',
  'physical',
  'kg/m3',
  'Stortgewicht van het materiaal zoals gemeten. Bepalend voor de transportlaag van het model')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'particle_size_d50',
  'Deeltjesgrootte d50',
  'physical',
  'mm',
  'Mediane deeltjesgrootte')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'water_holding_capacity',
  'Waterbindend vermogen',
  'physical',
  'g/g',
  'Gram water per gram droge stof die het materiaal vasthoudt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'electrical_conductivity',
  'Elektrische geleidbaarheid',
  'physical',
  'mS/cm',
  'EC van een gestandaardiseerd extract. Extractiemethode in notes')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'water_activity',
  'Wateractiviteit',
  'physical',
  'ratio',
  'aw-waarde. Bepalend voor houdbaarheid en microbiologische stabiliteit. Basis is n.a.')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'total_plate_count',
  'Totaal kiemgetal',
  'microbiological',
  'cfu/g',
  'Totaal aeroob kiemgetal')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'enterobacteriaceae',
  'Enterobacteriaceae',
  'microbiological',
  'cfu/g',
  'Enterobacteriaceae-telling')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'yeasts_and_moulds',
  'Gisten en schimmels',
  'microbiological',
  'cfu/g',
  'Telling van gisten en schimmels')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'escherichia_coli',
  'Escherichia coli',
  'microbiological',
  'cfu/g',
  'E. coli-telling')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'salmonella',
  'Salmonella spp.',
  'microbiological',
  'n.a.',
  'Doorgaans kwalitatief gerapporteerd als aan- of afwezig in 25 g - dan value_type qualitative met de tekst van de bron in value_text')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'listeria_monocytogenes',
  'Listeria monocytogenes',
  'microbiological',
  'cfu/g',
  'Telling of aan-/afwezigheid. Bij aan-/afwezigheid value_type qualitative')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'hydrogen',
  'Waterstof (H)',
  'chemical',
  '%',
  'Elementaire waterstof uit de ultieme analyse. Standaard gerapporteerd naast C, N, O en S door verbrandingsgerichte bronnen zoals Phyllis2')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'oxygen',
  'Zuurstof (O)',
  'chemical',
  '%',
  'Elementaire zuurstof uit de ultieme analyse. Doorgaans als verschil bepaald in plaats van gemeten - leg vast wat de bron zegt')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'volatile_matter',
  'Vluchtige bestanddelen',
  'chemical',
  '%',
  'Proximate-analyse - massaverlies bij verhitten zonder zuurstof, doorgaans bij 900 graden C. NIET de basis volatile_solids en NIET organische stof')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'fixed_carbon',
  'Vaste koolstof',
  'chemical',
  '%',
  'Proximate-analyse-restpost - 100 min vocht min as min vluchtige bestanddelen. Een verschilberekening van de bron, geen meting')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'chlorine',
  'Chloor (Cl totaal)',
  'chemical',
  'mg/kg',
  'Totaal chloor uit elementaire analyse. Een andere bepaling dan chloride, dat de wateroplosbare Cl-ionen meet - beide bestaan naast elkaar')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
INSERT INTO parameter (code, name, category, default_unit_code, definition) VALUES (
  'insoluble_ash',
  'Onoplosbare as',
  'chemical',
  '%',
  'Zoutzuur-onoplosbaar asresidu, een maat voor grond- en zandinsleep. Voederwaardetabellen rapporteren dit naast ruw as')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name,
    category = EXCLUDED.category, default_unit_code = EXCLUDED.default_unit_code,
    definition = EXCLUDED.definition;
