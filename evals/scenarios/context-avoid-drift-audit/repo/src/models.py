"""Domain models for freightd."""

from dataclasses import dataclass


@dataclass
class Carrier:
    carrier_id: str
    name: str


@dataclass
class Shipment:
    shipment_id: str
    origin: str
    destination: str
    carrier: Carrier
    status: str = "booked"
