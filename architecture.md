# Architecture — ATS Resume Score

## Stack
Python 3.10+, Streamlit (UI), pypdf + python-docx (parsing), scikit-learn (TF-IDF), sentence-transformers `all-MiniLM-L6-v2` (semantic similarity, optional), requests + Ollama (optional local LLM).

## Folder structure
```
ats_resume_analyzer/
├── app.py               # Streamlit UI only (layout, CSS, rendering, session state)
├── analyzer.py          # analyze(resume_text, jd_text) -> result dict (scores, risks, suggestions)
├── parser.py            # extract_text (PDF/DOCX), normalize, extract_sections (heading-based)
├── skills_db.py         # SKILLS (aliases), ROLE_PROFILES, find_skills(), detect_role()
├── scorer.py            # semantic_score() — SBERT, falls back to TF-IDF
├── suggestions_rule.py  # split_bullets(), has_metric(), ACTION_VERBS, WEAK_STARTS, regexes
├── suggestions_ai.py    # rule-based bullet rewrites (no LLM)
├── ai_mode.py           # Ollama client: list_models(), ai_feedback() with JSON-schema output
├── requirements.txt
└── README.md
```

## Data flow
```
file/paste ─► parser.extract_text ─► normalize ─► parser.extract_sections
                                                       │
JD (optional) ─────────────────────────────┐           ▼
                                           ▼      analyzer.analyze()
skills_db.find_skills ──► keyword coverage ─┤   ├─ risks + formatting score
scorer.semantic_score ──► semantic match ───┘   ├─ 7 category scores → overall → grade
                                                 └─ suggestions, keywords, notes
                                                       │
                          (AI mode on) ai_mode.ai_feedback(result) ─► result["ai"]
                                                       ▼
                                              app.py renders result
```

## Result schema (returned by analyze)
```
{ overall:int, grade:str, summary:str,
  scores:{Formatting,Keywords,Experience,Education,Skills,Impact,Readability: int 0-100},
  risks:[{title, severity:"high|medium|low", why, fix}],
  missing:[str], strong:[str],
  suggestions:[{priority, title, detail, example}],
  notes:[str], has_jd:bool,
  ai?: {summary, suggestions[], rewrites[{original, improved}], model} | {error} }
```

## Scoring (all rule-based, deterministic)
Overall = weighted sum: Keywords 0.20, Experience 0.20, Skills 0.15, Impact 0.15, Formatting 0.10, Education 0.10, Readability 0.10.
Grade: A ≥90, B+ ≥85, B ≥80, C+ ≥70, C ≥60, else D.
- **Keywords**: with JD → 0.6 × JD-skill coverage + 0.4 × semantic score. Without JD → coverage of the detected role's profile skills (divided by 60% of profile size).
- **Formatting**: 100 minus penalties (no email -15, no phone -10, missing section heading -5..-10, spaced headings -8, icons -5, short/long -5, unreadable -40).
- **Experience**: section present + length + action-verb ratio + metric ratio (+ 25% semantic vs JD if given). Missing = 20.
- **Education**: present + degree keyword + CGPA/year. Missing = 25.
- **Skills**: count of known skills in Skills section (+ 50% JD coverage if JD given).
- **Impact**: 60% share of bullets with numbers + 40% share starting with action verbs.
- **Readability**: word count, avg bullet length, long paragraphs, ALL-CAPS share, bullet usage.

## Key mechanisms
- **Section detection**: a line is a heading only if it matches a known alias exactly (≤4 words). Sections never copy the whole resume.
- **Skill matching**: regex with word boundaries (`java` ≠ `javascript`, `git` ≠ `digit`).
- **Bullets**: lines starting with any non-alphanumeric glyph begin a bullet; wrapped lines are joined.
- **Semantic score**: JD chunks vs resume chunks (120 words), best match per JD chunk, calibrated to 0-100. Falls back to TF-IDF if SBERT can't load.

## AI mode (Ollama)
`list_models()` → `ai_feedback()` POSTs `/api/chat` with a JSON schema (`format`), `think:false`, `num_ctx 8192`. Output is validated: priorities coerced, max 5 suggestions, max 4 rewrites, rewrites whose `original` isn't in the resume are dropped, `<think>` blocks stripped. Any failure → `{error}` and the app shows rule-based results only. **The LLM never changes scores.**

## Error handling
Scanned/empty PDF → clear message; unreadable file → message; no input → message; Ollama down/slow/invalid JSON → warning + fallback; SBERT unavailable → TF-IDF.

## Run
`pip install -r requirements.txt` → `python -m streamlit run app.py`. AI mode needs Ollama running with a pulled model (e.g. `ollama pull qwen3:8b`).