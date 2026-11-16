"""Bullet-level rewrite helper (rule-based, honest: no fake AI claims).
Fixes weak openers, flags missing action verbs/metrics, shows JD skills that fit."""
from suggestions_rule import split_bullets, has_metric, ACTION_VERBS, WEAK_STARTS


GERUNDS = {"building": "Built", "developing": "Developed", "creating": "Created", "designing": "Designed",
           "implementing": "Implemented", "managing": "Managed", "testing": "Tested", "analyzing": "Analyzed",
           "writing": "Wrote", "maintaining": "Maintained", "deploying": "Deployed", "optimizing": "Optimized"}


def rewrite_section(section_text, section_name, missing_skills=None):
    """Returns list of dicts: original, improved, notes."""
    results = []
    for b in split_bullets(section_text)[:10]:
        new, notes, low = b, [], b.lower()
        for weak, strong in sorted(WEAK_STARTS.items(), key=lambda x: -len(x[0])):
            if low.startswith(weak):
                rest = b[len(weak):].strip()
                nxt = rest.split()[0].lower() if rest else ""
                if nxt in GERUNDS:  # "Responsible for building X" -> "Built X"
                    new = GERUNDS[nxt] + rest[len(nxt):]
                    strong = GERUNDS[nxt]
                else:
                    new = strong + " " + rest
                notes.append(f"Replaced weak opener '{weak}' with '{strong}'")
                break
        else:
            first = b.split()[0].lower().strip(",.:;")
            if first not in ACTION_VERBS:
                notes.append("Start with a strong action verb (Built, Designed, Automated, Optimized...)")
        if not has_metric(new):
            notes.append("Add impact: numbers like accuracy %, users, time saved, dataset size")
            new = new.rstrip(". ") + " [add result: e.g. improved X by __%]"
        new = new[0].upper() + new[1:]
        if notes:
            results.append({"original": b, "improved": new, "notes": notes})
    return results
