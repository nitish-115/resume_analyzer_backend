"""
Role Fit Matcher
Scores a resume's content against keyword/skill profiles for common tech
roles, and returns a ranked list of best-fit roles with reasoning.
This is intentionally rule-based (no external API) so it works instantly,
offline, and for free.
"""
from typing import Dict, List

ROLE_PROFILES: Dict[str, Dict] = {
    "Machine Learning Engineer": {
        "keywords": [
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "keras", "cnn", "neural network", "model training", "scikit-learn",
            "sklearn", "computer vision", "nlp", "opencv", "mlflow",
            "transfer learning", "mobilenet", "classification", "regression",
            "feature engineering", "hyperparameter", "dataset", "accuracy",
        ],
        "weight_boost": ["tensorflow", "pytorch", "cnn", "model training", "mlflow"],
    },
    "Data Scientist": {
        "keywords": [
            "data science", "pandas", "numpy", "matplotlib", "seaborn",
            "statistics", "regression", "hypothesis testing", "eda",
            "exploratory data analysis", "jupyter", "visualization",
            "predictive model", "a/b testing", "correlation", "scikit-learn",
            "r language", "tableau", "power bi",
        ],
        "weight_boost": ["eda", "exploratory data analysis", "hypothesis testing", "a/b testing"],
    },
    "Data Analyst": {
        "keywords": [
            "sql", "excel", "power bi", "tableau", "data analysis",
            "dashboard", "reporting", "kpi", "data visualization",
            "pivot table", "google sheets", "data cleaning", "statistics",
            "business intelligence", "etl",
        ],
        "weight_boost": ["sql", "power bi", "tableau", "dashboard", "etl"],
    },
    "Software Development Engineer (SDE)": {
        "keywords": [
            "data structures", "algorithms", "system design", "java",
            "c++", "leetcode", "rest api", "microservices", "oop",
            "object oriented", "git", "unit testing", "debugging",
            "software development", "backend", "scalability", "design patterns",
        ],
        "weight_boost": ["data structures", "algorithms", "system design", "leetcode"],
    },
    "Backend Developer": {
        "keywords": [
            "fastapi", "django", "flask", "node.js", "express", "rest api",
            "database", "sql", "postgresql", "mongodb", "docker",
            "microservices", "api development", "backend", "authentication",
            "server", "kubernetes",
        ],
        "weight_boost": ["fastapi", "django", "flask", "node.js", "docker"],
    },
    "Frontend / Full-Stack Developer": {
        "keywords": [
            "react", "next.js", "javascript", "typescript", "html", "css",
            "tailwind", "vue", "angular", "frontend", "full stack",
            "responsive design", "redux", "ui/ux", "web development",
        ],
        "weight_boost": ["react", "next.js", "typescript", "full stack"],
    },
    "MLOps / Cloud Engineer": {
        "keywords": [
            "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd",
            "mlops", "deployment", "cloud", "jenkins", "terraform",
            "infrastructure", "devops", "model deployment", "monitoring",
        ],
        "weight_boost": ["mlops", "kubernetes", "ci/cd", "model deployment"],
    },
}


def compute_role_fit(raw_text: str, top_n: int = 3) -> List[Dict]:
    """
    Scores the resume text against each role profile.
    Returns the top N roles ranked by fit percentage, each with the
    specific matched keywords used as reasoning.
    """
    text_lower = raw_text.lower()
    results = []

    for role, profile in ROLE_PROFILES.items():
        keywords = profile["keywords"]
        boosted = set(profile.get("weight_boost", []))

        matched = [kw for kw in keywords if kw in text_lower]
        if not matched:
            continue

        # Base score: proportion of role keywords found.
        base_score = len(matched) / len(keywords)
        # Boost score if any high-signal keywords for this role are present.
        boost_hits = len([m for m in matched if m in boosted])
        boost_score = boost_hits / max(len(boosted), 1)

        combined = round(min(100, (base_score * 65 + boost_score * 35) * 100 / 1))
        # Normalize: base_score and boost_score are already 0..1, so scale to 0..100
        combined = round(min(100, base_score * 65 + boost_score * 35))

        results.append({
            "role": role,
            "fit_percentage": combined,
            "matched_keywords": sorted(matched, key=lambda k: k not in boosted)[:8],
        })

    results.sort(key=lambda r: r["fit_percentage"], reverse=True)
    top = results[:top_n]

    # Filter out near-zero noise matches (e.g. only 1 generic keyword)
    top = [r for r in top if r["fit_percentage"] >= 15]

    return top
