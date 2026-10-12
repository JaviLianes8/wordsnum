"""The public contract: every exported name and the full promise it makes."""

import dataclasses
import importlib.resources
import inspect
import re
import typing
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

import wordsnum
from wordsnum import (
    Kind,
    MisplacedWordError,
    ParsedNumber,
    UnknownWordError,
    WordsNumError,
    find_numbers,
    num_to_words,
    parse,
    words_to_decimal,
    words_to_fraction,
    words_to_num,
)

PUBLIC_API: list[str] = [
    "Kind",
    "MisplacedWordError",
    "ParsedNumber",
    "UnknownWordError",
    "WordsNumError",
    "find_numbers",
    "num_to_words",
    "parse",
    "words_to_decimal",
    "words_to_fraction",
    "words_to_num",
]
PARSERS = [parse, words_to_num, words_to_fraction, words_to_decimal]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(wordsnum.__all__) == sorted(PUBLIC_API)
    for name in wordsnum.__all__:
        assert hasattr(wordsnum, name)


def test_version_matches_the_project_metadata() -> None:
    project = (Path(__file__).parents[1] / "pyproject.toml").read_text("utf-8")
    version = re.search(r'^version = "([^"]+)"', project, re.MULTILINE)
    assert version is not None and version[1] == wordsnum.__version__
    assert '[project.scripts]\nwordsnum = "wordsnum._cli:main"' in project.replace("\r\n", "\n")
    assert re.search(r"^dependencies = \[\]$", project, re.MULTILINE)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("wordsnum").joinpath("py.typed").is_file()


def test_every_public_name_is_documented() -> None:
    for name in PUBLIC_API:
        if name != "Kind":
            assert inspect.getdoc(getattr(wordsnum, name)), name


@pytest.mark.parametrize("function", PARSERS)
def test_strict_is_keyword_only_and_defaults_to_lenient(function: typing.Any) -> None:
    parameter = inspect.signature(function).parameters["strict"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is False
    with pytest.raises(TypeError):
        function("one", True)


def test_kind_names_exactly_four_forms() -> None:
    assert set(typing.get_args(Kind)) == {"cardinal", "ordinal", "decimal", "fraction"}


def test_words_to_num_promise() -> None:
    assert words_to_num("one hundred and one") == 101 and type(words_to_num("one")) is int
    assert words_to_num("twenty-first") == 21
    assert words_to_num("three point one four") == 3.14
    assert words_to_num("three quarters") == 0.75
    assert words_to_num("minus 3 million") == -3_000_000


def test_parse_promise() -> None:
    text = "  Two Thousand and Twenty-One "
    result = parse(text)
    assert result == ParsedNumber(Fraction(2021), "cardinal", "Two Thousand and Twenty-One", 2, 29)
    assert text[result.start : result.end] == result.text
    assert [parse(t).kind for t in ("one", "first", "point one", "a half")] == list(
        typing.get_args(Kind)
    )


def test_exact_value_promises() -> None:
    assert words_to_fraction("one point one") == Fraction(11, 10)
    assert isinstance(words_to_fraction("one"), Fraction)
    assert words_to_decimal("one point one") == Decimal("1.1")
    assert isinstance(words_to_decimal("one"), Decimal)


def test_parsed_number_promise() -> None:
    result = parse("four halves")
    assert dataclasses.is_dataclass(result)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.value = Fraction(1)  # type: ignore[misc]
    assert (result.number, type(result.number)) == (2.0, float)
    assert result.to_decimal() == Decimal(2)
    assert parse("forty-second").number == 42


def test_find_numbers_promise() -> None:
    text = "twenty-one, then the 3rd, then two point five"
    matches = find_numbers(text)
    assert all(isinstance(match, ParsedNumber) for match in matches)
    assert [match.start for match in matches] == sorted(match.start for match in matches)
    assert [text[m.start : m.end] for m in matches] == ["twenty-one", "3rd", "two point five"]


def test_num_to_words_promise() -> None:
    for number in (0, 7, 101, -999_999, 10**63 + 21):
        assert words_to_num(num_to_words(number), strict=True) == number
        assert words_to_num(num_to_words(number, british=True), strict=True) == number
    assert parse(num_to_words(23, ordinal=True), strict=True).kind == "ordinal"
    with pytest.raises(ValueError):
        num_to_words(10**66)
    with pytest.raises(TypeError):
        num_to_words(1.5)  # type: ignore[arg-type]


def test_error_promises() -> None:
    assert issubclass(UnknownWordError, WordsNumError)
    assert issubclass(MisplacedWordError, WordsNumError)
    assert issubclass(WordsNumError, ValueError)
    for text, kind in (("one banana", UnknownWordError), ("one one", MisplacedWordError)):
        with pytest.raises(kind) as caught:
            words_to_num(text)
        assert (caught.value.word, caught.value.start, caught.value.end) == (text[4:], 4, len(text))
    with pytest.raises(WordsNumError) as empty:
        words_to_num("")
    assert empty.value.word is None


def test_docstring_examples_run() -> None:
    import doctest

    from wordsnum import _find, _parser, _spell

    for module in (_find, _parser, _spell):
        failures, attempted = doctest.testmod(module)
        assert failures == 0 and attempted > 0, module.__name__
