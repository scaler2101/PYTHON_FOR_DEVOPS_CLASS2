"""Explicit models keep network payloads separate from operational decisions."""
from dataclasses import asdict, dataclass, field

@dataclass(frozen=True)
class Finding:
    service_id: str
    owner: str
    severity: str
    reasons: list[str] = field(default_factory=list)
    incident_ids: list[str] = field(default_factory=list)

    def as_dict(self):
        return asdict(self)
