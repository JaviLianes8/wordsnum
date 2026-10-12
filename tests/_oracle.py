"""An independent English number speller used only as a test oracle.

It is written from the documented short-scale rules with a different algorithm from
the library (recursion on the largest scale instead of grouping by thousands), so a
shared mistake is unlikely. No third-party oracle is required.
"""

from __future__ import annotations

import random
from fractions import Fraction

SMALL = [
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
]
TENS = ["", "", *["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]]
SCALE_NAMES = [
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
]
SCALES = [(10 ** (3 * (index + 1)), name) for index, name in enumerate(SCALE_NAMES)][::-1]
IRREGULAR = {
    "one": "first",
    "two": "second",
    "three": "third",
    "five": "fifth",
    "eight": "eighth",
    "nine": "ninth",
    "twelve": "twelfth",
}
LIMIT = 10**66


def spell(n: int, *, british: bool = False) -> str:
    """Spell a non-negative integer below 10**66 in canonical form."""
    if n < 20:
        return SMALL[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        return TENS[tens] + (f"-{SMALL[unit]}" if unit else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        head = f"{SMALL[hundreds]} hundred"
        if not rest:
            return head
        return f"{head} {'and ' if british else ''}{spell(rest)}"
    for value, name in SCALES:
        if n >= value:
            count, rest = divmod(n, value)
            head = f"{spell(count, british=british)} {name}"
            if not rest:
                return head
            joiner = " and " if british and rest < 100 else " "
            return head + joiner + spell(rest, british=british)
    raise AssertionError("unreachable")


def ordinal_word(word: str) -> str:
    if word in IRREGULAR:
        return IRREGULAR[word]
    return word[:-1] + "ieth" if word.endswith("y") else word + "th"


def ordinalize(words: str) -> str:
    """Turn a canonical cardinal spelling into its ordinal."""
    head, _, last = words.rpartition(" ")
    stem, _, unit = last.rpartition("-")
    tail = f"{stem}-{ordinal_word(unit)}" if stem else ordinal_word(unit)
    return f"{head} {tail}" if head else tail


def random_int(rng: random.Random) -> int:
    """Draw an integer with a spread of sizes and plenty of zero groups."""
    shape = rng.random()
    if shape < 0.3:
        return rng.randrange(1000)
    if shape < 0.55:
        return rng.randrange(10 ** rng.randint(3, 12))
    groups = [rng.choice([0, 0, rng.randrange(1000)]) for _ in range(rng.randint(2, 22))]
    groups[0] = groups[0] or rng.randrange(1, 1000)
    return sum(group * 1000**power for power, group in enumerate(reversed(groups)))


def scramble(words: str, rng: random.Random) -> str:
    """Rewrite a canonical spelling in a lenient but equivalent way."""
    out = []
    pieces = words.split(" ")
    for index, word in enumerate(pieces):
        if "-" in word and rng.random() < 0.5:
            word = word.replace("-", rng.choice([" ", " - ", "--"]))
        if rng.random() < 0.3:
            word = word.upper() if rng.random() < 0.5 else word.capitalize()
        if word.lower() in SCALE_NAMES and index < len(pieces) - 1 and rng.random() < 0.3:
            word += ","
        out.append(word)
    gaps = [rng.choice([" ", "  ", "\t", " \n "]) for _ in out]
    text = "".join(word + gap for word, gap in zip(out, gaps, strict=True)).rstrip()
    return rng.choice(["", " ", "\t"]) + text + rng.choice(["", " ", "\n"])


DENOMINATOR_WORDS = {2: ("half", "halves"), 4: ("quarter", "quarters")}


def denominator_words(den: int) -> tuple[str, str]:
    if den in DENOMINATOR_WORDS:
        return DENOMINATOR_WORDS[den]
    singular = {100: "hundredth", 1000: "thousandth"}.get(den) or ordinalize(spell(den))
    return singular, singular + "s"


def random_fraction(rng: random.Random) -> tuple[str, Fraction]:
    """A spelled fraction or mixed number with its exact value."""
    den = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 25, 32, 64, 100, 1000])
    singular, plural = denominator_words(den)
    num = rng.randrange(0, 3 * den)
    if num == 1:
        article = "an" if singular[0] in "aeiou" else "a"  # by sound: "an eighth"
        lead = article if den >= 100 else rng.choice([article, "one"])
        text, value = f"{lead} {singular}", Fraction(1, den)
    else:
        text, value = f"{spell(num)} {plural}", Fraction(num, den)
    if 0 < value < 1 and rng.random() < 0.4:
        whole = rng.randrange(1, 10**6)
        text, value = f"{spell(whole)} and {text}", whole + value
    return text, value


def random_decimal(rng: random.Random) -> tuple[str, Fraction]:
    """A spelled decimal, sometimes with a trailing scale word, with its exact value."""
    digits = "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 8)))
    spoken = " ".join(SMALL[int(digit)] for digit in digits)
    value = Fraction(int(digits), 10 ** len(digits))
    if rng.random() < 0.3:
        whole = rng.randrange(1, 1000)
        value_scale, name = rng.choice(SCALES)
        text = f"{spell(whole)} point {spoken} {name}"
        return text, (whole + value) * value_scale
    whole = rng.choice([0, rng.randrange(10**9)])
    lead = "" if whole == 0 and rng.random() < 0.3 else f"{spell(whole)} "
    return f"{lead}point {spoken}", whole + value
