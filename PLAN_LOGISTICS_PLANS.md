# Plan: formele mobiliteits- en goederenvervoerplannen (G4 + G40)

Doel: voor alle 45 gemeenten (G4 + de 41 leden van het G40-stedennetwerk) op zoek
gaan naar **formele beleidsdocumenten** die de visie of strategie op mobiliteit
en/of goederenvervoer beschrijven, los van het coalitieakkoord 2026:

- **SUMP** — Sustainable Urban Mobility Plan (NL: mobiliteitsvisie, mobiliteitsplan,
  Gemeentelijk Verkeer- en Vervoerplan / GVVP)
- **SULP** — Sustainable Urban Logistics Plan (NL: duurzaam stedelijk logistiek plan,
  stadslogistiek-visie, actieplan stadslogistiek)
- **Goederenvervoeragenda**
- **Goederenvervoerstrategie**
- verwante varianten: goederenvervoervisie, uitvoeringsagenda stadslogistiek/
  goederenvervoer, logistiek actieplan

Dit is een tweede, onafhankelijke pass naast de coalitieakkoord-analyse
(zie `PLAN.md`). Belangrijk verschil: deze documenten zijn meerjarig en hoeven
niet uit 2026 te zijn. Een geldige visie uit bv. 2020 telt mee — er is **geen**
"na 18 maart 2026"-filter zoals bij de coalitieakkoorden.

## Bestanden

| Pad | Rol |
|---|---|
| `data/status.json` | Bron van waarheid. Elk record heeft nu ook een `logistics_plans`-veld. Zoektermen per doc_type staan onder `search_terms.logistics_plan_types`. |
| `data/raw/<slug>_<doctype>.pdf/.html/.txt` | Gedownloade plannen en geëxtraheerde tekst. Doctype-suffix (bv. `_sump`, `_sulp`, `_goederenvervoer`) voorkomt botsing met het al gedownloade coalitieakkoord (`data/raw/<slug>.pdf`). |
| `tools/fetch_and_grep.py` | **Ongewijzigd hergebruikt.** Download + grep; de meegegeven slug bepaalt alleen de bestandsnaam, dus `<slug>_sump` werkt zonder codewijziging. |
| `tools/build_logistics_html.py` | Bouwt `logistics.html` (los van `index.html`/`tools/build_html.py`, die alleen over de coalitieakkoorden gaan). Altijd draaien na elke wijziging. |
| `LOOP_PROMPT_LOGISTICS.md` | De exacte prompt voor de `/loop`-run van deze pass. |

Bewust gescheiden van de coalitieakkoord-pagina: `index.html` (coalitieakkoorden)
en `logistics.html` (SUMP/SULP/goederenvervoerplannen) zijn losse bestanden,
gebouwd door losse scripts uit dezelfde `data/status.json`. Eventueel worden ze
later samengevoegd, maar dat is nu niet aan de orde.

## Statuswaarden per gemeente (`logistics_plans.status`)

- `todo` – nog niet gezocht.
- `in_progress` – zoekactie gestart, analyse nog niet af.
- `found` – klaar: minstens één document gevonden en geanalyseerd (kan meerdere `documents`-items hebben).
- `not_found` – gezocht, maar niets gevonden. `retries` telt de pogingen; bij 3+ pogingen alleen nog wekelijks opnieuw proberen.

## Werkwijze per gemeente (één iteratie van de loop = één gemeente)

1. **Kies** de eerste gemeente in `data/status.json` met `logistics_plans.status`
   `todo`, daarna `in_progress`, daarna `not_found` met de laagste `retries`. Zet
   status op `in_progress` en vul `last_checked` (YYYY-MM-DD).
2. **Zoek** met WebSearch, per doc_type-categorie apart — in tegenstelling tot de
   coalitieakkoord-loop stop je niet bij de eerste hit: een gemeente kan meerdere
   losse documenten hebben (bv. zowel een mobiliteitsvisie als een apart
   goederenvervoerplan). Probeer minstens:
   - SUMP: `<gemeente> mobiliteitsvisie`, `<gemeente> mobiliteitsplan`,
     `<gemeente> GVVP`, `<gemeente> Sustainable Urban Mobility Plan`
   - SULP: `<gemeente> stadslogistiek visie`, `<gemeente> actieplan stadslogistiek`,
     `<gemeente> duurzaam stedelijk logistiek plan`, `<gemeente> Sustainable Urban Logistics Plan`
   - Goederenvervoer: `<gemeente> goederenvervoeragenda`, `<gemeente> goederenvervoerstrategie`,
     `<gemeente> goederenvervoervisie`, `<gemeente> logistiek actieplan`
   - Aanvullend per categorie: `site:<gemeente>.nl <zoekterm>` (domein soms afwijkend,
     zie `PLAN.md`), en `<gemeente> raadsinformatie <zoekterm>` voor documenten in
     raadsinformatiesystemen (`*.raadsinformatie.nl`, `*.bestuurlijkeinformatie.nl`,
     `*.notubiz.nl`, ibabs).
   Voorkeur voor bron: 1) PDF op gemeentesite, 2) PDF in raadsinformatiesysteem,
   3) HTML-pagina op gemeentesite. Geen datumfilter: het meest recente, nog
   geldige document per categorie is goed, ook als het van vóór 2026 is. Is een
   document expliciet vervangen of ingetrokken, gebruik dan het opvolgerdocument.
3. **Download en grep** met het bestaande `tools/fetch_and_grep.py`, met een
   samengesteld slug per document (`<slug>_sump`, `<slug>_sulp`,
   `<slug>_goederenvervoer`) zodat het niet het al gedownloade coalitieakkoord
   overschrijft:
   ```
   python3 tools/fetch_and_grep.py <slug>_sump "<url>" --term "stadslogistiek" --term "goederenvervoer" --term "bevoorrading" --context 400
   python3 tools/fetch_and_grep.py <slug>_sulp --local --term "hub" --term "laden en lossen"
   ```
   Gebruik gerichte `--term`-vlaggen (of hergebruik `--set primary` uit
   `PLAN.md` voor de stadslogistiek-termen) in plaats van blind alle tekst te lezen.
   Lukt de download niet: probeer een andere bron, of WebFetch op de HTML-pagina.
4. **Analyseer** per gevonden document:
   - `doc_type`: `SUMP`, `SULP`, `Goederenvervoeragenda`, `Goederenvervoerstrategie`
     of `Other` (bij twijfel: `Other` + toelichting in `notes`).
   - `title`, `date` (YYYY of YYYY-MM), `url`, `source_page`, `local_file`.
   - `quotes`: enkele letterlijke passages (met paginanummer) over stadslogistiek/
     goederenvervoer, zelfde kwaliteitsregels als in `PLAN.md` (letterlijk, geen
     parafrase, geen valse treffers).
   - `summary`: 1-3 zinnen over de visie/strategie t.a.v. stadslogistiek/goederenvervoer.
5. **Schrijf terug** naar `data/status.json`: voeg elk gevonden document toe aan
   `logistics_plans.documents` (lijst, dus bestaande items behouden), zet
   `logistics_plans.status` op `found` zodra er ≥1 document is, of `not_found`
   met `retries += 1` en een `notes`-regel bij niets gevonden. Gebruik een klein
   Python-script dat het JSON-bestand laadt, één record wijzigt en weer
   wegschrijft met `indent=2, ensure_ascii=False`. Nooit het hele bestand met de
   hand overtypen. Raak het bestaande `agreement`/`quotes`/coalitieakkoord-veld
   van het record niet aan.
6. **Bouw de HTML**: `python3 tools/build_logistics_html.py` (niet `build_html.py` &ndash; dat blijft uitsluitend voor de coalitieakkoorden in `index.html`).
7. **Rapporteer** in één regel: gemeente, gevonden doc_types (of "geen"),
   resterend aantal `todo`.

## Stopcriterium voor de loop

Stop (ScheduleWakeup met `stop: true`) als er geen gemeenten meer zijn met
`logistics_plans.status` `todo` of `in_progress`, én elke `not_found` minstens
3 `retries` heeft. Zolang er `not_found`-gemeenten zijn met < 3 retries:
doorgaan, maar probeer dan andere zoektermen/categorieën dan de vorige keer
(zie `notes`).

## Kwaliteitsregels

- Quotes zijn letterlijk, inclusief Nederlandse spelling en typografie.
- Verwar een SUMP/mobiliteitsvisie niet met het coalitieakkoord: dit zijn losse,
  vaak meerjarige beleidsdocumenten, soms door de raad vastgesteld vóór de
  huidige coalitieperiode.
- Eén gemeente kan meerdere documenten hebben (bv. een SUMP uit 2021 én een
  losse goederenvervoeragenda uit 2023) — voeg ze allebei toe aan `documents`.
- Gemeentenaam en slug niet wijzigen; ze zijn de sleutel, ook hier.
- Voeg geen gemeenten toe. De lijst in `status.json` is leidend.
