"""Key=value line parsing helpers."""


class Parser:
    """Parses simple key=value configuration lines."""

    def parse(self, text):
        result = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                continue
            result[key.strip()] = value.strip()
        return result
