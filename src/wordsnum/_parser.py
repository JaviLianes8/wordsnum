"""Parse a string that holds exactly one spelled-out English number."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

from ._errors import WordsNumError
from ._forms import parse_tokens
from ._result import ParsedNumber
from ._tokens import tokenize

__all__ = ["WordsNumError", "parse", "words_to_decimal", "words_to_fraction", "words_to_num"]


def parse(text: str, *, strict: bool = False) -> ParsedNumber:
    """Parse ``text`` as one number and return a ``ParsedNumber``.

    The whole string must be a single number; surrounding whitespace is allowed in
    lenient mode. Use ``find_numbers`` to pull numbers out of free text.

    Args:
        text: The number, such as ``"two thousand and twenty-one"``.
        strict: When ``False`` (the default) case, runs of whitespace, hyphens and
            commas between words are tolerated. When ``True`` only the canonical
            spelling is accepted: lowercase words, single spaces, a hyphen exactly
            between a tens word and a unit word, and no commas between words. Neither
            mode guesses misspelled words.

    Raises:
        UnknownWordError: A word is not a number word (``"banana"``, ``"fourty"``).
        MisplacedWordError: Number words appear in an order the grammar rejects.
        WordsNumError: The text holds no number words at all.

    >>> parse("three quarters").value
    Fraction(3, 4)
    >>> parse("twenty-first").kind
    'ordinal'
    """
    tokens = tokenize(text, strict=strict)
    value, kind = parse_tokens(tokens)
    start, end = tokens[0].start, tokens[-1].end
    return ParsedNumber(value, kind, text[start:end], start, end)


def words_to_num(text: str, *, strict: bool = False) -> int | float:
    """Convert spelled-out English to an ``int``, or a ``float`` when it is not whole.

    Cardinals and ordinals return ``int`` (``"twenty-first"`` is 21). Decimals and
    fractions return ``float`` (``"three point one four"`` is 3.14, ``"a half"`` is
    0.5). Use ``words_to_fraction`` or ``words_to_decimal`` for exact results.

    Args:
        text: The number, such as ``"one hundred and one"`` or ``"3 million"``.
        strict: Accept only the canonical spelling; see ``parse``.

    Raises:
        WordsNumError: The text is not a valid number (see ``parse`` for subclasses).

    >>> words_to_num("two million three hundred thousand")
    2300000
    >>> words_to_num("minus two point five")
    -2.5
    """
    return parse(text, strict=strict).number


def words_to_fraction(text: str, *, strict: bool = False) -> Fraction:
    """Convert spelled-out English to an exact ``Fraction``.

    >>> words_to_fraction("two and three quarters")
    Fraction(11, 4)
    >>> words_to_fraction("zero point one")
    Fraction(1, 10)
    """
    return parse(text, strict=strict).value


def words_to_decimal(text: str, *, strict: bool = False) -> Decimal:
    """Convert spelled-out English to a ``Decimal``.

    Exact for every cardinal, ordinal and decimal (``"one point one"`` is
    ``Decimal('1.1')``). A fraction without a terminating expansion, such as
    ``"two thirds"``, is rounded to the precision of the current ``decimal`` context.

    >>> words_to_decimal("one point one")
    Decimal('1.1')
    >>> words_to_decimal("seven hundredths")
    Decimal('0.07')
    """
    return parse(text, strict=strict).to_decimal()
