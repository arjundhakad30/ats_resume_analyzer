# Development Rules — ATS Resume Score

> AI assistants: read `prd.md`, `architecture.md`, `design.md`, then this file, before writing code. After finishing work, update `tasks.md` and `memory.md`.

## Code structure
1. `app.py` = UI only. No scoring logic, no regex, no file parsing there.
2. All scoring/risk/suggestion logic lives in `analyzer.py`; parsing in `parser.py`; skills in `skills_db.py`.
3. Keep functions small and single-purpose; add a one-line docstring to every public function.
4. Python 3.10+, PEP 8, descriptive names, type hints for new public functions.
5. No new dependency without a reason; add it to `requirements.txt` and mention it in `memory.md`.

## Scoring rules
1. Scores must be **deterministic**: same input → same output. No randomness, no LLM in scoring.
2. Every penalty/weight is a named constant or a visible number in `analyzer.py`; document changes in `architecture.md`.
3. Missing section ≠ 0 copied from another section; use an explicit low score and a risk entry.
4. Skill matching uses word-boundary regex only; add new skills to `skills_db.py` (lowercase aliases).
5. Never delete digits/symbols from resume text (C++, 92%, Node.js must survive parsing).

## AI / LLM rules
1. LLM only writes text (summary, suggestions, rewrites). It never changes scores.
2. Never invent resume facts: no fake skills, employers or numbers; unknown numbers use `[X%]` placeholders.
3. Use structured output (JSON schema) and validate every field; cap lengths and counts.
4. Drop any rewrite whose `original` bullet isn't in the resume.
5. LLM failure must never break the app — fall back to rule-based results with a warning.
6. Resume text goes only to local Ollama. No cloud API calls without explicit opt-in and a UI notice.

## Security & privacy
1. No API keys in code; use env vars or `st.secrets`.
2. Escape all user-derived text with `html.escape` before putting it in `unsafe_allow_html` markup.
3. Don't log or store resume content; keep it in `st.session_state` only.
4. Never commit `venv/`, `__pycache__/`, `.env`, or real resumes.

## Error handling
Catch exceptions at I/O boundaries (file read, HTTP). Show a short human message with `st.error`/`st.warning`; never show raw tracebacks to the user.

## Testing
- Before finishing a task: run the app, test (a) PDF, (b) DOCX, (c) pasted text, (d) with and without JD, (e) AI mode on and Ollama off.
- Keep a small sample resume + JD for regression checks (add to `tests/` when it exists).
- Fix the root cause; don't patch symptoms.

## Git
- Small commits, imperative message: `Add severity badges to risks`.
- One feature per commit/branch where possible; update `tasks.md` in the same commit.

## Documentation
- Update `README.md` when run steps change, `architecture.md` when the flow/schema changes, `memory.md` for decisions and bugs.