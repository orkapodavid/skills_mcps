#!/usr/bin/env python3
"""
extract_text.py — Structured text extraction from PDFs using PyMuPDF (fitz).

Usage:
  python extract_text.py --input sample.pdf --pages 1-3,6 --out out/text.json

Requirements:
  pip install pymupdf
"""
import argparse
import json
import time
from pathlib import Path

import fitz  # PyMuPDF


def parse_pages(pages_str, page_count):
    if not pages_str:
        return list(range(page_count))
    result = set()
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            a_i = max(1, int(a))
            b_i = min(page_count, int(b))
            for i in range(a_i, b_i + 1):
                result.add(i - 1)
        else:
            i = max(1, int(part))
            if i <= page_count:
                result.add(i - 1)
    return sorted(result)


def extract_text(doc: fitz.Document, page_indexes):
    pages = []
    for idx in page_indexes:
        page = doc.load_page(idx)
        blocks = page.get_text("rawdict")
        text = page.get_text("text")
        pages.append({"index": idx + 1, "text": text, "blocks": blocks.get("blocks", [])})
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to PDF")
    ap.add_argument("--pages", default="", help="1-indexed page ranges like '1-3,6'")
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--timeout_sec", type=int, default=120)
    args = ap.parse_args()

    start = time.time()
    in_path = Path(args.input)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    with fitz.open(in_path) as doc:
        page_indexes = parse_pages(args.pages, doc.page_count)
        pages = extract_text(doc, page_indexes)

    payload = {"ok": True, "pages": pages}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    elapsed = time.time() - start
    print(f"Wrote {out_path} in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
