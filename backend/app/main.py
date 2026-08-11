"""
Resume Analyzer API
Main FastAPI application entrypoint.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests

from app.parser import parse_resume
from app.scorer import compute_ats_score
from app.role_matcher import compute_role_fit
from app.job_matcher import compute_job_match, fetch_job_text_from_url

app = FastAPI(
    title="Resume Analyzer API",
    description="Upload a resume, get an ATS score, job match, and improvement suggestions.",
    version="1.0.0",
)

# Allow the Next.js frontend (any origin during dev; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your deployed frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Resume Analyzer API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Accepts a PDF or DOCX resume file.
    Returns parsed structure + ATS score breakdown.
    """
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max size is 5MB.")

    try:
        parsed = parse_resume(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    ats_result = compute_ats_score(parsed)
    role_fit = compute_role_fit(parsed["raw_text"])

    return {
        "filename": file.filename,
        "word_count": parsed["word_count"],
        "contact_info": parsed["contact_info"],
        "sections_detected": [k for k, v in parsed["sections"].items() if v.strip() and k != "other"],
        "ats_score": ats_result,
        "role_fit": role_fit,
    }


@app.post("/api/match-job")
async def match_job(
    file: UploadFile = File(...),
    job_url: Optional[str] = Form(None),
    job_text: Optional[str] = Form(None),
):
    """
    Accepts a resume file plus either a job posting URL or pasted job
    description text. Returns a skill-match breakdown: what's covered,
    what's missing, and what to add or emphasize.
    """
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    if not job_url and not job_text:
        raise HTTPException(status_code=400, detail="Provide either a job_url or job_text.")

    file_bytes = await file.read()
    try:
        parsed = parse_resume(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    resolved_job_text = job_text
    if not resolved_job_text and job_url:
        try:
            resolved_job_text = fetch_job_text_from_url(job_url)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except requests.exceptions.RequestException:
            raise HTTPException(
                status_code=422,
                detail="Couldn't fetch that job URL. Please paste the job description text instead."
            )

    match_result = compute_job_match(parsed["raw_text"], resolved_job_text)
    return match_result
