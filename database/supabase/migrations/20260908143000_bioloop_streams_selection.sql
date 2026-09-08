-- BioMobi vocabulary: the register's 80% stream selection, at object grain.
-- BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities)
--
-- GENERATED -- do not hand-edit. Regenerate with, from database/streams/:
--   ../.venv/Scripts/python tools/load_streams.py --emit-migration <path>
-- The source of truth is crosswalks/register_streams.csv (human DECISION gate)
-- plus the register corpus it is checked against on every run.
--
-- When the selection changes -- resolved gaps adding or renaming objects -- write
-- a NEW migration from the updated manifest; never edit this one. Every statement
-- is ON CONFLICT-guarded, so re-applying it is a no-op.
--
-- 20 objects, 4 + 7 commodity terms, 1 scheme.
-- No supply_observation rows: source_key is NOT NULL and the register's PDFs have
-- no citation keys yet (flag F-002).

-- 1. the facet
INSERT INTO classification_scheme (code, name) VALUES ('bioloop-commodity', 'Commodityniveau (BIOLOOP-register L2 -> L3)')
  ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

-- 2. the commodity ladder: L2 parents first, then L3 children pointing at them
INSERT INTO classification_term (scheme_code, code, label) VALUES ('bioloop-commodity', 'plantaardig-akkerbouw', 'Plantaardig - akkerbouw')
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label;
INSERT INTO classification_term (scheme_code, code, label) VALUES ('bioloop-commodity', 'varia', 'Varia')
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label;
INSERT INTO classification_term (scheme_code, code, label) VALUES ('bioloop-commodity', 'plantaardig-tuinbouw', 'Plantaardig - tuinbouw')
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label;
INSERT INTO classification_term (scheme_code, code, label) VALUES ('bioloop-commodity', 'dierlijk-vee', 'Dierlijk - vee')
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'granen', 'Granen', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'plantaardig-akkerbouw'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'oliehoudende-gewassen', 'Oliehoudende gewassen', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'plantaardig-akkerbouw'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'aardappelen-en-knolgewassen', 'Aardappelen en knolgewassen', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'plantaardig-akkerbouw'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'suikerbieten-en-nijverheidsgewassen', 'Suikerbieten en nijverheidsgewassen', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'plantaardig-akkerbouw'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'zetmeel-en-zetmeelproducten', 'Zetmeel en zetmeelproducten', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'varia'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'groenten-openlucht', 'Groenten openlucht', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'plantaardig-tuinbouw'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;
INSERT INTO classification_term (scheme_code, code, label, parent_term_id)
  SELECT 'bioloop-commodity', 'vlees', 'Vlees', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'dierlijk-vee'
  ON CONFLICT (scheme_code, code) DO UPDATE SET label = EXCLUDED.label,
    parent_term_id = EXCLUDED.parent_term_id;

-- 3. the objects
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'mais-stro',
  'Maisstro',
  'Maisstro dat na de oogst op het veld achterblijft en wordt ingewerkt (productieresidu).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Mais'' staat op rang 1 met 1.456.062 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''stro''; Grootste eigen claim 1.456.062 t (C-427 / MONBIO 3.0). Claims: C-246 C-427. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'raapzaad-schroot',
  'Kool- en raapzaadschroot',
  'Meel/schroot uit de persing van kool- en raapzaad (FEDIOL-crush). Belgisch cijfer, geen Vlaams.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Kool- en raapzaad'' staat op rang 2 met 857.931 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 852.000 t (C-520 / MONBIO 3.0). Claims: C-331 C-520. Geografie: Belgie. LET OP: het cijfer is Belgisch, niet Vlaams -- open vraag in state.md of BioMobi een Belgisch cijfer als Vlaams stroomvolume aanvaardt. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'raapzaad-stro',
  'Kool- en raapzaadstro',
  'Kool- en raapzaadstro dat van het veld wordt gehaald (nevenstroom).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Kool- en raapzaad'' staat op rang 2 met 857.931 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''stro''; Grootste eigen claim 7.818 t (C-256 / MONBIO 4.0). Claims: C-256 C-431. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'aardappel',
  'Aardappel',
  'De aardappel zelf: niet-geoogste en afgekeurde knollen, en de reststroom van de aardappelverwerking die de bron enkel als Prodcom 103113 benoemt (meel, gries, vlokken, korrels en pellets van gedroogde aardappelen). Geen bron in het corpus benoemt een fijner aardappelobject zoals schillen - zie gap G-10.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Aardappel'' staat op rang 3 met 855.393 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 429.871 t (C-057 / OVAM Monitor voedselverlies 2023). Claims: C-005 C-042 C-057 C-068 C-167 C-179 C-314 C-501. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'aardappel-loof',
  'Aardappelloof',
  'Aardappelloof, voor de oogst gedood en ondergewerkt (productieresidu).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Aardappel'' staat op rang 3 met 855.393 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''loof''; Grootste eigen claim 800.480 t (C-428 / MONBIO 3.0). Claims: C-247 C-428. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'suikerbiet',
  'Suikerbiet',
  'De biet zelf: afgekeurde en niet-geoogste suikerbieten.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Suikerbiet'' staat op rang 4 met 812.224 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 48.662 t (C-154 / OVAM Monitor voedselverlies 2020). Claims: C-041 C-056 C-067 C-154 C-166 C-178. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'suikerbiet-loof',
  'Suikerbietenloof',
  'Bietenloof dat op het veld achterblijft en wordt ingewerkt (productieresidu).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Suikerbiet'' staat op rang 4 met 812.224 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''loof''; Grootste eigen claim 463.884 t (C-429 / MONBIO 3.0). Claims: C-248 C-429. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'suikerbiet-pulp',
  'Bietenpulp',
  'Uitgeloogde bietenpulp uit de suikerfabriek (nevenstroom).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Suikerbiet'' staat op rang 4 met 812.224 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''pulp''; Grootste eigen claim 350.000 t (C-382 / MONBIO 4.0). Claims: C-382 C-575. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'zetmeel-reststroom',
  'Zetmeelreststroom',
  'Afvallen van zetmeelfabrieken en dergelijke (Prodcom 106220). LET OP: dit object is benoemd naar de fabriek die het verlaat, niet naar wat het is - de bron zegt niet meer dan dit.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Zetmeel'' staat op rang 5 met 284.549 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 284.549 t (C-550 / MONBIO 3.0). Claims: C-550. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'zemelen',
  'Zemelen',
  'Zemelen, slijpsel en andere resten van het bewerken van granen (Prodcom 106140).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Zemelen'' staat op rang 6 met 278.865 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 278.865 t (C-549 / MONBIO 3.0). Claims: C-358 C-549. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'tarwe-stro',
  'Tarwestro',
  'Tarwestro dat van het veld wordt gehaald, ingezet als strooisel of structuurmateriaal.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Tarwe'' staat op rang 7 met 255.836 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''stro''; Grootste eigen claim 255.836 t (C-249 / MONBIO 4.0). Claims: C-249 C-430. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'lijnzaad-schroot',
  'Lijnzaadschroot',
  'Meel/schroot uit de persing van lijnzaad (FEDIOL-crush). Belgisch cijfer, geen Vlaams.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Lijnzaad'' staat op rang 8 met 245.000 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 245.000 t (C-333 / MONBIO 4.0). Claims: C-333 C-522. Geografie: Belgie. LET OP: het cijfer is Belgisch, niet Vlaams -- open vraag in state.md of BioMobi een Belgisch cijfer als Vlaams stroomvolume aanvaardt. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'bloemkool',
  'Bloemkool',
  'De kool zelf: afgekeurde bloemkool. Het corpus meet dit object op drie ketenschakels (veld, veiling/doordraai, verwerkende industrie); die schakel hoort bij de waarneming, niet bij het object.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Bloemkool'' staat op rang 9 met 201.311 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 16.388 t (C-610 / ILVO 239 tuinbouw). Claims: C-610 C-611 C-612 C-769 C-778. Geografie: Belgie | Vlaanderen. Claims mengen Vlaamse en Belgische geografie. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'bloemkool-harten',
  'Bloemkoolharten',
  'Eetbare nevenstroom van machinaal geoogste bloemkool.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Bloemkool'' staat op rang 9 met 201.311 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''harten''; Grootste eigen claim 18.395 t (C-255 / MONBIO 4.0). Claims: C-255 C-437. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'bloemkool-loof',
  'Bloemkoolloof',
  'Blad- en stengelmassa van bloemkool, oogstrest op het veld. Twee bronnen benoemen hetzelfde materiaal anders (GeNeSys: blad- en stengelmassa; MONBIO: bloemkoolloof).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Bloemkool'' staat op rang 9 met 201.311 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''loof''; Grootste eigen claim 197.100 t (C-706 / GeNeSys ILVO 165). Claims: C-250 C-432 C-706. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'soja-schroot',
  'Sojaschroot',
  'Meel/schroot uit de persing van soja (FEDIOL-crush). Belgisch cijfer, geen Vlaams.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Soja'' staat op rang 10 met 170.000 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 170.000 t (C-519 / MONBIO 3.0). Claims: C-330 C-519. Geografie: Belgie. LET OP: het cijfer is Belgisch, niet Vlaams -- open vraag in state.md of BioMobi een Belgisch cijfer als Vlaams stroomvolume aanvaardt. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'slachtafval-niet-eetbaar',
  'Niet-eetbare ruwe slachtafvallen',
  'Niet-eetbare ruwe slachtafvallen (Prodcom 101160), NACE 10.11. De bron bundelt meerdere diersoorten - zie gap G-04.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Niet-eetbare slachtafvallen'' staat op rang 11 met 169.051 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 169.051 t (C-298 / MONBIO 4.0). Claims: C-298 C-483. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'dierlijk-vet',
  'Dierlijk vet',
  'Rund-, schapen-, geiten- of varkensvet (Prodcom 101150), NACE 10.11.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Dierlijk vet'' staat op rang 12 met 145.498 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 145.498 t (C-297 / MONBIO 4.0). Claims: C-297 C-482. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'spruiten',
  'Spruiten',
  'De spruit zelf: afgekeurde spruiten in het afzetkanaal industrie.',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Spruiten'' staat op rang 13 met 138.000 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Geen fractie: dit is de commodity zelf. Grootste eigen claim 5.452 t (C-618 / ILVO 239 tuinbouw). Claims: C-618 C-619 C-620. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;
INSERT INTO stream (code, canonical_name, description, notes) VALUES (
  'spruitstokken',
  'Spruitstokken',
  'Spruitstokken / stengelmassa, oogstrest op het veld. Twee bronnen benoemen hetzelfde materiaal anders (GeNeSys: stengelmassa; MONBIO: spruitstokken).',
  'Geregistreerd uit BIOLOOP kandidaat-stroomselectie 2026-09-04 (register, 80%-lijn = 13 commodities). Commodity ''Spruiten'' staat op rang 13 met 138.000 t/jaar (register-methode: het grootste cijfer dat een enkele bron aan de commodity geeft; NIET optelbaar over de fracties heen). Fractie ''stokken''; Grootste eigen claim 138.000 t (C-735 / GeNeSys ILVO 165). Claims: C-251 C-434 C-735. Geografie: Vlaanderen. Nog geen supply_observation -- zie F-002.')
  ON CONFLICT (code) DO UPDATE SET canonical_name = EXCLUDED.canonical_name,
    description = EXCLUDED.description, notes = EXCLUDED.notes;

-- 4. rebuild this loader's classification links -- its ownership namespace is
--    every code the manifest names, inside the scheme above. Nothing else is
--    touched, and no stream row is ever deleted.
DELETE FROM stream_classification sc USING classification_term t
  WHERE sc.term_id = t.term_id
    AND t.scheme_code = 'bioloop-commodity'
    AND sc.stream_code IN ('mais-stro', 'raapzaad-schroot', 'raapzaad-stro', 'aardappel', 'aardappel-loof', 'suikerbiet', 'suikerbiet-loof', 'suikerbiet-pulp', 'zetmeel-reststroom', 'zemelen', 'tarwe-stro', 'lijnzaad-schroot', 'bloemkool', 'bloemkool-harten', 'bloemkool-loof', 'soja-schroot', 'slachtafval-niet-eetbaar', 'dierlijk-vet', 'spruiten', 'spruitstokken');

-- each object is linked to its L3; the L2 is reachable through parent_term_id.
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'mais-stro', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'granen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'raapzaad-schroot', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'oliehoudende-gewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'raapzaad-stro', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'oliehoudende-gewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'aardappel', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'aardappelen-en-knolgewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'aardappel-loof', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'aardappelen-en-knolgewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'suikerbiet', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'suikerbieten-en-nijverheidsgewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'suikerbiet-loof', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'suikerbieten-en-nijverheidsgewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'suikerbiet-pulp', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'suikerbieten-en-nijverheidsgewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'zetmeel-reststroom', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'zetmeel-en-zetmeelproducten'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'zemelen', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'granen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'tarwe-stro', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'granen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'lijnzaad-schroot', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'oliehoudende-gewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'bloemkool', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'groenten-openlucht'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'bloemkool-harten', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'groenten-openlucht'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'bloemkool-loof', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'groenten-openlucht'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'soja-schroot', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'oliehoudende-gewassen'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'slachtafval-niet-eetbaar', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'vlees'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'dierlijk-vet', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'vlees'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'spruiten', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'groenten-openlucht'
  ON CONFLICT DO NOTHING;
INSERT INTO stream_classification (stream_code, term_id)
  SELECT 'spruitstokken', term_id FROM classification_term
   WHERE scheme_code = 'bioloop-commodity' AND code = 'groenten-openlucht'
  ON CONFLICT DO NOTHING;

