from io import BytesIO
from unittest import mock

import pytest
import requests

from pytorch_wheel_installer import core


@mock.patch("pytorch_wheel_installer.core.urlopen")
def test_extract_wheel_files(urlopen_mock):
    files = [f"file{idx}" for idx in range(3)]

    fmtstr = '<a href="href">{}</a><br>'
    content = "\n".join([fmtstr.format(file) for file in files]).encode("utf-8")

    class MockedBytesIO(BytesIO):
        def read(self):
            return content

    urlopen_mock.return_value = MockedBytesIO()

    assert core.extract_whl_files() == files


@pytest.mark.slow
def test_parse_wheel_files_smoke():
    files = core.extract_whl_files()
    for whl in core.parse_whl_files(files):
        url = whl.url
        if url == "https://download.pytorch.org/whl/torchtext-0.5.0-py3-none-any.whl":
            # see https://github.com/pytorch/text/issues/826
            continue
        response = requests.head(url)
        assert (
            response.status_code == 200
        ), f"Requesting {url} returned status code {response.status_code}."


def test_distributions_smoke():
    backend = "cpu"
    language = "py36"
    platform = "linux"

    files = core.extract_whl_files()
    whls = core.parse_whl_files(files)

    for distribution in ("torch", "torchvision", "torchaudio", "torchtext"):
        core.select_whl(whls, distribution, backend, language, platform)
