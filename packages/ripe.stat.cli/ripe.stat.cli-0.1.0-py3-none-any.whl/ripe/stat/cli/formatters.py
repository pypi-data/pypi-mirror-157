from datetime import datetime
from typing import Any, Callable, Sequence


def as_string(data: Any) -> str:
    if data is None:
        return ""
    return str(data)


def as_bool(data: Any) -> str:
    if data:
        return "✅"
    return "❌"


def as_list(data: Sequence[str]):
    return "\n".join(data)


def as_map(lat: float, lng: float) -> str:
    return f"https://www.google.com/maps/@{lat},{lng},12z"


def as_unixtime(timestamp: int) -> str:
    if not timestamp:
        return "[unknown]"
    return datetime.fromtimestamp(timestamp).isoformat()


def as_total_time(elapsed: int) -> str:
    return str(elapsed)


def as_flag(country_code: str) -> str:
    """
    This doesn't work because I can't figure out how to get flags to appear in
    the terminal.  Other emojis work just fine, but because flag emojis are
    actually the result of combining emojis for the letters in the ISO code,
    my terminal doesn't render them properly.  Instead of 🇨🇦, I get 🇨 🇦.
    """

    offset = ord("🇦") - ord("A")
    lft = chr(ord(country_code[0]) + offset)
    rgt = chr(ord(country_code[1]) + offset)

    return f"{lft}{rgt}"


def get_formatter(key: str) -> Callable:
    return {
        "str": as_string,
        "bool": as_bool,
        "list": as_list,
        "map": as_map,
        "unixtime": as_unixtime,
        "total_time": as_total_time,
        "flag": as_flag,
    }[
        key
    ]  # type: ignore
