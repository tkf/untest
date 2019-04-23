import pytest

from ..downloader import choose_version


@pytest.mark.parametrize(
    "releases, desired",
    [
        (["0.1", "0.2", "1.0"], "1.0"),
        (["1.0.0.dev", "1.0.0.alpha", "1.0.0.beta", "1.0.0.rc", "0.9"], "1.0.0.rc"),
    ],
)
def test_choose_version_pre(releases, desired):
    project = {"releases": releases}
    assert choose_version(project, True) == desired


def test_choose_version_non_pre():
    desired = "9.8.7"
    project = {"info": {"version": desired}}
    assert choose_version(project, False) == desired
