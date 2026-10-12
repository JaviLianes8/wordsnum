"""Parse spelled-out English numbers into int or float, fully typed and dependency-free."""

from __future__ import annotations

from ._parser import WordsNumError, words_to_num

__version__ = "0.1.0"

__all__ = ["WordsNumError", "words_to_num"]
