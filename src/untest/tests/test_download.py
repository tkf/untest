from click.testing import CliRunner

from .. import cli


def test_download(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli.main, ["--download-to", str(tmp_path), "download", "requests"]
    )
    assert result.exit_code == 0
