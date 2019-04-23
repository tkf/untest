import hashlib
from shutil import which
from subprocess import PIPE, run

import pytest

from ..downloader import check_md5, filehash

md5sum = which("md5sum")
sha256sum = which("sha256sum")


def _test_with_command(program, algorithm, filepath, chunk_size):
    filepath.write_text("".join(map(str, range(1000))))

    proc = run([program, str(filepath)], stdout=PIPE, universal_newlines=True)
    desired, _ = proc.stdout.split(None, 1)

    h = filehash(hashlib.new(algorithm), str(filepath), chunk_size)
    assert h.hexdigest() == desired


@pytest.mark.skipif(md5sum is None, reason="md5sum command does not exit")
@pytest.mark.parametrize("chunk_size", [1, 2, 3, -1])
def test_md5(tmp_path, chunk_size):
    _test_with_command(md5sum, "md5", tmp_path / "datafile", chunk_size)


@pytest.mark.skipif(sha256sum is None, reason="sha256sum command does not exit")
@pytest.mark.parametrize("chunk_size", [1, 2, 3, -1])
def test_sha256(tmp_path, chunk_size):
    _test_with_command(sha256sum, "sha256", tmp_path / "datafile", chunk_size)


def test_check_md5(tmp_path):
    filepath = tmp_path / "datafile"
    filepath.write_text("".join(map(str, range(1000))))

    dist = {"md5_digest": "dummy"}
    with pytest.raises(ValueError) as exc_info:
        check_md5(dist, str(filepath))

    assert "md5 digest does not match" in str(exc_info.value)
