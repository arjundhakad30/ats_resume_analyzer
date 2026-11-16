"""Skill database: canonical name -> list of aliases (all lowercase).
Matching is word-boundary based, so 'java' will NOT match 'javascript' and 'git' will NOT match 'digit'.
Add your own skills here."""
import re

SKILLS = {
    # languages
    "python": ["python"], "java": ["java"], "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript"], "c++": ["c++", "cpp"], "c#": ["c#"], "c": ["c programming", "embedded c"],
    "go": ["golang"], "rust": ["rust"], "kotlin": ["kotlin"], "swift": ["swift"], "php": ["php"],
    "r": ["r programming", "rstudio"], "matlab": ["matlab"], "bash": ["bash", "shell scripting"],
    # web
    "html": ["html", "html5"], "css": ["css", "css3"], "react": ["react", "reactjs", "react.js"],
    "angular": ["angular"], "vue": ["vue", "vuejs", "vue.js"], "node.js": ["node.js", "nodejs", "node js"],
    "express": ["express", "express.js"], "flask": ["flask"], "django": ["django"], "fastapi": ["fastapi"],
    "spring boot": ["spring boot", "springboot", "spring"], "rest api": ["rest api", "rest apis", "restful", "rest"],
    "streamlit": ["streamlit"], "tailwind": ["tailwind", "tailwindcss"], "bootstrap": ["bootstrap"],
    # data / ml
    "machine learning": ["machine learning", "ml"], "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"], "computer vision": ["computer vision"],
    "opencv": ["opencv"], "tensorflow": ["tensorflow"], "pytorch": ["pytorch"], "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"], "pandas": ["pandas"], "numpy": ["numpy"],
    "matplotlib": ["matplotlib"], "seaborn": ["seaborn"], "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data visualisation"], "statistics": ["statistics", "statistical"],
    "llm": ["llm", "llms", "large language model", "large language models"], "generative ai": ["generative ai", "genai"],
    "transformers": ["transformers", "hugging face", "huggingface"], "langchain": ["langchain"],
    "power bi": ["power bi", "powerbi"], "tableau": ["tableau"], "excel": ["excel", "ms excel"],
    "eda": ["eda", "exploratory data analysis"], "feature engineering": ["feature engineering"],
    # databases
    "sql": ["sql"], "mysql": ["mysql"], "postgresql": ["postgresql", "postgres"], "mongodb": ["mongodb", "mongo"],
    "sqlite": ["sqlite"], "firebase": ["firebase"], "redis": ["redis"], "nosql": ["nosql"],
    # devops / cloud / tools
    "git": ["git"], "github": ["github"], "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"], "azure": ["azure"], "gcp": ["gcp", "google cloud"],
    "linux": ["linux"], "ci/cd": ["ci/cd", "cicd", "jenkins", "github actions"], "jira": ["jira"],
    "postman": ["postman"], "agile": ["agile", "scrum"],
    # core CS
    "data structures": ["data structures", "dsa"], "algorithms": ["algorithms"], "oop": ["oop", "oops", "object oriented", "object-oriented"],
    "operating systems": ["operating systems"], "dbms": ["dbms"], "computer networks": ["computer networks", "networking"],
    # electronics / embedded
    "embedded systems": ["embedded systems", "embedded"], "iot": ["iot", "internet of things"],
    "arduino": ["arduino"], "raspberry pi": ["raspberry pi"], "vlsi": ["vlsi"], "verilog": ["verilog"],
    "vhdl": ["vhdl"], "pcb design": ["pcb design", "pcb"], "microcontrollers": ["microcontroller", "microcontrollers", "stm32", "8051"],
    "signal processing": ["signal processing", "dsp"], "autocad": ["autocad"], "labview": ["labview"],
}

def _pattern(alias):
    return re.compile(r"(?<![a-z0-9+#.])" + re.escape(alias) + r"(?![a-z0-9+#]|\.[a-z0-9])")

_PATTERNS = {skill: [_pattern(a) for a in aliases] for skill, aliases in SKILLS.items()}

def find_skills(text):
    """Return the set of canonical skills present in text (word-boundary safe)."""
    low = text.lower()
    return {skill for skill, pats in _PATTERNS.items() if any(p.search(low) for p in pats)}


# Used when no job description is given: expected keywords for the role the resume looks closest to.
ROLE_PROFILES = {
    "data science / ML": {"label": "data science / ML", "skills": [
        "python", "machine learning", "deep learning", "nlp", "pandas", "numpy", "scikit-learn", "tensorflow",
        "pytorch", "sql", "data analysis", "data visualization", "statistics", "feature engineering", "eda", "git"]},
    "web development": {"label": "web development", "skills": [
        "html", "css", "javascript", "react", "node.js", "express", "rest api", "sql", "mongodb", "git", "github",
        "docker", "typescript", "flask", "django"]},
    "software engineering": {"label": "software engineering", "skills": [
        "python", "java", "c++", "data structures", "algorithms", "oop", "sql", "git", "rest api", "linux",
        "docker", "dbms", "operating systems", "agile"]},
    "embedded / electronics": {"label": "embedded / electronics", "skills": [
        "c", "c++", "embedded systems", "microcontrollers", "arduino", "raspberry pi", "iot", "verilog", "vhdl",
        "vlsi", "pcb design", "matlab", "signal processing", "python"]},
}


def detect_role(found_skills):
    """Pick the role profile that overlaps most with the skills found in the resume."""
    best = max(ROLE_PROFILES.items(), key=lambda kv: len(found_skills & set(kv[1]["skills"])))
    if not (found_skills & set(best[1]["skills"])):
        best = ("software engineering", ROLE_PROFILES["software engineering"])
    return best
