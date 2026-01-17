from skills_db import SKILLS

def generate_suggestions(resume_text, jd_text, sections, missing_skills):
    suggestions = []

    # Missing skills
    if missing_skills:
        suggestions.append(f"Add missing skills: {', '.join(missing_skills)}")

    # Weak experience
    if len(sections.get("experience", "").split()) < 50:
        suggestions.append("Experience section is short: add measurable achievements and numbers")

    # Weak projects
    if len(sections.get("projects", "").split()) < 30:
        suggestions.append("Projects section is short: include technical details and results")

    # Short overall resume
    if len(resume_text.split()) < 200:
        suggestions.append("Overall resume is short: consider adding more skills, projects, and experience")

    # ATS-unfriendly patterns
    if "table" in resume_text.lower() or "image" in resume_text.lower():
        suggestions.append("Avoid tables/images: use plain text for ATS readability")

    return suggestions
