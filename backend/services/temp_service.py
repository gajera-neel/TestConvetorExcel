import json
from datetime import datetime

from config import TEMP_DIR


def _session_path(session_id: str):
    return TEMP_DIR / f"{session_id}.json"


def save_session(session: dict) -> dict:
    session.setdefault("updated_at", datetime.now().isoformat(timespec="seconds"))
    _session_path(session["id"]).write_text(json.dumps(session, indent=2), encoding="utf-8")
    return session


def load_session(session_id: str) -> dict | None:
    path = _session_path(session_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def list_sessions() -> list[dict]:
    sessions = []
    for path in TEMP_DIR.glob("*.json"):
        if path.name == "history.json":
            continue
        try:
            sessions.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return sorted(sessions, key=lambda item: item.get("updated_at", ""), reverse=True)


def latest_session() -> dict | None:
    sessions = list_sessions()
    return sessions[0] if sessions else None
