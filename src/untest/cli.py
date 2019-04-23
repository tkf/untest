import shlex
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

import click

from .downloader import download_package
from .utils import ignoring, unwrap


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--download-to",
    help=unwrap(
        """
        Directory to store downloaded files.  Use a temporary
        directory if not passed.
        """
    ),
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


def download_arguments(f):
    f = click.argument("package")(f)
    f = click.option("--pre/--no-pre", help="Download pre-release.")(f)
    f = click.option(
        "--index-url",
        default="https://test.pypi.org",
        help="PyPI server from which package information is retrieved.",
        show_default=True,
    )(f)
    return f


def upload_arguments(f):
    f = click.option(
        "--twine-upload",
        default="twine upload --",
        help=unwrap(
            """
            Command to be used to upload files to PyPI.
            """
        ),
    )(f)
    return f


@main.command()
@download_arguments
@upload_arguments
@click.pass_context
def mirror(ctx, package, index_url, pre, twine_upload):
    """
    Download `package` from test.pypi.org and upload it to pypi.org.

    Use environment variables to pass options to ``twine``.  See
    ``twine upload --help``.
    """
    files = list(Path(ctx.obj["download_to"]).iterdir())
    if files:
        download_to = ctx.obj["download_to"]
        ctx.fail(f"Directory {download_to!r} specified by --download-to is not empty.")

    ctx.invoke(download, package=package, index_url=index_url, pre=pre)
    ctx.invoke(upload, twine_upload=twine_upload)


@main.command()
@download_arguments
@click.pass_context
def download(ctx, package, index_url, pre):
    """
    Download `package` from test.pypi.org.
    """
    download_package(package, ctx.obj["download_to"], index_url=index_url, pre=pre)


@main.command()
@upload_arguments
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
