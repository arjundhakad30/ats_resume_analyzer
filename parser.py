import re
from collections import defaultdict
from pypdf import PdfReader

SECTION_ALIASES = {
    "skills": ["skills", "technical skills", "key skills", "core competencies", "tech stack", "technologies", "skills summary"],
    "experience": ["experience", "work experience", "professional experience", "internship", "internships",
                   "internship experience", "employment", "work history", "training"],
    "projects": ["projects", "academic projects", "personal projects", "project work", "key projects"],
    "education": ["education", "academic background", "academics", "qualifications", "educational qualification"],
    "summary": ["summary", "objective", "career objective", "profile", "professional summary", "about me", "career summary"],
    "other": ["certifications",
              "achievements", "extracurricular", "extracurricular activities", "positions of responsibility",
              "hobbies", "interests", "declaration", "languages", "courses", "awards"],
}
_ALIAS_TO_SECTION = {a: sec for sec, al in SECTION_ALIASES.items() for a in al}


def normalize(text):
    text = text.replace("\r", "\n").replace("\u00a0", " ")
    text = re.sub(r"[\u2022\u25cf\u25aa\u25a0\u25e6\u25cb\u00b7\uf0b7\uf0a7\x7f]", "•", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(file):
    """Read PDF or DOCX. Keeps case, digits, symbols (C++, 40%, Node.js stay intact)."""
    name = getattr(file, "name", "").lower()
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(file)
        parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                parts.extend(cell.text for cell in row.cells)
        return normalize("\n".join(parts))
    reader = PdfReader(file)
    pages = [(p.extract_text() or "") for p in reader.pages]  # extract_text can return None/empty
    return normalize("\n".join(pages))


def _heading_key(line):
    clean = re.sub(r"[^a-z& ]", "", line.lower()).replace("&", " and ")
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean or len(clean.split()) > 4 or line.strip().endswith("."):
        return None
    if clean in _ALIAS_TO_SECTION:
        return _ALIAS_TO_SECTION[clean]
    for alias, sec in _ALIAS_TO_SECTION.items():
        if clean.startswith(alias + " ") and len(clean.split()) <= 3 and sec in ("skills", "experience", "projects", "education"):
            return sec
    return None


def extract_sections(text):
    """Split resume by real headings. Returns only sections that were actually found."""
    buf, current = defaultdict(list), "header"
    for line in text.splitlines():
        key = _heading_key(line)
        if key:
            current = key
            continue
        if line.strip():
            buf[current].append(line.strip())
    return {k: "\n".join(v) for k, v in buf.items() if v}
