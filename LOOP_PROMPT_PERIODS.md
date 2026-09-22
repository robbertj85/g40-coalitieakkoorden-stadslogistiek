# Loop-prompt — geldigheidsperiode per document + Urban Node todo's

Start de run met (zelf-getimed, geen vast interval):

    /loop Lees PLAN_LOGISTICS_PLANS.md, secties "Urban Nodes (TEN-T) naast G4/G40" en "Geldigheidsperiode per document", en werk precies één gemeente af: kies eerst een gemeente in data["additional_urban_nodes"] met logistics_plans.status todo of in_progress (zoek daar een SUMP/SULP/goederenvervoerdocument volgens de bestaande werkwijze in PLAN_LOGISTICS_PLANS.md), anders de eerste gemeente (in municipalities of additional_urban_nodes) met minstens één document waarvan period_checked nog false is. Bepaal voor elk zo'n document het tijdvak (period) volgens de werkwijze in de sectie "Geldigheidsperiode per document" en zet period_checked op true, ook als period null blijft. Schrijf terug in data/status.json met een klein Python-script en draai daarna python3 tools/build_logistics_html.py. Rapporteer in één regel: gemeente, aantal documenten bijgewerkt, resterend aantal met period_checked false. Kies delaySeconds 60. Stop de loop alleen als er geen document meer is met period_checked false én additional_urban_nodes geen todo/in_progress meer heeft.

Tips voor de run:
- Gebruik eerst de al gedownloade tekst in `data/raw/<slug>_<doctype>.txt` (bestaat al
  voor bijna elk document) voordat je opnieuw gaat downloaden of zoeken.
- Titel bevat vaak al het tijdvak (bv. "2020-2030") — dat is meestal de snelste,
  betrouwbaarste bron. Verwar het niet met een jaartal-range van een ander,
  aangehaald beleidsstuk.
- Voor Middelburg (en eventuele andere `additional_urban_nodes`-gemeenten met
  status todo): eerst het document zoeken (zelfde werkwijze als de oorspronkelijke
  45-gemeenten-pass), dan pas de periode bepalen.
- Controle tussendoor:
  `python3 -c "import json;d=json.load(open('data/status.json'));docs=[doc for m in d['municipalities']+d.get('additional_urban_nodes',[]) for doc in (m.get('logistics_plans') or {}).get('documents',[])];print('open:',sum(1 for doc in docs if not doc.get('period_checked')),'/',len(docs))"`
- Open `logistics.html` in de browser om het resultaat te bekijken (vlaggetjes +
  geldigheidsperiode + vigerend/verstreken-indicatie).
