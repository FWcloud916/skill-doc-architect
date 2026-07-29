# freightd — Context

Freight booking daemon: accepts Shipment orders and schedules Carrier pickups.

## Language

**Shipment** — one booked movement of goods from origin to destination; the unit
every command operates on. Structure: [docs/domain-models.md](docs/domain-models.md).
_Avoid_: Delivery, Parcel — legacy names from the v0 prototype.

**Carrier** — the external company that physically moves a Shipment.
_Avoid_: Vendor

## Relationships

- A Carrier picks up many Shipments; a Shipment has exactly one Carrier.

## Flagged ambiguities

- "Delivery" meant both the Shipment and its final arrival event; ruled 2026-06-01:
  the movement is a "Shipment", the arrival event is "arrival".
