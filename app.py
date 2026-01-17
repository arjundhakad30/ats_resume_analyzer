import streamlit as st
from parser import extract_text, extract_sections
from scorer import section_scores, overall_score
from feedback import analyze_feedback
from suggestions_ai import rewrite_section
from suggestions_rule import generate_suggestions
from skills_db import SKILLS

st.set_page_config("ATS Resume Analyzer", layout="wide")
st.title("📄 ATS Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
jd_text = st.text_area("Paste Job Description", height=220)

if st.button("Analyze Resume"):
    if resume_file and jd_text:
        resume_text = extract_text(resume_file)
        sections = extract_sections(resume_text)

        # ATS scoring
        scores = section_scores(sections, jd_text)
        total_score = overall_score(scores)

        st.subheader("📊 Section-wise ATS Score")
        for sec, sc in scores.items():
            st.write(f"{sec.capitalize()}: {sc}%")

        st.metric("Overall ATS Score", f"{total_score}%")

        # Feedback & missing skills
        strengths, weaknesses, missing_skills = analyze_feedback(scores, resume_text, jd_text)

        st.subheader("✅ Good Things")
        for s in strengths:
            st.success(s)

        st.subheader("❌ Mistakes / Weak Points")
        for w in weaknesses:
            st.error(w)

        # Rule-based suggestions
        st.subheader("🛠 Suggestions (Offline Rules)")
        suggestions = generate_suggestions(resume_text, jd_text, sections, missing_skills)
        for sug in suggestions:
            st.write("✔️", sug)

        # AI-based suggestions (offline)
        st.subheader("✨ Resume Rewrite Suggestions")
        for sec, content in sections.items():
            if content:
                with st.expander(f"Improve {sec.capitalize()} Section"):
                    st.write(rewrite_section(content[:400], sec))

    else:
        st.error("Please upload a resume and paste the job description")
