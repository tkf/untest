from ..downloader import download_package


def test_download_package(tmp_path):
    download_package("requests", str(tmp_path))
