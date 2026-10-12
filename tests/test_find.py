"""find_numbers locates every number in free text with exact spans."""

import random

from _oracle import random_int, spell

from wordsnum import ParsedNumber, find_numbers


def _summary(text: str) -> list[tuple[str, object, str]]:
    return [(match.text, match.number, match.kind) for match in find_numbers(text)]


def test_spans_slice_back_to_the_matched_text() -> None:
    text = "We sold twenty-one boxes, then 3 million more, and a half on the 21st."
    matches = find_numbers(text)
    assert [text[match.start : match.end] for match in matches] == [m.text for m in matches]
    assert _summary(text) == [
        ("twenty-one", 21, "cardinal"),
        ("3 million", 3_000_000, "cardinal"),
        ("a half", 0.5, "fraction"),
        ("21st", 21, "ordinal"),
    ]


def test_longest_valid_reading_wins() -> None:
    assert _summary("one thousand, two hundred apples") == [
        ("one thousand, two hundred", 1200, "cardinal")
    ]
    assert _summary("one, two, three") == [
        ("one", 1, "cardinal"),
        ("two", 2, "cardinal"),
        ("three", 3, "cardinal"),
    ]
    assert _summary("one third two") == [("one third", 1 / 3, "fraction"), ("two", 2, "cardinal")]
    assert _summary("one and two") == [("one", 1, "cardinal"), ("two", 2, "cardinal")]


def test_decimals_negatives_and_digits_in_text() -> None:
    assert _summary("it fell minus two point five degrees to 3.14, then 2,500") == [
        ("minus two point five", -2.5, "decimal"),
        ("3.14", 3.14, "decimal"),
        ("2,500", 2500, "cardinal"),
    ]


def test_no_numbers_gives_an_empty_list() -> None:
    assert find_numbers("") == []
    assert find_numbers("nothing to see here, and a dog") == []


def test_results_are_parsed_numbers_with_offsets_into_the_input() -> None:
    text = "x  Ninety-Nine y"
    [match] = find_numbers(text)
    assert match == ParsedNumber(match.value, "cardinal", "Ninety-Nine", 3, 14)


def test_oracle_numbers_embedded_in_sentences_are_found_exactly() -> None:
    rng = random.Random(11)
    for _ in range(300):
        numbers = [random_int(rng) for _ in range(3)]
        text = " ".join(f"item {spell(number)} costs" for number in numbers)
        assert [match.number for match in find_numbers(text)] == numbers


def test_a_hostile_run_of_number_words_finishes() -> None:
    text = " ".join(["one", "and"] * 3000)
    matches = find_numbers(text)
    assert len(matches) == 3000
