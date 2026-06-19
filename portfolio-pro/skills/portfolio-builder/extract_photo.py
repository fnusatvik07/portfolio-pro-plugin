#!/usr/bin/env python3
"""
Extract a headshot from a resume / LinkedIn "Save to PDF" export.
Picks the most photo-like embedded image (large, roughly square, near the top) and saves it.
ToS-safe: reads only a local PDF the user provided. Does NOT scrape LinkedIn URLs.

Usage:  python3 extract_photo.py <input.pdf> [out.png]
Prints  "WROTE <path>"  on success, or "NO_PHOTO_FOUND" (exit 1) if none is suitable.
Needs:  pip install pymupdf
"""
import sys

def main():
    if len(sys.argv) < 2:
        print("usage: extract_photo.py <input.pdf> [out.png]"); return 2
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "photo.png"
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("NO_PHOTO_FOUND (install with: pip install pymupdf)"); return 1

    doc = fitz.open(src)
    best, best_score = None, -1.0
    for pno in range(min(2, len(doc))):          # headshots live on page 1 (sometimes 2)
        page = doc[pno]
        ph = page.rect.height or 1
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
            except Exception:
                continue
            w, h = pix.width, pix.height
            if w < 70 or h < 70:                  # too small = icon/bullet
                continue
            ar = w / h if h else 0
            if ar < 0.5 or ar > 2.0:              # skip banners / rules / logos
                continue
            rects = page.get_image_rects(xref) or []
            top = min((r.y0 for r in rects), default=0)
            score = float(w * h)                  # bigger is better
            score *= (1.0 - 0.5 * min(top / ph, 1.0))   # favor upper page
            if 0.75 <= ar <= 1.4:                 # square-ish = likely a face
                score *= 1.6
            if score > best_score:
                best_score, best = score, pix

    if best is None:
        print("NO_PHOTO_FOUND"); return 1
    if best.n - best.alpha >= 4:                  # CMYK -> RGB
        best = fitz.Pixmap(fitz.csRGB, best)
    best.save(out)
    print("WROTE " + out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
