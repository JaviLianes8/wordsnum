# Improvement round: ranked plan

Ranked by value to users. Every item keeps the existing API working; new names are added
alongside `words_to_num` and `WordsNumError`.

1. **A real grammar instead of a running sum.** The 0.1 parser added words together, so
   `"one two"` gave 3 and `"hundred thousand hundred"` gave a number. Replace it with a
   grammar that checks word order: groups below a thousand, scales in strictly
   decreasing order, `"and"` only where British usage puts it, `"zero"` only on its own.
2. **Scales to vigintillion.** Short scale from thousand up to vigintillion (10**63),
   with ordinal forms (`"millionth"`, `"decillionth"`). Covers "at least decillion".
3. **Fractions.** `"three quarters"`, `"a half"`, `"two thirds"`, `"seven hundredths"`,
   `"three thirty-seconds"`, and mixed numbers (`"two and three quarters"`).
4. **Exact results.** `words_to_fraction` and `words_to_decimal` return `Fraction` and
   `Decimal`, so `"one point one"` is exactly 11/10 and never a binary float.
5. **Typed errors that point at the bad word.** `UnknownWordError` (not a number word)
   and `MisplacedWordError` (a number word in the wrong place), both carrying `word`,
   `start` and `end` offsets into the original text.
6. **Strict and lenient modes.** Lenient (default) tolerates case, extra spacing,
   hyphens and commas. Strict accepts only the canonical lowercase spelling. Neither
   mode guesses typos.
7. **Mixed digits and words.** `"3 million"`, `"1.5 billion"`, `"2,500"`, `"21st"`.
8. **Decimals with a scale.** `"two point five million"`, and `"oh"` as a digit after
   the point (`"one point oh five"`).
9. **Finding numbers inside text.** `find_numbers` returns every number phrase in free
   text with its span, value and kind, using the longest valid reading.
10. **A structured result.** `parse` returns a `ParsedNumber` with the exact value, the
    kind (`cardinal`, `ordinal`, `decimal`, `fraction`) and the source span.
11. **The inverse for integers.** `num_to_words` spells an int (cardinal or ordinal,
    American or British) in exactly the canonical form strict mode accepts, so the two
    directions round-trip.
12. **A command line tool.** `wordsnum parse`, `wordsnum find` (reads stdin) and
    `wordsnum say`, with JSON output and errors on stderr.
13. **Documentation.** Docstrings on every public name and a GUIDE covering the grammar,
    the modes, the supported and unsupported forms.
14. **Tests as contracts.** A contract test over every public promise, a seeded
    round-trip against an independent spelling generator on thousands of numbers, and
    an end-to-end test that builds the wheel, installs it into a fresh virtual
    environment and drives the installed command.

Out of scope, documented as unsupported: "dozen", "score", "half a million", long-scale
billions, Roman numerals, spelling of non-integers, and guessing misspelled words.
