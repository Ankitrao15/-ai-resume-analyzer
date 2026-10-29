from pathlib import Path
import re
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.analyzer import analyze_resume, extract_text_from_file

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(
    title="AI Resume Analyzer",
    description="A portfolio-ready resume analysis and job-description matching API.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_BYTES = 5 * 1024 * 1024


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Resume Analyzer", "version": "1.0.0"}


@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = "",
):
    suffix = Path(resume.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Upload a .txt, .pdf, or .docx file.")
    content = await resume.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 5 MB.")
    try:
        resume_text = extract_text_from_file(content, suffix)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(resume_text.strip()) < 30:
        raise HTTPException(status_code=400, detail="Not enough readable text was found in the resume.")
    return analyze_resume(resume_text, job_description)


@app.post("/api/analyze-text")
async def analyze_text(payload: dict):
    resume_text = str(payload.get("resume_text", "")).strip()
    job_description = str(payload.get("job_description", "")).strip()
    if len(resume_text) < 30:
        raise HTTPException(status_code=400, detail="resume_text must contain at least 30 characters.")
    if len(resume_text) > 100_000 or len(job_description) > 30_000:
        raise HTTPException(status_code=413, detail="Text exceeds the supported length.")
    return analyze_resume(resume_text, job_description)


@app.get("/api/sample")
async def sample():
    sample_path = BASE_DIR / "sample_data" / "sample_resume.txt"
    return {"resume_text": sample_path.read_text(encoding="utf-8")}
