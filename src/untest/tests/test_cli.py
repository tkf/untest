import json
import shlex
import sys
from collections import namedtuple

import pytest
from click.testing import CliRunner

from .. import cli

TwineMock = namedtuple("TwineMock", ["twine_upload", "getargv"])


@pytest.fixture
def twine_mock(tmp_path):
    argv_path = tmp_path / "argv.json"
    code = f"import sys, json; json.dump(sys.argv, open({str(argv_path)!r}, 'w'))"
    twine_upload = " ".join(map(shlex.quote, [sys.executable, "-c", code]))

    def getargv():
        with open(str(argv_path)) as file:
            return json.load(file)

    yield TwineMock(twine_upload, getargv)


def test_download(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["--download-to", str(tmp_path), "download", "requests"]
    )
    assert result.exit_code == 0


def test_upload(tmp_path, twine_mock):
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

    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            "--download-to",
            str(download_to),
            "upload",
            "--twine-upload",
            twine_mock.twine_upload,
        ],
    )
    assert result.exit_code == 0

    argv = twine_mock.getargv()
    assert sorted(argv[-len(files) :]) == sorted(map(str, files))


def test_mirror(tmp_path, twine_mock):
    download_to = tmp_path / "download"
    download_to.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli.main,
        [
            "--download-to",
            str(download_to),
            "mirror",
            "--twine-upload",
            twine_mock.twine_upload,
            "requests",
        ],
    )
    assert result.exit_code == 0

    argv = twine_mock.getargv()
    assert argv[0] == "-c"
    assert len(argv) > 1  # more than one file must be downloaded
