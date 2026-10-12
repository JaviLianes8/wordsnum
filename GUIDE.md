# wordsnum guide

This guide describes exactly what `wordsnum` accepts, how each form is read, and what
it does not support.

## Public API

| Name | Returns | Purpose |
| --- | --- | --- |
| `words_to_num(text, *, strict=False)` | `int` or `float` | Quick conversion |
| `parse(text, *, strict=False)` | `ParsedNumber` | Exact value, kind and span |
| `words_to_fraction(text, *, strict=False)` | `Fraction` | Exact rational value |
| `words_to_decimal(text, *, strict=False)` | `Decimal` | Exact decimal value |
| `find_numbers(text)` | `list[ParsedNumber]` | Every number inside free text |
| `num_to_words(n, *, ordinal=False, british=False)` | `str` | Spell an integer |
| `ParsedNumber` | dataclass | `value`, `kind`, `text`, `start`, `end`, `number`, `to_decimal()` |
| `Kind` | `Literal` | `"cardinal"`, `"ordinal"`, `"decimal"`, `"fraction"` |
| `WordsNumError` | exception | Base error, a `ValueError` |
| `UnknownWordError` | exception | A word that is not a number word |
| `MisplacedWordError` | exception | A number word in a position the grammar rejects |

Every error carries `word`, `start` and `end`, with `text[start:end] == word`, or
`None` for all three when no single word is at fault (empty input).

## Cardinals

A cardinal is a sequence of groups, each below one thousand, joined by scale words in
strictly decreasing order:

- Units and teens: `zero` to `nineteen`. `zero` must stand alone.
- Tens: `twenty` to `ninety`, optionally followed by a unit: `twenty-one`, `forty two`.
- Hundreds: `one hundred`, `nine hundred ninety-nine`, `a hundred`.
- Scales, short scale: `thousand` (10**3), `million`, `billion`, `trillion`,
  `quadrillion`, `quintillion`, `sextillion`, `septillion`, `octillion`, `nonillion`,
  `decillion` (10**33), `undecillion`, `duodecillion`, `tredecillion`,
  `quattuordecillion`, `quindecillion`, `sexdecillion`, `septendecillion`,
  `octodecillion`, `novemdecillion` and `vigintillion` (10**63).
- A leading scale may drop its `one`: `hundred`, `thousand two hundred`.
- `a`/`an` stands for one before `hundred` or a scale: `a thousand and one`.
- Year style: a teen or tens word before `hundred` (`nineteen hundred eighty four`,
  `twenty-five hundred`) is accepted when no other scale word appears.
- British `and` is accepted after `hundred` (`one hundred and one`) and after a scale
  before a final group below one hundred (`one thousand and five`). Anywhere else it is
  an error.

Rejected examples: `one two`, `thousand million`, `one thousand one million`,
`zero hundred`, `one hundred hundred`, `one and two`.

## Ordinals

The last word may be an ordinal: `first`, `twelfth`, `twentieth`, `twenty-first`,
`one hundred and third`, `hundredth`, `one millionth`, `decillionth`. Digit ordinals
such as `21st`, `2nd`, `103rd` and `111th` work when the suffix is correct. Ordinals
are never negative.

## Decimals

`point` is followed by one-digit words (`zero` to `nine`, or `oh`):
`three point one four`, `point five`, `one point oh five`. One final scale word may
follow the digits when the whole part is below a thousand: `two point five million`.
Digit decimals also work: `3.14`, `1,234.5`, `1.5 billion`.

## Fractions

A numerator followed by a denominator word:

- `half`/`halves`, `quarter`/`quarters`, and ordinal denominators such as `thirds`,
  `fourths`, `hundredths`, `millionths`. A hyphenated compound also works:
  `three thirty-seconds`, `a twenty-first`.
- A numerator of one takes the singular (`a third`, `one half`); any other numerator
  takes the plural (`two thirds`, `zero halves`).
- `one` followed by a scale ordinal reads as an ordinal (`one hundredth` is the 100th);
  use `a hundredth` for the fraction 1/100.
- Mixed numbers: `one and a half`, `two and three quarters`. The reading after the last
  `and` is used as a mixed number only when that fraction is proper, so
  `one hundred and one third` is 100 1/3 while `two hundred and fifty thirds` is 250/3.
- `first` and `second` are not denominators on their own (`two seconds` is not 2/2).

## Signs and digits

`minus` or `negative` may lead any cardinal, decimal or fraction. Digit groups mix with
words: `3 million`, `5 hundred`, `2,500`, `1 million two hundred`. A digit group after
a scale must be below a thousand.

## Strict and lenient

Lenient mode, the default, ignores case, collapses whitespace and accepts hyphens and
commas between words. Strict mode accepts only the canonical form that `num_to_words`
writes: lowercase words, exactly one space between words, a hyphen exactly between a
tens word and a unit word (`twenty-one`, `thirty-second`), no commas between words and
no surrounding whitespace. Neither mode corrects spelling.

## Finding numbers in text

`find_numbers` scans free text, case-insensitively, and returns the longest valid
reading at each position. Words that are also everyday words are reported as numbers:
`no one` contains 1 and `just a second` contains the ordinal 2. Filter by `kind` or by
context when that matters.

## Unsupported forms

These are rejected rather than guessed:

- `dozen`, `score`, `gross`, `half a million`, `one and a half million`.
- Long-scale meanings (British `billion` as 10**12) and scales above vigintillion.
- Spelling-error correction of any kind.
- Roman numerals and other languages.
- Spelling non-integers with `num_to_words`.

## Command line

```
wordsnum parse WORDS... [--strict] [--exact] [--json]
wordsnum find [--text TEXT] [--exact] [--json]     # reads stdin without --text
wordsnum say NUMBER [--ordinal] [--british]
```

Without words, `parse` reads one number per non-empty stdin line. `--exact` prints
`3/4` and `1.1` instead of floats. Errors are printed to stderr and the exit status
is 1.
