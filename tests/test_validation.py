import argparse
import pytest

from nextgame.validation import (
    ensure_tag_options_do_not_conflict,
    ensure_weight_options_do_not_conflict,
    is_leap_year,
    validate_date,
    validate_float_one_to_five,
    validate_game_name,
    validate_game_players,
    validate_game_time,
    validate_positive_integer,
    validate_tags,
)


@pytest.mark.parametrize(
    ("incl_tags", "excl_tags"), 
    [
        (["tag1"], ["tag2"]),
        (["tag1", "tag2"], ["tag3"]),
        ([], ["tag1"]),
        (["tag1"], []),
        (None, ["tag1"]),
        (["tag1"], None),
        (None, None),
    ]
)
def test_ensure_tag_options_do_not_conflict_accepts_valid_values(incl_tags, excl_tags):
    ensure_tag_options_do_not_conflict(incl_tags, excl_tags)

@pytest.mark.parametrize(
    ("incl_tags", "excl_tags"),
    [
        (["tag1", "tag2"], ["tag1"]),
        (["tag1"], ["tag1", "tag2"]),
        (["tag1", "tag2"], ["tag1", "tag2"]),
    ]
)
def test_ensure_tag_options_do_not_conflict_rejects_invalid_values(incl_tags, excl_tags):
    with pytest.raises(ValueError):
        ensure_tag_options_do_not_conflict(incl_tags, excl_tags)

@pytest.mark.parametrize(
    ("min_weight", "max_weight"), 
    [
        (1, 5),
        (3, 3),
        (None, 3),
        (3, None),
        (None, None),
    ]
)
def test_ensure_weight_options_do_not_conflict_accepts_valid_values(min_weight, max_weight):
    ensure_weight_options_do_not_conflict(min_weight, max_weight)

@pytest.mark.parametrize(
    ("min_weight", "max_weight"),
    [
        (5, 1),
        (3, 2),
    ]
)
def test_ensure_weight_options_do_not_conflict_rejects_invalid_values(min_weight, max_weight):
    with pytest.raises(ValueError):
        ensure_weight_options_do_not_conflict(min_weight, max_weight)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (2000, True),
        (2020, True),
        (2028, True),
        (1900, False),
        (2025, False),
        (2026, False),
    ],
)
def test_is_leap_year(raw, expected):
    assert is_leap_year(raw) == expected

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2020-01-31", (2020, 1, 31)),
        ("2020-1-31", (2020, 1, 31)),
        ("2020-02-29", (2020, 2, 29)),
        ("1000-12-01", (1000, 12, 1)),
    ],
)
def test_validate_date_accepts_valid_values(raw, expected):
    assert validate_date(raw) == expected

@pytest.mark.parametrize("raw", [
    "20-01-01",      # bad year
    "2020-00-01",    # bad month
    "2020-13-01",    # bad month
    "2020-01-32",    # bad day
    "2020-09-31",    # bad day
    "2021-02-29",    # not a leap year
    "1900-02-29",    # not a leap year
    "2020/01/31",    # invalid separator
    "2020.01.31",    # invalid separator
    "2020-01-01-1",  # extra field
    "", "-1", "0", "5.1", "abc" # not year values
])
def test_validate_date_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_date(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", 1.0),
        ("5", 5.0),
        ("1.0", 1.0),
        ("5.0", 5.0),
        ("3.754", 3.754),
    ],
)
def test_validate_float_one_to_five_accepts_valid_values(raw, expected):
    assert validate_float_one_to_five(raw) == expected

@pytest.mark.parametrize("raw", ["", "-1", "0", "0.99", "5.1", "inf", "nan", "abc"])
def test_validate_float_one_to_five_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_float_one_to_five(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("collapse   internal   space", "collapse internal space"),
        ("   strip leading space", "strip leading space"),
        ("strip trailing space    ", "strip trailing space"),
        ("Preserve ALL Capitalization", "Preserve ALL Capitalization"),
        ("preserve symbols `~!@#$%^&*()-_=+}{[];,.\"<>?'/", "preserve symbols `~!@#$%^&*()-_=+}{[];,.\"<>?'/"),
        ("preserve nums 1234567890", "preserve nums 1234567890")
    ],
)
def test_validate_game_name_accepts_valid_values(raw, expected):
    assert validate_game_name(raw) == expected

@pytest.mark.parametrize("raw", ["", " ", "      ", "\n", "\t"])
def test_validate_game_name_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_game_name(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", (1, 1)),
        ("4", (4, 4)),
        ("1-5", (1, 5)),
        ("5-6", (5, 6)),
    ],
)
def test_validate_game_players_accepts_valid_values(raw, expected):
    assert validate_game_players(raw) == expected

@pytest.mark.parametrize("raw", ["", "0", "-1", "5-", "3.5", "0-1", "5-2", "5-5", "1--2", "-1-2", "inf", "abc"])
def test_validate_game_players_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_game_players(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", (1, 1)),
        ("4", (4, 4)),
        ("1-5", (1, 5)),
        ("5-6", (5, 6)),
    ],
)
def test_validate_game_time_accepts_valid_values(raw, expected):
    assert validate_game_time(raw) == expected

@pytest.mark.parametrize("raw", ["", "0", "-1", "5-", "3.5", "0-1", "5-2", "5-5", "1--2", "-1-2", "inf", "abc"])
def test_validate_game_time_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_game_time(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", 1),
        ("4", 4),
    ],
)
def test_validate_positive_integer_accepts_valid_values(raw, expected):
    assert validate_positive_integer(raw) == expected

@pytest.mark.parametrize("raw", ["", "0", "-1", "abc", "3.5"])
def test_validate_positive_integer_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_positive_integer(raw)

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("collapse   internal   space", "collapse internal space"),
        ("   strip leading space", "strip leading space"),
        ("strip trailing space    ", "strip trailing space"),
        ("FORCE lowerCASE", "force lowercase"),
        ("preserve symbols `~!@#$%^&*()-_=+}{[];,.\"<>?'/", "preserve symbols `~!@#$%^&*()-_=+}{[];,.\"<>?'/"),
        ("preserve nums 1234567890", "preserve nums 1234567890")
    ],
)
def test_validate_tags_accepts_valid_values(raw, expected):
    assert validate_tags(raw) == expected

@pytest.mark.parametrize("raw", ["", " ", "      ", "\n", "\t"])
def test_validate_tags_rejects_invalid_values(raw):
    with pytest.raises(argparse.ArgumentTypeError):
        validate_tags(raw)