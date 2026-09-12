from __future__ import annotations

from pathlib import Path
from datetime import datetime
from threading import RLock
import json
import re

BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "jarvis_memory.json"

MAX_RECENT_TURNS = 12
MAX_STORED_TURNS = 500
MAX_FACTS = 100
_lock = RLock()

def _now():
    return datetime.now().isoformat(timespec="seconds")

def _load():
    with _lock:
        if not MEMORY_FILE.exists():
            now = _now()
            return {
                "version": 1,
                "created_at": now,
                "updated_at": now,
                "facts": [],
                "history": []
            }
        try:
            data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("version", 1)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", _now())
        data.setdefault("facts", [])
        data.setdefault("history", [])
        if not isinstance(data["facts"], list):
            data["facts"] = []
        if not isinstance(data["history"], list):
            data["history"] = []
        return data

def _save(data):
    with _lock:
        data["updated_at"] = _now()
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = MEMORY_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(MEMORY_FILE)

def _clean(text, limit=4000):
    return str(text or "").strip()[:limit]

def _extract_explicit_memory(user_text):
    text = _clean(user_text, 1000)
    patterns = (
        r"^\s*remember that\s+(.+)$",
        r"^\s*remember\s+(.+)$",
        r"^\s*my name is\s+(.+)$",
        r"^\s*i like\s+(.+)$",
        r"^\s*i love\s+(.+)$",
        r"^\s*i prefer\s+(.+)$",
        r"^\s*i use\s+(.+)$",
        r"^\s*my favorite\s+(.+)$",
    )
    for pattern in patterns:
        m = re.match(pattern, text, flags=re.IGNORECASE)
        if m:
            value = re.sub(r"\s+", " ", m.group(1)).strip()
            if value:
                return f"User fact: {text}"
    return None

def remember(user_text, assistant_text):
    user_text = _clean(user_text)
    assistant_text = _clean(assistant_text)
    if not user_text and not assistant_text:
        return
    with _lock:
        data = _load()
        data["history"].append({
            "timestamp": _now(),
            "user": user_text,
            "assistant": assistant_text
        })
        data["history"] = data["history"][-MAX_STORED_TURNS:]
        fact = _extract_explicit_memory(user_text)
        if fact and fact.lower() not in {str(x).lower() for x in data["facts"]}:
            data["facts"].append(fact)
            data["facts"] = data["facts"][-MAX_FACTS:]
        _save(data)

def add_fact(fact):
    fact = re.sub(r"\s+", " ", str(fact or "").strip())
    if not fact:
        return
    with _lock:
        data = _load()
        if fact.lower() not in {str(x).lower() for x in data["facts"]}:
            data["facts"].append(fact)
            data["facts"] = data["facts"][-MAX_FACTS:]
            _save(data)

def get_facts():
    return list(_load().get("facts", []))

def get_recent_history(limit=MAX_RECENT_TURNS):
    return _load().get("history", [])[-max(1, int(limit)):]

def build_context():
    data = _load()
    sections = []
    facts = data.get("facts", [])
    if facts:
        sections.append("LONG-TERM MEMORY:\n" + "\n".join(f"- {x}" for x in facts[-MAX_FACTS:]))
    recent = data.get("history", [])[-MAX_RECENT_TURNS:]
    lines = []
    for turn in recent:
        user = str(turn.get("user", "")).strip()
        assistant = str(turn.get("assistant", "")).strip()
        if user:
            lines.append(f"User: {user}")
        if assistant:
            lines.append(f"JARVIS: {assistant}")
    if lines:
        sections.append("RECENT CONVERSATION:\n" + "\n".join(lines))
    return "\n\n".join(sections)

def clear_memory():
    with _lock:
        now = _now()
        _save({"version": 1, "created_at": now, "updated_at": now, "facts": [], "history": []})

def clear_history():
    with _lock:
        data = _load()
        data["history"] = []
        _save(data)

def clear_facts():
    with _lock:
        data = _load()
        data["facts"] = []
        _save(data)

def memory_stats():
    data = _load()
    return {
        "memory_file": str(MEMORY_FILE),
        "facts": len(data.get("facts", [])),
        "history_turns": len(data.get("history", [])),
        "updated_at": data.get("updated_at")
    }

def export_memory():
    return _load()

if __name__ == "__main__":
    print(json.dumps(memory_stats(), ensure_ascii=False, indent=2))
