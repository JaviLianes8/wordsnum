"""Parse spelled-out English numbers into int or float."""

from __future__ import annotations

from ._vocab import ADDENDS, ARTICLES, DIGITS, IGNORED, MULTIPLIERS, POINT, SIGNS


class WordsNumError(ValueError):
    """Raised when the text is not a valid spelled-out number."""


def words_to_num(text: str) -> int | float:
    """Convert spelled-out English to an int, or a float when it has a decimal part."""
    tokens = _tokenize(text)
    if not tokens:
        raise WordsNumError("no number words found in the input")
    sign, tokens = _take_sign(tokens)
    _check_articles(tokens)
    value: int | float = _parse_decimal(tokens) if POINT in tokens else _parse_integer(tokens)
    return sign * value


def _tokenize(text: str) -> list[str]:
    cleaned = text.lower().replace("-", " ").replace(",", " ")
    return [word for word in cleaned.split() if word not in IGNORED]


def _take_sign(tokens: list[str]) -> tuple[int, list[str]]:
    first = tokens[0]
    if first in SIGNS:
        rest = tokens[1:]
        if not rest:
            raise WordsNumError("a sign word needs a number after it")
        return SIGNS[first], rest
    return 1, tokens


def _check_articles(tokens: list[str]) -> None:
    for index, token in enumerate(tokens):
        if token in ARTICLES:
            following = tokens[index + 1] if index + 1 < len(tokens) else None
            if following not in MULTIPLIERS:
                raise WordsNumError(f"{token!r} must be followed by a scale word")


def _parse_integer(tokens: list[str]) -> int:
    total = 0
    current = 0
    for token in tokens:
        if token in MULTIPLIERS:
            multiplier = MULTIPLIERS[token]
            if multiplier == 100:
                current = (current or 1) * multiplier
            else:
                total += (current or 1) * multiplier
                current = 0
        elif token in ADDENDS:
            current += ADDENDS[token]
        else:
            raise WordsNumError(f"unexpected word: {token!r}")
    return total + current


def _parse_decimal(tokens: list[str]) -> float:
    point = tokens.index(POINT)
    if POINT in tokens[point + 1 :]:
        raise WordsNumError("more than one decimal point")
    whole_tokens = tokens[:point]
    fraction_tokens = tokens[point + 1 :]
    if not fraction_tokens:
        raise WordsNumError("no digits after the decimal point")
    whole = _parse_integer(whole_tokens) if whole_tokens else 0
    digits = ""
    for token in fraction_tokens:
        if token not in DIGITS:
            raise WordsNumError(f"expected a single digit after the point, got {token!r}")
        digits += str(DIGITS[token])
    return float(f"{whole}.{digits}")
