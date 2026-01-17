from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_score(text1, text2):
    embeddings = model.encode([text1, text2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0] * 100

def section_scores(sections, jd_text):
    scores = {}
    for section, content in sections.items():
        if content.strip():
            scores[section] = round(semantic_score(content, jd_text), 2)
        else:
            scores[section] = 0.0
    return scores

def overall_score(section_scores):
    return round(sum(section_scores.values()) / len(section_scores), 2)
