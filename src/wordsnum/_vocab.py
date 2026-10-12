"""Vocabulary tables mapping English number words to their numeric values."""

from __future__ import annotations

UNIT_WORDS: tuple[str, ...] = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
TENS_WORDS: tuple[str, ...] = (
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)
# Short scale, one entry per power of a thousand: thousand = 10**3 ... vigintillion = 10**63.
SCALE_WORDS: tuple[str, ...] = (
    "thousand",
    "million",
    "billion",
    "trillion",
    "quadrillion",
    "quintillion",
    "sextillion",
    "septillion",
    "octillion",
    "nonillion",
    "decillion",
    "undecillion",
    "duodecillion",
    "tredecillion",
    "quattuordecillion",
    "quindecillion",
    "sexdecillion",
    "septendecillion",
    "octodecillion",
    "novemdecillion",
    "vigintillion",
)

UNITS: dict[str, int] = {word: value for value, word in enumerate(UNIT_WORDS)}
TENS: dict[str, int] = {word: 20 + 10 * index for index, word in enumerate(TENS_WORDS)}
SCALES: dict[str, int] = {word: 1000 ** (index + 1) for index, word in enumerate(SCALE_WORDS)}
HUNDRED = "hundred"
LARGEST_SCALE: int = 1000 ** len(SCALE_WORDS)

_IRREGULAR_ORDINALS: dict[str, str] = {
    "one": "first",
    "two": "second",
    "three": "third",
    "five": "fifth",
    "eight": "eighth",
    "nine": "ninth",
    "twelve": "twelfth",
}


def ordinal_of(word: str) -> str:
    """Return the ordinal form of one cardinal word ("twenty" -> "twentieth")."""
    if word in _IRREGULAR_ORDINALS:
        return _IRREGULAR_ORDINALS[word]
    if word.endswith("y"):
        return word[:-1] + "ieth"
    return word + "th"


_CARDINAL_WORDS: tuple[str, ...] = (*UNIT_WORDS, *TENS_WORDS, HUNDRED, *SCALE_WORDS)
# Ordinal word -> the cardinal word it stands for ("first" -> "one").
ORDINALS: dict[str, str] = {ordinal_of(word): word for word in _CARDINAL_WORDS}

# Words that name a denominator when plural ("thirds") or after "a"/"one" ("a third").
# "first" and "second" only do so inside a hyphenated compound ("thirty-seconds").
_NOT_DENOMINATORS = frozenset({"zeroth", "first", "second"})
DENOMINATORS: dict[str, int] = {"half": 2, "quarter": 4}
for _ordinal, _cardinal in ORDINALS.items():
    if _ordinal not in _NOT_DENOMINATORS:
        _value = UNITS.get(_cardinal) or TENS.get(_cardinal) or SCALES.get(_cardinal, 100)
        DENOMINATORS[_ordinal] = _value
PLURAL_DENOMINATORS: dict[str, str] = {word + "s": word for word in DENOMINATORS}
PLURAL_DENOMINATORS["halves"] = "half"
# Plural ordinal units usable only after a hyphenated tens word ("twenty-firsts").
COMPOUND_PLURALS: dict[str, str] = {
    ordinal_of(word) + "s": ordinal_of(word) for word in UNIT_WORDS[1:10]
}

ARTICLES: frozenset[str] = frozenset({"a", "an"})
AND = "and"
POINT = "point"
SIGNS: frozenset[str] = frozenset({"minus", "negative"})
POINT_DIGITS: dict[str, int] = {**{word: UNITS[word] for word in UNIT_WORDS[:10]}, "oh": 0}

VOCABULARY: frozenset[str] = frozenset(
    {
        *_CARDINAL_WORDS,
        *ORDINALS,
        *DENOMINATORS,
        *PLURAL_DENOMINATORS,
        *COMPOUND_PLURALS,
        *ARTICLES,
        AND,
        POINT,
        *SIGNS,
        "oh",
    }
)
