"""Text formatting helpers."""


class Formatter:
    """Wraps and indents plain text."""

    def __init__(self, width=80):
        self.width = width

    def indent(self, text, spaces=2):
        prefix = " " * spaces
        return "\n".join(prefix + line for line in text.splitlines())

    def truncate(self, text, limit=None):
        limit = limit or self.width
        return text if len(text) <= limit else text[: limit - 1] + "…"
