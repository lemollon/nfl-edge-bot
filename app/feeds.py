import feedparser
from typing import List, Dict

FEEDS = [
    "https://www.espn.com/espn/rss/nfl/news",
    "https://www.nfl.com/news/rss/rss.xml",
]

TEAM_FEEDS = {
    "ARI": ["https://www.revengeofthebirds.com/rss/index.xml"],
    "ATL": ["https://www.thefalcoholic.com/rss/index.xml"],
    "BAL": ["https://www.baltimorebeatdown.com/rss/index.xml"],
    "BUF": ["https://www.buffalorumblings.com/rss/index.xml"],
    "CAR": ["https://www.catscratchreader.com/rss/index.xml"],
    "CHI": ["https://www.windycitygridiron.com/rss/index.xml"],
    "CIN": ["https://www.cincyjungle.com/rss/index.xml"],
    "CLE": ["https://www.dawgsbynature.com/rss/index.xml"],
    "DAL": ["https://www.bloggingtheboys.com/rss/index.xml"],
    "DEN": ["https://www.milehighreport.com/rss/index.xml"],
    "DET": ["https://www.prideofdetroit.com/rss/index.xml"],
    "GB":  ["https://www.acmepackingcompany.com/rss/index.xml"],
    "HOU": ["https://www.battleredblog.com/rss/index.xml"],
    "IND": ["https://www.stampedeblue.com/rss/index.xml"],
    "JAX": ["https://www.bigcatcountry.com/rss/index.xml"],
    "KC":  ["https://www.arrowheadpride.com/rss/index.xml"],
    "LAC": ["https://www.boltsfromtheblue.com/rss/index.xml"],
    "LAR": ["https://www.turfshowtimes.com/rss/index.xml"],
    "LV":  ["https://www.silverandblackpride.com/rss/index.xml"],
    "MIA": ["https://www.thephinsider.com/rss/index.xml"],
    "MIN": ["https://www.dailynorseman.com/rss/index.xml"],
    "NE":  ["https://www.patspulpit.com/rss/index.xml"],
    "NO":  ["https://www.canalstreetchronicles.com/rss/index.xml"],
    "NYG": ["https://www.bigblueview.com/rss/index.xml"],
    "NYJ": ["https://www.ganggreennation.com/rss/index.xml"],
    "PHI": ["https://www.bleedinggreennation.com/rss/index.xml"],
    "PIT": ["https://www.behindthesteelcurtain.com/rss/index.xml"],
    "SF":  ["https://www.ninersnation.com/rss/index.xml"],
    "SEA": ["https://www.fieldgulls.com/rss/index.xml"],
    "TB":  ["https://www.bucsnation.com/rss/index.xml"],
    "TEN": ["https://www.musiccitymiracles.com/rss/index.xml"],
    "WAS": ["https://www.hogshaven.com/rss/index.xml"],
}

def fetch_news(max_items: int = 20, teams: List[str] = None) -> List[Dict]:
    items = []
    sources = FEEDS[:]
    if teams:
        for t in teams:
            sources += TEAM_FEEDS.get(t.upper(), [])
    for url in sources:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:max_items]:
                items.append({
                    "title": e.get("title",""),
                    "summary": e.get("summary",""),
                    "link": e.get("link",""),
                    "published": e.get("published",""),
                    "source": url
                })
        except Exception:
            continue
    return items[:max_items]
