"""Find every spelled-out number inside free text."""

from __future__ import annotations

from collections.abc import Sequence

from ._errors import WordsNumError
from ._forms import parse_tokens
from ._result import ParsedNumber
from ._tokens import Token, gap_ok, scan

# No real number phrase is longer than this; the cap bounds the work on hostile input.
_MAX_TOKENS = 160


def find_numbers(text: str) -> list[ParsedNumber]:
    """Return every number written in ``text``, in order, as ``ParsedNumber`` objects.

    Number words, digit groups (``"3"``, ``"2,500"``, ``"1.5"``, ``"21st"``) and their
    mixtures (``"3 million"``) are recognised, case-insensitively, when they are
    separated only by whitespace, hyphens or commas. Each match is the longest valid
    reading starting at its first word, so ``"one, two, three"`` gives three numbers
    while ``"one thousand, two hundred"`` gives one. ``start`` and ``end`` are offsets
    into ``text``.

    Everyday words that are also numbers are reported too: ``"no one"`` yields 1 and
    ``"just a second"`` yields the ordinal 2. Filter on ``kind`` or context if needed.

    >>> [match.number for match in find_numbers("I paid twenty-one pounds for 3 pies")]
    [21, 3]
    """
    found: list[ParsedNumber] = []
    for run in _runs(text, scan(text)):
        found.extend(_matches(text, run))
    return found


def _runs(text: str, tokens: Sequence[Token]) -> list[list[Token]]:
    """Group known tokens that are separated only by lenient separators."""
    runs: list[list[Token]] = []
    current: list[Token] = []
    for token in tokens:
        if not token.known:
            if current:
                runs.append(current)
            current = []
            continue
        if current and not gap_ok(text, current[-1], token):
            runs.append(current)
            current = []
        current.append(token)
    if current:
        runs.append(current)
    return runs


def _matches(text: str, run: Sequence[Token]) -> list[ParsedNumber]:
    found: list[ParsedNumber] = []
    start = 0
    while start < len(run):
        end = min(len(run), start + _MAX_TOKENS)
        while end > start:
            try:
                value, kind = parse_tokens(run[start:end])
            except WordsNumError as error:
                end = _shorter(run, start, end, error)
                continue
            first, last = run[start], run[end - 1]
            found.append(
                ParsedNumber(value, kind, text[first.start : last.end], first.start, last.end)
            )
            break
        start = max(end, start + 1)
    return found


def _shorter(run: Sequence[Token], start: int, end: int, error: WordsNumError) -> int:
    """Pick the next, shorter candidate end after a failed parse.

    Everything after the offending word is dropped at once, but the offending word
    itself is kept for one more try, since as the last word it may read differently
    ("one third" is a fraction, while "one third two" fails at "third").
    """
    for index in range(start, end - 1):
        if run[index].start == error.start:
            return index + 1
    return end - 1
