import re
from decimal import Decimal


class ResultRowParser:
    def __init__(self, row):
        self.row = row
        self.last_match = None

    def parse(self):
        values = []
        while self.row:
            value = self.parse_value()
            values.append(value)

            comma = self.consume(r',')
            if not comma and self.row:
                raise Exception('Unexpected result row value: ' + self.row)

            if comma and not self.row:
                raise Exception('Unexpected end of result row')

        return values

    def parse_value(self):
        if self.consume(r'^NULL'):
            return None
        elif self.consume(r'^TRUE'):
            return True
        elif self.consume(r'^FALSE'):
            return False
        elif self.consume(r"^'([^']*)'"):
            # Extract the string content without quotes from the captured group
            return self.last_match.group(1)
        elif (self.consume(r'^(-?\d+\.?\d*[eE][+-]?\d+)')):
            # Scientific notation - parse as float
            return float(self.last_match.group(1))
        elif (self.consume(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)')):
            # ISO 8601 timestamp with optional timezone (e.g., 2024-01-15T10:30:00Z)
            return self.last_match.group(1)
        elif (self.consume(r'^(\d{4}-\d{2}-\d{2})')):
            # ISO 8601 date (e.g., 2024-01-15)
            return self.last_match.group(1)
        elif (self.consume(r'^(\d{2}:\d{2}:\d{2}(?:\.\d+)?)')):
            # ISO 8601 time (e.g., 14:30:00 or 14:30:00.123456)
            return self.last_match.group(1)
        elif (self.consume(r'^(P(?:\d+Y)?(?:\d+M)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+S)?)?)')):
            # ISO 8601 duration/interval (e.g., P1D, PT5H30M, P2Y3M10D)
            return self.last_match.group(1)
        elif (self.consume(r'^(-?\d+\.\d+)')):
            # Decimal number - use Python Decimal for arbitrary precision
            return Decimal(self.last_match.group(1))
        elif (self.consume(r'^(-?\d+)')):
            return int(self.last_match.group(1))
        else:
            raise Exception('Unexpected result row value: ' + self.row)

    def consume(self, regex):
        regex_obj = re.compile(regex)
        match = regex_obj.match(self.row)
        if match:
            self.row = self.row[match.end():].strip()
            self.last_match = match  # Store the match object, not the string
            return match.group()  # But still return the string for backward compatibility
