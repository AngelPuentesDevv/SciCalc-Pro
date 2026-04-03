import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Profile:
    user_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    avatar_url: str | None = None
    preferred_precision: int = 10
    angle_mode: str = "DEG"
    theme: str = "LIGHT"
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_deleted: bool = False
