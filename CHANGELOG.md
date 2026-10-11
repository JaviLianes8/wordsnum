# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

- First release.
- `words_to_num` parses spelled-out English numbers into `int` or `float`.
- Handles units, teens, tens, hundreds, and scales up to trillion.
- Accepts "and", hyphenated words, articles ("a hundred"), ordinals, negatives, and decimals.
- Raises `WordsNumError` with a clear message on unparseable input.
