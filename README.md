# AI Resume Analyzer — ResumeLens

A portfolio-ready resume review web application built with **Python, FastAPI, HTML, CSS, and JavaScript**. It scans a resume for common sections and listed skills, gives practical improvement suggestions, and optionally compares resume skills with a pasted job description.

> This is a transparent, rule-based analyzer. It does not call an external AI service, does not require an API key, and does not predict hiring outcomes.

## Features

- Upload resumes in `.txt`, `.pdf`, and `.docx` formats (5 MB maximum).
- Resume checklist score with a breakdown of detectable signals.
- Skill detection grouped by category.
- Job description skill overlap and skills to review.
- Suggestions for resume structure, action verbs, and quantified achievements.
- JSON API, browser UI, sample resume and sample job description.
- Automated tests for core analysis behavior.
- Uploaded file content is processed in memory; the app does not intentionally save uploaded resumes.

## Project structure

```text
ai_resume_analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── analyzer.py
│   ├── templates/index.html
│   └── static/
│       ├── app.js
│       └── styles.css
├── sample_data/
│   ├── sample_resume.txt
│   └── sample_job_description.txt
├── tests/test_analyzer.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer (Python 3.11/3.12 recommended)
- pip
- Internet access only to install dependencies

## Setup and run

### Windows PowerShell

```powershell
cd ai_resume_analyzer
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run this in the current terminal session or use Command Prompt activation instead:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
cd ai_resume_analyzer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser. API documentation is at **http://127.0.0.1:8000/docs**.

## Demo

1. Open the app.
2. Upload `sample_data/sample_resume.txt`.
3. Open `sample_data/sample_job_description.txt` and paste its content into the job description box.
4. Click **Analyze resume**.
5. Review the overall checklist score, detected skills, section checks, job match, and suggestions.

Scores are heuristic checklist metrics, not an actual ATS score. Skill matching is based on a maintained keyword list; synonyms and context may be missed. Do not add skills to a resume unless you can substantiate them.

## API examples

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Analyze text as JSON

```bash
curl -X POST http://127.0.0.1:8000/api/analyze-text \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Python Developer. Email: demo@example.com. Skills: Python, FastAPI, SQL. Experience: Developed APIs. Projects: Built a demo application. Education: Computer Science degree.","job_description":"Python FastAPI SQL Docker"}'
```

### Upload a file

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -F "resume=@sample_data/sample_resume.txt" \
  -F "job_description=Python FastAPI PostgreSQL SQL Docker"
```

### Sample endpoint

`GET /api/sample` returns the bundled sample resume as JSON.

## Run tests

```bash
pytest -q
```

## How the score works

The checklist combines detected skills, common resume sections, contact details, action verbs, numeric evidence, and a basic word-count range. The calculation is intentionally inspectable in `app/analyzer.py`. Job match is the percentage of recognized job-description skills also detected in the resume.

## Privacy and responsible use

- The app does not intentionally persist uploaded resume files.
- Do not upload sensitive documents to a public deployment without reviewing its security, logging, retention, and privacy setup.
- Before production deployment, add authentication, rate limiting, request logging controls, malware scanning, and a clear privacy notice.
- This tool is for personal improvement and should not be used as the sole basis for hiring, rejection, or other consequential decisions.
