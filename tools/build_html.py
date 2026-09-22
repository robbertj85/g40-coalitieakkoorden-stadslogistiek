#!/usr/bin/env python3
"""Render data/status.json to index.html (sorted by municipality name)."""
import json, pathlib, html, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.load(open(ROOT / "data" / "status.json", encoding="utf-8"))
munis = sorted(data["municipalities"], key=lambda m: m["municipality"].lstrip("'").lower())

STATUS_LABEL = {
    "todo": ("Nog niet gezocht", "grey"),
    "in_progress": ("Bezig", "amber"),
    "found_analysed": ("Akkoord geanalyseerd", "green"),
    "not_found": ("Nog geen akkoord gevonden", "red"),
    "no_agreement": ("Geen (klassiek) coalitieakkoord", "purple"),
}
def e(s):
    return html.escape(str(s)) if s is not None else ""

INSIGHTS_HTML = (pathlib.Path(__file__).parent / "insights.html").read_text(encoding="utf-8")

counts = {}
for m in munis:
    counts[m["status"]] = counts.get(m["status"], 0) + 1
with_cl = sum(1 for m in munis if m.get("city_logistics_found") is True)
without_cl = sum(1 for m in munis if m.get("city_logistics_found") is False)

rows = []
for m in munis:
    a = m["agreement"]
    label, color = STATUS_LABEL.get(m["status"], (m["status"], "grey"))
    link = f'<a href="{e(a["url"])}" target="_blank">{e(a["title"] or "bron")}</a>' if a.get("url") else "&mdash;"
    cl = {True: "Ja", False: "Nee", None: "?"}[m.get("city_logistics_found")]
    rows.append(f'<tr><td><a href="#{e(m["slug"])}">{e(m["municipality"])}</a></td><td>{e(m["group"])}</td>'
                f'<td><span class="badge {color}">{e(label)}</span></td><td>{cl}</td><td>{len(m.get("quotes") or [])}</td><td>{link}</td></tr>')

sections = []
for m in munis:
    a = m["agreement"]
    label, color = STATUS_LABEL.get(m["status"], (m["status"], "grey"))
    parts = [f'<section id="{e(m["slug"])}" class="muni">',
             f'<h2>{e(m["municipality"])} <span class="grp">{e(m["group"])}</span> <span class="badge {color}">{e(label)}</span></h2>']
    if a.get("title") or a.get("url"):
        meta = []
        if a.get("title"): meta.append(f'<b>Akkoord:</b> {e(a["title"])}')
        if a.get("type"): meta.append(f'<b>Type:</b> {e(a["type"])}')
        if a.get("parties"): meta.append(f'<b>Partijen:</b> {e(", ".join(a["parties"]))}')
        if a.get("date"): meta.append(f'<b>Datum:</b> {e(a["date"])}')
        if a.get("url"): meta.append(f'<b>Document:</b> <a href="{e(a["url"])}" target="_blank">{e(a["url"])}</a>')
        if a.get("source_page"): meta.append(f'<b>Bronpagina:</b> <a href="{e(a["source_page"])}" target="_blank">{e(a["source_page"])}</a>')
        if a.get("local_file"): meta.append(f'<b>Lokale kopie:</b> <code>{e(a["local_file"])}</code>')
        parts.append('<p class="meta">' + " &middot; ".join(meta) + "</p>")
    quotes = m.get("quotes") or []
    if quotes:
        parts.append("<h3>Stadslogistiek / goederenvervoer &ndash; letterlijke passages</h3><ul class='quotes'>")
        for q in quotes:
            ref = f' <span class="ref">(p. {e(q["page"])})</span>' if q.get("page") else ""
            term = f'<span class="term">{e(q["term"])}</span> ' if q.get("term") else ""
            parts.append(f'<li>{term}<q>{e(q["text"])}</q>{ref}</li>')
        parts.append("</ul>")
    elif m["status"] == "found_analysed":
        parts.append('<p class="none">Geen expliciete passages over stadslogistiek of goederenvervoer gevonden.</p>')
    if m.get("mobility_summary"):
        parts.append(f'<h3>Mobiliteit / bereikbaarheid</h3><p>{e(m["mobility_summary"])}</p>')
    if m.get("economy_summary"):
        parts.append(f'<h3>Economie / binnenstad</h3><p>{e(m["economy_summary"])}</p>')
    if m.get("notes"):
        parts.append(f'<p class="notes"><b>Opmerkingen:</b> {e(m["notes"])}</p>')
    if m.get("last_checked"):
        parts.append(f'<p class="checked">Laatst gecontroleerd: {e(m["last_checked"])}</p>')
    parts.append("</section>")
    sections.append("\n".join(parts))

page = f"""<!DOCTYPE html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stadslogistiek in coalitieakkoorden 2026</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#ddd;--card:#f7f7f5;--accent:#0b5fa5}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#141416;--fg:#e8e8e8;--muted:#9a9a9a;--line:#333;--card:#1e1e22;--accent:#6db3f2}}}}
:root[data-theme="dark"]{{--bg:#141416;--fg:#e8e8e8;--muted:#9a9a9a;--line:#333;--card:#1e1e22;--accent:#6db3f2}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin-inline:auto}}
h1{{font-size:1.6rem}} h2{{font-size:1.25rem;margin:0 0 .4rem}} h3{{font-size:1rem;margin:1rem 0 .3rem;color:var(--muted)}}
a{{color:var(--accent)}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}} th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.badge{{display:inline-block;padding:1px 8px;border-radius:10px;font-size:.75rem;color:#fff;vertical-align:middle}}
.grey{{background:#888}} .amber{{background:#c78a00}} .green{{background:#2e8b57}} .red{{background:#b23a3a}} .purple{{background:#6f42c1}}
.grp{{font-size:.8rem;color:var(--muted);margin-left:4px}}
.muni{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;margin:16px 0}}
.meta{{font-size:.9rem;color:var(--muted);word-break:break-word}}
.quotes li{{margin-bottom:.6rem}} q{{font-style:italic}} .ref,.term{{font-size:.8rem;color:var(--muted)}} .term{{font-weight:600}}
.none{{color:var(--muted);font-style:italic}} .checked{{font-size:.75rem;color:var(--muted)}}
.summary{{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0}} .summary div{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px}}
.overflow{{overflow-x:auto}}
.overview{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin:16px 0}}
.overview li{{margin-bottom:.7rem}}
.small{{font-size:.9rem}}
.insights{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:4px 16px 16px;margin:24px 0}}
.insights summary{{cursor:pointer;font-weight:600;padding:12px 0;font-size:1.05rem}}
.insights .insights-body{{margin-top:8px}}
.insights h3{{margin:1.2rem 0 .4rem;color:var(--fg)}}
.insights li{{margin-bottom:.5rem}}
.insights table{{margin-top:.5rem}}
.insights .tag{{display:inline-block;font-size:.7rem;color:var(--muted);border:1px solid var(--line);border-radius:8px;padding:0 6px;margin-left:4px}}
</style></head><body>
<h1>Stadslogistiek en goederenvervoer in coalitieakkoorden 2026 (G4 + G40)</h1>
<p>Overzicht van de coalitie-/bestuursakkoorden na de gemeenteraadsverkiezingen van 18 maart 2026, met letterlijke passages over stadslogistiek en goederenvervoer. Waar die ontbreken: samenvatting van mobiliteits- en economieplannen. Gesorteerd op gemeentenaam. Bijgewerkt: {e(datetime.date.today())}.</p>
<p class="small"><a href="/g40-themas/">&rarr; Thema-analyse van dezelfde akkoorden: het algemene beeld en de zeven DMI-thema's</a></p>
<div class="summary">
<div><b>{len(munis)}</b> gemeenten</div>
<div><b>{counts.get("found_analysed",0)}</b> geanalyseerd</div>
<div><b>{with_cl}</b> met expliciete stadslogistiek</div>
<div><b>{without_cl}</b> zonder</div>
<div><b>{counts.get("not_found",0) + counts.get("todo",0) + counts.get("in_progress",0)}</b> open</div>
</div>
<section class="overview">
<h2>Overzicht: gemeenschappelijke lijnen in de akkoorden</h2>
<p>Van de 45 gemeenten zijn er 42 akkoorden geanalyseerd. In 25 daarvan staat een expliciete passage over stadslogistiek of goederenvervoer; de overige geanalyseerde akkoorden behandelen het onderwerp niet apart (wel vaak impliciet via mobiliteitsbeleid). Zeven terugkerende lijnen:</p>
<ul>
<li><b>Zero-emissiezones: verdeeld beeld.</b> Ongeveer tien gemeenten pauzeren, vertragen of schrappen de invoering &ndash; Den Haag stelt emissieklasse 6 en zero-emissie uit naar 2035, Utrecht stelt de uitbreiding uit, Ede stopt de invoering volledig, Helmond, Schiedam en Zaanstad zien af van een zone, Dordrecht en Leeuwarden voeren deze bestuursperiode geen zone in, Assen handhaaft de bestaande zone zonder uitbreiding en Almere houdt de buitenwijken erbuiten. Netcongestie en de gevolgen voor het verdienvermogen van ondernemers zijn de meest genoemde redenen. Daartegenover houden vijf gemeenten vast aan invoering of uitbreiding: Amsterdam breidt uit in 2028, Arnhem benut de maximale ruimte binnen de landelijke regels, Deventer voert eind 2027 in, Alphen aan den Rijn evalueert de recent ingevoerde zone en Zwolle bereidt zich voor op de wettelijke verplichting in 2030.</li>
<li><b>Logistieke hubs zijn het meest genoemde alternatief.</b> Alkmaar, Apeldoorn, Arnhem, Deventer, Dordrecht (bouwhubs), Leeuwarden (stadsrandshub en wijkhubs), Maastricht (elektrische goederenhubs), Sittard-Geleen (distributiehubs), Den Haag (overslagplekken op bedrijventerreinen) en Alphen aan den Rijn (vrachtwagenparkeren bij de eigen hubfunctie) zetten in op bundeling van bevoorrading aan de stadsrand of in wijken.</li>
<li><b>Vrachtwagenparkeren en bereikbare bedrijventerreinen</b> komen terug bij Alphen aan den Rijn, Lelystad, Schiedam, Zwolle en Oss.</li>
<li><b>Gerichte weringsmaatregelen voor zwaar verkeer</b> op specifieke straten of in dorpskernen: Tilburg verbiedt doorgaand vrachtverkeer op de Ringbaan West, Arnhem agendeert de toename van transport van gevaarlijke stoffen, Dordrecht wil vrachtverkeer in de binnenstad verminderen en Alkmaar weert landbouw- en zwaar verkeer uit de dorpen.</li>
<li><b>Vervoer over water en spoor als duurzaam alternatief</b> speelt vooral in de havensteden: Rotterdam zet in op modal shift naar water, Deventer wil de Prins Bernhardsluis moderniseren voor de binnenvaart, Oss werkt aan een trimodale haven op Elzenburg en Sittard-Geleen noemt spoor, water en buisleidingen naast distributiehubs.</li>
<li><b>Pakketbezorging</b> wordt slechts door enkele gemeenten benoemd: Den Haag wil pakketpunten in de wijken en bundelt horeca- en afvallogistiek, Deventer onderzoekt pakketkluizen, terwijl Alkmaar juist kritisch is op de ruimtelijke impact van maaltijdbezorging.</li>
<li><b>Terughoudendheid bij ruimte-intensieve logistiek:</b> Almere weert distributiecentra en datacenters die niet aan de lokale economie dienen, en Alkmaar is kritisch op functies met beperkte toegevoegde waarde of negatieve effecten op de openbare ruimte.</li>
</ul>
</section>
<div class="overflow"><table><thead><tr><th>Gemeente</th><th>Groep</th><th>Status</th><th>Stadslogistiek?</th><th>#passages</th><th>Akkoord</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
{"".join(sections)}
{INSIGHTS_HTML}
<script>
(function(){{function open(){{if(location.hash==="#analyse"){{var d=document.getElementById("analyse");if(d){{d.open=true;d.scrollIntoView();}}}}}}
open();window.addEventListener("hashchange",open);}})();
</script>
</body></html>"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
print(f"index.html written: {len(munis)} municipalities, {counts}")
