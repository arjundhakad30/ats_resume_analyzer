# ATS Resume Checker (Streamlit)

Upload a resume (PDF/DOCX) or paste its text, optionally add a job description, and get:
- Overall ATS score + grade, summary
- 7 category scores: Formatting, Keywords, Experience, Education, Skills, Impact, Readability
- ATS risks with severity (high/medium/low), why they matter, and how to fix
- Missing / strong keyword chips (JD-based, or generic for the detected role when no JD is given)
- Prioritized suggestions with ready-to-use rewrite text
- Parsing notes (words extracted, sections detected)

## AI mode (optional, local, free)
Uses a local model through [Ollama](https://ollama.com) - nothing leaves your PC. Scores stay rule-based (stable);
the model only writes the summary, suggestions and bullet rewrites. Invented bullets are filtered out.
```
ollama pull qwen3:8b      # or qwen3:4b for a lighter model
```
Then turn on **Use local AI (Ollama)** in the sidebar. If Ollama is off, the app falls back to rule-based results.

## Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` UI | `analyzer.py` scoring, risks, suggestions | `parser.py` PDF/DOCX + section detection
- `skills_db.py` skills + role profiles (add your own) | `scorer.py` semantic similarity (SBERT, TF-IDF fallback)
- `ai_mode.py` Ollama client (JSON-schema output) | `suggestions_rule.py` bullet helpers | `suggestions_ai.py` rule-based bullet rewrites
