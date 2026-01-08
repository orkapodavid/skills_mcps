# PyMuPDF Agent Skill (Improved)

This package refines and extends the original SkillsMP "pymupdf - Agent Skill by Genius-Cai" content for direct use by coding agents and automation workflows.

It provides:
- Clean, actionable API semantics for common PDF tasks (text, images, metadata)
- Ready-to-run Python scripts with CLI flags
- Structured JSON tool schema for agents to invoke functions safely
- Robust error handling, logging, and performance tips
- Security considerations and sandbox best practices

## Quick Start

- Python 3.12+
- Install: `pip install pymupdf pillow`  (PyMuPDF installs as `fitz`)

```bash
python examples/extract_text.py --input tests/sample.pdf --pages 1-3 --out out/text.json
python examples/extract_images.py --input tests/sample.pdf --dpi 200 --out out/images/
```

## Core Capabilities

1) Extract structured text
- Per page blocks, spans, bbox, font info
- Page range selection, maximum pages, timeouts

2) Extract images
- Rasterize full pages or export embedded images
- Control DPI, format (PNG/JPG), and compression

3) Metadata and outline
- Document info (author, title, creation date)
- TOC/outline tree

4) Page rendering
- Render pages to images for preview/annotation

## Agent Tool Schema (skill.json)

See `tools/skill.json` for machine-callable functions:
- `extract_text`: returns structured text per page
- `extract_images`: writes images to a directory, returns manifest
- `get_metadata`: returns document info
- `render_pages`: renders to PNG/JPG

All functions validate inputs and return clear success/error payloads.

## Best Practices

- Prefer page ranges to avoid loading entire documents
- Use DPI 150–200 for readable previews; 300+ for OCR
- Handle encrypted PDFs by checking `doc.is_encrypted` and calling `doc.authenticate(password)`
- Use `try/except` at function boundaries; fail fast with explicit messages

## Security Notes

- Never execute embedded JavaScript in PDFs
- Do not trust external links inside PDFs
- Limit maximum pages/time to prevent resource exhaustion

## Changelog

- 2026-01-09: Initial improved version for coding agents
