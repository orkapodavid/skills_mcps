---
name: PyMuPDF
description: This skill should be used when the user asks to "extract text from PDF", "extract images from PDF", "read PDF metadata", "render PDF pages", "convert PDF to image", or "manipulate PDFs".
version: 1.0.0
---

# PyMuPDF Skill

This skill provides capabilities for interacting with PDF documents using the PyMuPDF (fitz) library. It includes tools for text extraction, image handling, and document rendering.

## Core Capabilities

To interact with PDFs, use the following capabilities:

1.  **Extract Structured Text**: Get text with layout information (blocks, spans, fonts).
2.  **Extract Images**: specific embedded images or render whole pages.
3.  **Read Metadata**: Access document properties and Table of Contents (TOC).
4.  **Render Pages**: Convert PDF pages to raster images (PNG/JPG) for preview.

## Usage

### Quick Start with Examples

Use the provided example scripts in `examples/` for common tasks.

**Extract Text:**
To extract text to JSON:
```bash
python examples/extract_text.py --input path/to/doc.pdf --pages 1-3 --out out/text.json
```

**Extract/Render Images:**
To render pages as images:
```bash
python examples/extract_images.py --input path/to/doc.pdf --dpi 200 --mode render --out out/images/
```

### Script Usage Guidelines

- Always specify `--input` with an absolute path.
- Use `--pages` to limit scope (e.g., "1-5,7").
- Check output directories for results.

## Best Practices

- **Page Ranges**: Prefer processing specific page ranges rather than entire documents to save memory.
- **DPI Settings**: Use 150-200 DPI for readable previews; 300+ for OCR or high-quality printing.
- **Fail Fast**: Handle `file not found` or `encrypted PDF` errors explicitly.
- **Security**:
    - Do not execute embedded JavaScript.
    - Validate PDF origins if processing untrusted files.
    - Set timeouts for large document processing.

## Additional Resources

### Reference Files

- **`references/api-cheatsheet.md`**: Quick reference for PyMuPDF (fitz) Python API.
- **`references/tool-definitions.md`**: Documentation for the structured tool definitions in `tools/skill.json`.

### Example Files

- **`examples/extract_text.py`**: Script for structured text extraction.
- **`examples/extract_images.py`**: Script for image extraction and page rendering.

### Tools

- **`tools/skill.json`**: JSON schema definitions for agentic usage.
