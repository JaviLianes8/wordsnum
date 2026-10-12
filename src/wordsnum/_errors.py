"""Exceptions raised when text is not a valid spelled-out number."""

from __future__ import annotations


class WordsNumError(ValueError):
    """Raised when the text is not a valid spelled-out number.

    It subclasses ``ValueError``, so ``except ValueError`` keeps working. When the
    problem can be pinned to one word, ``word`` holds that word as written and
    ``start``/``end`` are its offsets in the original text, so that
    ``text[error.start:error.end] == error.word``. Otherwise all three are ``None``
    (for example on empty input).
    """

    def __init__(
        self,
        message: str,
        *,
        word: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        super().__init__(message)
        self.word = word
        self.start = start
        self.end = end


class UnknownWordError(WordsNumError):
    """Raised for a word that is not an English number word at all, such as ``"banana"``.

    Misspellings are never guessed: ``"fourty"`` raises this error too.
    """


class MisplacedWordError(WordsNumError):
    """Raised for a number word in a position the grammar does not allow.

    Examples: ``"one two"``, ``"thousand million"``, ``"minus"`` with nothing after it,
    or ``"one thirds"`` (a numerator of one takes a singular denominator).
    """
