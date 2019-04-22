import hashlib
import os
from urllib.request import urlretrieve

import packaging
import requests


def download_package(package, directory, pypi="https://test.pypi.org", pre=False):
    """
    Download `package` from `pypi` in `directory`.
    """
    project = requests.get(f"{pypi}/pypi/{package}/json").json()
    if pre:
        version = sorted(project["releases"], key=packaging.version.parse)[-1]
    else:
        version = project["info"]["version"]
    release = project["releases"][version]

    for dist in release:
        dest = os.path.join(directory, dist["url"].rsplit("/", 1)[-1])
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
