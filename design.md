# Design System — ATS Resume Score (Streamlit)

Goal: clean, calm, card-based UI similar to modern resume checkers, built only with Streamlit + small CSS injected via `st.markdown(unsafe_allow_html=True)`.

## Layout
- `layout="wide"`, content max-width 1200px.
- Top: pill badge "Smart ATS Analysis" → page title "ATS Resume Checker" → one-line subtitle (grey).
- Two columns `[3, 2]`: **left** input card (bordered container), **right** "What You'll Get" card.
- Results appear below a divider under header "ATS Scan Results".
- Sidebar: "AI mode (local)" — toggle, Ollama address, model selectbox, privacy caption.

## Input card (top → bottom)
File uploader (PDF/DOCX) → caption tip → "Or Paste Resume Text" (height 180) → "Job Description (optional)" (height 160) → caption → buttons: **Check ATS Score** (primary) + **Reset** (secondary).

## Results order
1. Score ring (left) + Summary box (right; AI summary box below it if AI mode is on)
2. Section Scores — 7 bars in two columns
3. ATS Risks (Fix These) — cards with severity badge, why, Fix
4. Missing Keywords (red chips) | Strong Keywords (green chips)
5. Top Suggestions — cards with priority badge + grey example box
6. AI Suggestions + Suggested Bullet Rewrites (only if AI mode on)
7. Parsing Notes

## Colors
| Use | Value |
|-----|-------|
| Primary / bars | `#6c5ce7` → `#8e7cf3` gradient |
| Section headings | `#4a3fb5` |
| Pill background / text | `#eef0fb` / `#4b4fa8` |
| Body text / muted | `#1f2937` / `#6b7280` |
| Card border / bar track | `#e5e7eb` |
| Score ring | green `#10b981` (≥80), amber `#f59e0b` (60-79), red `#ef4444` (<60) |
| Severity high | bg `#fee2e2`, text `#b91c1c` |
| Severity medium | bg `#fef3c7`, text `#b45309` |
| Severity low | bg `#e0e7ff`, text `#4338ca` |
| Missing chip | bg `#fff1f2`, text `#be123c`, border `#fecdd3` |
| Strong chip | bg `#ecfdf5`, text `#047857`, border `#a7f3d0` |

## Components
- **Score ring**: 150px SVG, stroke 10, score number 30px bold, "ATS SCORE" label 9px, "Grade: X" below.
- **Score bar**: label left, `value/100` right, 10px high, fully rounded.
- **Card**: 1px border, radius 12px, padding 12×16, white background; title 600 weight, detail 14px grey.
- **Severity badge**: 12px bold, radius 6px, lowercase text.
- **Chip**: radius 999px, 13px, padding 5×12.
- **Example box**: `#f3f4f6`, radius 8px, 14px text. Rewrite "After" box uses `#ecfdf5`.

## Typography & spacing
Streamlit default font. Section heading 18px bold (`.h`). Keep 10-14px vertical gaps between cards.

## States
- **Empty**: only input area + "What You'll Get".
- **Loading**: `st.spinner("Scanning resume...")`; AI mode: "Asking <model> (can take a minute on CPU)...".
- **Errors**: `st.error` for missing input/unreadable file; `st.warning` when AI mode is skipped.
- **No risks / no suggestions**: green `st.success` message.

## Rules
- Always `html.escape` user text. Never rely on colour alone — severity also shown as text.
- Keep one primary action per screen. Don't add new colours outside this table.
- Mobile: columns stack naturally; keep chips wrapping.