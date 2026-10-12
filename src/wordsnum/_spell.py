"""Spell an integer in English words, the inverse of the parser for whole numbers."""

from __future__ import annotations

from ._vocab import LARGEST_SCALE, SCALE_WORDS, TENS_WORDS, UNIT_WORDS, ordinal_of


def num_to_words(number: int, *, ordinal: bool = False, british: bool = False) -> str:
    """Spell ``number`` in canonical English words.

    The output is exactly the canonical form that ``parse(..., strict=True)`` accepts,
    so ``words_to_num(num_to_words(n)) == n`` for every supported ``n``, and the same
    holds with ``ordinal=True`` (the result parses as an ordinal of value ``n``).

    Args:
        number: An ``int`` whose absolute value is below 10**66 (one thousand
            vigintillion). ``bool`` is rejected.
        ordinal: Spell the ordinal (``"twenty-first"``) instead of the cardinal.
        british: Insert ``"and"`` the British way, after ``"hundred"`` and before a
            final group below one hundred (``"one thousand and five"``).

    Raises:
        TypeError: ``number`` is not an ``int``.
        ValueError: ``number`` is out of range, or negative with ``ordinal=True``.

    >>> num_to_words(1234)
    'one thousand two hundred thirty-four'
    >>> num_to_words(101, british=True)
    'one hundred and one'
    >>> num_to_words(21, ordinal=True)
    'twenty-first'
    """
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError(f"num_to_words() needs an int, got {type(number).__name__}")
    if abs(number) >= LARGEST_SCALE * 1000:
        raise ValueError("num_to_words() supports absolute values below 10**66")
    if number < 0 and ordinal:
        raise ValueError("an ordinal cannot be negative")
    words = _cardinal(abs(number), british=british)
    if ordinal:
        words = _to_ordinal(words)
    return f"minus {words}" if number < 0 else words


def _cardinal(number: int, *, british: bool) -> str:
    if number == 0:
        return "zero"
    groups: list[int] = []
    while number:
        number, group = divmod(number, 1000)
        groups.append(group)
    parts: list[str] = []
    for power in range(len(groups) - 1, -1, -1):
        group = groups[power]
        if not group:
            continue
        if british and power == 0 and parts and group < 100:
            parts.append("and")
        parts.append(_group(group, british=british))
        if power:
            parts.append(SCALE_WORDS[power - 1])
    return " ".join(parts)


def _group(number: int, *, british: bool) -> str:
    hundreds, rest = divmod(number, 100)
    parts: list[str] = []
    if hundreds:
        parts += [UNIT_WORDS[hundreds], "hundred"]
        if rest and british:
            parts.append("and")
    if rest:
        parts.append(_below_hundred(rest))
    return " ".join(parts)


def _below_hundred(number: int) -> str:
    if number < 20:
        return UNIT_WORDS[number]
    tens, unit = divmod(number, 10)
    word = TENS_WORDS[tens - 2]
    return f"{word}-{UNIT_WORDS[unit]}" if unit else word


def _to_ordinal(words: str) -> str:
    head, space, last = words.rpartition(" ")
    stem, hyphen, unit = last.rpartition("-")
    last = f"{stem}{hyphen}{ordinal_of(unit)}"
    return f"{head}{space}{last}"
