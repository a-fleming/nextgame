import argparse


def error_if_tag_options_conflict(args):
    # prevent same tag in both include/exclude
    include = set(args.include_tags or [])
    exclude = set(args.exclude_tags or [])
    conflicts = include & exclude
    if conflicts:
        args.parser.error(f"Tags cannot be both included and excluded: {', '.join(sorted(conflicts))}")

def is_leap_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    return False

def validate_date(value):
    # YYYY-MM-DD
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

def validate_float_one_to_five(value):
    try:
        v = float(value)
        if 1 <= v <= 5:
            return v
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("must be a number between 1.0 and 5.0")

def validate_game_name(value):
    # strip leading and trailing whitespace
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("game name cannot be empty")

    # collapse internal whitespace
    value = " ".join(value.split())
    return value

def validate_game_players(value):
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
	
def validate_game_time(value):
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

def validate_positive_integer(value):
    try:
        value = int(value)
        if value > 0:
            return value
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")
    raise argparse.ArgumentTypeError("must be greater than 0")

def validate_tags(value):
    # strip leading and trailing whitespace
    value = value.strip()

    if not value:
        raise argparse.ArgumentTypeError("tag cannot be empty")

    # collapse internal whitespace
    value = " ".join(value.split())
    return value.lower()
