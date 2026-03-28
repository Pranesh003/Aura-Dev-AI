from typing import Dict, List
from fastapi import WebSocket

# Shared in-memory state decoupled from main.py to prevent circular imports
jobs: Dict[str, dict] = {}
connected_clients: Dict[str, List[WebSocket]] = {}
