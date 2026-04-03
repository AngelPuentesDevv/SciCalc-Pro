import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Calculation:
    expression: str
    result: str
    user_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    precision_digits: int = 10
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_deleted: bool = False
    sync_version: int = 0
    device_id: str | None = None
