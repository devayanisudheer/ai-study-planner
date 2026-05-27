"""
extractor.py — Extract raw text from PDF, image, or plain text files.
Uses pdfplumber for PDFs and EasyOCR (pure Python, no Tesseract needed) for images.
"""

import os
import io


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
        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        text = "\n".join(text_parts).strip()
        if len(text) > 100:
            return text
        # If very little text, it may be a scanned PDF — let user know
        raise RuntimeError(
            "This PDF appears to be scanned (image-only) and contains no selectable text.\n\n"
            "💡 Tip: Open the PDF, select all text (Ctrl+A), copy it, "
            "then paste into the text box on the right."
        )
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")


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
