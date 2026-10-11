# wordsnum

Parse spelled-out English numbers into int or float, fully typed and dependency-free.

## Install

```
pip install wordsnum
```

## Usage

```python
from wordsnum import words_to_num

words_to_num("two hundred fifty")              # 250
words_to_num("one thousand two hundred thirty four")  # 1234
words_to_num("twenty-one")                     # 21
words_to_num("one hundred and one")            # 101
words_to_num("a hundred")                      # 100
words_to_num("minus forty two")                # -42
words_to_num("three point one four")           # 3.14
words_to_num("twenty-first")                   # 21 (ordinals)
words_to_num("two million three hundred thousand")   # 2300000
```

Integers come back as `int`, anything with a decimal part as `float`. Unparseable
text raises `WordsNumError` with a message that names the offending word:

```python
from wordsnum import WordsNumError, words_to_num

try:
    words_to_num("two hundred banana")
except WordsNumError as error:
    print(error)  # unexpected word: 'banana'
```

Supported: units, teens, tens, hundreds, and scales up to trillion; "and" fillers;
hyphenated words ("twenty-one"); the articles "a" and "an" before a scale; ordinals
("first", "twelfth", "hundredth"); negatives ("minus", "negative"); and decimals
read digit by digit after "point".

## Why

Turning words back into numbers is the reverse of spelling them out, and the existing
options are thin. `word2number` has not seen a release since 2017, ships no type hints,
and mishandles several common phrasings. `numerizer` is a port of a Ruby gem, is
untyped, and returns strings rather than numbers. `text2num` is maintained but builds
on a Rust extension, which is a heavy dependency for a small parsing job.

`wordsnum` is a small, pure-Python parser with zero runtime dependencies, a `py.typed`
marker, a clean `mypy --strict` build, and a single obvious entry point that returns a
native `int` or `float`. (Spelling numbers out in the other direction is already well
served by `num2words`, so this library does not attempt it.)

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
