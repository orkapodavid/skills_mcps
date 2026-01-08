# Agent Tool Definitions

The file `tools/skill.json` contains machine-readable definitions for the following tools:

## `extract_text`
Extracts structured text from selected pages of a PDF.
- **Inputs**: `input` (path), `pages` (range string), `max_pages`, `timeout_sec`
- **Outputs**: Structured text blocks per page.

## `extract_images`
Exports page renders or embedded images to a directory.
- **Inputs**: `input` (path), `pages`, `dpi`, `mode` (render/embedded), `format`, `out_dir`
- **Outputs**: List of saved image paths.

## `get_metadata`
Returns document metadata and table of contents.
- **Inputs**: `input` (path)
- **Outputs**: Metadata dictionary and TOC array.

## `render_pages`
Renders pages to images for preview.
- **Inputs**: `input` (path), `pages`, `dpi`, `format`, `out_dir`
- **Outputs**: List of rendered image paths.
