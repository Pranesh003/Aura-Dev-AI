import datetime
import json
import os
import threading
from typing import Any, Dict, List, Optional

_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory")
_LOCK = threading.Lock()


def _ensure_dir() -> None:
    os.makedirs(_BASE_DIR, exist_ok=True)


def append_memory(stream: str, payload: Dict[str, Any]) -> None:
    """
    Append a structured memory entry to a JSONL stream.
    Intended for long-horizon project history and agent decisions.
    """
    _ensure_dir()
    path = os.path.join(_BASE_DIR, f"{stream}.jsonl")
    entry: Dict[str, Any] = dict(payload)
    entry.setdefault("ts", datetime.datetime.utcnow().isoformat() + "Z")
    with _LOCK, open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_memory(stream: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Load entries from a JSONL memory stream.
    If limit is provided, only the most recent N entries are returned.
    """
    _ensure_dir()
    path = os.path.join(_BASE_DIR, f"{stream}.jsonl")
    if not os.path.exists(path):
        return []

    items: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit is not None and limit > 0:
        return items[-limit:]
    return items


def summarize_memory(stream: str, limit: int = 20) -> str:
    """
    Lightweight textual view over recent memory entries.
    Agents can use this as a context primer before planning.
    """
    entries = load_memory(stream, limit=limit)
    if not entries:
        return "No prior memory available for this project stream."

    lines: List[str] = []
    for idx, e in enumerate(entries, start=1):
        ts = e.get("ts", "unknown_ts")
        kind = e.get("kind", "event")
        summary = e.get("summary") or e.get("status") or e.get("note") or ""
        lines.append(f"{idx}. [{ts}] ({kind}) {summary}")
    return "\n".join(lines)

