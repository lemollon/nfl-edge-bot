import feedparser
from urllib.parse import quote_plus
from typing import List, Dict

def _google_news_rss_query(q: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"

def fetch_player_news(players: List[str], team_hint: str = "", max_items_per_player: int = 5) -> List[Dict]:
    items = []
    for p in players:
        if not p.strip(): 
            continue
        q = f"{p} {team_hint} NFL" if team_hint else f"{p} NFL"
        url = _google_news_rss_query(q)
        d = feedparser.parse(url)
        for e in d.entries[:max_items_per_player]:
            items.append({
                "player": p,
                "title": e.get("title",""),
                "summary": e.get("summary",""),
                "link": e.get("link",""),
                "published": e.get("published",""),
                "source": "google_news_rss"
            })
    return items
