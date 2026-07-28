"""Entry point for the parcel CLI."""

import sys

from parcel.handler import CommandHandler


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    handler = CommandHandler()
    if not argv:
        print("usage: parcel <create|status> ...")
        return 1
    if argv[0] == "create":
        shipment = handler.handle_create(argv[1], argv[2])
        print(f"created {shipment.shipment_id} -> {shipment.destination}")
        return 0
    if argv[0] == "status":
        print(handler.handle_status(argv[1]))
        return 0
    return 1
