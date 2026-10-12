"""The cardinal grammar: what it accepts, what it rejects, and where errors point."""

import pytest

from wordsnum import MisplacedWordError, UnknownWordError, WordsNumError, parse, words_to_num


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hundred", 100),
        ("thousand", 1000),
        ("a thousand and one", 1001),
        ("one million and one", 1_000_001),
        ("a hundred thousand", 100_000),
        ("one hundred thousand and five", 100_005),
        ("nineteen hundred eighty four", 1984),
        ("twenty-five hundred", 2500),
        ("ninety-nine hundred and ninety-nine", 9999),
        ("one decillion", 10**33),
        ("nine hundred ninety-nine vigintillion", 999 * 10**63),
        ("one vigintillion one", 10**63 + 1),
        ("one quattuordecillion", 10**45),
        ("seven septendecillion", 7 * 10**54),
        ("two billion three", 2_000_000_003),
        ("forty", 40),
        ("ninety nine", 99),
        ("eleven", 11),
    ],
)
def test_valid_cardinals(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize(
    ("text", "word", "start"),
    [
        ("one two", "two", 4),
        ("thousand million", "million", 9),
        ("one thousand one million", "million", 17),
        ("one thousand one thousand", "thousand", 17),
        ("zero hundred", "zero", 0),
        ("one thousand zero", "zero", 13),
        ("zero zero", "zero", 0),
        ("twenty zero", "zero", 7),
        ("ten one", "one", 4),
        ("one hundred hundred", "hundred", 12),
        ("one and two", "and", 4),
        ("and", "and", 0),
        ("one hundred and", "and", 12),
        ("one thousand and two hundred", "hundred", 21),
        ("one hundred and zero", "zero", 16),
        ("a", "a", 0),
        ("a five", "a", 0),
        ("nineteen hundred thousand", "thousand", 17),
        ("one million nineteen hundred", "nineteen", 12),
        ("one hundred hundred thousand", "hundred", 12),
        ("2 thousand 1500", "1500", 11),
        ("1.5 two", "two", 4),
        ("minus", "minus", 0),
        ("minus minus one", "minus", 6),
        ("one minus", "minus", 4),
        ("minus first", "first", 6),
    ],
)
def test_misplaced_words_point_at_the_offender(text: str, word: str, start: int) -> None:
    with pytest.raises(MisplacedWordError) as caught:
        parse(text)
    error = caught.value
    assert (error.word, error.start, error.end) == (word, start, start + len(word))
    assert text[error.start : error.end] == word
    assert str(start) in str(error)


@pytest.mark.parametrize(
    ("text", "word", "start"),
    [
        ("banana", "banana", 0),
        ("two hundred banana", "banana", 12),
        ("fourty two", "fourty", 0),
        ("twentyone", "twentyone", 0),
        ("two & three", "&", 4),
        ("-5", "-", 0),
        ("one,", ",", 3),
        ("twenty-one-", "-", 10),
        ("22st", "22st", 0),
        ("1.5th", "1.5th", 0),
        ("&&", "&&", 0),
        ("  ?  ", "?", 2),
    ],
)
def test_unknown_words_point_at_the_offender(text: str, word: str, start: int) -> None:
    with pytest.raises(UnknownWordError) as caught:
        parse(text)
    error = caught.value
    assert (error.word, error.start, error.end) == (word, start, start + len(word))


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_empty_input_raises_the_base_error_without_a_word(text: str) -> None:
    with pytest.raises(WordsNumError) as caught:
        parse(text)
    assert type(caught.value) is WordsNumError
    assert (caught.value.word, caught.value.start, caught.value.end) == (None, None, None)


def test_errors_are_value_errors() -> None:
    assert issubclass(WordsNumError, ValueError)
    assert issubclass(UnknownWordError, WordsNumError)
    assert issubclass(MisplacedWordError, WordsNumError)


def test_typos_are_never_guessed() -> None:
    for typo in ["fourty", "ninty", "thre", "milion", "hundered", "twelth"]:
        with pytest.raises(UnknownWordError):
            words_to_num(typo)
