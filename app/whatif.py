import json
from prompts import SYSTEM_PROMPT

WHATIF_INSTRUCTIONS = "You are the Strategy Evaluator. Rate each archetype from 0..100 given context. Return JSON: {'scores': [{'name':'Run-heavy','score':..,'why':'...'}]}"

DEFAULT_ARCHETYPES = [
    {"name":"Run-heavy (gap & duo)", "desc":"Pound interior, set up play-action"},
    {"name":"Pass-heavy (11 personnel)", "desc":"Spread & attack with quick + deep shots"},
    {"name":"Balanced RPO", "desc":"Mix RPO, constraint plays, stress apex defender"},
    {"name":"Explosive Shots", "desc":"Low volume, high aDOT shots + max protect"},
]

def score_archetypes(llm, context_text: str, custom=None):
    arch = custom if custom else DEFAULT_ARCHETYPES
    items = "\n".join([f"- {a['name']}: {a['desc']}" for a in arch])
    user_msg = f"{WHATIF_INSTRUCTIONS}\n\nContext:\n{context_text}\n\nArchetypes:\n{items}"
    out = llm.chat(SYSTEM_PROMPT, user_msg)
    try:
        data = json.loads(out); return data.get("scores", [])
    except Exception:
        return [{"name":a["name"], "score":75, "why":"fallback"} for a in arch]
