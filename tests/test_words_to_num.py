import pytest

from wordsnum import WordsNumError, words_to_num


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("zero", 0),
        ("one", 1),
        ("nine", 9),
    ],
)
def test_units(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ten", 10),
        ("eleven", 11),
        ("thirteen", 13),
        ("nineteen", 19),
    ],
)
def test_teens(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("twenty", 20),
        ("forty", 40),
        ("ninety", 90),
    ],
)
def test_tens(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("one hundred", 100),
        ("two hundred fifty", 250),
        ("nine hundred ninety nine", 999),
    ],
)
def test_hundreds(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("one thousand", 1000),
        ("one thousand two hundred thirty four", 1234),
        ("one million", 1_000_000),
        ("two million three hundred thousand", 2_300_000),
        ("one billion", 1_000_000_000),
        ("one trillion", 1_000_000_000_000),
    ],
)
def test_thousands_and_scales(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("one hundred and one", 101),
        ("one thousand and five", 1005),
        ("two thousand and twenty two", 2022),
    ],
)
def test_and_is_ignored(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("twenty-one", 21),
        ("forty-two", 42),
        ("ninety-nine", 99),
        ("one hundred twenty-three", 123),
    ],
)
def test_hyphenated(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a hundred", 100),
        ("an hundred", 100),
        ("a thousand", 1000),
        ("a million", 1_000_000),
    ],
)
def test_article_scales(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("first", 1),
        ("second", 2),
        ("third", 3),
        ("fifth", 5),
        ("twelfth", 12),
        ("twentieth", 20),
        ("twenty-first", 21),
        ("hundredth", 100),
        ("two hundredth", 200),
        ("millionth", 1_000_000),
    ],
)
def test_ordinals(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("minus five", -5),
        ("negative forty two", -42),
        ("minus one hundred", -100),
    ],
)
def test_negatives(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("three point one four", 3.14),
        ("zero point five", 0.5),
        ("point five", 0.5),
        ("negative two point five", -2.5),
        ("one hundred point zero one", 100.01),
    ],
)
def test_decimals(text: str, expected: float) -> None:
    assert words_to_num(text) == pytest.approx(expected)


def test_decimal_returns_a_float() -> None:
    assert isinstance(words_to_num("one point zero"), float)


def test_integer_returns_an_int() -> None:
    assert isinstance(words_to_num("one hundred"), int)


def test_whitespace_and_commas_are_tolerated() -> None:
    assert words_to_num("  one thousand, two hundred  ") == 1200


def test_case_is_ignored() -> None:
    assert words_to_num("Two Hundred FIFTY") == 250


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "and",
        "banana",
        "two hundred banana",
        "point",
        "one point",
        "one point ten",
        "three point four point five",
        "a",
        "a five",
        "minus",
    ],
)
def test_invalid_input_raises(text: str) -> None:
    with pytest.raises(WordsNumError):
        words_to_num(text)
