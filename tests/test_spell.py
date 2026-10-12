"""num_to_words spells integers in the canonical form."""

import pytest

from wordsnum import num_to_words


@pytest.mark.parametrize(
    ("number", "kwargs", "expected"),
    [
        (0, {}, "zero"),
        (7, {}, "seven"),
        (21, {}, "twenty-one"),
        (100, {}, "one hundred"),
        (101, {}, "one hundred one"),
        (101, {"british": True}, "one hundred and one"),
        (1005, {"british": True}, "one thousand and five"),
        (1100, {"british": True}, "one thousand one hundred"),
        (2_000_022, {"british": True}, "two million and twenty-two"),
        (1234, {}, "one thousand two hundred thirty-four"),
        (-42, {}, "minus forty-two"),
        (10**33, {}, "one decillion"),
        (10**66 - 1, {}, None),
        (1, {"ordinal": True}, "first"),
        (12, {"ordinal": True}, "twelfth"),
        (20, {"ordinal": True}, "twentieth"),
        (0, {"ordinal": True}, "zeroth"),
        (103, {"ordinal": True, "british": True}, "one hundred and third"),
        (1000, {"ordinal": True}, "one thousandth"),
        (99, {"ordinal": True}, "ninety-ninth"),
    ],
)
def test_spellings(number: int, kwargs: dict[str, bool], expected: str | None) -> None:
    words = num_to_words(number, **kwargs)
    if expected is None:
        assert words.startswith("nine hundred ninety-nine vigintillion")
    else:
        assert words == expected


@pytest.mark.parametrize("number", [10**66, -(10**66)])
def test_out_of_range_raises_value_error(number: int) -> None:
    with pytest.raises(ValueError):
        num_to_words(number)


def test_negative_ordinals_raise_value_error() -> None:
    with pytest.raises(ValueError):
        num_to_words(-1, ordinal=True)


@pytest.mark.parametrize("value", [True, 1.0, "1", None])
def test_non_ints_raise_type_error(value: object) -> None:
    with pytest.raises(TypeError):
        num_to_words(value)  # type: ignore[arg-type]
