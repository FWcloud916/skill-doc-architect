import unittest

from atlas_cli.main import main


class MainTest(unittest.TestCase):
    def test_callable(self):
        self.assertTrue(callable(main))
