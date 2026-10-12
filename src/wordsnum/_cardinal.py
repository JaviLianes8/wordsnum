"""Grammar for cardinal numbers: groups below a thousand joined by decreasing scales."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from typing import NoReturn

from ._errors import MisplacedWordError
from ._tokens import Token
from ._vocab import AND, ARTICLES, HUNDRED, SCALES, TENS, UNITS


def fail(token: Token, reason: str) -> NoReturn:
    """Raise a ``MisplacedWordError`` that points at ``token``."""
    raise MisplacedWordError(
        f"{reason}: {token.raw!r} at position {token.start}",
        word=token.raw,
        start=token.start,
        end=token.end,
    )


@dataclass
class _Reader:
    tokens: Sequence[Token]
    index: int = 0
    decimal: bool = field(default=False)

    def peek(self) -> Token | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def word(self) -> str | None:
        token = self.peek()
        return None if token is None else token.word

    def take(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token


def parse_cardinal(tokens: Sequence[Token]) -> tuple[Fraction, bool]:
    """Parse a whole cardinal. Returns the value and whether a decimal digit group was used.

    ``tokens`` must be non-empty and must not hold a sign word.
    """
    if len(tokens) == 1 and tokens[0].word == "zero":
        return Fraction(0), False
    reader = _Reader(tokens)
    total = Fraction(0)
    last_scale = 0
    while True:
        group_token = reader.peek()
        assert group_token is not None
        value, wide = _group(reader, first=last_scale == 0)
        if last_scale and value >= 1000:
            fail(group_token, "a group after a scale word must be below a thousand")
        scale_token = reader.peek()
        if scale_token is None:
            if wide and last_scale:
                fail(group_token, "a teen or tens hundred cannot follow a scale word")
            return total + value, reader.decimal
        if scale_token.word not in SCALES:
            fail(scale_token, "unexpected word")
        scale = SCALES[scale_token.word]
        if last_scale and scale >= last_scale:
            fail(scale_token, "scale words must get smaller from left to right")
        if wide:
            fail(scale_token, "a teen or tens hundred cannot take a scale word")
        if value == 0:
            fail(scale_token, "a scale word needs a non-zero number before it")
        reader.take()
        total += value * scale
        last_scale = scale
        if reader.peek() is None:
            return total, reader.decimal
        if reader.word() == AND:
            and_token = reader.take()
            target = reader.peek() or and_token
            rest = _below_hundred(reader)
            if not rest:
                fail(target, "'and' after a scale word needs 1 to 99")
            if (extra := reader.peek()) is not None:
                fail(extra, "nothing may follow the number after 'and'")
            return total + rest, reader.decimal


def _group(reader: _Reader, *, first: bool) -> tuple[Fraction, bool]:
    """Read one group. Returns its value and whether it is a wide ``nineteen hundred``."""
    token = reader.peek()
    assert token is not None
    if token.word in SCALES and first:
        return Fraction(1), False
    if token.word in ARTICLES:
        reader.take()
        following = reader.word()
        if following in SCALES:
            return Fraction(1), False
        if following != HUNDRED:
            fail(token, "an article must be followed by 'hundred' or a scale word")
        return _hundreds(reader, Fraction(1)), False
    if token.word == HUNDRED and first:
        return _hundreds(reader, Fraction(1)), False
    number = token.number
    if number is not None:
        reader.take()
        if "." in token.word:
            if not first:
                fail(token, "digits with a decimal point must start the number")
            reader.decimal = True
            after = reader.peek()
            if after is not None and after.word not in SCALES:
                fail(after, "digits with a decimal point can only take a scale word")
            return number, False
        if reader.word() != HUNDRED:
            return number, False
        prefix = number
    else:
        below = _below_hundred(reader)
        if below is None:
            fail(token, "unexpected word")
        if below == 0:
            fail(token, "'zero' must stand alone")
        prefix = Fraction(below)
        if reader.word() != HUNDRED:
            return prefix, False
    if not 1 <= prefix <= 99:
        fail(token, "'hundred' needs a number from 1 to 99 before it")
    return _hundreds(reader, prefix), prefix >= 10


def _hundreds(reader: _Reader, prefix: Fraction) -> Fraction:
    reader.take()
    value = prefix * 100
    if reader.word() == AND:
        and_token = reader.take()
        target = reader.peek() or and_token
        rest = _below_hundred(reader)
        if not rest:
            fail(target, "'and' after 'hundred' needs 1 to 99")
        return value + rest
    rest = _below_hundred(reader)
    if rest == 0:
        fail(reader.tokens[reader.index - 1], "'zero' must stand alone")
    return value + (rest or 0)


def _below_hundred(reader: _Reader) -> int | None:
    word = reader.word()
    if word in UNITS:
        reader.take()
        return UNITS[word]
    if word in TENS:
        reader.take()
        unit = reader.word()
        if unit in UNITS and 1 <= UNITS[unit] <= 9:
            reader.take()
            return TENS[word] + UNITS[unit]
        return TENS[word]
    return None
