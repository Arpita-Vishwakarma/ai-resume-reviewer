# ResumeAI — Instant Resume Feedback (FastAPI + LangChain + Gemini)

**Upload your resume → Get instant AI feedback and improvement suggestions.**  
Powered by **LangChain**, **FastAPI**, and **Gemini** with a lightweight HTML/CSS frontend.


## Project overview
ResumeAI accepts user resume files (PDF, DOCX, TXT) via a web UI or API, extracts content, and runs a multi-step analysis pipeline to produce human-friendly feedback: structure, grammar, keyword match, role suitability, ATS-compatibility tips, and suggested rewordings. The analysis is orchestrated with LangChain and uses Gemini (or other configured LLM) for scoring and rewrite suggestions.

---

## Features
- Upload resume (PDF / DOCX / TXT) via web UI or API  
- Content extraction (text from PDF/DOCX)  
- Multi-pass analysis:
  - Structural suggestions (sections & order)
  - Language/grammar improvements
  - Role & keyword matching (against provided JD)
  - ATS friendliness checks (format, fonts, bullets)
  - Actionable rewrite suggestions and sample bullets
- Download revised resume draft & textual summary report  
- Simple logging and optional webhook callbacks

---

## Tech stack
- **Backend**: Python, **FastAPI**, Uvicorn  
- **LLM orchestration**: **LangChain**  
- **LLM**: Google **Gemini** (or configurable provider)  
- **File parsing**: `python-docx`, `pdfminer.six` / `PyMuPDF`  
- **Frontend**: Static **HTML**, **CSS**, minimal JavaScript (or SPA)  
- **Storage**: Local (dev) / S3-compatible for production  
- **Optional**: Docker, nginx, Celery/RQ for async workers

---

## Architecture
1. **Frontend** sends file + optional job description to backend.  
2. **FastAPI** receives file, saves temporarily, and enqueues/executes analysis.  
3. **Parser** extracts text + metadata from resume.  
4. **LangChain pipeline** orchestrates prompts & LLM calls (Gemini or alternative).  
5. **Backend** returns a JSON report and an optional downloadable suggested resume file.  
6. **Cleanup** temporary files per retention policy.

---

## Getting started

### Prerequisites
- Python 3.10+ (3.11 recommended)  
- `pip` or `poetry`  
- (Optional) Docker & Docker Compose  
- Credentials for Gemini (or chosen LLM) and LangChain-compatible setup

### Install
```bash
# create & activate venv
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
