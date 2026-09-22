# Loop-prompt — mobiliteits- en goederenvervoerplannen

Start de run met (zelf-getimed, geen vast interval):

    /loop Lees PLAN_LOGISTICS_PLANS.md en werk precies één gemeente af uit data/status.json volgens de werkwijze daarin (eerst logistics_plans.status todo, dan in_progress, dan not_found met de minste retries). Zoek naar SUMP/mobiliteitsvisie, SULP/stadslogistiek-visie en goederenvervoeragenda/-strategie documenten. Gebruik tools/fetch_and_grep.py voor downloaden en zoeken (samengesteld slug per document, bv. <slug>_sump), schrijf het resultaat terug in data/status.json onder logistics_plans met een klein Python-script, en draai daarna python3 tools/build_logistics_html.py (niet build_html.py, dat blijft apart voor de coalitieakkoorden in index.html). Rapporteer in één regel: gemeente, gevonden doc_types, resterende todo. Kies delaySeconds 60. Stop de loop alleen als er geen gemeenten meer zijn met logistics_plans.status todo of in_progress én elke not_found minstens 3 retries heeft.

Tips voor de run:
- Model: haiku is voldoende voor het zoek- en invulwerk; schakel naar een groter
  model bij gemeenten waar de documenten lastig te vinden of te classificeren zijn.
- Een gemeente kan meerdere documenten hebben (SUMP + losse goederenvervoeragenda) —
  probeer alle drie de categorieën, stop niet bij de eerste hit.
- Controle tussendoor: `python3 -c "import json;d=json.load(open('data/status.json'));print({s:sum(1 for m in d['municipalities'] if m['logistics_plans']['status']==s) for s in ['todo','in_progress','found','not_found']})"`
- Open `index.html` in de browser om het resultaat te bekijken.
