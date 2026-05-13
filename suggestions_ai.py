# suggestions_ai.py

def rewrite_section(section_text, section_name):
    section_name = section_name.capitalize()

    if not section_text or len(section_text.strip()) == 0:
        return f"No content found in {section_name} section."

    return f"""
Improved {section_name} Section:

• Start points with strong action verbs.
• Add measurable impact like accuracy, %, time saved, users, or project result.
• Match keywords from the job description.
• Keep sentences short and ATS-friendly.
• Avoid tables, images, symbols, and unnecessary formatting.

Sample Rewrite:

{section_text[:300]}

Better Format Example:
• Developed and improved {section_name.lower()} content using relevant keywords and clear achievements.
• Highlighted technical skills, project impact, and practical experience in an ATS-friendly format.
"""