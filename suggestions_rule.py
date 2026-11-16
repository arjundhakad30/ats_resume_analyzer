import re

ACTION_VERBS = {
    "built", "developed", "designed", "implemented", "created", "led", "managed", "automated", "optimized",
    "improved", "reduced", "increased", "deployed", "analyzed", "engineered", "integrated", "launched",
    "trained", "tested", "debugged", "architected", "migrated", "delivered", "achieved", "collaborated",
    "configured", "established", "streamlined", "researched", "evaluated", "constructed", "programmed", "simulated",
    "wrote", "maintained", "applied", "processed", "extracted", "visualized", "organized", "coordinated", "presented",
}
WEAK_STARTS = {
    "responsible for": "Managed", "worked on": "Built", "worked with": "Collaborated with", "helped": "Supported",
    "helped in": "Contributed to", "involved in": "Contributed to", "assisted in": "Supported", "participated in": "Contributed to",
    "tasked with": "Executed", "duties included": "Handled", "was part of": "Contributed to",
}
METRIC_RE = re.compile(r"(\d+(\.\d+)?\s?(%|x\b|k\b|\+))|\b\d{2,}\b|[$\u20b9]")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s-]{8,}\d)")
_BULLET_START = re.compile(r"^[^\w(\[\s]")


def _strip_glyph(line):
    return re.sub(r"^[^A-Za-z0-9(\[]+", "", line.strip())


def split_bullets(text):
    """Group lines into bullets. Wrapped continuation lines are joined to their bullet."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    marked = any(_BULLET_START.match(l) for l in lines)
    bullets, cur = [], None
    for l in lines:
        if not marked:
            if len(l.split()) >= 5:
                bullets.append(_strip_glyph(l))
            continue
        if _BULLET_START.match(l):
            if cur:
                bullets.append(cur)
            cur = _strip_glyph(l)
        elif cur and (l[0].islower() or (not cur.endswith((".", ":")) and len(l.split()) >= 3)):
            cur += " " + l
        else:  # sub-heading / project title
            if cur:
                bullets.append(cur)
            cur = None
    if cur:
        bullets.append(cur)
    return [b for b in bullets if len(b.split()) >= 4]


def has_metric(s):
    return bool(METRIC_RE.search(s))


def first_word(s):
    return s.split()[0].lower().strip(",.:;") if s.split() else ""
