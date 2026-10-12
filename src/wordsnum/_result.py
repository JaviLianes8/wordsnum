"""The structured result of parsing one number."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from ._forms import Kind


@dataclass(frozen=True)
class ParsedNumber:
    """One parsed number with its exact value, its kind and where it was found.

    Attributes:
        value: The exact value as a ``Fraction`` (``"three point one four"`` is
            ``Fraction(157, 50)``, never a rounded float).
        kind: ``"cardinal"`` (``"forty two"``), ``"ordinal"`` (``"forty-second"``,
            ``"21st"``), ``"decimal"`` (``"two point five"``, ``"1.5 million"``) or
            ``"fraction"`` (``"three quarters"``, ``"two and a half"``).
        text: The source text of the number, exactly as written.
        start: Offset of the first character of the number in the parsed string.
        end: Offset just past the last character, so ``source[start:end] == text``.
    """

    value: Fraction
    kind: Kind
    text: str
    start: int
    end: int

    @property
    def number(self) -> int | float:
        """The value as ``words_to_num`` returns it.

        An ``int`` for cardinals and ordinals, a ``float`` for decimals and fractions
        (even when the value is whole, such as ``"four halves"``).
        """
        if self.kind in ("cardinal", "ordinal"):
            return int(self.value)
        return self.value.numerator / self.value.denominator

    def to_decimal(self) -> Decimal:
        """The value as a ``Decimal``.

        Exact whenever the value has a terminating decimal expansion, which covers every
        cardinal, ordinal and decimal. A fraction such as ``"one third"`` is divided in
        the current ``decimal`` context and so is rounded to its precision.
        """
        value = self.value
        if value.denominator == 1:
            return Decimal(value.numerator)
        denominator = value.denominator
        twos = fives = 0
        while denominator % 2 == 0:
            denominator //= 2
            twos += 1
        while denominator % 5 == 0:
            denominator //= 5
            fives += 1
        if denominator != 1:
            return Decimal(value.numerator) / Decimal(value.denominator)
        places = max(twos, fives)
        scaled = value.numerator * 10**places // value.denominator
        return Decimal(f"{scaled}E-{places}")
