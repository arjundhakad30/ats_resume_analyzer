from skills_db import SKILLS

def analyze_feedback(section_scores, resume_text, jd_text):
    strengths = []
    weaknesses = []
    missing_skills = []

    for section, score in section_scores.items():
        if score >= 70:
            strengths.append(f"Strong {section.capitalize()} section")
        else:
            weaknesses.append(f"Weak {section.capitalize()} section")

    # Missing skills
    missing_skills = [s for s in SKILLS if s in jd_text.lower() and s not in resume_text.lower()]
    if missing_skills:
        weaknesses.append(f"Missing key technical skills: {', '.join(missing_skills)}")

    return strengths, weaknesses, missing_skills
