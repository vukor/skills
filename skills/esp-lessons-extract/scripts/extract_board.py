#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow", "pymupdf"]
# ///
"""Prepare a Miro board PDF export for reading.

Miro exports each board area as one huge raster image per PDF page (no text
layer). This script:
  1. extracts the embedded page images at full resolution (PyMuPDF; pages
     without an embedded image are rendered at 200 dpi),
  2. cuts each page into overlapping vertical tiles small enough to view,
     upscaling short pages so small text stays legible,
  3. runs tesseract (eng+rus) on every tile if it is installed and writes a
     rough OCR draft. Without tesseract the OCR step is skipped: read the
     tiles yourself.

Usage:
  uv run extract_board.py <board.pdf> <out_dir>

Dependencies (pillow, pymupdf) come from the inline script metadata above,
so `uv run` needs nothing preinstalled. Without uv:
  python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pillow pymupdf
  /tmp/venv/bin/python extract_board.py <board.pdf> <out_dir>

Output in <out_dir>:
  page-N.png            full-resolution page image
  tiles/pN_TT.png       tiles to open with the Read tool for visual checking
  ocr/pN_TT.txt         OCR draft per tile (only when tesseract is present)
  ocr/page-N.txt        all tiles of a page concatenated, with tile markers
  index.txt             page sizes, tile list, upscale factors, text-layer flag
"""
import os
import shutil
import subprocess
import sys

try:
    import pymupdf
    from PIL import Image
except ImportError as e:
    sys.exit(f"missing Python module ({e.name}). Run with `uv run {sys.argv[0]} ...` "
             "or install pillow and pymupdf (see the module docstring).")

Image.MAX_IMAGE_PIXELS = None

TILE_W = 1700          # tile width in source pixels for normal pages
OVERLAP = 150          # overlap so text cut at a tile edge appears whole in one tile
LOW_RES_HEIGHT = 1500  # pages shorter than this are treated as low-res
LOW_RES_TILE_W = 1100
LOW_RES_SCALE = 3
MID_HEIGHT = 2200      # pages up to this height get a mild upscale (wide strips)
MID_TILE_W = 1500
MID_SCALE = 1.5
TEXT_LAYER_MIN = 50    # chars of extractable text that count as a real text layer


def ocr(path):
    for lang in ("eng+rus", "eng"):
        r = subprocess.run(["tesseract", path, "-", "-l", lang, "--psm", "3"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return "\n".join(l for l in r.stdout.splitlines() if l.strip())
    return ""


def page_image(doc, page):
    """Largest embedded image of the page, or the rendered page if there is none."""
    best = None
    for info in page.get_images(full=True):
        xref, w, h = info[0], info[2], info[3]
        if best is None or w * h > best[1] * best[2]:
            best = (xref, w, h)
    if best:
        pix = pymupdf.Pixmap(doc, best[0])
        if pix.n - pix.alpha > 3:  # CMYK etc.
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        mode = "RGBA" if pix.alpha else "RGB"
        return Image.frombytes(mode, (pix.width, pix.height), pix.samples).convert("RGB")
    pix = page.get_pixmap(dpi=200)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf, out = sys.argv[1], sys.argv[2]
    has_ocr = bool(shutil.which("tesseract"))
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    os.makedirs(os.path.join(out, "ocr"), exist_ok=True)

    doc = pymupdf.open(pdf)
    index = []
    for pno, page in enumerate(doc, 1):
        text_layer = len(page.get_text().strip()) >= TEXT_LAYER_MIN
        im = page_image(doc, page)
        im.save(os.path.join(out, f"page-{pno}.png"))
        W, H = im.size
        if H < LOW_RES_HEIGHT:
            tw, scale = LOW_RES_TILE_W, LOW_RES_SCALE
        elif H < MID_HEIGHT:
            tw, scale = MID_TILE_W, MID_SCALE
        else:
            tw, scale = TILE_W, 1
        x, t, page_txt = 0, 0, []
        while x < W:
            tile = im.crop((x, 0, min(W, x + tw), H))
            if scale != 1:
                tile = tile.resize((round(tile.width * scale), round(tile.height * scale)), Image.LANCZOS)
            # skip blank tiles
            if tile.convert("L").getextrema()[0] < 240:
                tp = os.path.join(out, "tiles", f"p{pno}_{t:02d}.png")
                tile.save(tp)
                if has_ocr:
                    text = ocr(tp)
                    with open(os.path.join(out, "ocr", f"p{pno}_{t:02d}.txt"), "w") as f:
                        f.write(text)
                    page_txt.append(f"=== tile p{pno}_{t:02d} (x {x}-{min(W, x + tw)})\n{text}")
                t += 1
            x += tw - OVERLAP
        if has_ocr:
            with open(os.path.join(out, "ocr", f"page-{pno}.txt"), "w") as f:
                f.write("\n\n".join(page_txt))
        notes = []
        if scale != 1:
            notes.append(f"tiles upscaled x{scale:g}")
        if text_layer:
            notes.append("HAS TEXT LAYER: try pdftotext / page.get_text()")
        index.append(f"page {pno}: {W}x{H}, {t} tiles" + (f" ({', '.join(notes)})" if notes else ""))

    if not has_ocr:
        index.append("OCR skipped: tesseract not installed; read tiles/ directly (brew install tesseract for drafts)")
    with open(os.path.join(out, "index.txt"), "w") as f:
        f.write("\n".join(index) + "\n")
    print("\n".join(index))


if __name__ == "__main__":
    main()
