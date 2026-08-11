"""
Job Match Engine
Given a job description (pasted text or a URL), extracts the skills and
requirements it emphasizes, and compares them against the resume to show
what's already covered, what's missing, and what to add.
"""
import re
from collections import Counter
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# A broad master skill list — shared vocabulary used to scan both the resume
# and the job description, so matches are apples-to-apples.
MASTER_SKILLS: List[str] = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "r language", "sql", "html", "css", "kotlin", "swift", "scala",
    # ML / AI
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "sklearn", "nlp", "computer vision", "cnn", "opencv",
    "neural network", "mlflow", "transfer learning", "llm", "rag",
    "prompt engineering", "hugging face", "generative ai", "langchain",
    # Data
    "pandas", "numpy", "matplotlib", "seaborn", "power bi", "tableau",
    "data analysis", "data visualization", "etl", "statistics", "excel",
    "data structures", "algorithms",
    # Web / Backend
    "react", "next.js", "node.js", "express", "django", "flask", "fastapi",
    "rest api", "graphql", "microservices", "redux", "tailwind", "vue",
    "angular",
    # Infra / Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "jenkins",
    "terraform", "git", "github", "linux", "devops", "mlops",
    # Databases
    "mongodb", "postgresql", "mysql", "redis", "firebase",
    # Soft / process
    "agile", "scrum", "system design", "unit testing", "debugging",
    "communication", "leadership", "problem solving", "teamwork",
]

STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will",
    "this", "that", "have", "has", "role", "team", "work", "job", "we",
    "to", "of", "in", "on", "a", "an", "is", "as", "be", "or", "at",
}


def fetch_job_text_from_url(url: str) -> str:
    """Attempts to fetch and extract readable text from a job posting URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    cleaned = "\n".join(lines)

    if len(cleaned.split()) < 40:
        raise ValueError(
            "Couldn't extract enough text from that page — it may require "
            "login or JavaScript. Please paste the job description text instead."
        )
    return cleaned


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    return [s for s in MASTER_SKILLS if s in text_lower]


def top_jd_keywords(job_text: str, jd_skills: List[str], limit: int = 10) -> List[str]:
    """
    Ranks matched skills by how often they're mentioned in the JD, as a proxy
    for what the employer emphasizes most.
    """
    text_lower = job_text.lower()
    counts = Counter({skill: text_lower.count(skill) for skill in jd_skills})
    ranked = [skill for skill, _ in counts.most_common(limit)]
    return ranked


def compute_job_match(resume_text: str, job_text: str) -> Dict:
    jd_skills = extract_skills(job_text)
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
            "jd_top_requirements": [],
            "suggestions": [
                "Couldn't detect specific technical skills in this job description. "
                "Try pasting the full job description text for a more accurate match."
            ],
        }

    matched = sorted([s for s in jd_skills if s in resume_skills])
    missing = sorted([s for s in jd_skills if s not in resume_skills])

    match_pct = round((len(matched) / len(jd_skills)) * 100)
    top_requirements = top_jd_keywords(job_text, jd_skills)

    suggestions = []
    if missing:
        priority_missing = [s for s in top_requirements if s in missing][:6]
        if priority_missing:
            suggestions.append(
                "This job emphasizes these skills your resume doesn't currently show: "
                + ", ".join(priority_missing)
                + ". If you have real experience with any of these, add them explicitly."
            )
    if matched:
        emphasized_matches = [s for s in top_requirements if s in matched][:5]
        if emphasized_matches:
            suggestions.append(
                "Good news — you already have skills this job emphasizes most: "
                + ", ".join(emphasized_matches)
                + ". Make sure these appear early and clearly on your resume, not buried."
            )
    if match_pct < 40:
        suggestions.append(
            "Your overall keyword overlap with this job is low. Consider whether "
            "this role is a strong fit, or tailor your resume's language to match "
            "the job's terminology more closely."
        )

    return {
        "match_percentage": match_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "jd_top_requirements": top_requirements,
        "suggestions": suggestions,
    }
