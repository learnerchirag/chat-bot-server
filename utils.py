from dateutil import parser
from datetime import datetime

def parse_datetime(value: str) -> datetime:
    if isinstance(value, str):
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        try:
            print(value, parser.isoparse(value))
            return parser.isoparse(value)
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {value}") from e