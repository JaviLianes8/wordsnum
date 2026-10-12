"""Strict mode accepts only the canonical spelling; lenient mode tolerates formatting."""

import pytest

from wordsnum import MisplacedWordError, UnknownWordError, parse, words_to_num


@pytest.mark.parametrize(
    "text",
    [
        "twenty-one",
        "one hundred and one",
        "one hundred one",
        "two thousand and twenty-two",
        "minus forty-two",
        "three quarters",
        "twenty ninths",
        "twenty-ninths" + "",  # rejected later for its missing numerator, not its spelling
        "three thirty-seconds",
        "one point oh five",
        "3 million",
        "2,500",
        "21st",
    ],
)
def test_canonical_spellings_pass_the_strict_spelling_check(text: str) -> None:
    try:
        parse(text, strict=True)
    except MisplacedWordError as error:
        assert "strict" not in str(error)


@pytest.mark.parametrize(
    ("text", "word"),
    [
        ("twenty one", "one"),
        ("Twenty-one", "Twenty"),
        ("one  hundred", "hundred"),
        ("one-hundred", "hundred"),
        ("twenty first", "first"),
        ("one thousand, two hundred", "two"),
        ("3million", "million"),
    ],
)
def test_strict_rejects_formatting_and_names_the_word(text: str, word: str) -> None:
    with pytest.raises(MisplacedWordError) as caught:
        parse(text, strict=True)
    assert caught.value.word == word
    assert "strict" in str(caught.value)
    parse(text)  # every one of these is fine when lenient


@pytest.mark.parametrize("text", [" one", "one ", "\tone\n"])
def test_strict_rejects_surrounding_whitespace(text: str) -> None:
    with pytest.raises(UnknownWordError):
        parse(text, strict=True)
    assert words_to_num(text) == 1


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("  one   thousand,\ttwo hundred  ", 1200),
        ("TWENTY - ONE", 21),
        ("one-hundred-and-five", 105),
        ("Two Hundred FIFTY", 250),
        ("one thousand,two hundred", 1200),
    ],
)
def test_lenient_tolerates_spacing_case_hyphens_and_commas(text: str, expected: int) -> None:
    assert words_to_num(text) == expected


@pytest.mark.parametrize("text", ["one; two", "one.", "one/two", "(one)"])
def test_lenient_still_rejects_other_punctuation(text: str) -> None:
    with pytest.raises(UnknownWordError):
        words_to_num(text)


@pytest.mark.parametrize(("text", "word"), [("a eighth", "a"), ("an hundred", "an")])
def test_strict_checks_the_article(text: str, word: str) -> None:
    with pytest.raises(MisplacedWordError) as caught:
        parse(text, strict=True)
    assert caught.value.word == word
    parse(text)
    assert parse("an eighth", strict=True).value == parse("a eighth").value
