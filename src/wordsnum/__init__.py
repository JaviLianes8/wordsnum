"""Parse spelled-out English numbers into int or float, fully typed and dependency-free.

Start with ``words_to_num`` for a quick ``int``/``float``, ``parse`` for the exact value
and kind, ``find_numbers`` to pull numbers out of free text, and ``num_to_words`` to
spell an integer back out.
"""

from __future__ import annotations

from ._errors import MisplacedWordError, UnknownWordError, WordsNumError
from ._find import find_numbers
from ._forms import Kind
from ._parser import parse, words_to_decimal, words_to_fraction, words_to_num
from ._result import ParsedNumber
from ._spell import num_to_words

__version__ = "0.2.0"

__all__ = [
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
