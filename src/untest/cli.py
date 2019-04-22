import shlex
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

import click

from .downloader import download_package
from .utils import ignoring


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--download-to",
    help="""
    Directory to store downloaded files.  Use a temporary directory if
    not passed.
    """,
)
@click.pass_context
def main(ctx, download_to):
    ctx.ensure_object(dict)

    if not download_to:
        download_to = tempfile.mkdtemp(prefix="tmp-untest-")

        @ctx.call_on_close
        def remove_download_to():
            shutil.rmtree(download_to, ignore_errors=True)

    else:
        Path(download_to).mkdir(parents=True, exist_ok=True)

    ctx.obj["download_to"] = download_to


def mirror_like_command(f):
    f = click.pass_context(f)
    f = click.argument("package")(f)
    f = main.command()(f)
    return f


@mirror_like_command
def mirror(ctx, package):
    """
    Download `package` from test.pypi.org and upload it to pypi.org.

    Use environment variables to pass options to ``twine``.  See
    ``twine upload --help``.
    """
    files = list(Path(ctx.obj["download_to"]).iterdir())
    if files:
        download_to = ctx.obj["download_to"]
        ctx.fail(f"Directory {download_to!r} specified by --download-to is not empty.")

    ctx.forward(download)
    ctx.invoke(upload)


@mirror_like_command
def download(ctx, package):
    """
    Download `package` from test.pypi.org.
    """
    download_package(package, ctx.obj["download_to"])


@main.command()
@click.option(
    "--twine-upload",
    default="twine upload --",
    help="""
    Command to be used to upload files to PyPI.
    """,
)
@click.pass_context
def upload(ctx, twine_upload):
    """
    Run ``twine upload`` with the files stored in `--download-to`.

    Use environment variables to pass options to ``twine``.  See
    ``twine upload --help``.
    """
    cmd = shlex.split(twine_upload)
    cmd.extend(map(str, Path(ctx.obj["download_to"]).iterdir()))
    with ignoring(signal.SIGINT):
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
