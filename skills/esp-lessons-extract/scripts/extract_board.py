#!/usr/bin/env python3
"""Prepare a Miro board PDF export for reading.

Miro exports each board area as one huge raster image per PDF page (no text
layer). This script:
  1. extracts the embedded page images at full resolution (pdfimages),
  2. cuts each page into overlapping vertical tiles small enough to view,
     upscaling short (low-resolution) pages so small text stays legible,
  3. runs tesseract (eng+rus) on every tile and writes a rough OCR draft.

Usage:
  python3 extract_board.py <board.pdf> <out_dir>

Output in <out_dir>:
  page-N.png            full-resolution page image
  tiles/pN_TT.png       tiles to open with the Read tool for visual checking
  ocr/pN_TT.txt         OCR draft per tile
  ocr/page-N.txt        all tiles of a page concatenated, with tile markers
  index.txt             page sizes, tile list, which pages are low-res
"""
import os
import shutil
import subprocess
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

TILE_W = 1700          # tile width in source pixels for normal pages
OVERLAP = 150          # overlap so text cut at a tile edge appears whole in one tile
LOW_RES_HEIGHT = 1500  # pages shorter than this are treated as low-res
LOW_RES_TILE_W = 1100
LOW_RES_SCALE = 3


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def ocr(path):
    for lang in ("eng+rus", "eng"):
        r = run(["tesseract", path, "-", "-l", lang, "--psm", "3"])
        if r.returncode == 0:
            return "\n".join(l for l in r.stdout.splitlines() if l.strip())
    return ""


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf, out = sys.argv[1], sys.argv[2]
    for tool in ("pdfimages", "tesseract"):
        if not shutil.which(tool):
            sys.exit(f"missing tool: {tool}")
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    os.makedirs(os.path.join(out, "ocr"), exist_ok=True)

    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    r = run(["pdfimages", "-png", pdf, os.path.join(raw, "img")])
    if r.returncode != 0:
        sys.exit(r.stderr)
    imgs = sorted(os.listdir(raw))
    if not imgs:
        sys.exit("no embedded images found; the PDF may have a text layer — try pdftotext first")

    index = []
    for pno, name in enumerate(imgs, 1):
        im = Image.open(os.path.join(raw, name)).convert("RGB")
        page_path = os.path.join(out, f"page-{pno}.png")
        im.save(page_path)
        W, H = im.size
        low = H < LOW_RES_HEIGHT
        tw = LOW_RES_TILE_W if low else TILE_W
        x, t, page_txt = 0, 0, []
        while x < W:
            tile = im.crop((x, 0, min(W, x + tw), H))
            if low:
                tile = tile.resize((tile.width * LOW_RES_SCALE, tile.height * LOW_RES_SCALE), Image.LANCZOS)
            # skip blank tiles
            if tile.convert("L").getextrema()[0] < 240:
                tp = os.path.join(out, "tiles", f"p{pno}_{t:02d}.png")
                tile.save(tp)
                text = ocr(tp)
                with open(os.path.join(out, "ocr", f"p{pno}_{t:02d}.txt"), "w") as f:
                    f.write(text)
                page_txt.append(f"=== tile p{pno}_{t:02d} (x {x}-{min(W, x + tw)})\n{text}")
                t += 1
            x += tw - OVERLAP
        with open(os.path.join(out, "ocr", f"page-{pno}.txt"), "w") as f:
            f.write("\n\n".join(page_txt))
        index.append(f"page {pno}: {W}x{H}{' LOW-RES (tiles upscaled x3)' if low else ''}, {t} tiles")

    shutil.rmtree(raw)
    with open(os.path.join(out, "index.txt"), "w") as f:
        f.write("\n".join(index) + "\n")
    print("\n".join(index))


if __name__ == "__main__":
    main()
