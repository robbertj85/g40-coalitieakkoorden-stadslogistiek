#!/usr/bin/env python3
"""Render data/status.json's logistics_plans field to logistics.html (sorted by municipality name).

Separate from build_html.py / index.html on purpose: index.html is about the
coalition agreements, this page is about standalone SUMP/SULP/goederenvervoer-
agenda/-strategie documents. They may be merged later, but for now stay apart.
"""
import json, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.load(open(ROOT / "data" / "status.json", encoding="utf-8"))
munis = sorted(data["municipalities"], key=lambda m: m["municipality"].lstrip("'").lower())

STATUS_LABEL = {
    "todo": ("Nog niet gezocht", "grey"),
    "in_progress": ("Bezig", "amber"),
    "found": ("Document(en) gevonden", "green"),
    "not_found": ("Nog geen document gevonden", "red"),
}

def e(s):
    return html.escape(str(s)) if s is not None else ""

def lp(m):
    return m.get("logistics_plans") or {"status": "todo", "retries": 0, "last_checked": None, "documents": [], "notes": ""}

counts = {}
for m in munis:
    counts[lp(m)["status"]] = counts.get(lp(m)["status"], 0) + 1

rows = []
for m in munis:
    p = lp(m)
    label, color = STATUS_LABEL.get(p["status"], (p["status"], "grey"))
    docs = p.get("documents") or []
    doc_types = ", ".join(sorted({d.get("doc_type") or "Other" for d in docs})) if docs else "&mdash;"
    rows.append(f'<tr><td><a href="#{e(m["slug"])}">{e(m["municipality"])}</a></td><td>{e(m["group"])}</td>'
                f'<td><span class="badge {color}">{e(label)}</span></td><td>{len(docs)}</td><td>{doc_types}</td></tr>')

sections = []
for m in munis:
    p = lp(m)
    label, color = STATUS_LABEL.get(p["status"], (p["status"], "grey"))
    parts = [f'<section id="{e(m["slug"])}" class="muni">',
             f'<h2>{e(m["municipality"])} <span class="grp">{e(m["group"])}</span> <span class="badge {color}">{e(label)}</span></h2>']
    docs = p.get("documents") or []
    if docs:
        for doc in docs:
            dmeta = [f'<b>{e(doc.get("doc_type") or "Other")}</b>']
            if doc.get("title"): dmeta.append(e(doc["title"]))
            if doc.get("date"): dmeta.append(e(doc["date"]))
            if doc.get("url"): dmeta.append(f'<a href="{e(doc["url"])}" target="_blank">document</a>')
            if doc.get("source_page"): dmeta.append(f'<a href="{e(doc["source_page"])}" target="_blank">bronpagina</a>')
            if doc.get("local_file"): dmeta.append(f'<code>{e(doc["local_file"])}</code>')
            parts.append('<p class="meta">' + " &middot; ".join(dmeta) + "</p>")
            if doc.get("summary"):
                parts.append(f'<p>{e(doc["summary"])}</p>')
            quotes = doc.get("quotes") or []
            if quotes:
                parts.append("<ul class='quotes'>")
                for q in quotes:
                    ref = f' <span class="ref">(p. {e(q["page"])})</span>' if q.get("page") else ""
                    term = f'<span class="term">{e(q["term"])}</span> ' if q.get("term") else ""
                    parts.append(f'<li>{term}<q>{e(q["text"])}</q>{ref}</li>')
                parts.append("</ul>")
    elif p["status"] == "not_found":
        parts.append('<p class="none">Nog geen SUMP, SULP of goederenvervoeragenda/-strategie gevonden.</p>')
    else:
        parts.append('<p class="none">Nog niet onderzocht.</p>')
    if p.get("notes"):
        parts.append(f'<p class="notes"><b>Opmerkingen:</b> {e(p["notes"])}</p>')
    if p.get("last_checked"):
        parts.append(f'<p class="checked">Laatst gecontroleerd: {e(p["last_checked"])}</p>')
    parts.append("</section>")
    sections.append("\n".join(parts))

page = f"""<!DOCTYPE html>
<html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mobiliteits- en goederenvervoerplannen (SUMP/SULP) &ndash; G4 + G40</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#ddd;--card:#f7f7f5;--accent:#0b5fa5}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#141416;--fg:#e8e8e8;--muted:#9a9a9a;--line:#333;--card:#1e1e22;--accent:#6db3f2}}}}
:root[data-theme="dark"]{{--bg:#141416;--fg:#e8e8e8;--muted:#9a9a9a;--line:#333;--card:#1e1e22;--accent:#6db3f2}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin-inline:auto}}
h1{{font-size:1.6rem}} h2{{font-size:1.25rem;margin:0 0 .4rem}} h3{{font-size:1rem;margin:1rem 0 .3rem;color:var(--muted)}}
a{{color:var(--accent)}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}} th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.badge{{display:inline-block;padding:1px 8px;border-radius:10px;font-size:.75rem;color:#fff;vertical-align:middle}}
.grey{{background:#888}} .amber{{background:#c78a00}} .green{{background:#2e8b57}} .red{{background:#b23a3a}}
.grp{{font-size:.8rem;color:var(--muted);margin-left:4px}}
.muni{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px;margin:16px 0}}
.meta{{font-size:.9rem;color:var(--muted);word-break:break-word}}
.quotes li{{margin-bottom:.6rem}} q{{font-style:italic}} .ref,.term{{font-size:.8rem;color:var(--muted)}} .term{{font-weight:600}}
.none{{color:var(--muted);font-style:italic}} .checked{{font-size:.75rem;color:var(--muted)}}
.summary{{display:flex;gap:16px;flex-wrap:wrap;margin:12px 0}} .summary div{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px}}
.overflow{{overflow-x:auto}}
.small{{font-size:.9rem}}
</style></head><body>
<h1>Mobiliteits- en goederenvervoerplannen (SUMP/SULP) &ndash; G4 + G40</h1>
<p>Los van de coalitieakkoorden: formele beleidsdocumenten die de visie/strategie op mobiliteit en/of goederenvervoer beschrijven &ndash; Sustainable Urban Mobility Plans (SUMP/mobiliteitsvisie), Sustainable Urban Logistics Plans (SULP/stadslogistiek-visie) en goederenvervoeragenda's/-strategie&euml;n. Gesorteerd op gemeentenaam. Bijgewerkt: {e(datetime.date.today())}.</p>
<p class="small"><a href="index.html">&larr; Coalitieakkoorden 2026 (apart bestand)</a></p>
<div class="summary">
<div><b>{len(munis)}</b> gemeenten</div>
<div><b>{counts.get("found",0)}</b> met document(en) gevonden</div>
<div><b>{counts.get("not_found",0)}</b> nog niet gevonden</div>
<div><b>{counts.get("todo",0) + counts.get("in_progress",0)}</b> nog te onderzoeken</div>
</div>
<div class="overflow"><table><thead><tr><th>Gemeente</th><th>Groep</th><th>Status</th><th>#documenten</th><th>Type(n)</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
{"".join(sections)}
</body></html>"""
(ROOT / "logistics.html").write_text(page, encoding="utf-8")
print(f"logistics.html written: {len(munis)} municipalities, {counts}")
