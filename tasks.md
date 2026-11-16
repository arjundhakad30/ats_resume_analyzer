# Tasks — ATS Resume Score

Update this file whenever a feature is finished. Format: `- [x] done` / `- [ ] todo`.

## Done
- [x] Streamlit app: upload PDF + paste JD, score and feedback (v1)
- [x] Fix fake section scoring: real heading-based section detection
- [x] Keep digits/symbols in text (C++, 92%, Node.js)
- [x] Word-boundary skill matching + 100+ skills (incl. electronics/embedded)
- [x] Calibrated semantic score (chunked, SBERT with TF-IDF fallback)
- [x] DOCX support and paste-text option
- [x] 7 category scores + overall + grade
- [x] ATS risks with severity, why, fix
- [x] Missing / strong keyword chips (JD-based or role-based generic)
- [x] Prioritised suggestions with ready-to-paste examples
- [x] Parsing notes, scanned-PDF handling, Reset button
- [x] Streamlit UI matching the reference layout (ring, bars, cards, chips)
- [x] Local AI mode (Ollama, JSON-schema output, validation, fallback)
- [x] Installed Ollama + qwen3:4b / qwen3:8b on dev laptop

## In progress
- [ ] Test AI mode with real Ollama on both models; compare quality/speed
- [ ] Push v3 to GitHub (`arjundhakad30/ats_resume_analyzer`)

## Next
- [ ] Add `tests/` with sample resumes + JDs and pytest for parser, skills, scoring
- [ ] Tune score weights/penalties on 5-10 real resumes
- [ ] Expand `skills_db.py` (more roles: ECE/VLSI, core engineering, cloud)
- [ ] Role selector dropdown for no-JD mode
- [ ] Export report as PDF / download button
- [ ] Compare two resume versions (before/after score)
- [ ] Screenshots + demo GIF in README
- [ ] Deploy rule-based version (Streamlit Community Cloud; AI mode won't work there)

## Ideas / maybe
- [ ] Hindi/multilingual resumes
- [ ] ATS-friendly resume template download
- [ ] Optional cloud LLM with explicit user consent