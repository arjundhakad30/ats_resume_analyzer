"""Optional local-LLM feedback via Ollama. Scores stay rule-based; the LLM only writes summary, suggestions and bullet rewrites.
Everything runs on your PC (http://localhost:11434) - resume text never leaves your system."""
import json
import re
import requests

DEFAULT_HOST = "http://localhost:11434"
PREFERRED = ["qwen3:8b", "qwen3:14b", "qwen3:4b", "gemma3:4b"]

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "suggestions": {"type": "array", "items": {"type": "object", "properties": {
            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
            "title": {"type": "string"}, "detail": {"type": "string"}, "example": {"type": "string"}},
            "required": ["priority", "title", "detail", "example"]}},
        "rewrites": {"type": "array", "items": {"type": "object", "properties": {
            "original": {"type": "string"}, "improved": {"type": "string"}},
            "required": ["original", "improved"]}},
    },
    "required": ["summary", "suggestions", "rewrites"],
}

SYSTEM = ("You are an expert ATS resume reviewer for students and freshers. Use ONLY facts present in the resume text. "
          "Never invent skills, employers, tools, numbers or achievements. When a number is needed, use a placeholder like [X%]. "
          "Be specific and concise. Reply with JSON only.")


class AIError(Exception):
    pass


def _base(host):
    return (host or DEFAULT_HOST).rstrip("/")


def list_models(host=DEFAULT_HOST, timeout=2):
    """Names of installed Ollama chat models (embedding models are hidden)."""
    r = requests.get(_base(host) + "/api/tags", timeout=timeout)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", []) if "embed" not in m["name"].lower()]


def pick_default(models):
    for p in PREFERRED:
        if p in models:
            return p
    return next((m for m in models if m.startswith("qwen3")), models[0])


def _prompt(resume_text, jd_text, result, model):
    risks = "; ".join(r["title"] for r in result["risks"][:6]) or "none"
    scores = ", ".join(f"{k} {v}" for k, v in result["scores"].items())
    p = (f"RESUME:\n{resume_text[:7000]}\n\nJOB DESCRIPTION:\n{(jd_text or '').strip()[:3000] or 'Not provided'}\n\n"
         f"AUTOMATIC CHECK RESULTS (already computed, do not change them):\n- Overall {result['overall']}/100 ({result['grade']}); {scores}\n"
         f"- Missing keywords: {', '.join(result['missing']) or 'none'}\n- Detected risks: {risks}\n\n"
         "TASK:\n1. summary: 2-3 plain sentences on how this resume would fare with an ATS and the biggest gap.\n"
         "2. suggestions: 3-5 specific, actionable items, most important first. 'example' must be ready-to-paste text based only on the resume.\n"
         "3. rewrites: up to 4 of the weakest bullets, 'original' copied EXACTLY from the resume, 'improved' = stronger action verb, "
         "clearer impact, JD keywords only if the resume really supports them, [X%] placeholder for unknown numbers.")
    return p + ("\n/no_think" if model.lower().startswith("qwen3") else "")


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _clean(data, resume_text):
    rn = _norm(resume_text)
    sugg = []
    for s in (data.get("suggestions") or [])[:5]:
        if not isinstance(s, dict) or not str(s.get("title", "")).strip():
            continue
        pr = s.get("priority") if s.get("priority") in ("high", "medium", "low") else "medium"
        sugg.append({"priority": pr, "title": str(s["title"])[:120], "detail": str(s.get("detail", ""))[:400],
                     "example": str(s.get("example", ""))[:400]})
    rw = []
    for x in (data.get("rewrites") or [])[:4]:
        if not isinstance(x, dict):
            continue
        o, n = str(x.get("original", "")).strip(), str(x.get("improved", "")).strip()
        head = " ".join(_norm(o).split()[:6])
        if o and n and _norm(o) != _norm(n) and head and head in rn:   # drop bullets the model invented
            rw.append({"original": o[:400], "improved": n[:400]})
    return {"summary": str(data.get("summary", "")).strip()[:700], "suggestions": sugg, "rewrites": rw}


def ai_feedback(model, resume_text, jd_text, result, host=DEFAULT_HOST, timeout=240):
    payload = {"model": model, "stream": False, "format": SCHEMA, "think": False,
               "messages": [{"role": "system", "content": SYSTEM},
                            {"role": "user", "content": _prompt(resume_text, jd_text, result, model)}],
               "options": {"temperature": 0.2, "num_ctx": 8192, "num_predict": 1400}}
    url = _base(host) + "/api/chat"
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code == 400 and "think" in r.text.lower():   # older Ollama / model without thinking support
            payload.pop("think")
            r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise AIError("Ollama is not running. Start the Ollama app and try again.")
    except requests.exceptions.Timeout:
        raise AIError("The model took too long. Try a smaller model (e.g. qwen3:4b).")
    except requests.exceptions.HTTPError as e:
        raise AIError(f"Ollama error: {e.response.text[:200]}")
    content = re.sub(r"<think>.*?</think>", "", r.json()["message"]["content"], flags=re.S).strip()
    try:
        m = re.search(r"\{.*\}", content, flags=re.S)
        data = json.loads(m.group(0) if m else content)
    except Exception:
        raise AIError("The model returned an invalid answer. Try again or use a larger model.")
    out = _clean(data, resume_text)
    if not out["summary"] and not out["suggestions"]:
        raise AIError("The model returned an empty answer.")
    return out
