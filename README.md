# wordsnum

Parse spelled-out English numbers into int or float, fully typed and dependency-free.

## Install

```
pip install wordsnum
```

## Usage

```python
from wordsnum import words_to_num

words_to_num("two hundred fifty")  # 250
words_to_num("two thousand and twenty-one")  # 2021
words_to_num("nineteen hundred eighty four")  # 1984
words_to_num("a hundred")  # 100
words_to_num("minus forty two")  # -42
words_to_num("twenty-first")  # 21 (ordinals)
words_to_num("three point one four")  # 3.14
words_to_num("two point five million")  # 2500000.0
words_to_num("two and three quarters")  # 2.75
words_to_num("3 million")  # 3000000
words_to_num("one decillion")  # 10**33
```

Cardinals and ordinals come back as `int`; decimals and fractions as `float`.

### Exact values, kinds and spans

```python
from wordsnum import parse, words_to_decimal, words_to_fraction

words_to_fraction("two thirds")  # Fraction(2, 3)
words_to_decimal("one point one")  # Decimal('1.1')

result = parse("  Seven Hundredths ")
result.value  # Fraction(7, 100)
result.kind  # 'fraction'  (also 'cardinal', 'ordinal', 'decimal')
result.text, result.start, result.end  # ('Seven Hundredths', 2, 18)
```

### Numbers inside text

```python
from wordsnum import find_numbers

for match in find_numbers("We sold twenty-one boxes, then 3 million more."):
    print(match.start, match.end, match.number, match.text)
# 8 18 21 twenty-one
# 31 40 3000000 3 million
```

### Spelling integers

```python
from wordsnum import num_to_words

num_to_words(1234)  # 'one thousand two hundred thirty-four'
num_to_words(1005, british=True)  # 'one thousand and five'
num_to_words(21, ordinal=True)  # 'twenty-first'
```

`num_to_words` writes exactly the canonical form that strict parsing accepts, so the
two directions round-trip.

### Strict and lenient

By default case, extra spaces, hyphens and commas are tolerated. `strict=True` accepts
only the canonical spelling (lowercase, single spaces, `twenty-one` hyphenated, no
commas). Neither mode guesses typos: `"fourty"` is always an error.

### Errors that point at the problem

```python
from wordsnum import MisplacedWordError, UnknownWordError, words_to_num

try:
    words_to_num("two hundred banana")
except UnknownWordError as error:
    print(error.word, error.start, error.end)  # banana 12 18

try:
    words_to_num("one thousand one million")
except MisplacedWordError as error:
    print(error)  # scale words must get smaller from left to right: 'million' at position 17
```

Both subclass `WordsNumError`, which subclasses `ValueError`.

## Command line

```
wordsnum parse two thousand and twenty-one        # 2021
wordsnum parse three quarters --exact             # 3/4
echo "minus forty two" | wordsnum parse           # -42
echo "I owe you twenty-one pounds" | wordsnum find
wordsnum say 21 --ordinal                         # twenty-first
```

Run `wordsnum --help` for every option. Errors go to stderr with exit status 1.

See [GUIDE.md](GUIDE.md) for the full grammar and the list of unsupported forms.

## Why

Turning words back into numbers is the reverse of spelling them out, and the existing
options are thin. `word2number` has not seen a release since 2017, ships no type hints,
and mishandles several common phrasings. `numerizer` is a port of a Ruby gem, is
untyped, and returns strings rather than numbers. `text2num` is maintained but builds
on a Rust extension, which is a heavy dependency for a small parsing job.

`wordsnum` is a small, pure-Python parser with zero runtime dependencies, a `py.typed`
marker, a clean `mypy --strict` build, a real grammar that rejects malformed input
instead of summing words, and exact results when you need them.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
