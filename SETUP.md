# Resume Analyzer — Backend Setup

## 1. Unzip and open in VS Code
Unzip this file to `~/Desktop/resume-analyzer/` so you end up with:
```
resume-analyzer/
  backend/
    app/
      __init__.py
      main.py
      parser.py
      scorer.py
    requirements.txt
```
Open the `resume-analyzer` folder in VS Code.

## 2. Create a virtual environment
In the VS Code terminal:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```
(Your terminal prompt should now show `(venv)` at the start)

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Run the server
```bash
uvicorn app.main:app --reload
```
You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

## 5. Test it works
Open a browser and go to: **http://127.0.0.1:8000/docs**

This opens FastAPI's auto-generated docs. Click on `POST /api/analyze` → "Try it out" → upload any resume PDF → Execute. You should get back a JSON response with your ATS score.

## Next steps
Once this works locally, we'll:
1. Add JD matching (paste a job description → get match %)
2. Add LLM-powered suggestions + resume rewrite
3. Build the Next.js frontend
4. Push to GitHub
5. Deploy live (Render for backend, Vercel for frontend)

## Troubleshooting
- **"command not found: uvicorn"** → make sure `(venv)` shows in your terminal prompt; if not, re-run `source venv/bin/activate`
- **Port already in use** → run `uvicorn app.main:app --reload --port 8001` instead
