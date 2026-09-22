# Loop-prompt

Start de run met (zelf-getimed, geen vast interval):

    /loop Lees PLAN.md en werk precies één gemeente af uit data/status.json volgens de werkwijze in PLAN.md (eerst status todo, dan in_progress, dan not_found met de minste retries). Gebruik tools/fetch_and_grep.py voor downloaden en zoeken, schrijf het resultaat terug in data/status.json met een klein Python-script, en draai daarna python3 tools/build_html.py. Rapporteer in één regel: gemeente, status, aantal quotes, aantal resterende todo. Kies delaySeconds 60. Stop de loop alleen als er geen gemeenten meer zijn met status todo of in_progress én elke not_found minstens 3 retries heeft.

Tips voor de run:
- Model: haiku is voldoende voor het zoek- en invulwerk. Bij een gemeente waar de
  kolomtekst onleesbaar is, kun je die gemeente overslaan (notes invullen) en later
  met een groter model afmaken.
- Controle tussendoor: `python3 -c "import json;d=json.load(open('data/status.json'));print({s:sum(1 for m in d['municipalities'] if m['status']==s) for s in ['todo','in_progress','found_analysed','not_found','no_agreement']})"`
- Open `index.html` in de browser om het resultaat te bekijken.
