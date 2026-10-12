"""Fractions, decimals, ordinals, digits and exact results."""

from decimal import Decimal, localcontext
from fractions import Fraction

import pytest

from wordsnum import MisplacedWordError, parse, words_to_decimal, words_to_fraction, words_to_num


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a half", Fraction(1, 2)),
        ("one half", Fraction(1, 2)),
        ("three quarters", Fraction(3, 4)),
        ("a quarter", Fraction(1, 4)),
        ("three fourths", Fraction(3, 4)),
        ("two thirds", Fraction(2, 3)),
        ("one third", Fraction(1, 3)),
        ("five eighths", Fraction(5, 8)),
        ("seven hundredths", Fraction(7, 100)),
        ("a hundredth", Fraction(1, 100)),
        ("a millionth", Fraction(1, 1_000_000)),
        ("three thirty-seconds", Fraction(3, 32)),
        ("a twenty-first", Fraction(1, 21)),
        ("twenty ninths", Fraction(20, 9)),
        ("twenty-ninths", None),
        ("four halves", Fraction(2)),
        ("zero thirds", Fraction(0)),
        ("one and a half", Fraction(3, 2)),
        ("two and three quarters", Fraction(11, 4)),
        ("one hundred and one third", Fraction(301, 3)),
        ("one hundred and one thirds", Fraction(101, 3)),
        ("two hundred and fifty thirds", Fraction(250, 3)),
        ("minus one and a half", Fraction(-3, 2)),
        ("3 quarters", Fraction(3, 4)),
    ],
)
def test_fractions(text: str, expected: Fraction | None) -> None:
    if expected is None:
        with pytest.raises(MisplacedWordError):
            parse(text)
        return
    result = parse(text)
    assert (result.value, result.kind) == (expected, "fraction")
    assert isinstance(words_to_num(text), float)


@pytest.mark.parametrize(
    "text", ["one thirds", "two third", "two quarter", "thirds", "half", "a seconds", "1.5 thirds"]
)
def test_malformed_fractions(text: str) -> None:
    with pytest.raises(MisplacedWordError):
        parse(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("first", 1),
        ("zeroth", 0),
        ("twenty-first", 21),
        ("one hundred and first", 101),
        ("one hundredth", 100),
        ("two hundredth", 200),
        ("thirty-second", 32),
        ("one decillionth", 10**33),
        ("a millionth", None),
        ("21st", 21),
        ("2nd", 2),
        ("103rd", 103),
        ("111th", 111),
    ],
)
def test_ordinals(text: str, expected: int | None) -> None:
    result = parse(text)
    if expected is None:
        assert result.kind == "fraction"
        return
    assert (result.value, result.kind, result.number) == (expected, "ordinal", expected)


@pytest.mark.parametrize("text", ["11st", "2th", "21th", "13rd"])
def test_digit_ordinals_need_the_right_suffix(text: str) -> None:
    with pytest.raises(ValueError):
        parse(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("three point one four", Fraction(314, 100)),
        ("point five", Fraction(1, 2)),
        ("one point oh five", Fraction(105, 100)),
        ("two point five million", Fraction(2_500_000)),
        ("nine point nine nine hundred", Fraction(999)),
        ("minus zero point two", Fraction(-1, 5)),
        ("1.5 billion", Fraction(1_500_000_000)),
        ("3.14", Fraction(314, 100)),
        ("1,234.5", Fraction(24690, 20)),
    ],
)
def test_decimals(text: str, expected: Fraction) -> None:
    result = parse(text)
    assert (result.value, result.kind) == (expected, "decimal")
    assert isinstance(result.number, float)


def test_digit_groups() -> None:
    assert words_to_num("42") == 42
    assert words_to_num("2,500") == 2500
    assert words_to_num("3 million") == 3_000_000
    assert words_to_num("5 hundred") == 500
    assert words_to_num("1 million two hundred") == 1_000_200
    with pytest.raises(MisplacedWordError):
        words_to_num("250 thousand and 3")


def test_exact_results() -> None:
    assert words_to_fraction("zero point one") == Fraction(1, 10)
    assert words_to_decimal("one point one") == Decimal("1.1")
    assert words_to_decimal("seven hundredths") == Decimal("0.07")
    assert words_to_decimal("one decillion and one") == Decimal(10**33 + 1)
    assert words_to_decimal("one decillion point five") == Decimal("1" + "0" * 33 + ".5")
    assert words_to_decimal("minus three quarters") == Decimal("-0.75")
    with localcontext() as context:
        context.prec = 5
        assert words_to_decimal("two thirds") == Decimal("0.66667")


def test_return_types() -> None:
    assert type(words_to_num("one hundred")) is int
    assert type(words_to_num("twenty-first")) is int
    assert type(words_to_num("one point zero")) is float
    assert type(words_to_num("a half")) is float


def test_a_leading_minus_on_digits_is_a_sign() -> None:
    assert words_to_num("-5") == -5
    assert words_to_num("-1.5 million") == -1_500_000.0
    assert words_to_num("-2,500") == -2500


def test_halves_is_the_only_plural_of_half() -> None:
    assert words_to_num("two halves") == 1.0
    with pytest.raises(ValueError):
        words_to_num("two halfs")


def test_values_too_large_for_a_float_raise_a_words_num_error() -> None:
    from wordsnum import WordsNumError

    huge = "9" * 300 + ".5 vigintillion"
    with pytest.raises(WordsNumError, match="too large"):
        words_to_num(huge)
    assert words_to_fraction(huge) == (Fraction("9" * 300) + Fraction(1, 2)) * 10**63
