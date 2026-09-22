#!/usr/bin/env python3
"""Controleert dat elk „citaat” in tools/insights.html letterlijk voorkomt in een bron:
coalitie-quotes (status.json), ruwe akkoordtekst (data/raw/<slug>.txt), DMI-stukken of de
vorige versie van de analyse (git HEAD). Exit 1 bij een afwijking. Controleert ook de #anker-links."""
import json, re, sys, html, pathlib, subprocess, glob
ROOT = pathlib.Path(__file__).resolve().parent.parent
DMI = pathlib.Path('/Users/robbertjanssen/Documents/dev/dmi-slimmelogistiek')
frag = (ROOT/'tools/insights.html').read_text(encoding='utf-8')
text = html.unescape(frag)
norm = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'").replace('‘', "'")).strip()
d = json.load(open(ROOT/'data/status.json'))
slugs = {m['slug'] for m in d['municipalities']}
corpus = []
for m in d['municipalities']:
    for q in m.get('quotes') or []: corpus.append(q['text'])
for f in glob.glob(str(ROOT/'data/raw/*.txt')): corpus.append(open(f, errors='ignore').read())
for f in glob.glob(str(DMI/'dmi_slimme_logistiek_md/*.md')) + glob.glob(str(DMI/'*.md')): corpus.append(open(f, errors='ignore').read())
try: corpus.append(subprocess.check_output(['git','show','HEAD:tools/build_html.py'], cwd=ROOT).decode())
except Exception: pass
corpus = [norm(html.unescape(c)) for c in corpus]
bad = 0
for frag_q in re.findall(r'„(.+?)”', text):
    q = norm(frag_q)
    if not any(q in c for c in corpus):
        print('NIET GEVONDEN:', frag_q); bad += 1
for a in re.findall(r'href="#([^"]+)"', frag):
    if a not in slugs: print('ONBEKEND ANKER:', a); bad += 1
print(f'{len(re.findall(r"„(.+?)”", text))} citaten gecontroleerd, {bad} problemen')
sys.exit(1 if bad else 0)
