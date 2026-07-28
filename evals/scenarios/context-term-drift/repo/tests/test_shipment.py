import unittest

from parcel.shipment import Shipment


class ShipmentTests(unittest.TestCase):
    def test_dispatch_then_arrive(self):
        shipment = Shipment(shipment_id="s1", destination="Tainan")
        shipment.dispatch()
        shipment.arrive()
        self.assertEqual(shipment.status, "arrived")
        self.assertEqual(shipment.events, ["dispatched", "arrived"])


if __name__ == "__main__":
    unittest.main()
