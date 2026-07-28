import unittest

from textutils.formatter import Formatter
from textutils.parser import Parser


class FormatterTests(unittest.TestCase):
    def test_indent(self):
        self.assertEqual(Formatter().indent("a\nb"), "  a\n  b")

    def test_parse(self):
        self.assertEqual(Parser().parse("k = v\n# c\n"), {"k": "v"})


if __name__ == "__main__":
    unittest.main()
