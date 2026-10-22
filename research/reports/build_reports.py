"""Build the PDF versions of the two reports from their Markdown sources.

    python research/reports/build_reports.py            (from the project root)

Uses only tools that were already on the lab PC (2026-10-22): the system Python with markdown-it-py
(Markdown → HTML) and headless Google Chrome or Microsoft Edge (HTML → PDF). Nothing is installed or
downloaded. The Markdown files are the editable sources; the PDFs are regenerated from them.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[2]
DOCS = [
    (ROOT / "research/reports/PILOT_TEST_VERSION_COMPLETE_REPORT.md",
     ROOT / "research/reports/PILOT_TEST_VERSION_COMPLETE_REPORT.pdf", "Pilot / Test Version — Complete Report"),
    (ROOT / "research/design_proposals/05_FULL_DATASET_EXECUTION_PLAN.md",
     ROOT / "research/reports/FULL_DATASET_EXECUTION_PLAN.pdf", "Full-Dataset Execution Plan (Proposal 05)"),
]
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]

CSS = """
@page { size: A4; margin: 18mm 15mm 18mm 15mm;
  @bottom-center { content: "Page " counter(page) " of " counter(pages); font: 9pt "Segoe UI", sans-serif; color: #555; }
  @top-right { content: "__RUNNING__"; font: 8pt "Segoe UI", sans-serif; color: #777; } }
@page :first { @bottom-center { content: none; } @top-right { content: none; } }
html { font: 10pt/1.45 "Segoe UI", "Nirmala UI", "Vrinda", Arial, sans-serif; color: #1d1d1b; }
body { margin: 0; }
.title-page { break-after: page; padding-top: 55mm; }
.title-page h1 { font-size: 24pt; line-height: 1.2; margin: 0 0 6mm; border: 0; }
.title-page h2 { font-size: 16pt; color: #2c5f9e; margin: 0 0 14mm; border: 0; break-before: avoid; }
.title-page p { font-size: 10.5pt; margin: 0 0 3mm; }
h1, h2, h3, h4 { break-after: avoid; page-break-after: avoid; color: #111; }
h2 { font-size: 15pt; border-bottom: 1.5px solid #2c5f9e; padding-bottom: 2pt; margin: 16pt 0 8pt; }
h3 { font-size: 12.5pt; margin: 13pt 0 6pt; }
h4 { font-size: 11pt; margin: 12pt 0 5pt; color: #2c5f9e; }
h2#table-of-contents + ol { columns: 2; column-gap: 10mm; font-size: 9.5pt; }
h2#table-of-contents + ol + hr { break-after: page; border: 0; }
p, li { orphans: 3; widows: 3; }
a { color: #2c5f9e; text-decoration: none; }
code { font: 8.6pt Consolas, "Cascadia Mono", monospace; background: #f3f3f0; padding: 0 2px; border-radius: 2px;
       overflow-wrap: anywhere; }
pre { background: #f6f6f3; border: 1px solid #ddd; border-radius: 3px; padding: 6pt 8pt; white-space: pre-wrap;
      overflow-wrap: anywhere; break-inside: avoid; font-size: 8.4pt; }
pre code { background: none; padding: 0; font-size: 8.4pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8.4pt; table-layout: auto; }
th, td { border: 1px solid #c9c9c4; padding: 3pt 4pt; vertical-align: top; overflow-wrap: anywhere; }
th { background: #eef2f7; text-align: left; }
tr { break-inside: avoid; }
img { max-width: 100%; height: auto; display: block; margin: 8pt auto; break-inside: avoid; }
blockquote { border-left: 4px solid #b7791f; background: #fdf6e7; margin: 8pt 0; padding: 4pt 10pt; }
hr { border: 0; border-top: 1px solid #ddd; margin: 12pt 0; }
"""


def slug(text: str) -> str:
    """GitHub-style heading id: lower case, keep word characters, spaces and hyphens, spaces → hyphens."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def render(md_path: Path, running: str) -> str:
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    tokens = md.parse(md_path.read_text(encoding="utf-8"))
    headings = {}
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open":
            text = tokens[i + 1].content
            tok.attrSet("id", slug(text))
            m = re.match(r"(\d+)\.\s", text)
            if m and tok.tag == "h2":
                headings[int(m.group(1))] = slug(text)
        for child in tok.children or []:   # images live inside inline tokens
            if child.type == "image":
                src = child.attrGet("src")
                if src and not re.match(r"^[a-z]+:", src):
                    f = (md_path.parent / src).resolve()
                    child.attrSet("src", f"{f.as_uri()}?v={f.stat().st_mtime_ns}")   # never a cached copy
    body = md.renderer.render(tokens, md.options, {})

    def link_toc(match: re.Match) -> str:
        items = re.findall(r"<li>(.*?)</li>", match.group(2), flags=re.S)
        linked = [f'<li><a href="#{headings.get(n, "")}">{t}</a></li>' if n in headings else f"<li>{t}</li>"
                  for n, t in enumerate(items, 1)]
        return match.group(1) + "\n".join(linked) + match.group(3)

    body = re.sub(r'(<h2 id="table-of-contents">Table of contents</h2>\s*<ol>)(.*?)(</ol>)', link_toc, body,
                  count=1, flags=re.S)
    css = CSS.replace("__RUNNING__", running.replace('"', "'"))
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(running)}</title>'
            f"<style>{css}</style></head><body>{body}</body></html>")


def page_count(pdf: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)", pdf.read_bytes()))


def main() -> int:
    browser = next((b for b in BROWSERS if Path(b).exists()), None)
    if browser is None:
        print("No Chrome or Edge found; open the .html files and print them to PDF by hand.")
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="bdsl_reports_"))
    try:
        for md_path, pdf_path, running in DOCS:
            html_path = tmp / (md_path.stem + ".html")
            html_path.write_text(render(md_path, running), encoding="utf-8")
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            fresh = tmp / pdf_path.name
            subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--user-data-dir={tmp / 'profile'}", f"--print-to-pdf={fresh}", html_path.as_uri()],
                           check=True, capture_output=True, timeout=300)
            if not fresh.exists() or fresh.stat().st_size == 0:
                print(f"{pdf_path.name}: the browser wrote no PDF")
                return 1
            try:
                shutil.copyfile(fresh, pdf_path)
            except PermissionError:
                keep = Path(tempfile.gettempdir()) / pdf_path.name
                shutil.copyfile(fresh, keep)
                print(f"{pdf_path.name}: target is open in another program (close it and re-run); new PDF kept at {keep}")
                continue
            print(f"{pdf_path.relative_to(ROOT)}: {pdf_path.stat().st_size:,} bytes, {page_count(pdf_path)} pages")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
