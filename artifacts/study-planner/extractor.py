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
        end_index = _find_syllabus_end(pages_text, start_index)
        text = "\n".join(pages_text[start_index:end_index]).strip()

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


def _is_textbook_page(text: str) -> bool:
    """
    Return True if the page looks like textbook body content (dense prose)
    rather than a syllabus outline (short topic lines).
    """
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 4:
        return False

    word_counts = [len(l.split()) for l in lines]
    avg_words = sum(word_counts) / len(word_counts)

    # Lines that read like prose sentences
    sentence_lines = sum(
        1 for l in lines
        if l.rstrip().endswith((".", "?", "!")) and len(l.split()) > 8
    )
    prose_ratio = sentence_lines / len(lines)

    # Long-line ratio — textbook paragraphs have many long lines
    long_lines = sum(1 for w in word_counts if w > 14)
    long_ratio = long_lines / len(lines)

    # Textbook prose markers
    PROSE_MARKERS = re.compile(
        r"\b(therefore|however|thus|hence|moreover|furthermore|"
        r"in\s+this\s+(chapter|section|unit)|as\s+shown\s+in|"
        r"figure\s+\d|table\s+\d|example\s+\d|definition\s*:|"
        r"theorem\s*:|proof\s*:|note\s*:|refers?\s+to|"
        r"is\s+defined\s+as|can\s+be\s+(written|expressed|shown))\b",
        re.IGNORECASE,
    )
    prose_marker_hits = len(PROSE_MARKERS.findall(text))

    # Decide: high average word count + high prose ratio → textbook
    if avg_words > 13 and prose_ratio > 0.35:
        return True
    if long_ratio > 0.45 and prose_marker_hits >= 2:
        return True
    if prose_marker_hits >= 4:
        return True

    return False


def _find_syllabus_end(pages_text: list, start: int) -> int:
    """
    Return the index (exclusive) where syllabus content ends.
    Stops as soon as we hit consecutive textbook-body pages.
    Ensures we always include at least a few pages after start.
    """
    MIN_SYLLABUS_PAGES = 2   # always include at least this many pages
    CONSECUTIVE_PROSE_LIMIT = 2  # stop after this many consecutive prose pages

    consecutive_prose = 0
    end = len(pages_text)

    for i in range(start, len(pages_text)):
        if i < start + MIN_SYLLABUS_PAGES:
            continue
        if _is_textbook_page(pages_text[i]):
            consecutive_prose += 1
            if consecutive_prose >= CONSECUTIVE_PROSE_LIMIT:
                end = i - (CONSECUTIVE_PROSE_LIMIT - 1)
                break
        else:
            consecutive_prose = 0

    return end


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
