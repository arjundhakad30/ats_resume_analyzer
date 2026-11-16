# PRD — ATS Resume Score

## 1. Overview
A Streamlit web app that analyses a resume against an optional job description (JD) and returns an ATS-style score, risks, keyword gaps and ready-to-use improvements. Built for students and freshers who want quick, free, private feedback.

## 2. Problem
- Students don't know why resumes get rejected by ATS (missing keywords, bad headings, no numbers, unreadable PDFs).
- Online checkers are paid, give unexplained scores, and upload resumes to third-party servers.

## 3. Target users
Engineering students / freshers applying to internships and campus drives (data science, web, software, embedded/electronics).

## 4. Goals
1. Explainable score: every number can be traced to a rule.
2. Actionable output: each problem comes with a fix and example text.
3. Works free and offline (local LLM optional).
4. Stable: same resume + same JD = same score.

## 5. Non-goals
- Not an official ATS (Workday/Greenhouse give no public score; ours is an estimate).
- No resume builder / template editor (for now).
- No user accounts or cloud storage.

## 6. Features
| ID | Feature | Priority |
|----|---------|----------|
| F1 | Upload PDF/DOCX or paste resume text | Must |
| F2 | Optional JD input | Must |
| F3 | Overall score (0-100) + grade (A, B+, B, C+, C, D) + summary | Must |
| F4 | 7 category scores: Formatting, Keywords, Experience, Education, Skills, Impact, Readability | Must |
| F5 | ATS risks with severity (high/medium/low), why, fix | Must |
| F6 | Missing / strong keyword chips (JD-based, or generic per detected role) | Must |
| F7 | Top suggestions with priority + ready-to-paste example | Must |
| F8 | Parsing notes (words extracted, sections detected) | Should |
| F9 | Local AI mode (Ollama): AI summary, suggestions, bullet rewrites | Should |
| F10 | Reset button, clear error messages (scanned PDF, empty input) | Must |

## 7. User flow
Open app → upload resume or paste text → (optional) paste JD → (optional) turn on AI mode → Check ATS Score → read score, fix risks, copy suggested text → edit resume → re-run.

## 8. Inputs / outputs
- Input: PDF, DOCX, or text; JD text.
- Output: score ring, 7 bars, risks, keyword chips, suggestions, parsing notes, optional AI blocks.

## 9. Constraints
- Python + Streamlit only; free to run.
- Resume text must not leave the user's machine (AI mode uses local Ollama).
- Must work on a normal laptop (CPU only is acceptable).

## 10. Success metrics
- Scores differ clearly between a good and a weak resume.
- No crash on scanned PDF, empty text, Ollama off, or invalid model JSON.
- User can go from upload to results in < 10 s (rule-based mode).

## 11. Future scope
Export report (PDF), compare two resume versions, role selector, more skills in DB, multi-language resumes, deploy rule-based version online.