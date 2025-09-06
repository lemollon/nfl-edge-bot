import json, os
from pathlib import Path

DATA_DIR = Path(os.getenv("STATE_DIR", "app/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEADER_FILE = DATA_DIR / "leaderboard.json"
PLANS_FILE = DATA_DIR / "plans.json"

def _load(path: Path):
    if not path.exists(): return []
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return []

def _save(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_plan(plan: dict):
    items = _load(PLANS_FILE); items.append(plan); _save(PLANS_FILE, items)

def list_plans():
    return _load(PLANS_FILE)

def add_leaderboard_entry(entry: dict):
    items = _load(LEADER_FILE); items.append(entry); _save(LEADER_FILE, items)

def leaderboard(week: int | None = None):
    items = _load(LEADER_FILE)
    if week is not None:
        items = [x for x in items if int(x.get("week", 0)) == int(week)]
    items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)
    return items[:100]

def ladder():
    items = _load(LEADER_FILE)
    agg = {}
    for it in items:
        u = it.get("user","anon")
        agg.setdefault(u, {"user": u, "total_score": 0, "weeks": set()})
        agg[u]["total_score"] += int(it.get("score", 0))
        agg[u]["weeks"].add(int(it.get("week", 0)))
    out = [{"user": u, "total_score": row["total_score"], "weeks_played": len(row["weeks"])} for u,row in agg.items()]
    out.sort(key=lambda x: x["total_score"], reverse=True)
    return out[:100]
