"""Scoring. Uses Sentence-BERT when available; falls back to TF-IDF if the model can't load (offline etc.).
Final scores combine skill-keyword coverage (exact, explainable) + semantic similarity (calibrated)."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills_db import find_skills




_model = None
_backend = None


def get_backend():
    """Load SBERT once (cached in module). Returns 'sbert' or 'tfidf'."""
    global _model, _backend
    if _backend is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _backend = "sbert"
        except Exception:
            _backend = "tfidf"
    return _backend


def _chunks(text, size=120):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [""]


def _calibrate(sim, backend):
    # raw cosine is never near 100%; stretch the realistic range to 0-100
    lo, hi = (0.15, 0.65) if backend == "sbert" else (0.02, 0.35)
    return max(0.0, min(1.0, (sim - lo) / (hi - lo))) * 100


def semantic_score(resume_text, jd_text):
    """Average over JD chunks of the best-matching resume chunk (handles long text, no 256-token truncation)."""
    backend = get_backend()
    r_chunks, j_chunks = _chunks(resume_text), _chunks(jd_text)
    if backend == "sbert":
        r = _model.encode(r_chunks)
        j = _model.encode(j_chunks)
        sim = cosine_similarity(j, r)
    else:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit(r_chunks + j_chunks)
        sim = cosine_similarity(vec.transform(j_chunks), vec.transform(r_chunks))
    return _calibrate(float(sim.max(axis=1).mean()), backend)


def skill_coverage(text, jd_skills):
    """% of JD-required skills present in text (None if JD lists no known skills)."""
    if not jd_skills:
        return None
    return len(find_skills(text) & jd_skills) / len(jd_skills) * 100
