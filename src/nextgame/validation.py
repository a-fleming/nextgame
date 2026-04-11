"""Validation helpers shared across the CLI.

Most of these are small on purpose. The main job here is to normalize raw
argparse input and raise clean errors before command handlers have to care.
"""

import argparse


def ensure_tag_options_do_not_conflict(include_tags: list[str] | None, exclude_tags: list[str] | None) -> None:
    """Raise if the same tag shows up in both include and exclude lists."""
    include = set(include_tags or [])
    exclude = set(exclude_tags or [])
    conflicts = include & exclude
    if conflicts:
        raise ValueError(f"Tags cannot be both included and excluded: {', '.join(sorted(conflicts))}")


def ensure_weight_options_do_not_conflict(min_weight: float | None, max_weight: float | None) -> None:
    """Raise if the requested minimum weight is higher than the maximum."""
    if min_weight is None or max_weight is None:
        return
    if min_weight > max_weight:
        raise ValueError(f"--min-weight cannot be greater than --max-weight")

def is_leap_year(year: int) -> bool:
    """Return True if the year is a leap year in the Gregorian calendar."""
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    return False

def validate_date(value: str) -> tuple[int, int, int]:
    """Validate a date string and return it as a `(year, month, day)` tuple.

    This accepts single-digit month/day input even though the help text shows
    `YYYY-MM-DD`. That is mostly a CLI convenience choice.
    """
    sections = value.split("-")
    if len(sections) != 3:
        raise argparse.ArgumentTypeError("date must be formatted as YYYY-MM-DD")
    year_str, month_str, day_str = sections
    try:
        year = int(year_str)
        if year < 1000:
            raise argparse.ArgumentTypeError(f"'{year_str}' is not a valid year")
        month = int(sections[1])
        if month < 1 or month > 12:
            raise argparse.ArgumentTypeError(f"'{month_str}' is not a valid month")
        day = int(sections[2])
    except ValueError:
        raise argparse.ArgumentTypeError("date sections must be integers")
    if day < 1 or day > 31:
        raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day")
    if month in [4, 6, 9, 11] and day > 30:
        raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}'")
    if month == 2:
        # handle special cases for February
        if day > 28 and not is_leap_year(year):
            raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}' and year '{year_str}'")
        elif day > 29:
            raise argparse.ArgumentTypeError(f"'{day_str}' is not a valid day for month '{month_str}' and year '{year_str}'")
    return year, month, day

def validate_float_one_to_five(value: str) -> float:
    """Validate a numeric weight/rating on the 1.0 to 5.0 scale."""
    try:
        v = float(value)
        if 1 <= v <= 5:
            return v
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("must be a number between 1.0 and 5.0")

def validate_game_name(value: str) -> str:
    """Normalize a game name while preserving its visible casing."""
    # Trim the edges but do not force lowercase. Game names are shown back to
    # the user later, so preserving their original casing reads better.
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("game name cannot be empty")

    # Collapse extra spaces so lookups and display stay consistent.
    value = " ".join(value.split())
    return value

def validate_game_players(value: str) -> tuple[int, int]:
    """Validate a player count or player range."""
    sections = value.split("-")
    if len(sections) == 1:
        try:
            game_players = int(value)
            if game_players <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            return game_players, game_players
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    if len(sections) == 2:
        if sections[0] == "":
            raise argparse.ArgumentTypeError("missing minimum")
        if sections[1] == "":
            raise argparse.ArgumentTypeError("missing maximum")
        try:
            low = int(sections[0])
            high = int(sections[1])
            if low <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            if low >= high:
                raise argparse.ArgumentTypeError("minimum must be less than maximum")
            return low, high
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    raise argparse.ArgumentTypeError("range must be in the format <min_players>-<max_players> (e.g. 3-5)")
	
def validate_game_time(value: str) -> tuple[int, int]:
    """Validate a play-time value or range in minutes."""
    sections = value.split("-")
    if len(sections) == 1:
        try:
            game_time = int(value)
            if game_time <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            return game_time, game_time
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    if len(sections) == 2:
        if sections[0] == "":
            raise argparse.ArgumentTypeError("missing minimum")
        if sections[1] == "":
            raise argparse.ArgumentTypeError("missing maximum")
        try:
            low = int(sections[0])
            high = int(sections[1])
            if low <= 0:
                raise argparse.ArgumentTypeError("must be greater than 0")
            if low >= high:
                raise argparse.ArgumentTypeError("minimum must be less than maximum")
            return low, high
        except ValueError:
            raise argparse.ArgumentTypeError("must be a single integer or two integers separated by a dash '-'")
    raise argparse.ArgumentTypeError("range must be in the format <min_time>-<max_time> (e.g. 60-90)")

def validate_positive_integer(value: str) -> int:
    """Validate a positive integer value."""
    try:
        value = int(value)
        if value > 0:
            return value
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")
    raise argparse.ArgumentTypeError("must be greater than 0")

def validate_tags(value: str) -> str:
    """Normalize a tag into the lowercase form used throughout the app."""
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("tag cannot be empty")

    # Tags are treated like identifiers, so normalize spacing and casing here
    # instead of making every caller remember to do it.
    value = " ".join(value.split())
    return value.lower()
