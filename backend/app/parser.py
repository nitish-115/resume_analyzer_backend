"""
Resume Parser
Extracts raw text and structured sections from PDF/DOCX resumes.
"""
import re
import io
import pdfplumber
import docx
from typing import Dict, List


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text(file_bytes: bytes, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


# --- Section detection ---

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "internships", "internship"
    ],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "summary": ["summary", "objective", "profile", "about"],
    "achievements": ["achievements", "awards", "honors"],
}


def detect_sections(text: str) -> Dict[str, str]:
    """Split resume text into sections based on common headers."""
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {key: [] for key in SECTION_HEADERS}
    sections["other"] = []

    current_section = "other"
    for line in lines:
        clean = line.strip().lower().strip(":").strip()
        matched = None
        if 0 < len(clean) < 40:
            for section, keywords in SECTION_HEADERS.items():
                if clean in keywords or any(clean == kw for kw in keywords):
                    matched = section
                    break
        if matched:
            current_section = matched
            continue
        sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def extract_contact_info(text: str) -> Dict[str, bool]:
    email_found = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
    phone_found = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}", text))
    linkedin_found = "linkedin.com" in text.lower()
    github_found = "github.com" in text.lower()
    portfolio_found = bool(re.search(r"https?://[^\s]+\.(dev|me|io|com|in|netlify\.app|vercel\.app)", text.lower()))

    return {
        "email": email_found,
        "phone": phone_found,
        "linkedin": linkedin_found,
        "github": github_found,
        "portfolio_or_links": portfolio_found,
    }


def parse_resume(file_bytes: bytes, filename: str) -> Dict:
    raw_text = extract_text(file_bytes, filename)
    if not raw_text.strip():
        raise ValueError("Could not extract text from file. It may be a scanned/image-based document.")

    sections = detect_sections(raw_text)
    contact = extract_contact_info(raw_text)

    return {
        "raw_text": raw_text,
        "sections": sections,
        "contact_info": contact,
        "word_count": len(raw_text.split()),
    }
