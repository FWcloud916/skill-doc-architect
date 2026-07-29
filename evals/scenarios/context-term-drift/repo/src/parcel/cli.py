"""Entry point for the parcel CLI."""

import json
import os
import sys
from pathlib import Path

from parcel.handler import CommandHandler

STATE_FILE = Path(".parcel.json")


def load_handler():
    handler = CommandHandler()
    if not STATE_FILE.is_file():
        return handler
    try:
        entries = json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        print(f"warning: {STATE_FILE} is unreadable; starting from empty state",
              file=sys.stderr)
        return handler
    for entry in entries:
        shipment = handler.handle_create(entry["shipment_id"], entry["destination"])
        shipment.status = entry["status"]
        shipment.events = entry["events"]
    return handler


def save_handler(handler):
    payload = json.dumps([
        {"shipment_id": s.shipment_id, "destination": s.destination,
         "status": s.status, "events": s.events}
        for s in handler.shipments.values()
    ])
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(payload)
    os.replace(tmp, STATE_FILE)


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
        try:
            print(handler.handle_status(argv[1]))
        except KeyError:
            print(f"no such shipment: {argv[1]}", file=sys.stderr)
            return 1
        return 0
    print(f"unknown command: {argv[0]}", file=sys.stderr)
    return 1
