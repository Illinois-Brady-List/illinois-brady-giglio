#!/usr/bin/env python3
"""Render the methodology markdown to a PDF using headless Chrome.

Usage:
    python md_to_pdf.py [illinois-brady-giglio-methodology.md] [--out methodology.pdf]

Requires: pip install markdown, and Google Chrome installed.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import markdown

TITLE = "Illinois Brady/Giglio officer database: Methodology"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: Letter; margin: 0.8in; }
body { font: 10.5pt/1.5 Georgia, 'Times New Roman', serif; color: #1a1a1a; }
h1 { font-size: 20pt; line-height: 1.2; margin: 0 0 14pt; }
h2 { font-size: 14pt; margin: 20pt 0 6pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt; }
blockquote { margin: 8pt 0; padding: 2pt 12pt; border-left: 3px solid #bbb; color: #444; font-size: 9.5pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
ul, ol { padding-left: 20pt; }
"""


def build(md_path, pdf_path):
    body = markdown.markdown(open(md_path, encoding="utf-8").read(), extensions=["tables", "sane_lists"])
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>{TITLE}</title>'
            f"<style>{CSS}</style></head><body><h1>{TITLE}</h1>{body}</body></html>")
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "methodology.html")
        open(src, "w", encoding="utf-8").write(html)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={os.path.abspath(pdf_path)}", "file://" + src],
                       check=True, capture_output=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md", nargs="?", default="illinois-brady-giglio-methodology.md")
    ap.add_argument("--out", default="illinois-brady-giglio-methodology.pdf")
    a = ap.parse_args()
    if not os.path.exists(CHROME):
        sys.exit("Google Chrome not found at " + CHROME)
    build(a.md, a.out)
    print("Wrote", a.out)
