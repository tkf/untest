import shutil
import tempfile
from pathlib import Path

import click

from .downloader import download_package


@click.group()
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
    ctx.forward(download)
    ctx.forward(upload)


@mirror_like_command
def download(ctx, package):
    download_package(package, ctx.obj["download_to"])


@mirror_like_command
def upload(ctx, package):
    raise NotImplementedError


if __name__ == "__main__":
    main()
