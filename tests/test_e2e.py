"""End to end: build the wheel, install it into a fresh venv and drive the real script.

Nothing is mocked. The build uses the project's own backend, so it needs either
``hatchling`` installed locally or network access for an isolated build.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str | Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    return subprocess.run(
        [str(arg) for arg in args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=600,
        check=False,
    )


@pytest.fixture(scope="module")
def installed(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Return the installed ``wordsnum`` script and the venv's python."""
    work = tmp_path_factory.mktemp("e2e")
    build = [sys.executable, "-m", "build", "--wheel", "--outdir", work / "dist", ROOT]
    if importlib.util.find_spec("hatchling") is not None:
        build.append("--no-isolation")
    built = _run(*build)
    assert built.returncode == 0, built.stdout + built.stderr
    [wheel] = (work / "dist").glob("wordsnum-*.whl")
    venv = work / "venv"
    assert _run(sys.executable, "-m", "venv", venv).returncode == 0
    bin_dir = venv / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / ("python.exe" if os.name == "nt" else "python")
    install = _run(python, "-m", "pip", "install", "--no-index", "--no-deps", wheel)
    assert install.returncode == 0, install.stdout + install.stderr
    script = bin_dir / ("wordsnum.exe" if os.name == "nt" else "wordsnum")
    assert script.exists()
    return script, python


def test_installed_script_parses_finds_and_says(installed: tuple[Path, Path]) -> None:
    script, _ = installed
    parsed = _run(script, "parse", "two", "thousand", "and", "twenty-one")
    assert (parsed.returncode, parsed.stdout, parsed.stderr) == (0, "2021\n", "")
    exact = _run(script, "parse", "--exact", stdin="three quarters\none point one\n")
    assert exact.stdout == "3/4\n1.1\n"
    found = _run(script, "find", "--json", stdin="I paid twenty-one pounds for 3 pies")
    assert [item["value"] for item in json.loads(found.stdout)] == [21, 3]
    said = _run(script, "say", "1005", "--british")
    assert said.stdout == "one thousand and five\n"


def test_installed_script_reports_errors_on_stderr(installed: tuple[Path, Path]) -> None:
    script, _ = installed
    failed = _run(script, "parse", "two", "banana")
    assert (failed.returncode, failed.stdout) == (1, "")
    assert "banana" in failed.stderr
    assert "examples:" in _run(script, "--help").stdout


def test_installed_package_is_typed_and_importable(installed: tuple[Path, Path]) -> None:
    _, python = installed
    code = (
        "import importlib.resources, wordsnum;"
        "print(wordsnum.__version__, wordsnum.words_to_num('a half'),"
        "importlib.resources.files('wordsnum').joinpath('py.typed').is_file(),"
        "wordsnum.__file__)"
    )
    result = _run(python, "-c", code)
    version, value, typed, location = result.stdout.split()
    assert (value, typed) == ("0.5", "True")
    assert str(ROOT / "src") not in location
    import wordsnum

    assert version == wordsnum.__version__
