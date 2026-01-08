# PyMuPDF (fitz) API Cheatsheet

## Basic Document Handling

```python
import fitz

# Open document
doc = fitz.open("filename.pdf")

# Get page count
count = doc.page_count

# Get metadata
meta = doc.metadata

# Close document
doc.close()
```

## Page Access

```python
# specific page (0-indexed)
page = doc[0]

# Iterate over pages
for page in doc:
    # do something
    pass
```

## Text Extraction

```python
# Plain text
text = page.get_text("text")

# Structured blocks (tuple)
# (x0, y0, x1, y1, "lines in block", block_no, block_type)
blocks = page.get_text("blocks")

# Detailed dictionary (JSON-like)
data = page.get_text("dict")
```

## Image Extraction

```python
# Get list of images on page
img_list = page.get_images()

for img in img_list:
    xref = img[0]
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(f"image_{xref}.png")
```

## Rendering (Rasterization)

```python
# Render page to image
pix = page.get_pixmap(dpi=150)
pix.save("page_0.png")
```

## PDF Manipulation

```python
# Insert page
doc.insert_page(1, text="Hello World", fontsize=11)

# Delete page
doc.delete_page(0)

# Save
doc.save("output.pdf", garbage=4, deflate=True)
```
