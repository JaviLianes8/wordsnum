"""Top-level number forms: signs, decimals, fractions, ordinals and plain cardinals."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from fractions import Fraction
from typing import Literal

from ._cardinal import fail, parse_cardinal
from ._errors import WordsNumError
from ._tokens import Token
from ._vocab import (
    AND,
    ARTICLES,
    COMPOUND_PLURALS,
    DENOMINATORS,
    HUNDRED,
    ORDINALS,
    PLURAL_DENOMINATORS,
    POINT,
    POINT_DIGITS,
    SCALES,
    SIGNS,
    TENS,
    UNITS,
)

Kind = Literal["cardinal", "ordinal", "decimal", "fraction"]
_SCALE_ORDINALS = frozenset(word for word, base in ORDINALS.items() if base in SCALES)
_SCALE_ORDINALS |= {"hundredth"}


def parse_tokens(tokens: Sequence[Token]) -> tuple[Fraction, Kind]:
    """Parse one complete number from a non-empty token list."""
    sign = 1
    if tokens[0].word.startswith("-"):
        first = tokens[0]
        unsigned = replace(first, word=first.word[1:], raw=first.raw[1:], start=first.start + 1)
        sign, tokens = -1, [unsigned, *tokens[1:]]
    elif tokens[0].word in SIGNS:
        if len(tokens) == 1:
            fail(tokens[0], "a sign word needs a number after it")
        sign, tokens = -1, tokens[1:]
    for token in tokens:
        if token.word in SIGNS or token.word.startswith("-"):
            fail(token, "a sign can only come first")
    value, kind = _unsigned(tokens)
    if sign < 0 and kind == "ordinal":
        fail(tokens[0], "an ordinal cannot be negative")
    return sign * value, kind


def _unsigned(tokens: Sequence[Token]) -> tuple[Fraction, Kind]:
    if any(token.word == POINT for token in tokens):
        return _decimal(tokens), "decimal"
    last = tokens[-1]
    if last.digit_ordinal is not None:
        if len(tokens) > 1:
            fail(last, "a digit ordinal must stand alone")
        return Fraction(last.digit_ordinal), "ordinal"
    fraction = _fraction(tokens)
    if fraction is not None:
        return fraction, "fraction"
    if last.word in ORDINALS:
        cardinal = replace(last, word=ORDINALS[last.word])
        value, decimal = parse_cardinal([*tokens[:-1], cardinal])
        if decimal:
            fail(last, "an ordinal cannot have a decimal part")
        return value, "ordinal"
    value, decimal = parse_cardinal(tokens)
    return value, "decimal" if decimal else "cardinal"


def _decimal(tokens: Sequence[Token]) -> Fraction:
    point = next(index for index, token in enumerate(tokens) if token.word == POINT)
    whole_tokens, rest = tokens[:point], tokens[point + 1 :]
    digits = ""
    while len(digits) < len(rest) and rest[len(digits)].word in POINT_DIGITS:
        digits += str(POINT_DIGITS[rest[len(digits)].word])
    if not digits:
        fail(rest[0] if rest else tokens[point], "expected a digit word after 'point'")
    tail = rest[len(digits) :]
    scale = 1
    if tail:
        scale_word = tail[0].word
        if scale_word not in SCALES and scale_word != HUNDRED:
            fail(tail[0], "only one-digit words or a final scale word may follow 'point'")
        if len(tail) > 1:
            fail(tail[1], "nothing may follow the scale word of a decimal")
        scale = SCALES.get(scale_word, 100)
    whole = Fraction(0)
    if whole_tokens:
        whole, decimal = parse_cardinal(whole_tokens)
        if decimal:
            fail(tokens[point], "digits with a decimal point cannot be followed by 'point'")
        if tail and whole >= 1000:
            fail(tail[0], "a decimal with a scale word needs a whole part below a thousand")
    return (whole + Fraction(int(digits), 10 ** len(digits))) * scale


def _fraction(tokens: Sequence[Token]) -> Fraction | None:
    """Parse ``tokens`` as a fraction, or return ``None`` when they do not end in one."""
    found = _denominator(tokens)
    if found is None:
        return None
    numerator_tokens, denominator, plural = found
    last = tokens[-1]
    if not numerator_tokens:
        fail(last, "a fraction needs a numerator before its denominator")
    and_at = [index for index, token in enumerate(numerator_tokens) if token.word == AND]
    if and_at and and_at[-1] > 0:
        whole_tokens, part_tokens = (
            numerator_tokens[: and_at[-1]],
            numerator_tokens[and_at[-1] + 1 :],
        )
        try:
            whole = _whole(whole_tokens)
            part = _numerator(part_tokens, last, plural)
        except WordsNumError:
            pass
        else:
            if part < denominator:
                return whole + Fraction(part, denominator)
    return Fraction(_numerator(numerator_tokens, last, plural), denominator)


def _denominator(tokens: Sequence[Token]) -> tuple[Sequence[Token], int, bool] | None:
    """Split off a denominator. Returns numerator tokens, denominator and plurality."""
    last, word = tokens[-1], tokens[-1].word
    before = tokens[-2].word if len(tokens) > 1 else None
    if last.hyphen_before and before in TENS:
        unit = COMPOUND_PLURALS.get(word, word)
        if unit in ORDINALS and 1 <= UNITS.get(ORDINALS[unit], 0) <= 9:
            value = TENS[before] + UNITS[ORDINALS[unit]]
            plural = word in COMPOUND_PLURALS
            numerator = tokens[:-2]
            if plural or _single_one(numerator, allow_one=True):
                return numerator, value, plural
            return None
    if word in PLURAL_DENOMINATORS:
        return tokens[:-1], DENOMINATORS[PLURAL_DENOMINATORS[word]], True
    if word in ("half", "quarter"):
        return tokens[:-1], DENOMINATORS[word], False
    if word in DENOMINATORS and _single_one(tokens[:-1], allow_one=word not in _SCALE_ORDINALS):
        return tokens[:-1], DENOMINATORS[word], False
    return None


def _single_one(numerator: Sequence[Token], *, allow_one: bool) -> bool:
    """Whether the numerator ends in "a"/"an" (or "one") as a whole or after "and"."""
    if not numerator:
        return False
    if len(numerator) > 1 and numerator[-2].word != AND:
        return False
    last = numerator[-1].word
    return last in ARTICLES or (allow_one and last == "one")


def _whole(tokens: Sequence[Token]) -> int:
    value, decimal = parse_cardinal(tokens)
    if decimal:
        fail(tokens[-1], "the whole part of a mixed number must be an integer")
    return int(value)


def _numerator(tokens: Sequence[Token], denominator: Token, plural: bool) -> int:
    if not tokens:
        fail(denominator, "a fraction needs a numerator before its denominator")
    if len(tokens) == 1 and tokens[0].word in ARTICLES:
        value = 1
    else:
        number, decimal = parse_cardinal(tokens)
        if decimal or number.denominator != 1:
            fail(tokens[-1], "a numerator must be a whole number")
        value = int(number)
    if value == 1 and plural:
        fail(denominator, "a numerator of one takes a singular denominator")
    if value != 1 and not plural:
        fail(denominator, "a numerator other than one takes a plural denominator")
    return value
