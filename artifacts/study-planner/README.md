# 📚 AI Study Planner

An AI-powered personalized study planner for BTech and degree students. Upload your syllabus, extract every topic automatically, tick what you've already covered, and get a rainbow-coloured day-by-day study plan with PDF export.

![AI Study Planner](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)

## ✨ Features

- **Upload syllabus** as PDF or plain text file, or paste text directly
- **Auto-extract topics** using a smart heuristic parser
- **Track progress** — tick topics you've already studied with a live progress bar
- **Generate a plan** — day-by-day schedule from today to your exam date
- **Rainbow UI** — animated gradient hero, colour-coded day cards
- **PDF export** — download your plan as a styled PDF
- **No API key needed** — fully offline, works out of the box

## 🚀 Run locally

### 1. Clone the repo
```bash
git clone https://github.com/your-username/ai-study-planner.git
cd ai-study-planner
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` automatically.

## 📁 File structure

```
study-planner/
├── app.py            # Main Streamlit UI
├── extractor.py      # PDF & text extraction
├── topic_parser.py   # Topic extraction (heuristic)
├── planner.py        # Day-by-day plan generator
├── pdf_export.py     # PDF export with ReportLab
└── requirements.txt  # Python dependencies
```

## 🛠️ How to use

1. **Step 1** — Upload your syllabus PDF or paste the text
2. **Step 2** — Click *Extract all topics* — the parser pulls every topic out automatically
3. **Step 3** — Tick any topics you've already studied
4. **Step 4** — Set your exam date and click *Generate plan*
5. **Step 5** — View your day-by-day rainbow plan and download as PDF

## 📦 Dependencies

| Package | Purpose |
|---|---|
| streamlit | Web UI |
| pdfplumber | PDF text extraction |
| PyMuPDF | Scanned PDF fallback |
| Pillow | Image handling |
| reportlab | PDF export |
| numpy | Array support |

## ☁️ Deploy on Replit

This project is ready to deploy on [Replit](https://replit.com) with one click. The production run command is already configured.

## 📄 License

MIT — free to use, modify, and share.
