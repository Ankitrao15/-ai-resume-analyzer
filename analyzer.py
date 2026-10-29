"""Rule-based resume analysis. No external AI API key is required."""
from collections import Counter
from io import BytesIO
from pathlib import Path
import re
from typing import Dict, List

SKILL_GROUPS = {
    "Programming": ["python", "java", "javascript", "typescript", "c++", "sql"],
    "Backend & APIs": ["fastapi", "django", "flask", "rest api", "api", "spring boot", "node.js"],
    "Data & ML": ["pandas", "numpy", "scikit-learn", "machine learning", "deep learning", "data analysis", "power bi", "tableau", "matplotlib"],
    "Databases": ["postgresql", "mysql", "sqlite", "mongodb", "database"],
    "Tools & Cloud": ["git", "github", "docker", "aws", "azure", "linux", "ci/cd"],
    "Professional": ["communication", "leadership", "teamwork", "problem solving", "agile"],
}

ACTION_VERBS = [
    "built", "created", "developed", "designed", "implemented", "improved",
    "automated", "analyzed", "delivered", "deployed", "optimized", "led",
    "managed", "reduced", "increased", "tested", "maintained",
]
SECTION_HINTS = {
    "Contact details": ["email", "phone", "linkedin", "github"],
    "Summary / objective": ["summary", "objective", "profile"],
    "Skills": ["skills", "technical skills", "technologies"],
    "Experience": ["experience", "internship", "employment", "work history"],
    "Projects": ["projects", "project experience"],
    "Education": ["education", "degree", "university", "college"],
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _contains_phrase(text: str, phrase: str) -> bool:
    # Use word boundaries for simple tokens and escaped phrase matching for terms with punctuation.
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def extract_text_from_file(content: bytes, suffix: str) -> str:
    if suffix == ".txt":
        return content.decode("utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError("Could not read this PDF. Try exporting it as a text-based PDF or .txt file.") from exc
    if suffix == ".docx":
        try:
            from docx import Document
            doc = Document(BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            raise ValueError("Could not read this DOCX file. Please check that it is a valid Word document.") from exc
    raise ValueError("Unsupported file type. Use .txt, .pdf, or .docx.")


def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    text = _normalise(resume_text)
    jd = _normalise(job_description)
    found_by_group: Dict[str, List[str]] = {}
    all_skills = []
    for group, skills in SKILL_GROUPS.items():
        found = [skill for skill in skills if _contains_phrase(text, skill)]
        if found:
            found_by_group[group] = found
            all_skills.extend(found)

    jd_skills = []
    if jd:
        for skills in SKILL_GROUPS.values():
            for skill in skills:
                if _contains_phrase(jd, skill) and skill not in jd_skills:
                    jd_skills.append(skill)
    matched = [skill for skill in jd_skills if _contains_phrase(text, skill)]
    missing = [skill for skill in jd_skills if skill not in matched]
    match_score = round((len(matched) / len(jd_skills)) * 100) if jd_skills else None

    section_status = {}
    for label, hints in SECTION_HINTS.items():
        section_status[label] = any(hint in text for hint in hints)
    action_verb_count = sum(1 for verb in ACTION_VERBS if _contains_phrase(text, verb))
    quantified = len(re.findall(r"(?<!\w)(?:\d+(?:\.\d+)?%?|\$\s?\d+|₹\s?\d+)(?!\w)", resume_text))
    word_count = len(re.findall(r"\b[\w+#.-]+\b", resume_text))
    email_present = bool(re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text, re.I))
    phone_present = bool(re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", resume_text))
    project_present = section_status["Projects"]
    experience_present = section_status["Experience"]

    score = 0
    score += min(len(all_skills) * 3, 24)
    score += sum(8 for value in section_status.values() if value)
    score += 8 if email_present else 0
    score += 5 if phone_present else 0
    score += min(action_verb_count * 2, 10)
    score += min(quantified * 2, 10)
    score += 5 if 250 <= word_count <= 900 else (2 if word_count >= 120 else 0)
    score = min(score, 100)

    suggestions = []
    if not email_present:
        suggestions.append("Add a professional email address in the contact section.")
    if not phone_present:
        suggestions.append("Add a reachable phone number, if appropriate for your applications.")
    if not section_status["Summary / objective"]:
        suggestions.append("Add a 2–3 line professional summary tailored to the target role.")
    if not section_status["Skills"]:
        suggestions.append("Create a clear technical-skills section with relevant keywords.")
    if not project_present:
        suggestions.append("Include 2–3 projects with your contribution, tools, and outcome.")
    if not experience_present:
        suggestions.append("Add internships, work experience, or relevant practical experience.")
    if action_verb_count < 3:
        suggestions.append("Start bullet points with strong action verbs such as built, automated, tested, or improved.")
    if quantified < 2:
        suggestions.append("Quantify results where truthful (e.g., processing time reduced by 20%).")
    if jd and missing:
        suggestions.append("Address missing job-description skills only if you genuinely have them; otherwise plan to learn them.")
    if word_count < 120:
        suggestions.append("The resume looks short; add relevant details without padding it with unrelated content.")
    if word_count > 1000:
        suggestions.append("Consider trimming repetitive details to keep the resume focused.")

    return {
        "overall_score": score,
        "score_label": "Strong" if score >= 75 else "Developing" if score >= 50 else "Needs improvement",
        "word_count": word_count,
        "detected_skills": found_by_group,
        "skill_count": len(all_skills),
        "sections": section_status,
        "contact_checks": {"email_detected": email_present, "phone_detected": phone_present},
        "writing_signals": {"action_verbs_detected": action_verb_count, "quantified_items_detected": quantified},
        "job_match": {
            "score": match_score,
            "required_skills_found": matched,
            "skills_to_review": missing,
            "skills_detected_in_job_description": jd_skills,
        },
        "suggestions": suggestions,
        "disclaimer": "This is a transparent, rule-based guide—not a hiring decision or a guarantee of interview success. Review results manually and do not add skills you do not have."
    }
