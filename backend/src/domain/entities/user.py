import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    email: str
    password_hash: str
    display_name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_deleted: bool = False
