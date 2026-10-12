"""Seeded round trips against the independent oracle in ``_oracle.py``."""

import random
from fractions import Fraction

import pytest
from _oracle import (
    LIMIT,
    ordinalize,
    random_decimal,
    random_fraction,
    random_int,
    scramble,
    spell,
)

from wordsnum import num_to_words, parse, words_to_fraction, words_to_num

CASES = 3000


def _ints(seed: int) -> list[int]:
    rng = random.Random(seed)
    return [random_int(rng) for _ in range(CASES)] + [0, 1, LIMIT - 1, 10**33, 10**63]


@pytest.mark.parametrize("british", [False, True])
def test_oracle_cardinals_parse_back_exactly_in_strict_mode(british: bool) -> None:
    for number in _ints(1):
        words = spell(number, british=british)
        result = parse(words, strict=True)
        assert (result.value, result.kind) == (number, "cardinal"), words


def test_oracle_ordinals_parse_back_exactly_in_strict_mode() -> None:
    for number in _ints(2):
        words = ordinalize(spell(number))
        result = parse(words, strict=True)
        assert (result.value, result.kind) == (number, "ordinal"), words


def test_negative_oracle_cardinals_parse_back() -> None:
    for number in _ints(3)[:500]:
        if number:
            assert words_to_num(f"minus {spell(number)}", strict=True) == -number


def test_lenient_scrambles_parse_to_the_same_value() -> None:
    rng = random.Random(4)
    for number in _ints(4):
        words = scramble(spell(number, british=rng.random() < 0.5), rng)
        assert words_to_num(words) == number, repr(words)


def test_scrambled_text_is_rejected_in_strict_mode_unless_canonical() -> None:
    rng = random.Random(5)
    for number in _ints(5)[:1000]:
        canonical = spell(number)
        words = scramble(canonical, rng)
        if words != canonical:
            with pytest.raises(ValueError):
                parse(words, strict=True)


@pytest.mark.parametrize("british", [False, True])
def test_num_to_words_matches_the_oracle(british: bool) -> None:
    for number in _ints(6):
        assert num_to_words(number, british=british) == spell(number, british=british)
        assert num_to_words(number, ordinal=True) == ordinalize(spell(number))
        if number:
            assert num_to_words(-number) == f"minus {spell(number)}"


def test_num_to_words_round_trips_through_the_parser() -> None:
    for number in _ints(7):
        for british in (False, True):
            assert words_to_num(num_to_words(number, british=british), strict=True) == number
            ordinal = parse(num_to_words(number, ordinal=True, british=british), strict=True)
            assert (ordinal.value, ordinal.kind) == (number, "ordinal")


def test_oracle_fractions_parse_back_exactly() -> None:
    rng = random.Random(8)
    for _ in range(CASES):
        words, value = random_fraction(rng)
        result = parse(words, strict=True)
        assert (result.value, result.kind) == (value, "fraction"), words


def test_oracle_decimals_parse_back_exactly() -> None:
    rng = random.Random(9)
    for _ in range(CASES):
        words, value = random_decimal(rng)
        assert words_to_fraction(words, strict=True) == value, words
        assert parse(words).kind == "decimal"


def test_digit_groups_mixed_with_scale_words() -> None:
    rng = random.Random(10)
    for _ in range(1000):
        count = rng.randrange(1, 1000)
        power = rng.randrange(1, 22)
        name = spell(1000**power).split(" ")[1]
        assert words_to_num(f"{count:,} {name}") == count * 1000**power
        assert words_to_fraction(f"{count}.5 {name}") == (count + Fraction(1, 2)) * 1000**power
