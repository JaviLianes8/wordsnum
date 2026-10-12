# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

- Replace the word-summing parser with a real grammar. Behaviour change: malformed
  input that 0.1.0 summed into a number is now rejected with `MisplacedWordError`, for
  example "one two" (was 3), "one, two" (was 3), "and one" (was 1), "one and" (was 1)
  and "thousand million".
- Scales up to vigintillion (10**63), with ordinal forms.
- Fractions ("three quarters", "a half", "seven hundredths", "three thirty-seconds")
  and mixed numbers ("two and three quarters").
- Decimals with a final scale word ("two point five million") and "oh" after "point".
- Digit groups mixed with words ("3 million", "2,500", "1.5 billion", "21st", "-5").
- `parse` returns a `ParsedNumber` with the exact value, kind and source span.
- `words_to_fraction` and `words_to_decimal` return exact results.
- `find_numbers` finds every number inside free text.
- `num_to_words` spells integers in the canonical form, round-tripping with the parser.
- `strict=True` accepts only the canonical spelling.
- Typed errors `UnknownWordError` and `MisplacedWordError` carry `word`, `start` and `end`.
- The `wordsnum` command line tool: `parse`, `find` and `say`.
- GUIDE.md documents the full grammar and the unsupported forms.

## [0.1.0]

- First release.
- `words_to_num` parses spelled-out English numbers into `int` or `float`.
- Handles units, teens, tens, hundreds, and scales up to trillion.
- Accepts "and", hyphenated words, articles ("a hundred"), ordinals, negatives, and decimals.
- Raises `WordsNumError` with a clear message on unparseable input.
