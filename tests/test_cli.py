"""The command line tool, driven in-process through ``main``."""

import io
import json

import pytest

from wordsnum import __version__
from wordsnum._cli import main


def _run(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, *args: str, stdin: str = ""
) -> tuple[int, str, str]:
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    code = main(list(args))
    out, err = capsys.readouterr()
    return code, out, err


def test_parse_words_as_arguments(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    assert _run(capsys, monkeypatch, "parse", "two", "thousand", "and", "twenty-one") == (
        0,
        "2021\n",
        "",
    )


def test_parse_lines_from_stdin(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    code, out, _ = _run(capsys, monkeypatch, "parse", stdin="minus forty two\n\n a half\n")
    assert (code, out) == (0, "-42\n0.5\n")


def test_parse_exact_and_json(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    assert _run(capsys, monkeypatch, "parse", "three", "quarters", "--exact")[1] == "3/4\n"
    assert _run(capsys, monkeypatch, "parse", "one point one", "--exact")[1] == "1.1\n"
    out = _run(capsys, monkeypatch, "parse", "1.5 million", "--json")[1]
    assert json.loads(out) == {
        "value": 1500000.0,
        "exact": "1500000",
        "kind": "decimal",
        "text": "1.5 million",
        "start": 0,
        "end": 11,
    }


def test_parse_strict(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    code, out, err = _run(capsys, monkeypatch, "parse", "twenty one", "--strict")
    assert (code, out) == (1, "")
    assert "hyphen" in err


def test_find_from_stdin_and_text(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    code, out, _ = _run(capsys, monkeypatch, "find", stdin="I owe you twenty-one pounds")
    assert (code, out) == (0, "10\t20\t21\ttwenty-one\n")
    out = _run(capsys, monkeypatch, "find", "--text", "a half and 3", "--json", "--exact")[1]
    assert [item["exact"] for item in json.loads(out)] == ["1/2", "3"]


def test_find_with_nothing_found_prints_nothing(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    assert _run(capsys, monkeypatch, "find", stdin="no digits here") == (0, "", "")


def test_say(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    assert _run(capsys, monkeypatch, "say", "1,234", "--british")[1] == (
        "one thousand two hundred and thirty-four\n"
    )
    assert _run(capsys, monkeypatch, "say", "21", "--ordinal")[1] == "twenty-first\n"
    assert _run(capsys, monkeypatch, "say", "-7")[1] == "minus seven\n"


@pytest.mark.parametrize(
    "args",
    [
        ("parse", "two", "banana"),
        ("parse",),
        ("say", "1.5"),
        ("say", "10" * 40),
        ("say", "-1", "--ordinal"),
        ("bogus",),
        (),
    ],
)
def test_errors_go_to_stderr_with_status_1(capsys, monkeypatch, args) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    try:
        code = main(list(args))
    except SystemExit as stop:
        code = stop.code  # type: ignore[assignment]
    out, err = capsys.readouterr()
    assert (code, out) == (1, "")
    assert "error" in err


def test_version_and_help(capsys) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(SystemExit) as stop:
        main(["--version"])
    assert stop.value.code == 0
    assert capsys.readouterr().out.strip() == f"wordsnum {__version__}"
    with pytest.raises(SystemExit):
        main(["--help"])
    assert "wordsnum parse two thousand and twenty-one" in capsys.readouterr().out
