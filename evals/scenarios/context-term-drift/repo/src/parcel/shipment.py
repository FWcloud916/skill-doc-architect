"""Shipment lifecycle: created -> dispatched -> arrived."""

from dataclasses import dataclass, field


@dataclass
class Shipment:
    shipment_id: str
    destination: str
    status: str = "created"
    events: list = field(default_factory=list)

    def dispatch(self):
        self.status = "dispatched"
        self.events.append("dispatched")

    def arrive(self):
        self.status = "arrived"
        self.events.append("arrived")
