#!/usr/bin/env python3
"""Download a coalition agreement (PDF or HTML), store it under data/raw/<slug>,
extract plain text, and print keyword hits with page numbers and context.

Usage:
  python3 tools/fetch_and_grep.py <slug> <url> [--set primary|mobility|economy|all] [--max-hits N] [--context N]
  python3 tools/fetch_and_grep.py <slug> --local            # re-grep an already downloaded file
  python3 tools/fetch_and_grep.py <slug> --local --term "laden en lossen"   # grep one custom term

Output is deliberately compact so a small model can read it. Page numbers come
from pdftotext form feeds (1-based). For HTML sources the page is always 1.
"""
import sys, os, re, json, subprocess, html, argparse, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
STATUS = ROOT / "data" / "status.json"
# terms that must start a word (avoids "handhaven" -> haven, "aanpakket" etc.)
WORD_START = {"haven", "pakket", "transport", "ov"}

def load_terms(which):
    cfg = json.load(open(STATUS))["search_terms"]
    if which == "all":
        return cfg["primary"] + cfg["mobility"] + cfg["economy"]
    return cfg[which]

def download(slug, url):
    RAW.mkdir(parents=True, exist_ok=True)
    tmp = RAW / f"{slug}.download"
    try:
        subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0 (research bot)", "-o", str(tmp), "--max-time", "120", url], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["curl", "-sSL", "--http1.1", "-A", "Mozilla/5.0 (research bot)", "-o", str(tmp), "--max-time", "120", url], check=True)
    head = open(tmp, "rb").read(5)
    if head.startswith(b"%PDF"):
        dest = RAW / f"{slug}.pdf"
    else:
        dest = RAW / f"{slug}.html"
    os.replace(tmp, dest)
    return dest

def extract_text(path):
    txt_path = path.with_suffix(".txt")
    if path.suffix == ".pdf":
        subprocess.run(["pdftotext", str(path), str(txt_path)], check=True)
        raw = open(txt_path, encoding="utf-8", errors="ignore").read()
        raw = raw.replace("\u00ad", "")                      # soft hyphens
        raw = re.sub(r"(\w)-\n(?=[a-z])", r"\1", raw)        # hyphenation across lines
        open(txt_path, "w", encoding="utf-8").write(raw)
    else:
        raw = open(path, encoding="utf-8", errors="ignore").read()
        raw = re.sub(r"(?is)<(script|style|nav|footer|header).*?</\1>", " ", raw)
        raw = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|br)>", "\n", raw)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = html.unescape(raw)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        open(txt_path, "w", encoding="utf-8").write(raw)
    return txt_path

def grep(txt_path, terms, max_hits, context):
    text = open(txt_path, encoding="utf-8", errors="ignore").read()
    pages = text.split("\f")
    hits = []
    seen = set()
    for pno, page in enumerate(pages, 1):
        flat = re.sub(r"\s+", " ", page)
        for term in terms:
            pat = re.escape(term)
            if term.lower() in WORD_START:
                pat = r"(?<![A-Za-z])" + pat
            for m in re.finditer(pat, flat, flags=re.IGNORECASE):
                start = max(0, m.start() - context)
                end = min(len(flat), m.end() + context)
                key = (pno, start // (context * 2))
                if key in seen:
                    continue
                seen.add(key)
                hits.append((pno, term, flat[start:end].strip()))
    total = len(hits)
    for pno, term, ctx in hits[:max_hits]:
        print(f"[p.{pno}] ({term}) ...{ctx}...")
    print(f"\n== {total} hits total, {len(pages)} pages, text file: {txt_path.relative_to(ROOT)} ==")
    if total > max_hits:
        print(f"== showing first {max_hits}; rerun with --max-hits or --term to narrow ==")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--set", default="primary", choices=["primary", "mobility", "economy", "all"])
    ap.add_argument("--term", action="append")
    ap.add_argument("--max-hits", type=int, default=40)
    ap.add_argument("--context", type=int, default=250)
    a = ap.parse_args()
    if a.local:
        cands = [RAW / f"{a.slug}.pdf", RAW / f"{a.slug}.html"]
        path = next((c for c in cands if c.exists()), None)
        if not path:
            sys.exit(f"no downloaded file for {a.slug}")
    else:
        if not a.url:
            sys.exit("url required unless --local")
        path = download(a.slug, a.url)
        print(f"saved: {path.relative_to(ROOT)}")
    txt = extract_text(path)
    terms = a.term if a.term else load_terms(a.set)
    grep(txt, terms, a.max_hits, a.context)
