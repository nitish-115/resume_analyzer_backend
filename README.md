# Resume Analyzer — Backend

FastAPI backend powering an AI resume analysis tool. Parses PDF/DOCX resumes,
computes a transparent ATS compatibility score, detects the best-fit job
roles, and matches a resume against any job description or link.

**Live API:** https://resume-analyzer-backend-n3qp.onrender.com/docs
**Frontend:** https://github.com/Mohsin2106/resume-analyzer-frontend
**Live site:** https://resume-analyzer-mohsin.vercel.app

## Features
- **ATS Scoring** — 6-category, fully explainable score (contact info, section
  structure, action verbs, quantified achievements, formatting, keyword
  relevance) with a per-check breakdown, not a black-box number.
- **Role Fit Detection** — ranks the resume against 7 common tech role
  profiles (ML Engineer, Data Scientist, SDE, Backend/Frontend Dev, MLOps)
  and shows the exact keywords driving each match.
- **Job Description Matching** — paste a job link or raw text; the API
  extracts the skills/requirements it emphasizes and returns what the resume
  already covers, what's missing, and what to add.

## Tech Stack
Python · FastAPI · pdfplumber · python-docx · BeautifulSoup · Render (deploy)

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyze` | Upload a resume → ATS score + role fit |
| POST | `/api/match-job` | Upload a resume + job link/text → skill match |

## Running locally
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API docs.
