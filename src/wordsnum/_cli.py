"""Command line interface: ``wordsnum parse``, ``wordsnum find`` and ``wordsnum say``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from typing import NoReturn

from . import __version__
from ._errors import WordsNumError
from ._find import find_numbers
from ._parser import parse
from ._result import ParsedNumber
from ._spell import num_to_words

_EXAMPLES = """\
examples:
  wordsnum parse two thousand and twenty-one       -> 2021
  wordsnum parse three quarters --exact            -> 3/4
  wordsnum parse "1.5 million" --json
  echo "minus forty two" | wordsnum parse          -> -42 (one number per line)
  echo "I owe you twenty-one pounds" | wordsnum find
  wordsnum say 1234 --british                      -> one thousand two hundred and thirty-four
  wordsnum say 21 --ordinal                        -> twenty-first

Errors go to stderr and the exit status is 1.
"""


class _Parser(argparse.ArgumentParser):
    """An argument parser whose usage errors exit with status 1, like every other error."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="wordsnum",
        description="Parse spelled-out English numbers, find them in text, or spell integers.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"wordsnum {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    parse_cmd = commands.add_parser(
        "parse", help="parse one number (words as arguments, or one per stdin line)"
    )
    parse_cmd.add_argument("words", nargs="*", help="the number words; read stdin when omitted")
    parse_cmd.add_argument("--strict", action="store_true", help="accept only canonical spelling")
    _add_output_flags(parse_cmd)

    find_cmd = commands.add_parser("find", help="list every number in text read from stdin")
    find_cmd.add_argument("--text", help="search this text instead of stdin")
    _add_output_flags(find_cmd)

    say_cmd = commands.add_parser("say", help="spell an integer in words")
    say_cmd.add_argument("number", help="the integer to spell, such as 1234 or -7")
    say_cmd.add_argument("--ordinal", action="store_true", help="spell the ordinal form")
    say_cmd.add_argument("--british", action="store_true", help="use British 'and'")
    return parser


def _add_output_flags(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--exact", action="store_true", help="print exact values (3/4, 3.14) instead of floats"
    )
    command.add_argument("--json", action="store_true", help="print JSON objects")


def _value(match: ParsedNumber, *, exact: bool) -> str:
    if not exact or match.kind in ("cardinal", "ordinal"):
        return str(match.number)
    if match.kind == "decimal":
        return str(match.to_decimal())
    return str(match.value)


def _record(match: ParsedNumber, *, exact: bool) -> dict[str, object]:
    return {
        "value": match.number,
        "exact": _value(match, exact=True),
        "kind": match.kind,
        "text": match.text,
        "start": match.start,
        "end": match.end,
    }


def _run_parse(args: argparse.Namespace) -> None:
    if args.words:
        lines = [" ".join(args.words)]
    else:
        lines = [line for line in sys.stdin.read().splitlines() if line.strip()]
    if not lines:
        raise WordsNumError("no input: pass number words or pipe them on stdin")
    for line in lines:
        match = parse(line, strict=args.strict)
        if args.json:
            print(json.dumps(_record(match, exact=args.exact)))
        else:
            print(_value(match, exact=args.exact))


def _run_find(args: argparse.Namespace) -> None:
    text = args.text if args.text is not None else sys.stdin.read()
    matches = find_numbers(text)
    if args.json:
        print(json.dumps([_record(match, exact=args.exact) for match in matches]))
        return
    for match in matches:
        print(f"{match.start}\t{match.end}\t{_value(match, exact=args.exact)}\t{match.text}")


def _run_say(args: argparse.Namespace) -> None:
    try:
        number = int(args.number.replace(",", "").replace("_", ""))
    except ValueError:
        raise ValueError(f"not an integer: {args.number!r}") from None
    print(num_to_words(number, ordinal=args.ordinal, british=args.british))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line tool and return its exit status (0 on success, 1 on error)."""
    args = _build_parser().parse_args(argv)
    handlers = {"parse": _run_parse, "find": _run_find, "say": _run_say}
    try:
        handlers[args.command](args)
    except (ValueError, TypeError) as error:
        print(f"wordsnum: error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
