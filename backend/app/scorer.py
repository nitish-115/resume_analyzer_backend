"""
ATS Scoring Engine
Rule-based, transparent scoring — every point is explainable, no black box.
"""
import re
from typing import Dict, List

ACTION_VERBS = {
    "achieved", "improved", "built", "created", "developed", "designed",
    "led", "managed", "increased", "decreased", "reduced", "implemented",
    "launched", "optimized", "automated", "engineered", "deployed",
    "architected", "streamlined", "delivered", "resolved", "spearheaded",
    "trained", "mentored", "analyzed", "researched", "collaborated"
}

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "involved in",
    "duties included", "assisted with"
]

BAD_ATS_ELEMENTS = [
    "table", "text box", "header", "footer"
]


def score_contact_info(contact: Dict[str, bool]) -> Dict:
    max_points = 15
    checks = []
    points = 0

    weights = {
        "email": 5, "phone": 4, "linkedin": 3, "github": 2, "portfolio_or_links": 1
    }
    for key, present in contact.items():
        w = weights.get(key, 0)
        if present:
            points += w
            checks.append({"check": f"{key.replace('_', ' ').title()} found", "passed": True, "points": w})
        else:
            checks.append({"check": f"{key.replace('_', ' ').title()} missing", "passed": False, "points": 0})

    return {"category": "Contact Info", "score": points, "max_score": max_points, "checks": checks}


def score_sections(sections: Dict[str, str]) -> Dict:
    max_points = 20
    required = ["experience", "education", "skills", "projects"]
    points = 0
    checks = []
    per_section = max_points // len(required)

    for sec in required:
        present = bool(sections.get(sec, "").strip())
        if present:
            points += per_section
            checks.append({"check": f"'{sec.title()}' section present", "passed": True, "points": per_section})
        else:
            checks.append({"check": f"'{sec.title()}' section missing", "passed": False, "points": 0})

    return {"category": "Section Structure", "score": points, "max_score": max_points, "checks": checks}


def score_action_verbs(raw_text: str) -> Dict:
    max_points = 20
    words = re.findall(r"\b[a-zA-Z]+\b", raw_text.lower())
    word_set = set(words)
    verbs_found = word_set.intersection(ACTION_VERBS)
    verb_count = len(verbs_found)

    # scale: 8+ distinct action verbs = full marks
    points = min(max_points, round((verb_count / 8) * max_points))

    weak_hits = [p for p in WEAK_PHRASES if p in raw_text.lower()]
    penalty = min(8, len(weak_hits) * 2)
    points = max(0, points - penalty)

    checks = [
        {"check": f"{verb_count} strong action verbs found ({', '.join(list(verbs_found)[:6])}{'...' if verb_count > 6 else ''})",
         "passed": verb_count >= 5, "points": points},
    ]
    if weak_hits:
        checks.append({
            "check": f"Weak phrases found: {', '.join(weak_hits)} (reduces impact)",
            "passed": False, "points": -penalty
        })

    return {"category": "Action Verbs & Impact Language", "score": points, "max_score": max_points, "checks": checks}


def score_quantification(raw_text: str) -> Dict:
    max_points = 15
    # numbers, percentages, currency, multipliers
    matches = re.findall(r"\b\d+(\.\d+)?\s*(%|percent|x|\+)?\b", raw_text)
    numeric_lines = len(re.findall(r"\b\d+(\.\d+)?%?\b", raw_text))

    points = min(max_points, round((numeric_lines / 6) * max_points))
    checks = [{
        "check": f"{numeric_lines} quantified metrics found (numbers, %, counts)",
        "passed": numeric_lines >= 4,
        "points": points
    }]
    return {"category": "Quantified Achievements", "score": points, "max_score": max_points, "checks": checks}


def score_length_format(raw_text: str, word_count: int) -> Dict:
    max_points = 10
    points = 0
    checks = []

    if 350 <= word_count <= 800:
        points += 6
        checks.append({"check": f"Good length ({word_count} words)", "passed": True, "points": 6})
    elif word_count < 350:
        points += 2
        checks.append({"check": f"Too short ({word_count} words) — add more detail", "passed": False, "points": 2})
    else:
        points += 3
        checks.append({"check": f"Too long ({word_count} words) — trim to 1 page", "passed": False, "points": 3})

    bullet_count = len(re.findall(
    r"^[\s]*[•\-\*‣◦▪●○➤➢✓✔·o]\s+\S", raw_text, re.MULTILINE
    ))
    if bullet_count < 3:
        short_lines = [
            l for l in raw_text.split("\n")
            if l.strip() and len(l.strip().split()) <= 18 and not l.strip().endswith(".")
        ]
        bullet_count = max(bullet_count, min(len(short_lines), 15))
    if bullet_count >= 6:
        points += 4
        checks.append({"check": f"{bullet_count} bullet points used (good scannability)", "passed": True, "points": 4})
    else:
        checks.append({"check": f"Only {bullet_count} bullet points — use more for readability", "passed": False, "points": 0})

    return {"category": "Length & Formatting", "score": points, "max_score": max_points, "checks": checks}


def score_keyword_density(raw_text: str) -> Dict:
    """Checks for presence of common tech/skill-adjacent keywords as a generic ATS-readiness signal."""
    max_points = 20
    common_keywords = [
        "python", "java", "javascript", "sql", "machine learning", "react",
        "node", "aws", "docker", "git", "api", "cloud", "agile", "data",
        "algorithm", "database", "cnn", "nlp", "model", "deployment", "testing"
    ]
    text_lower = raw_text.lower()
    found = [kw for kw in common_keywords if kw in text_lower]
    points = min(max_points, round((len(found) / 10) * max_points))

    checks = [{
        "check": f"{len(found)} relevant technical keywords found: {', '.join(found[:8])}{'...' if len(found) > 8 else ''}",
        "passed": len(found) >= 6,
        "points": points
    }]
    return {"category": "Keyword Relevance", "score": points, "max_score": max_points, "checks": checks}


def compute_ats_score(parsed_resume: Dict) -> Dict:
    """Combines all scoring sub-modules into one transparent breakdown."""
    raw_text = parsed_resume["raw_text"]
    sections = parsed_resume["sections"]
    contact = parsed_resume["contact_info"]
    word_count = parsed_resume["word_count"]

    breakdown: List[Dict] = [
        score_contact_info(contact),
        score_sections(sections),
        score_action_verbs(raw_text),
        score_quantification(raw_text),
        score_length_format(raw_text, word_count),
        score_keyword_density(raw_text),
    ]

    total_score = sum(b["score"] for b in breakdown)
    max_total = sum(b["max_score"] for b in breakdown)
    percentage = round((total_score / max_total) * 100) if max_total else 0

    # Generate top-level improvement suggestions from failed checks
    suggestions = []
    for category in breakdown:
        for check in category["checks"]:
            if not check["passed"]:
                suggestions.append(f"[{category['category']}] {check['check']}")

    return {
        "total_score": total_score,
        "max_score": max_total,
        "percentage": percentage,
        "breakdown": breakdown,
        "suggestions": suggestions[:10],
    }
