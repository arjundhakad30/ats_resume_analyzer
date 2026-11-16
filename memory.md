# Project Memory — ATS Resume Score

Update after every important decision, bug or fix. Newest entries at the top of each section.

## Project snapshot
Streamlit ATS resume checker. Rule-based scoring (deterministic) + optional local AI text (Ollama). GitHub: `arjundhakad30/ats_resume_analyzer`.

## Decisions
- **D6** — AI mode uses local Ollama, default model `qwen3:8b` (`qwen3:4b` as light option). Reason: free, private, 32 GB RAM is enough.
- **D5** — LLM never changes scores; it only writes summary/suggestions/rewrites. Reason: stability and explainability.
- **D4** — Ollama output uses JSON schema (`format`) + validation + fallback. Reason: small models break plain "reply in JSON" 3-8% of the time.
- **D3** — Without a JD, keywords are matched against a role profile (data science, web, software, embedded) auto-detected from the resume.
- **D2** — Missing sections score low and raise a risk; they are never filled with copied text.
- **D1** — UI copies the reference tool's structure (score ring, 7 bars, risks, chips, suggestions) but is pure Streamlit.

## Bugs & solutions
| Problem | Cause | Fix |
|---------|-------|-----|
| Section scores almost identical | `extract_sections` gave the whole resume to every section | Split by real headings only |
| `C++`, `Node.js`, `92%` lost | Text cleaning removed digits/symbols | Keep original text; normalise only whitespace/bullets |
| `java` matched `javascript`, `git` matched `digit` | Substring matching | Word-boundary regex |
| Most sections showed "Weak" | Raw cosine rarely reaches 70% | Calibrated 0-100 range + skill coverage |
| Weak openers not detected | PDF bullet glyph came as `\x7f` / private-use char | Strip any leading non-alphanumeric glyph; normalise glyphs |
| Wrapped bullet lines counted as separate bullets | Line-based splitting | Join continuation lines to their bullet |
| "Built building REST APIs" | Naive verb replacement | Gerund map (building → Built) |
| `numpy.dtype size changed` on run | numpy/scikit-learn mismatch in Anaconda | Use a fresh venv, or `python -m pip install -U numpy scipy scikit-learn`; run with `python -m streamlit run app.py` |
| `ollama` not recognised in PowerShell | Terminal opened before install | Open a new PowerShell / restart |

## Environment
- Windows laptop, 32 GB RAM, 1 TB storage, Anaconda installed (can conflict with project packages → prefer venv).
- Ollama installed; models pulled: `qwen3:4b` (2.5 GB), `qwen3:8b` (5.2 GB). Ollama address: `http://localhost:11434`.
- SBERT model needs internet on first run (cached afterwards); app falls back to TF-IDF if it can't load.

## Known limitations
- Score is an estimate, not a real ATS output.
- Scanned/image PDFs can't be read (no OCR).
- On CPU, AI mode may take 30-90 s per resume (estimate — measure with `ollama run <model> --verbose`).
- Skill list is finite; unknown skills are ignored.

## Open questions
- Which model gives better rewrites: `qwen3:4b` or `qwen3:8b`?
- Are the score weights realistic on real resumes?

## How to update this file
Add a line to Decisions (next D-number) or a row to Bugs & solutions the moment something is decided or fixed. Keep entries short: what, why, how.