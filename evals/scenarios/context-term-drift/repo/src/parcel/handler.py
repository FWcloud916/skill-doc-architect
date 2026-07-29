"""Command handler wiring for the CLI."""

from parcel.shipment import Shipment


class CommandHandler:
    """Generic dispatcher from CLI verbs to shipment operations."""

    def __init__(self):
        self.shipments = {}

    def handle_create(self, shipment_id, destination):
        shipment = Shipment(shipment_id=shipment_id, destination=destination)
        self.shipments[shipment_id] = shipment
        return shipment

    def handle_status(self, shipment_id):
        return self.shipments[shipment_id].status
