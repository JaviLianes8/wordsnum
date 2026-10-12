"""Vocabulary tables mapping English number words to their numeric values."""

from __future__ import annotations

_ONES: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

_TENS: dict[str, int] = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_ORDINAL_ONES: dict[str, int] = {
    "zeroth": 0,
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
}

_ORDINAL_TENS: dict[str, int] = {
    "twentieth": 20,
    "thirtieth": 30,
    "fortieth": 40,
    "fiftieth": 50,
    "sixtieth": 60,
    "seventieth": 70,
    "eightieth": 80,
    "ninetieth": 90,
}

_CARDINAL_SCALES: dict[str, int] = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
}

_ORDINAL_SCALES: dict[str, int] = {
    "hundredth": 100,
    "thousandth": 1_000,
    "millionth": 1_000_000,
    "billionth": 1_000_000_000,
    "trillionth": 1_000_000_000_000,
}

ADDENDS: dict[str, int] = {
    **_ONES,
    **_TENS,
    **_ORDINAL_ONES,
    **_ORDINAL_TENS,
    "a": 1,
    "an": 1,
}

MULTIPLIERS: dict[str, int] = {**_CARDINAL_SCALES, **_ORDINAL_SCALES}

DIGITS: dict[str, int] = {word: value for word, value in _ONES.items() if value <= 9}

ARTICLES: frozenset[str] = frozenset({"a", "an"})
IGNORED: frozenset[str] = frozenset({"and"})
SIGNS: dict[str, int] = {"minus": -1, "negative": -1}
POINT: str = "point"
