#!/usr/bin/env python3
"""
extract_images.py — Render pages or export embedded images using PyMuPDF (fitz).

Usage:
  python extract_images.py --input sample.pdf --pages 1-2 --dpi 200 --mode render --format png --out out/images

Requirements:
  pip install pymupdf pillow
"""
import argparse
import json
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


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


def render_pages(doc: fitz.Document, page_indexes, dpi: int, fmt: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for idx in page_indexes:
        pix = doc.load_page(idx).get_pixmap(matrix=mat)
        out_path = out_dir / f"page_{idx+1}.{fmt}"
        pix.save(out_path.as_posix())
        paths.append(out_path.as_posix())
    return paths


def export_embedded_images(doc: fitz.Document, page_indexes, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for idx in page_indexes:
        page = doc.load_page(idx)
        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha < 4:  # RGB/RGBA
                out_path = out_dir / f"page_{idx+1}_xref_{xref}.png"
                pix.save(out_path.as_posix())
                paths.append(out_path.as_posix())
            else:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                out_path = out_dir / f"page_{idx+1}_xref_{xref}.png"
                pix.save(out_path.as_posix())
                paths.append(out_path.as_posix())
            pix = None
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--pages", default="")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--mode", choices=["render", "embedded"], default="render")
    ap.add_argument("--format", choices=["png", "jpg"], default="png")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out)
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    with fitz.open(in_path) as doc:
        page_indexes = parse_pages(args.pages, doc.page_count)
        if args.mode == "render":
            paths = render_pages(doc, page_indexes, args.dpi, args.format, out_dir)
        else:
            paths = export_embedded_images(doc, page_indexes, out_dir)

    manifest = {"ok": True, "images": paths}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
