import html
import streamlit as st
from parser import extract_text, normalize
from analyzer import analyze, CATEGORIES
from scorer import get_backend
from ai_mode import DEFAULT_HOST, list_models, pick_default, ai_feedback

st.set_page_config("ATS Resume Checker", page_icon="📄", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.pill {display:inline-block; padding:3px 12px; border-radius:999px; background:#eef0fb; color:#4b4fa8; font-weight:600; font-size:13px;}
.sub {color:#6b7280; margin-top:-8px;}
.h {color:#4a3fb5; font-weight:700; font-size:18px; margin:10px 0 6px;}
.bar-wrap {margin-bottom:14px;}
.bar-top {display:flex; justify-content:space-between; font-weight:600; font-size:14px; color:#1f2937;}
.bar {height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden; margin-top:4px;}
.bar > div {height:100%; background:linear-gradient(90deg,#6c5ce7,#8e7cf3); border-radius:999px;}
.chip {display:inline-block; padding:5px 12px; margin:3px 4px 3px 0; border-radius:999px; font-size:13px; font-weight:500;}
.chip.miss {background:#fff1f2; color:#be123c; border:1px solid #fecdd3;}
.chip.good {background:#ecfdf5; color:#047857; border:1px solid #a7f3d0;}
.card {border:1px solid #e5e7eb; border-radius:12px; padding:12px 16px; margin-bottom:10px; background:#fff;}
.card .t {font-weight:600; color:#111827;}
.card .d {color:#4b5563; font-size:14px; margin-top:2px;}
.card .f {color:#065f46; font-size:14px; margin-top:4px;}
.sev {font-size:12px; font-weight:700; padding:2px 8px; border-radius:6px; margin-left:6px; text-transform:lowercase;}
.sev.high {background:#fee2e2; color:#b91c1c;} .sev.medium {background:#fef3c7; color:#b45309;} .sev.low {background:#e0e7ff; color:#4338ca;}
.ex {background:#f3f4f6; border-radius:8px; padding:8px 12px; margin-top:8px; font-size:14px; color:#374151;}
.sumbox {background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px; padding:14px 18px; color:#374151;}
.ring {display:flex; flex-direction:column; align-items:center;}
.ring .grade {font-weight:700; color:#374151; margin-top:4px;}
</style>
""", unsafe_allow_html=True)

esc = html.escape


def ring(score, grade):
    color = "#10b981" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"
    c = 2 * 3.14159 * 52
    off = c * (1 - score / 100)
    return f"""<div class="ring"><svg width="150" height="150" viewBox="0 0 120 120">
      <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="10"/>
      <circle cx="60" cy="60" r="52" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
        stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}" transform="rotate(-90 60 60)"/>
      <text x="60" y="58" text-anchor="middle" font-size="30" font-weight="700" fill="#111827">{score}</text>
      <text x="60" y="76" text-anchor="middle" font-size="9" font-weight="600" fill="#6b7280">ATS SCORE</text>
    </svg><div class="grade">Grade: {grade}</div></div>"""


def bar(label, val):
    return f'<div class="bar-wrap"><div class="bar-top"><span>{label}</span><span>{val}/100</span></div><div class="bar"><div style="width:{val}%"></div></div></div>'


def reset():
    st.session_state.pop("result", None)
    st.session_state["paste_text"] = ""
    st.session_state["jd_text"] = ""
    st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1


@st.cache_resource(show_spinner="Loading matching model...")
def load_backend():
    return get_backend()


load_backend()
st.session_state.setdefault("uploader_key", 0)

with st.sidebar:
    st.header("AI mode (local)")
    ai_on = st.toggle("Use local AI (Ollama)", key="ai_on", help="Adds AI-written summary, suggestions and bullet rewrites. Scores stay rule-based.")
    host = st.text_input("Ollama address", DEFAULT_HOST, key="ollama_host")
    model = None
    if ai_on:
        try:
            models = list_models(host)
        except Exception:
            models = []
        if models:
            model = st.selectbox("Model", models, index=models.index(pick_default(models)), key="ai_model")
        else:
            st.warning("Ollama not reachable or no model installed. Start Ollama and run `ollama pull qwen3:8b`.")
    st.caption("Runs on your PC - resume text never leaves your system.")

st.markdown('<span class="pill">Smart ATS Analysis</span>', unsafe_allow_html=True)
st.title("ATS Resume Checker")
st.markdown('<p class="sub">Upload your resume and get a polished ATS-style analysis with scores, risks, and keyword suggestions.</p>', unsafe_allow_html=True)

left, right = st.columns([3, 2], gap="large")
with left:
    with st.container(border=True):
        resume_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"], key=f"up_{st.session_state['uploader_key']}")
        st.caption("Tip: if PDF extraction returns empty text, upload DOCX or paste resume text below.")
        paste = st.text_area("Or Paste Resume Text", height=180, key="paste_text", placeholder="Paste resume text here if you do not want to upload a file...")
        jd = st.text_area("Job Description (optional)", height=160, key="jd_text",
                          placeholder="Paste the job description here to detect missing keywords and improve job-match feedback...")
        st.caption("Adding a job description gives stronger keyword and alignment suggestions.")
        b1, b2, _ = st.columns([2, 1, 4])
        run = b1.button("Check ATS Score", type="primary", use_container_width=True)
        b2.button("Reset", on_click=reset, use_container_width=True)
with right:
    with st.container(border=True):
        st.markdown('<div class="h">What You\'ll Get</div>', unsafe_allow_html=True)
        st.markdown("- Overall ATS-style score and grade\n- Section-by-section scoring breakdown\n- ATS risks and why they matter\n- Missing keyword suggestions\n- Ready-to-use rewrite recommendations")

if run:
    text = ""
    try:
        if resume_file is not None:
            text = extract_text(resume_file)
        elif paste.strip():
            text = normalize(paste)
    except Exception as e:
        st.error(f"Could not read the file ({e}). Try DOCX or paste the text.")
        st.stop()
    if not text.strip():
        st.error("Please upload a resume (PDF/DOCX) or paste the resume text.")
        st.stop()
    with st.spinner("Scanning resume..."):
        res = analyze(text, jd)
    if ai_on:
        if model:
            with st.spinner(f"Asking {model} (can take a minute on CPU)..."):
                try:
                    res["ai"] = ai_feedback(model, text, jd, res, host)
                    res["ai"]["model"] = model
                except Exception as e:
                    res["ai"] = {"error": str(e)}
        else:
            res["ai"] = {"error": "Ollama is not reachable or has no model installed."}
    st.session_state["result"] = res

r = st.session_state.get("result")
if r:
    st.divider()
    st.header("ATS Scan Results")
    c1, c2 = st.columns([1, 3], gap="large")
    c1.markdown(ring(r["overall"], r["grade"]), unsafe_allow_html=True)
    c2.markdown(f'<div class="h">Summary</div><div class="sumbox">{esc(r["summary"])}</div>', unsafe_allow_html=True)

    ai = r.get("ai") or {}
    if ai.get("error"):
        st.warning(f"AI mode skipped: {ai['error']} Showing rule-based results.")
    elif ai.get("summary"):
        c2.markdown(f'<div class="h">AI Summary ({esc(ai.get("model", ""))})</div><div class="sumbox">{esc(ai["summary"])}</div>', unsafe_allow_html=True)

    st.markdown('<div class="h">Section Scores</div>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="large")
    for i, cat in enumerate(CATEGORIES):
        (a if i % 2 == 0 else b).markdown(bar(cat, r["scores"][cat]), unsafe_allow_html=True)

    st.markdown('<div class="h">ATS Risks (Fix These)</div>', unsafe_allow_html=True)
    if r["risks"]:
        for k in r["risks"]:
            st.markdown(f'<div class="card"><span class="t">{esc(k["title"])}</span><span class="sev {k["severity"]}">{k["severity"]}</span>'
                        f'<div class="d">{esc(k["why"])}</div><div class="f"><b>Fix:</b> {esc(k["fix"])}</div></div>', unsafe_allow_html=True)
    else:
        st.success("No major ATS risks found.")

    k1, k2 = st.columns(2, gap="large")
    with k1:
        st.markdown('<div class="h">Missing Keywords</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="chip miss">{esc(m)}</span>' for m in r["missing"]) or "No missing keywords detected.", unsafe_allow_html=True)
        if not r["has_jd"]:
            st.caption("Generic suggestions - paste a job description for exact matching.")
    with k2:
        st.markdown('<div class="h">Strong Keywords</div>', unsafe_allow_html=True)
        st.markdown("".join(f'<span class="chip good">{esc(m)}</span>' for m in r["strong"]) or "No known skills detected.", unsafe_allow_html=True)

    st.markdown('<div class="h">Top Suggestions</div>', unsafe_allow_html=True)
    for s in r["suggestions"]:
        ex = f'<div class="ex">{esc(s["example"])}</div>' if s.get("example") else ""
        st.markdown(f'<div class="card"><span class="t">{esc(s["title"])}</span><span class="sev {s["priority"]}">{s["priority"]}</span>'
                    f'<div class="d">{esc(s["detail"])}</div>{ex}</div>', unsafe_allow_html=True)
    if not r["suggestions"]:
        st.success("No suggestions - resume looks solid.")

    if ai.get("suggestions"):
        st.markdown(f'<div class="h">AI Suggestions ({esc(ai.get("model", ""))})</div>', unsafe_allow_html=True)
        for s in ai["suggestions"]:
            ex = f'<div class="ex">{esc(s["example"])}</div>' if s.get("example") else ""
            st.markdown(f'<div class="card"><span class="t">{esc(s["title"])}</span><span class="sev {s["priority"]}">{s["priority"]}</span>'
                        f'<div class="d">{esc(s["detail"])}</div>{ex}</div>', unsafe_allow_html=True)
    if ai.get("rewrites"):
        st.markdown('<div class="h">Suggested Bullet Rewrites</div>', unsafe_allow_html=True)
        for w in ai["rewrites"]:
            st.markdown(f'<div class="card"><div class="d"><b>Before:</b> {esc(w["original"])}</div>'
                        f'<div class="ex" style="background:#ecfdf5"><b>After:</b> {esc(w["improved"])}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="h">Parsing Notes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sumbox">{"<br>".join(esc(n) for n in r["notes"])}</div>', unsafe_allow_html=True)
