"""
extractor.py — Extract raw text from PDF, image, or plain text files.
Uses pdfplumber for PDFs and EasyOCR (pure Python, no Tesseract needed) for images.
"""

import io
import re


def extract_from_file(uploaded_file) -> str:
    """
    Accepts a Streamlit UploadedFile object.
    Returns extracted raw text string.
    """
    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".txt"):
        return _extract_text(data)
    elif name.endswith(".pdf"):
        return _extract_pdf(data)
    elif name.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")):
        return _extract_image(data)
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def _extract_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def _extract_pdf(data: bytes) -> str:
    try:
        import pdfplumber
        pages_text = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                pages_text.append(t)

        start_index = _find_syllabus_start(pages_text)
        text = "\n".join(pages_text[start_index:]).strip()

        if len(text) > 100:
            return text
        raise RuntimeError(
            "This PDF appears to be scanned (image-only) and contains no selectable text.\n\n"
            "💡 Tip: Open the PDF, select all text (Ctrl+A), copy it, "
            "then paste into the text box on the right."
        )
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")


def _find_syllabus_start(pages_text: list) -> int:
    """
    Return the index of the page where the syllabus content begins.
    Looks for headings and structural keywords common in academic syllabi.
    Falls back to page 0 if nothing specific is found.
    """
    # Strong signals — a line that is clearly a syllabus section header
    STRONG = re.compile(
        r"""
        ^\s*                        # start of line, optional whitespace
        (
            syllabus |
            course\s*(outline|content|structure|details|description) |
            curriculum |
            unit\s*[-–—:]?\s*[1I] |    # Unit 1 / Unit I
            module\s*[-–—:]?\s*[1I] |   # Module 1 / Module I
            chapter\s*[-–—:]?\s*[1I] |
            topics?\s*(covered|to\s+be\s+covered) |
            subject\s*(content|outline) |
            detailed\s*syllabus |
            theory\s*syllabus |
            part\s*[-–—:]?\s*[aA1I]
        )
        \b
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE,
    )

    # Weaker signals — general academic content markers
    WEAK = re.compile(
        r"""
        ^\s*
        (
            unit\s*[-–—:]?\s*\d+ |
            module\s*[-–—:]?\s*\d+ |
            chapter\s*[-–—:]?\s*\d+ |
            lecture\s*[-–—:]?\s*\d+ |
            section\s*[-–—:]?\s*\d+
        )
        \b
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE,
    )

    # Skip obvious non-syllabus pages: title/cover, TOC, acknowledgements, etc.
    SKIP = re.compile(
        r"table\s+of\s+contents|acknowledgement|preface|foreword|"
        r"certificate|declaration|dedication|index\s*$|^\s*page\s+\d",
        re.IGNORECASE,
    )

    best_strong = None
    best_weak = None

    for i, text in enumerate(pages_text):
        if not text.strip():
            continue
        if SKIP.search(text) and i < 5:
            continue
        if STRONG.search(text):
            if best_strong is None:
                best_strong = i
        elif WEAK.search(text):
            if best_weak is None:
                best_weak = i

    if best_strong is not None:
        return best_strong
    if best_weak is not None:
        return best_weak
    return 0   # fallback: use entire document


def _extract_image(data: bytes) -> str:
    """Use EasyOCR if available; otherwise show a friendly fallback message."""
    try:
        import easyocr
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(data)).convert("RGB")
        img_array = np.array(img)

        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        results = reader.readtext(img_array, detail=0, paragraph=True)
        return "\n".join(results)
    except ImportError:
        raise RuntimeError(
            "Image OCR is not available in this environment.\n\n"
            "💡 Tip: Open the image, copy the text manually, "
            "then paste it into the text box on the right — that works perfectly!"
        )
    except Exception as e:
        raise RuntimeError(f"Image OCR failed: {e}")
