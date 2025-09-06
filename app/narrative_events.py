import random

def surprise_event(feed_items):
    if not feed_items: return None
    it = random.choice(feed_items)
    title = it.get("title","")
    neg = any(w in title.lower() for w in ["injury","out","setback","suspension","sore","questionable","limited"])
    pos = any(w in title.lower() for w in ["returns","full participant","activated","extension","all-pro","breakout"])
    impact = 0
    if neg: impact -= 1.0
    if pos: impact += 0.8
    return {"title": title, "summary": it.get("summary",""), "impact": impact, "link": it.get("link","")}
