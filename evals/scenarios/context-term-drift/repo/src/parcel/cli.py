"""Entry point for the parcel CLI."""

import json
import sys
from pathlib import Path

from parcel.handler import CommandHandler

STATE_FILE = Path(".parcel.json")


def load_handler():
    handler = CommandHandler()
    if STATE_FILE.is_file():
        for entry in json.loads(STATE_FILE.read_text()):
            shipment = handler.handle_create(entry["shipment_id"], entry["destination"])
            shipment.status = entry["status"]
            shipment.events = entry["events"]
    return handler


def save_handler(handler):
    STATE_FILE.write_text(json.dumps([
        {"shipment_id": s.shipment_id, "destination": s.destination,
         "status": s.status, "events": s.events}
        for s in handler.shipments.values()
    ]))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    handler = load_handler()
    if not argv:
        print("usage: parcel <create|status> ...")
        return 1
    if argv[0] == "create":
        if len(argv) != 3:
            print("usage: parcel create <id> <destination>", file=sys.stderr)
            return 2
        shipment = handler.handle_create(argv[1], argv[2])
        save_handler(handler)
        print(f"created {shipment.shipment_id} -> {shipment.destination}")
        return 0
    if argv[0] == "status":
        if len(argv) != 2:
            print("usage: parcel status <id>", file=sys.stderr)
            return 2
        print(handler.handle_status(argv[1]))
        return 0
    print(f"unknown command: {argv[0]}", file=sys.stderr)
    return 1
