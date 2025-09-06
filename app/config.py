from datetime import datetime, timezone

SEASON = 2025
WEEK_DEADLINES_UTC = {1: "2025-09-04T23:00:00Z", 2: "2025-09-11T23:00:00Z", 3: "2025-09-18T23:00:00Z", 4: "2025-09-25T23:00:00Z"}

def parse_iso_z(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))

def is_submission_open(week: int, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    ts = WEEK_DEADLINES_UTC.get(week)
    if not ts: 
        return True
    return now < parse_iso_z(ts)
