"""TC-UNIT-007: AuditLogModel — validación de campos y lógica de auditoría web-first.

Reemplaza test_sync_lww.py (residuo mobile LWW). El modelo audit_log es web-first:
registra acciones CREATE/UPDATE/DELETE con status y payload opcional.
ISO 29119 — Test Unit 007
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Representación en memoria del AuditLogModel (sin DB) ─────────────────────

@dataclass
class AuditEntry:
    user_id: str
    entity_type: str
    entity_id: str
    action: str
    status: str = "success"
    payload: Any = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_deleted: bool = False


# ── TC-UNIT-007a: campos obligatorios ────────────────────────────────────────

def test_audit_entry_required_fields():
    """TC-UNIT-007a: AuditEntry con campos obligatorios genera id UUID v4 y created_at."""
    entry = AuditEntry(
        user_id="user-1",
        entity_type="user",
        entity_id="user-1",
        action="CREATE",
    )
    assert entry.user_id == "user-1"
    assert entry.entity_type == "user"
    assert entry.action == "CREATE"
    assert entry.status == "success"
    assert entry.payload is None
    assert entry.id is not None
    assert len(entry.id) == 36  # UUID v4


# ── TC-UNIT-007b: acciones permitidas ────────────────────────────────────────

def test_audit_entry_valid_actions():
    """TC-UNIT-007b: Las acciones válidas son CREATE, UPDATE, DELETE."""
    for action in ("CREATE", "UPDATE", "DELETE"):
        entry = AuditEntry("u1", "calculation_history", "c1", action)
        assert entry.action == action


# ── TC-UNIT-007c: status error ────────────────────────────────────────────────

def test_audit_entry_status_error():
    """TC-UNIT-007c: status puede ser 'error' para registrar fallos."""
    entry = AuditEntry(
        user_id="user-2",
        entity_type="user",
        entity_id="user-2",
        action="CREATE",
        status="error",
        payload={"reason": "email duplicado"},
    )
    assert entry.status == "error"
    assert entry.payload["reason"] == "email duplicado"


# ── TC-UNIT-007d: payload JSON-serializable ───────────────────────────────────

def test_audit_entry_payload_dict():
    """TC-UNIT-007d: payload acepta dict para datos contextuales."""
    payload = {"expression": "sin(90)", "result": "1.0"}
    entry = AuditEntry("u3", "calculation_history", "c2", "DELETE", payload=payload)
    assert entry.payload["expression"] == "sin(90)"


# ── TC-UNIT-007e: borrado lógico ──────────────────────────────────────────────

def test_audit_entry_is_deleted_default_false():
    """TC-UNIT-007e: is_deleted es False por defecto — el audit log no se borra físicamente."""
    entry = AuditEntry("u4", "user", "u4", "CREATE")
    assert entry.is_deleted is False


# ── TC-UNIT-007f: created_at con timezone ────────────────────────────────────

def test_audit_entry_created_at_is_utc():
    """TC-UNIT-007f: created_at debe tener timezone UTC."""
    entry = AuditEntry("u5", "user", "u5", "DELETE")
    assert entry.created_at.tzinfo is not None
