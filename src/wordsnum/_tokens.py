"""Split text into number tokens with their offsets, and check what lies between them."""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from itertools import pairwise
from typing import NoReturn

from ._errors import MisplacedWordError, UnknownWordError, WordsNumError
from ._vocab import ARTICLES, COMPOUND_PLURALS, ORDINALS, TENS, UNITS, VOCABULARY

_TOKEN = re.compile(
    r"(?:(?<![^\s(])-)?"  # a minus sign glued to digits at the start of a word: -5
    r"(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?"  # 2,500 or 1,234.5
    r"|\d+(?:\.\d+)?(?:st|nd|rd|th)?)"  # 42, 3.14, 21st
    r"|[A-Za-z]+",
    re.IGNORECASE | re.ASCII,
)
_DIGITS = re.compile(r"-?[\d,]+(?:\.\d+)?", re.ASCII)
# Longer digit runs are not numbers anyone writes, and Python refuses to convert them.
MAX_DIGITS = 1000
_ORDINAL_DIGITS = re.compile(r"(\d+)(st|nd|rd|th)", re.ASCII)
_LENIENT_GAP = re.compile(r"[\s,\-]*")
_LENIENT_EDGE = re.compile(r"\s*")


@dataclass(frozen=True)
class Token:
    """One word or digit group: lowercased ``word``, the ``raw`` text and its offsets."""

    word: str
    raw: str
    start: int
    end: int
    hyphen_before: bool

    @property
    def number(self) -> Fraction | None:
        """The value of a plain digit token such as ``2,500`` or ``1.5``, else ``None``."""
        if len(self.word) > MAX_DIGITS or _DIGITS.fullmatch(self.word) is None:
            return None
        return Fraction(self.word.replace(",", ""))

    @property
    def digit_ordinal(self) -> int | None:
        """The value of a digit ordinal with the right suffix (``21st``), else ``None``."""
        match = _ORDINAL_DIGITS.fullmatch(self.word)
        if match is None or len(self.word) > MAX_DIGITS:
            return None
        value = int(match.group(1))
        return value if match.group(2) == _suffix(value) else None

    @property
    def known(self) -> bool:
        """Whether this token can be part of a number."""
        if self.word in VOCABULARY:
            return True
        return self.number is not None or self.digit_ordinal is not None


def _suffix(value: int) -> str:
    if value % 100 in (11, 12, 13):
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")


def scan(text: str) -> list[Token]:
    """Find every candidate token in ``text`` without validating anything."""
    tokens: list[Token] = []
    previous_end = 0
    for match in _TOKEN.finditer(text):
        gap = text[previous_end : match.start()]
        raw = match.group()
        tokens.append(Token(raw.lower(), raw, match.start(), match.end(), "-" in gap))
        previous_end = match.end()
    return tokens


def gap_ok(text: str, left: Token, right: Token) -> bool:
    """Whether the text between two tokens is a lenient separator."""
    return _LENIENT_GAP.fullmatch(text, left.end, right.start) is not None


def tokenize(text: str, *, strict: bool) -> list[Token]:
    """Tokenize a whole string that must contain one number and nothing else."""
    tokens = scan(text)
    if not tokens:
        stray = text.strip()
        if stray:
            start = text.index(stray[0])
            raise UnknownWordError(
                f"unexpected text: {stray!r}", word=stray, start=start, end=len(text.rstrip())
            )
        raise WordsNumError("no number words found in the input")
    for token in tokens:
        if not token.known:
            raise UnknownWordError(
                f"unexpected word: {token.raw!r} at position {token.start}",
                word=token.raw,
                start=token.start,
                end=token.end,
            )
    _check_edges(text, tokens, strict=strict)
    for left, right in pairwise(tokens):
        _check_gap(text, left, right, strict=strict)
    if strict:
        for token, following in zip(tokens, [*tokens[1:], None], strict=True):
            if token.raw != token.word:
                _misplaced(token, "strict mode needs lowercase words")
            if token.word in ARTICLES and following is not None:
                article = "an" if following.word[0] in "aeiou" else "a"
                if token.word != article:
                    _misplaced(token, f"strict mode needs {article!r} before {following.raw!r}")
    return tokens


def _check_edges(text: str, tokens: list[Token], *, strict: bool) -> None:
    head, tail = text[: tokens[0].start], text[tokens[-1].end :]
    for edge, start in ((head, 0), (tail, tokens[-1].end)):
        if edge and (strict or _LENIENT_EDGE.fullmatch(edge) is None):
            _stray(edge, start)


def _check_gap(text: str, left: Token, right: Token, *, strict: bool) -> None:
    gap = text[left.end : right.start]
    if not strict:
        if _LENIENT_GAP.fullmatch(gap) is None:
            _stray(gap, left.end)
        return
    if left.word in TENS and right.word in COMPOUND_PLURALS and gap in (" ", "-"):
        return  # "twenty ninths" is 20/9 and "twenty-ninths" is a plural 1/29: both valid
    joins_tens = left.word in TENS and 1 <= UNITS.get(ORDINALS.get(right.word, right.word), 0) <= 9
    if gap == ("-" if joins_tens else " "):
        return
    expected = "a hyphen" if joins_tens else "a single space"
    _misplaced(right, f"strict mode needs {expected} before {right.raw!r}")


def _stray(gap: str, offset: int) -> NoReturn:
    stripped = gap.strip() or gap
    start = offset + gap.index(stripped)
    raise UnknownWordError(
        f"unexpected text: {stripped!r} at position {start}",
        word=stripped,
        start=start,
        end=start + len(stripped),
    )


def _misplaced(token: Token, reason: str) -> NoReturn:
    raise MisplacedWordError(
        f"{reason} (at position {token.start})", word=token.raw, start=token.start, end=token.end
    )
