import PyPDF2
import re

def extract_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return clean_text(text)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    return text

def extract_sections(text):
    sections = {
        "skills": "",
        "experience": "",
        "projects": ""
    }

    if "skills" in text:
        sections["skills"] = text
    if "experience" in text or "internship" in text:
        sections["experience"] = text
    if "project" in text:
        sections["projects"] = text

    return sections
