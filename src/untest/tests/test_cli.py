import json
import shlex
import sys

from click.testing import CliRunner

from .. import cli


def test_download(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["--download-to", str(tmp_path), "download", "requests"]
    )
    assert result.exit_code == 0


def test_upload(tmp_path):
    download_to = tmp_path / "download"
    download_to.mkdir()
    files = [
        # Dummy files to be passed to dummy `twine upload`:
        download_to / "aaa",
        download_to / "bbb",
        download_to / "ccc",
    ]
    for path in files:
        path.touch()

    argv_path = tmp_path / "argv.json"
    code = f"import sys, json; json.dump(sys.argv, open({str(argv_path)!r}, 'w'))"
    twine_mock = " ".join(map(shlex.quote, [sys.executable, "-c", code]))

    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        ["--download-to", str(download_to), "upload", "--twine-upload", twine_mock],
    )
    assert result.exit_code == 0

    with open(str(argv_path)) as file:
        argv = json.load(file)

    assert sorted(argv[-len(files) :]) == sorted(map(str, files))
