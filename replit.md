# AI Study Planner

An AI-powered personalized study planner for BTech/degree students. Upload a syllabus (PDF, image, or text), extract topics, tick what you've already studied, and generate a day-by-day rainbow study plan. PDF export included.

## Run & Operate

- `streamlit run artifacts/study-planner/app.py --server.port 18986 --server.address 0.0.0.0 --server.headless true` — run the Streamlit app
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000, unused currently)
- Required env: none for core features; `GEMINI_API_KEY` optional for AI-powered topic extraction

## Stack

- Python 3.11, Streamlit
- pdfplumber — PDF text extraction
- PyMuPDF — scanned PDF → image → OCR fallback
- easyocr — image OCR (optional; graceful fallback if missing)
- ReportLab — PDF export
- google-generativeai — Gemini AI topic extraction (optional)
- pnpm workspaces, Node.js 24, TypeScript 5.9 (monorepo scaffold)

## Where things live

- `artifacts/study-planner/app.py` — main Streamlit UI
- `artifacts/study-planner/extractor.py` — PDF/image/text extraction
- `artifacts/study-planner/topic_parser.py` — topic extraction (Gemini + heuristic)
- `artifacts/study-planner/planner.py` — day-by-day plan generator
- `artifacts/study-planner/pdf_export.py` — PDF export with ReportLab
- `.streamlit/config.toml` — Streamlit server config

## Architecture decisions

- All logic is pure Python/Streamlit — no separate backend needed
- EasyOCR is optional; the app shows a clear error message if not installed rather than crashing
- Gemini API key is optional; built-in heuristic planner works without any key
- Material Icons font is explicitly imported in CSS to prevent icon ligatures from rendering as raw text

## Product

- Upload syllabus as PDF, image, or pasted text
- AI extracts all study topics automatically (heuristic + optional Gemini)
- Tick topics already studied with a progress bar
- Generate day-by-day study schedule from today to exam date
- Download plan as a styled PDF

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Streamlit Material Icons overlap: always import `https://fonts.googleapis.com/icon?family=Material+Icons+Sharp` in the CSS block, otherwise icon ligature text (e.g. "upload", "_arrow_right") shows as raw text overlapping labels
- easyocr fails to install on this Replit environment; handle ImportError gracefully in extractor.py

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
