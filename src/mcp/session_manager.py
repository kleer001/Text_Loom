"""
Session Manager for MCP Server

Provides workspace isolation for concurrent LLM operations.
Each session has its own node environment and global store.
"""

import uuid
import tempfile
import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from core.base_classes import NodeEnvironment
from core.global_store import GlobalStore
from core.flowstate_manager import save_flowstate, load_flowstate


@dataclass
class Session:
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    workspace_file: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.workspace_file is None:
            temp_dir = Path(tempfile.gettempdir()) / "text_loom_sessions"
            temp_dir.mkdir(exist_ok=True)
            self.workspace_file = temp_dir / f"{self.session_id}.json"


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            metadata=metadata or {}
        )
        self.sessions[session_id] = session

        with self.use_session(session_id):
            NodeEnvironment.nodes.clear()
            self._clear_globals()

        return session_id

    def _clear_globals(self):
        global_store = GlobalStore()
        for key in list(global_store.list().keys()):
            global_store.delete(key)

    def use_session(self, session_id: str):
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        return SessionContext(self, session_id)

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        session = self.sessions.pop(session_id, None)
        if session and session.workspace_file and session.workspace_file.exists():
            session.workspace_file.unlink()
            return True
        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat(),
                "metadata": s.metadata
            }
            for s in self.sessions.values()
        ]

    def export_session(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session or not session.workspace_file.exists():
            return {}

        with open(session.workspace_file) as f:
            return json.load(f)

    def import_session(self, session_id: str, flowstate: Dict[str, Any]) -> None:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        with open(session.workspace_file, 'w') as f:
            json.dump(flowstate, f, indent=2)


class SessionContext:
    def __init__(self, manager: SessionManager, session_id: str):
        self.manager = manager
        self.session_id = session_id
        self.session = manager.sessions[session_id]
        self.saved_state_file = None

    def __enter__(self):
        temp_save = Path(tempfile.gettempdir()) / f"tl_save_{uuid.uuid4()}.json"
        save_flowstate(str(temp_save))
        self.saved_state_file = temp_save

        if self.session.workspace_file.exists():
            load_flowstate(str(self.session.workspace_file))
        else:
            NodeEnvironment.nodes.clear()
            self.manager._clear_globals()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_flowstate(str(self.session.workspace_file))

        if self.saved_state_file and self.saved_state_file.exists():
            load_flowstate(str(self.saved_state_file))
            self.saved_state_file.unlink()


_global_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    return _global_session_manager
