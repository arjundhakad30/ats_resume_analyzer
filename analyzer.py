"""Full ATS analysis: 7 category scores, grade, risks, keywords, prioritized suggestions."""
import re
from parser import extract_sections
from skills_db import find_skills, detect_role
from scorer import semantic_score, get_backend
from suggestions_rule import split_bullets, has_metric, first_word, ACTION_VERBS, WEAK_STARTS, EMAIL_RE, PHONE_RE
from suggestions_ai import rewrite_section

CATEGORIES = ["Formatting", "Keywords", "Experience", "Education", "Skills", "Impact", "Readability"]
WEIGHTS = {"Keywords": 0.20, "Experience": 0.20, "Skills": 0.15, "Impact": 0.15,
           "Formatting": 0.10, "Education": 0.10, "Readability": 0.10}
DEGREE_RE = re.compile(r"\b(b\.?\s?tech|m\.?\s?tech|b\.?\s?sc|m\.?\s?sc|bca|mca|mba|bachelor|master|diploma|ph\.?d|engineering|12th|10th|hsc|ssc|cbse)\b", re.I)
GRADE_RE = re.compile(r"(cgpa|gpa|percentage|%|\b(19|20)\d{2}\b)", re.I)
SYMBOL_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uE000-\uF8FF]")
SPACED_HEADING_RE = re.compile(r"\b[A-Z] [A-Z]{3,}\b")
SEV_ORDER = {"high": 0, "medium": 1, "low": 2}


def _clamp(x):
    return int(max(0, min(100, round(x))))


def grade(score):
    return ("A" if score >= 90 else "B+" if score >= 85 else "B" if score >= 80 else
            "C+" if score >= 70 else "C" if score >= 60 else "D")


def _spaced_headings(text):
    return any(len(SPACED_HEADING_RE.findall(l)) >= 2 for l in text.splitlines() if len(l) < 45)


def analyze(resume_text, jd_text=""):
    jd_text = (jd_text or "").strip()
    has_jd = bool(jd_text)
    sections = extract_sections(resume_text)
    words = len(resume_text.split())
    found = find_skills(resume_text)
    jd_skills = find_skills(jd_text) if has_jd else set()
    role_key, role = detect_role(found)

    bullets = split_bullets(sections.get("experience", "") + "\n" + sections.get("projects", ""))
    nb = len(bullets)
    metric_ratio = sum(has_metric(b) for b in bullets) / nb if nb else 0.0
    action_ratio = sum(first_word(b) in ACTION_VERBS for b in bullets) / nb if nb else 0.0
    weak_bullets = [b for b in bullets if b.lower().startswith(tuple(WEAK_STARTS))]

    # ---------------- risks + formatting ----------------
    risks, fmt = [], 100

    def risk(title, sev, why, fix, pen=0):
        nonlocal fmt
        risks.append({"title": title, "severity": sev, "why": why, "fix": fix})
        fmt -= pen

    if words < 50:
        risk("Almost no text could be extracted", "high", "ATS cannot read scanned/image resumes - it will see an empty resume.",
             "Export a text-based PDF (File > Download > PDF) or upload DOCX.", 40)
    if not EMAIL_RE.search(resume_text):
        risk("No email address found", "high", "Recruiters and ATS parsers need contact details to create your profile.",
             "Add your email at the top of the resume.", 15)
    if not PHONE_RE.search(resume_text):
        risk("No phone number found", "medium", "Missing contact details can get your profile rejected or unreachable.",
             "Add a phone number with country code near your email.", 10)
    low = resume_text.lower()
    if "linkedin" not in low and "github" not in low:
        risk("Contact information lacks clickable links (LinkedIn / GitHub)", "low",
             "Some ATS and recruiters prefer quick access to your profiles and work.",
             "Add linkedin.com/in/yourname and github.com/yourname in the header.", 5)
    for sec, sev, pen in (("skills", "high", 10), ("experience", "high", 10), ("education", "medium", 8), ("projects", "medium", 5)):
        if sec not in sections:
            risk(f"'{sec.capitalize()}' section heading not detected", sev,
                 "ATS maps your content using standard section headings; unlabeled content may be ignored.",
                 f"Add a clear heading named '{sec.capitalize()}'" + (" (or 'Internship')." if sec == "experience" else "."), pen)
    if _spaced_headings(resume_text):
        risk("Inconsistent spacing in section headers (e.g. 'P ROFESSIONAL S UMMARY')", "medium",
             "May cause parsing errors - ATS may fail to recognise those sections.",
             "Use plain standard headings such as 'Professional Summary'; avoid small-caps fonts.", 8)
    if SYMBOL_RE.search(resume_text):
        risk("Icons / special symbols detected", "medium", "Emoji and icon fonts often turn into garbage characters in ATS.",
             "Replace icons with plain text labels (Email:, Phone:).", 5)
    if resume_text.count("|") > 8:
        risk("Possible table / multi-column layout", "low", "Tables and columns can scramble reading order in ATS.",
             "Use a single-column layout with simple headings.", 3)
    if 50 <= words < 250:
        risk(f"Resume is short ({words} words)", "medium", "Too little content gives ATS few keywords to match.",
             "Add project details, tools used and results (target 300-700 words).", 5)
    elif words > 900:
        risk(f"Resume is long ({words} words)", "low", "Long resumes dilute keywords and are skimmed by recruiters.",
             "Trim to 1 page (2 max for experienced candidates).", 5)
    if nb and metric_ratio < 0.3:
        risk(f"Few quantified achievements ({sum(has_metric(b) for b in bullets)}/{nb} bullets have numbers)", "medium",
             "Numbers prove impact; resumes without them rank lower with recruiters.",
             "Add %, accuracy, users, records processed, time saved.")
    if weak_bullets:
        risk(f"{len(weak_bullets)} bullets start with weak phrases ('Responsible for', 'Worked on')", "low",
             "Weak openers hide what you actually achieved.", "Start each bullet with an action verb: Built, Designed, Automated.")
    risks.sort(key=lambda r: SEV_ORDER[r["severity"]])

    # ---------------- keywords ----------------
    if has_jd:
        sem = semantic_score(resume_text, jd_text)
        cov = len(found & jd_skills) / len(jd_skills) * 100 if jd_skills else None
        kw = sem if cov is None else 0.6 * cov + 0.4 * sem
        missing = sorted(jd_skills - found)
        strong = sorted(found & jd_skills) or sorted(found)
    else:
        expected = set(role["skills"])
        kw = len(found & expected) / max(1.0, len(expected) * 0.6) * 100
        missing = [s for s in role["skills"] if s not in found][:8]
        strong = sorted(found)

    # ---------------- other categories ----------------
    exp = sections.get("experience", "")
    if exp:
        ew = len(exp.split())
        eb = split_bullets(exp)
        e_act = sum(first_word(b) in ACTION_VERBS for b in eb) / len(eb) if eb else 0
        e_met = sum(has_metric(b) for b in eb) / len(eb) if eb else 0
        exp_score = 30 + 25 * min(1, ew / 120) + 25 * e_act + 20 * min(1, e_met / 0.5)
        if has_jd:
            exp_score = 0.75 * exp_score + 0.25 * semantic_score(exp, jd_text)
    else:
        exp_score = 20

    edu = sections.get("education", "")
    edu_score = 25 if not edu else 60 + (20 if DEGREE_RE.search(edu) else 0) + (20 if GRADE_RE.search(edu) else 0)

    sk_sec = sections.get("skills", "")
    if sk_sec:
        n = len(find_skills(sk_sec))
        skills_score = 40 + min(50, n * 5) + 10 * (n >= 3)
        if jd_skills:
            skills_score = 0.5 * skills_score + 0.5 * (len(found & jd_skills) / len(jd_skills) * 100)
    else:
        skills_score = min(60, 20 + len(found) * 4)

    impact = 25 if not nb else 100 * (0.6 * min(1, metric_ratio / 0.6) + 0.4 * action_ratio)

    read = 100
    if words < 250:
        read -= 20
    elif words > 900:
        read -= 15
    if nb:
        avg = sum(len(b.split()) for b in bullets) / nb
        read -= 0 if 8 <= avg <= 28 else (20 if avg > 35 else 10)
    if any(len(l.split()) > 45 for l in resume_text.splitlines()):
        read -= 10
    caps = [w for w in resume_text.split() if len(w) > 3 and w.isupper()]
    if words and len(caps) / words > 0.15:
        read -= 10
    if exp and not nb:
        read -= 10

    scores = {"Formatting": _clamp(fmt), "Keywords": _clamp(kw), "Experience": _clamp(exp_score),
              "Education": _clamp(edu_score), "Skills": _clamp(skills_score), "Impact": _clamp(impact),
              "Readability": _clamp(read)}
    overall = _clamp(sum(scores[c] * WEIGHTS[c] for c in CATEGORIES))

    # ---------------- suggestions ----------------
    sugg = []
    if missing:
        pr = "high" if len(missing) >= 3 else "medium"
        sugg.append({"priority": pr, "title": "Add more relevant keywords",
                     "detail": f"Add keywords related to {', '.join(missing[:6])} - only if you genuinely have them.",
                     "example": f"Experience with {', '.join(missing[:3])} in [project / workflow name]."})
    rewrites = rewrite_section("\n".join("• " + b for b in bullets), "bullets") if bullets else []
    no_metric = [r for r in rewrites if any("Add impact" in n for n in r["notes"])]
    if nb and metric_ratio < 0.5 and no_metric:
        sugg.append({"priority": "high" if metric_ratio < 0.3 else "medium", "title": "Add quantified impact in projects/experience",
                     "detail": "Include outcomes: %, accuracy, users, time saved, records processed.",
                     "example": no_metric[0]["improved"]})
    weak_rw = [r for r in rewrites if any("weak opener" in n for n in r["notes"])]
    if weak_rw:
        sugg.append({"priority": "medium", "title": "Replace weak bullet openers", "detail": "Start bullets with strong action verbs.",
                     "example": weak_rw[0]["improved"]})
    if _spaced_headings(resume_text):
        sugg.append({"priority": "medium", "title": "Improve section header formatting",
                     "detail": "Standardize section headers to remove extra spaces and use conventional capitalization.",
                     "example": "Professional Summary"})
    miss_secs = [s.capitalize() for s in ("skills", "experience", "education", "projects") if s not in sections]
    if miss_secs:
        sugg.append({"priority": "high", "title": "Add standard section headings",
                     "detail": f"Not detected: {', '.join(miss_secs)}.", "example": " / ".join(miss_secs)})
    if "summary" not in sections:
        top = ", ".join(sorted(found)[:3]) or "[your top skills]"
        sugg.append({"priority": "low", "title": "Add a short professional summary",
                     "detail": "2-3 lines at the top tailored to the role help ATS and recruiters.",
                     "example": f"[Your degree] student skilled in {top}, with hands-on project experience. Seeking a {role['label']} role."})
    if "linkedin" not in low and "github" not in low:
        sugg.append({"priority": "low", "title": "Add LinkedIn and GitHub links", "detail": "Make your profile one click away.",
                     "example": "LinkedIn: linkedin.com/in/yourname | GitHub: github.com/yourname"})
    if not EMAIL_RE.search(resume_text) or not PHONE_RE.search(resume_text):
        sugg.append({"priority": "high", "title": "Add complete contact details", "detail": "Email and phone must be in the header.",
                     "example": "yourname@email.com | +91 XXXXX XXXXX"})
    sugg.sort(key=lambda s: SEV_ORDER[s["priority"]])

    # ---------------- summary + notes ----------------
    ranked = sorted(CATEGORIES, key=lambda c: scores[c], reverse=True)
    parts = [f"Strongest areas: {ranked[0]} ({scores[ranked[0]]}) and {ranked[1]} ({scores[ranked[1]]}).",
             f"Needs most work: {ranked[-1]} ({scores[ranked[-1]]})."]
    parts.append("Keywords were matched against your job description." if has_jd else
                 f"No job description provided, so keyword matching is generic for {role['label']} roles.")
    found_secs = [s for s in ("summary", "skills", "experience", "projects", "education") if s in sections]
    notes = [f"Extracted {words} words. Sections detected: {', '.join(found_secs) or 'none'}.",
             f"Matching engine: {'Sentence-BERT' if get_backend() == 'sbert' else 'TF-IDF fallback'}."]
    if words >= 250 and found_secs:
        notes.append("Resume text is complete and parsed well.")

    return {"overall": overall, "grade": grade(overall), "summary": " ".join(parts), "scores": scores,
            "risks": risks, "missing": missing, "strong": strong[:16], "suggestions": sugg[:6],
            "notes": notes, "has_jd": has_jd}
