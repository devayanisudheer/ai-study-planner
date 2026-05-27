# 📚 AI Study Planner

An AI-powered study planning web application that automatically extracts syllabus topics, tracks learning progress, and generates personalized exam preparation schedules for students.

![AI Study Planner](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)

---

## ✨ Features

- Upload syllabus as PDF or plain text
- Automatically extract topics
- Track completed topics with progress bar
- Generate personalized day-by-day study plans
- Rainbow-coloured modern UI
- Export study plans as PDF
- No API key required

---

## 🚀 Live Demo

Add your deployed link here:

```txt
https://your-replit-app.replit.app
```

---

## 🛠️ Tech Stack

- Python
- Streamlit
- pdfplumber
- PyMuPDF
- ReportLab
- NumPy

---

## 📦 Installation

### Clone the repository

```bash
git clone https://github.com/devayanisudheer/ai-study-planner.git
cd ai-study-planner
```

### Create virtual environment

```bash
python -m venv .venv
```

### Activate environment

#### Windows

```bash
.\.venv\Scripts\activate
```

#### Mac/Linux

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```bash
study-planner/
│
├── app.py
├── extractor.py
├── topic_parser.py
├── planner.py
├── pdf_export.py
└── requirements.txt
```

---

## 📸 Screenshots

Add screenshots here later.

---

## 🔮 Future Improvements

- AI-based topic difficulty analysis
- Pomodoro timer integration
- Mobile responsive UI
- Cloud sync support

---

## 📄 License

MIT License
