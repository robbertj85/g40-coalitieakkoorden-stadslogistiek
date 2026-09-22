# Plan: stadslogistiek in de coalitieakkoorden 2026 van G4 + G40

Doel: voor alle 45 gemeenten (G4 + de 41 leden van het G40-stedennetwerk) het
coalitie-/bestuursakkoord vinden dat na de gemeenteraadsverkiezingen van
18 maart 2026 is gesloten, en daaruit alle passages over stadslogistiek en
goederenvervoer letterlijk overnemen. Waar die ontbreken: samenvatting van de
plannen voor mobiliteit en stedelijke economie. Resultaat: `index.html`,
gesorteerd op gemeente, met bronlinks en paginaverwijzingen.

## Bestanden

| Pad | Rol |
|---|---|
| `data/status.json` | Enige bron van waarheid. Eén record per gemeente (45). Bevat ook de zoektermen. |
| `data/raw/<slug>.pdf/.html/.txt` | Gedownloade akkoorden en de geëxtraheerde tekst. |
| `tools/fetch_and_grep.py` | Download een akkoord, extraheert tekst, print treffers met paginanummer. |
| `tools/build_html.py` | Bouwt `index.html` uit `status.json`. Altijd draaien na elke wijziging. |
| `tools/insights.html` | De clusteranalyse: welke akkoorden iets over stadslogistiek zeggen en welke gemeenten ongeveer hetzelfde willen (uitklapbaar blok bovenaan `index.html`). Handgeschreven; elk „citaat” moet letterlijk in een bron staan. |
| `tools/verify_insights.py` | Controleert dat elk „citaat” in `insights.html` letterlijk voorkomt in `status.json`, `data/raw/*.txt`, de DMI-stukken (`../dmi-slimmelogistiek`) of de vorige versie, en dat alle `#anker`-links bestaan. Draaien vóór `build_html.py`. |
| `LOOP_PROMPT.md` | De exacte prompt voor de `/loop`-run. |
| `index.html` | Het eindresultaat. |

## Statuswaarden per gemeente

- `todo` – nog niet gezocht.
- `in_progress` – akkoord gevonden/gedownload, analyse nog niet af.
- `found_analysed` – klaar: akkoord gevonden, quotes + samenvattingen ingevuld.
- `not_found` – gezocht, maar (nog) geen akkoord gevonden. `retries` telt de pogingen; bij 3+ pogingen alleen nog wekelijks opnieuw proberen.
- `no_agreement` – gemeente heeft aantoonbaar geen klassiek coalitieakkoord (bijv. raadsakkoord op hoofdlijnen zonder document, of formatie is mislukt). Toelichting in `notes`.

## Werkwijze per gemeente (één iteratie van de loop = één gemeente)

1. **Kies** de eerste gemeente in `data/status.json` met status `todo`, daarna
   `in_progress`, daarna `not_found` met de laagste `retries`. Zet status op
   `in_progress` en vul `last_checked` (YYYY-MM-DD).
2. **Zoek het akkoord** met WebSearch. Probeer in deze volgorde, stop zodra je een
   officieel document hebt:
   - `<gemeente> coalitieakkoord 2026-2030`
   - `<gemeente> coalitieakkoord 2026 pdf`
   - `<gemeente> bestuursakkoord 2026` / `raadsakkoord 2026` / `hoofdlijnenakkoord 2026` / `coalitieprogramma 2026`
   - `site:<gemeente>.nl coalitieakkoord` (domein soms afwijkend: denhaag.nl, s-hertogenbosch.nl, sittard-geleen.nl, alphenaandenrijn.nl, haarlemmermeer.nl)
   - `<gemeente> raadsinformatie coalitieakkoord 2026` (portalen: `*.raadsinformatie.nl`, `*.bestuurlijkeinformatie.nl`, `*.notubiz.nl`, `ibabs`)
   - `<gemeente> nieuwe coalitie 2026` (nieuwsberichten geven partijen, datum en vaak de link)
   Voorkeur voor bron: 1) PDF op gemeentesite, 2) PDF in raadsinformatiesysteem,
   3) PDF op partijsite, 4) HTML-pagina op gemeentesite. Let op: alleen akkoorden
   van ná 18 maart 2026. Een akkoord "2022-2026" is de vorige periode: negeren.
   Verwar het niet met het landelijke coalitieakkoord "Aan de slag 2026-2030".
3. **Download en grep**:
   ```
   python3 tools/fetch_and_grep.py <slug> "<url>"                 # primaire termen (stadslogistiek e.d.)
   python3 tools/fetch_and_grep.py <slug> --local --set mobility   # daarna mobiliteit
   python3 tools/fetch_and_grep.py <slug> --local --set economy    # daarna economie
   python3 tools/fetch_and_grep.py <slug> --local --term "laden en lossen" --context 500   # ruimere context van één passage
   ```
   Lukt de download niet (403, login, geen PDF): probeer een andere bron uit
   stap 2, of gebruik WebFetch op de HTML-pagina en noteer in `notes` dat de
   paginanummers ontbreken.
4. **Analyseer**:
   - Elke treffer op een primaire term die écht over goederenvervoer, bevoorrading,
     stadslogistiek, bouwlogistiek, pakketbezorging, ZE-zone voor vracht/bestel,
     hubs voor goederen, laden/lossen, venstertijden voor bevoorrading, binnenvaart
     of haven gaat → als quote opnemen: **letterlijk**, volledige zin(nen), met
     paginanummer en de gevonden term. Geen parafrase. Schrap valse treffers
     (bijv. "handhaven", "investeringspakket", "hub" als het om een OV-/parkeerhub
     gaat – die hoort bij mobiliteit).
   - `city_logistics_found`: `true` als er ≥1 echte quote is, anders `false`.
   - `mobility_summary`: 3–6 zinnen over bereikbaarheid, auto, parkeren, fiets, OV,
     30 km/u, autoluw, milieuzone/ZE-zone. Altijd invullen, ook als er wél
     stadslogistiek-quotes zijn.
   - `economy_summary`: 2–5 zinnen over economie, binnenstad, ondernemers,
     bedrijventerreinen, werklocaties. Altijd invullen.
   - `agreement`: `title` (officiële titel), `type` (coalitieakkoord / bestuursakkoord /
     raadsakkoord / hoofdlijnenakkoord), `parties` (lijst), `date` (presentatiedatum,
     YYYY-MM-DD of YYYY-MM), `url` (direct document), `source_page` (webpagina
     waar het document staat), `local_file` (bijv. `data/raw/utrecht.pdf`).
5. **Schrijf terug** naar `data/status.json` (status `found_analysed`, of
   `not_found` met `retries += 1` en een `notes`-regel met wat je geprobeerd hebt).
   Gebruik een klein Python-script dat het JSON-bestand laadt, één record wijzigt
   en weer wegschrijft met `indent=2, ensure_ascii=False`. Nooit het hele bestand
   met de hand overtypen.
6. **Bouw de HTML**: `python3 tools/build_html.py`.
7. **Rapporteer** in één regel: gemeente, status, aantal quotes, resterend aantal `todo`.

## Stopcriterium voor de loop

Stop (ScheduleWakeup met `stop: true`) als er geen gemeenten meer zijn met status
`todo` of `in_progress`, én elke `not_found` minstens 3 `retries` heeft. Zolang
er `not_found`-gemeenten zijn met < 3 retries: doorgaan, maar probeer dan andere
zoektermen dan de vorige keer (zie `notes`).

Formaties kunnen in september 2026 nog lopen. Een gemeente die nog geen akkoord
heeft, is geen fout: status `not_found`, in `notes` de stand van de formatie
(bijv. "informateur benoemd 2026-06; nog geen akkoord op 2026-09-22").

## Kwaliteitsregels

- Quotes zijn letterlijk, inclusief Nederlandse spelling en typografie. Splits niet
  midden in een zin. Als de PDF-tekst door kolommen door elkaar loopt, lees dan de
  ruimere context (`--context 600`) en reconstrueer de zin uit het origineel; noteer
  in `notes` als je twijfelt.
- Alle 45 gemeenten komen in `index.html`, ook de niet-gevonden.
- Gemeentenaam en slug niet wijzigen; ze zijn de sleutel.
- Voeg geen gemeenten toe. Bij twijfel over het G40-lidmaatschap: de lijst in
  `status.json` is leidend (41 leden per g40stedennetwerk.nl, incl. Amstelveen).

## Voorbeeld

Utrecht (`slug: utrecht`) is volledig ingevuld als voorbeeld van het gewenste
detailniveau. Bekijk dat record in `data/status.json` voordat je begint.

---

# Deel 2: thema-analyse over alle akkoorden (`themes.html`)

Naast het stadslogistiek-rapport staat een tweede rapport dat het hele corpus als
één geheel leest: het algemene beeld (18 thema's) plus een doorsnede op de zeven
DMI-thema's (gebiedsontwikkeling, woningbouw, mobiliteit, energietransitie,
bodem & ondergrond, digitalisering, AI).

## Bestanden

| Pad | Rol |
|---|---|
| `tools/theme_config.json` | Themataxonomie. Drie groepen: `general` (18 algemene thema's), `dmi` (de eerste doorsnede van 7) en `dmi_formeel` (de 7 officiele DMI-thema's). Plus `subtopics` en `scope`. Enige plek waar de taxonomie staat. |
| `tools/theme_scan.py` | Scant `data/raw/*.txt` en schrijft `data/themes.json` (meting) + `data/theme_extracts.json` (leesmateriaal). |
| `data/themes.json` | **Gegenereerd** – niet met de hand bewerken. |
| `data/analysis.json` | **Handgeschreven** duiding + geselecteerde letterlijke citaten. |
| `tools/build_themes_html.py` | Rendert `themes.html`. |
| `tools/quote.py` | Toont volledige zinnen rond een zoekterm, met paginanummer – om citaten te kiezen. |
| `tools/verify_quotes.py` | Faalt als een citaat niet letterlijk op de opgegeven pagina staat. |

## Vaste volgorde na elke wijziging

```
python3 tools/theme_scan.py          # meting bijwerken
python3 tools/build_themes_html.py   # themes.html bouwen
python3 tools/verify_quotes.py       # citaatcontrole (exit 1 bij afwijking)
```

## Twee DMI-indelingen naast elkaar

Het rapport telt hetzelfde corpus langs twee indelingen, die allebei blijven staan:

- **Deel B** &ndash; de eerste doorsnede (`dmi`): gebiedsontwikkeling, woningbouw,
  mobiliteit, energietransitie, bodem & ondergrond, digitalisering, AI.
- **Deel C** &ndash; de officiele DMI-indeling (`dmi_formeel`): ruimte op
  uiteenlopende schaalniveaus, woningbouw, digitaal, energie, water/bodem/
  ondergrond, bereikbaarheid, parkeren & stedelijk-regionaal verkeer.

Ze snijden het corpus bewust anders aan: in deel C hoort water bij bodem en
ondergrond (waardoor dat thema van 216 naar 674 vermeldingen gaat), valt
mobiliteit uiteen in twee thema's en vormen digitalisering en AI er samen een.

## De scope-meting

`scope` in `theme_config.json` bevat vijf groepen (data & ontsluiting,
intelligentie & analytics, visualisatie & modellering, monitoring & meten,
kennis & disseminatie). Die worden **per thema gemeten binnen de passages van dat
thema zelf** (±250 tekens rond elke treffer). Zo meet je niet of een akkoord
uberhaupt over data gaat, maar of het over data gaat *op dit onderwerp*. Het
scherpste resultaat: binnen water/bodem/ondergrond komt in alle 41 akkoorden
samen geen enkel woord uit 'data & ontsluiting' voor.

Het thema Digitaal scoort per definitie hoog (thema-termen en scope-termen
overlappen daar) en dient als ijkpunt, niet als bevinding.

## Meetregels

- Overlappende treffers tellen als één vermelding (`merge_spans`), zodat
  'woningbouw' in 'woningbouwopgave' niet dubbel telt.
- Terugkerende kop-/voetregels (op ≥30% van de pagina's) worden eerst verwijderd
  (`strip_boilerplate`). Zonder die stap telde de paginavoet van Deventer 55 keer
  mee als vermelding van laadinfrastructuur.
- Deelonderwerpen tellen alleen *binnen* de passages van het thema zelf (±250
  tekens rond elke treffer), zodat 'ethiek' alleen bij AI meetelt als het ook
  echt over AI gaat.
- Documenten onder `MIN_WORDS_FOR_RATE` (3.000 woorden) blijven buiten de
  ranglijsten per 10.000 woorden; dat betreft nu alleen Haarlem.
- Nieuwe term toevoegen? Altijd eerst de treffers bekijken met `tools/quote.py`
  vóór je hem in `theme_config.json` zet. Zo zijn 'profilering' (stadsprofilering,
  geen AI), 'zorgen' (werkwoord) en 'ondergrondse container/parkeergarage'
  als valse treffers eruit gehaald. In de formele indeling gold dat ook voor
  `ring` (zat in 'verandering', 'inrichting' &ndash; 3.695 valse treffers),
  `doorstroming` (gaat meestal over de woningmarkt) en het kale `toegankelijk`
  (meestal digitaal of sociaal, niet fysiek bereikbaar).
- De DMI-instrumenten (DSGO, GIM, SIM, NDS/FDS, ZoN, DSFL, Talking Traffic,
  ROMO, SPS) zijn apart nageteld en komen niet voor. De treffers op BIM, DSM en
  grondbank zijn gecontroleerd en vals: respectievelijk de Bossche Investerings
  Maatschappij, het chemiebedrijf DSM en een budgetregel van een ontwikkelbedrijf.

## Citaatregels

Citaten zijn letterlijk en staan aantoonbaar op de genoemde pagina. Een aantal
PDF's is in kolommen opgemaakt, waardoor `pdftotext` zinnen door elkaar haalt
(o.a. Alphen aan den Rijn, Amstelveen, Breda, Enschede, Utrecht). Uit die
documenten alleen citeren waar de passage aaneengesloten loopt; in de overige
gevallen de inhoud beschrijven in plaats van citeren.

## Deployment

Beide rapporten draaien als eigen container op de Hetzner-host, op het
docker-netwerk `web`, zonder gepubliceerde poorten. Nginx Proxy Manager
(proxy host `prototype.transportlab.app`) heeft per rapport een custom location
die zonder URI-rewrite doorzet naar de containernaam, dus het pad moet ook in de
container bestaan.

| Rapport | Bron | Build-context | Container | URL |
| --- | --- | --- | --- | --- |
| Stadslogistiek | `index.html` | `Dockerfile` | `g40-stadslogistiek` | `/g40-stadslogistiek/` |
| SUMP/SULP-plannen | `logistics.html` | `Dockerfile` (zelfde container) | `g40-stadslogistiek` | `/g40-sump-sulp/` |
| Thema's | `themes.html` | `deploy/g40-themas/` | `g40-themas` | `/g40-themas/` |

Themarapport uitrollen (bouwt en vervangt de container over SSH, host `hetzner`
uit `~/.ssh/config`):

```bash
python3 tools/build_themes_html.py
./deploy/g40-themas/deploy.sh
```

Het themarapport bevat geen verwijzingen naar het stadslogistiekrapport; beide
zijn los te openen.
