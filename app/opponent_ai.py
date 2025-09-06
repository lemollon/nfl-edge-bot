import json
from prompts import SYSTEM_PROMPT

AI_INSTRUCTIONS = "You are the Opponent AI Coach. Given the same context, propose 2-3 key calls that counter the user's likely strategy. Return JSON: {'picks': ['...'], 'rationale': '...'}"

def generate_ai_plan(llm, context_text: str, user_prompt: str):
    user_msg = f"{AI_INSTRUCTIONS}\n\nContext:\n{context_text}\n\nUser prompt:\n{user_prompt}"
    out = llm.chat(SYSTEM_PROMPT, user_msg)
    if not out.strip().startswith("{"):
        out = '{"picks": ["Mix coverages, bracket WR1", "Blitz selectively vs 3rd & long"], "rationale": "Counter deep shots; disrupt timing."}'
    try:
        return json.loads(out)
    except Exception:
        return {"picks": ["Mix coverages, bracket WR1", "Blitz selectively vs 3rd & long"], "rationale":"Fallback AI plan."}
