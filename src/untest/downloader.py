import hashlib
import os
from logging import getLogger
from urllib.request import urlretrieve

import packaging.version
import requests

logger = getLogger(__name__)


def choose_version(project, pre):
    if pre:
        return sorted(project["releases"], key=packaging.version.parse)[-1]
    else:
        return project["info"]["version"]


def download_package(package, directory, index_url="https://test.pypi.org", pre=False):
    """
    Download `package` from `index_url` in `directory`.
    """
    project = requests.get(f"{index_url}/pypi/{package}/json").json()
    release = project["releases"][choose_version(project, pre)]

    for n, dist in enumerate(release, 1):
        dest = os.path.join(directory, dist["url"].rsplit("/", 1)[-1])
        logger.info("Downloading (%d/%d) %s", len(release), n, dist["url"])
        urlretrieve(dist["url"], dest)
        check_md5(dist, dest)


def check_md5(dist, dest):
    md5_digest = filehash(hashlib.md5(), dest).hexdigest()
    if md5_digest != dist["md5_digest"]:
        raise ValueError(
            "md5 digest does not match\n"
            f"pypi      : {dist['md5_digest']}\n"
            f"downloaded: {md5_digest}"
        )


def filehash(hash, path, chunk_size=1024):
    with open(path, "rb") as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            hash.update(data)
    return hash
