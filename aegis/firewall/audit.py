"""SQLite audit log and session risk store."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "aegis.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                session_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                risk_score REAL NOT NULL,
                attack_types TEXT NOT NULL,
                explanation TEXT NOT NULL,
                raw_text TEXT,
                sanitized_text TEXT,
                twin_json TEXT,
                findings_json TEXT,
                status TEXT NOT NULL DEFAULT 'final',
                analyst_note TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS session_risk (
                session_id TEXT PRIMARY KEY,
                risk_score REAL NOT NULL DEFAULT 0,
                turn_count INTEGER NOT NULL DEFAULT 0,
                history_json TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS quarantine_queue (
                event_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                FOREIGN KEY(event_id) REFERENCES audit_events(id)
            );
            """
        )


def log_event(
    session_id: str,
    decision: str,
    risk_score: float,
    attack_types: list[str],
    explanation: str,
    raw_text: str = "",
    sanitized_text: str = "",
    twin: Optional[dict[str, Any]] = None,
    findings: Optional[list[dict[str, Any]]] = None,
    status: str = "final",
) -> int:
    init_db()
    ts = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO audit_events
            (ts, session_id, decision, risk_score, attack_types, explanation,
             raw_text, sanitized_text, twin_json, findings_json, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                session_id,
                decision,
                risk_score,
                json.dumps(attack_types),
                explanation,
                raw_text,
                sanitized_text,
                json.dumps(twin or {}),
                json.dumps(findings or []),
                status,
            ),
        )
        event_id = int(cur.lastrowid)
        if decision == "quarantine":
            conn.execute(
                """
                INSERT OR REPLACE INTO quarantine_queue (event_id, created_at, payload_json)
                VALUES (?, ?, ?)
                """,
                (
                    event_id,
                    ts,
                    json.dumps(
                        {
                            "session_id": session_id,
                            "risk_score": risk_score,
                            "attack_types": attack_types,
                            "explanation": explanation,
                            "raw_text": raw_text,
                        }
                    ),
                ),
            )
        return event_id


def list_events(limit: int = 100) -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def list_quarantine() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT q.event_id, q.created_at, q.payload_json, e.status, e.explanation
            FROM quarantine_queue q
            JOIN audit_events e ON e.id = q.event_id
            WHERE e.status = 'pending'
            ORDER BY q.event_id DESC
            """
        ).fetchall()
    out = []
    for r in rows:
        payload = json.loads(r["payload_json"])
        out.append(
            {
                "event_id": r["event_id"],
                "created_at": r["created_at"],
                "status": r["status"],
                "explanation": r["explanation"],
                **payload,
            }
        )
    return out


def resolve_quarantine(event_id: int, action: str, note: str = "") -> bool:
    init_db()
    status = "approved" if action == "approve" else "denied"
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE audit_events SET status = ?, analyst_note = ? WHERE id = ? AND status = 'pending'",
            (status, note, event_id),
        )
        conn.execute("DELETE FROM quarantine_queue WHERE event_id = ?", (event_id,))
        return cur.rowcount > 0


def get_session_risk(session_id: str) -> dict[str, Any]:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM session_risk WHERE session_id = ?", (session_id,)
        ).fetchone()
    if not row:
        return {"session_id": session_id, "risk_score": 0.0, "turn_count": 0, "history": []}
    return {
        "session_id": row["session_id"],
        "risk_score": row["risk_score"],
        "turn_count": row["turn_count"],
        "history": json.loads(row["history_json"]),
    }


def bump_session_risk(session_id: str, delta: float, note: str) -> float:
    init_db()
    current = get_session_risk(session_id)
    new_score = min(1.0, max(0.0, float(current["risk_score"]) + delta))
    history = current["history"]
    history.append({"delta": delta, "note": note, "ts": datetime.now(timezone.utc).isoformat()})
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO session_risk (session_id, risk_score, turn_count, history_json)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                risk_score = excluded.risk_score,
                turn_count = session_risk.turn_count + 1,
                history_json = excluded.history_json
            """,
            (session_id, new_score, 1, json.dumps(history[-50:])),
        )
    return new_score


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["attack_types"] = json.loads(d.get("attack_types") or "[]")
    d["twin"] = json.loads(d.get("twin_json") or "{}")
    d["findings"] = json.loads(d.get("findings_json") or "[]")
    return d
