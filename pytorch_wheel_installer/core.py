import re
from collections import namedtuple
from typing import Any, Iterable, List, Union
from urllib.parse import urljoin
from urllib.request import urlopen

from .utils import Backend, Language, Platform

__all__ = ["find_links"]

Whl = namedtuple(
    "whl", ("distribution", "version", "backend", "language", "platform", "url")
)

BACKEND_PATTERN = r"((?P<backend>(cpu|cu\d+))/)?"
DISTRIBUTION_PATTERN = r"(?P<distribution>torch(vision|audio|text)?)"
VERSION_PATTERN = r"(?P<version>\d+[.]\d+([.]\d+)?([.]post\d+)?)(%2B(cpu|cu\d+))?"
LANGUAGE_PATTERN = r"(?P<language>\w+)-\w+"
PLATFORM_PATTERN = r"(?P<platform>\w+)"
FILE_PATTERN = re.compile(
    (
        fr"^"
        fr"{BACKEND_PATTERN}"
        fr"{DISTRIBUTION_PATTERN}-"
        fr"{VERSION_PATTERN}-"
        fr"{LANGUAGE_PATTERN}-"
        fr"{PLATFORM_PATTERN}"
        fr"[.]whl$"
    )
)


def find_links(
    distributions: Union[Iterable[str], str],
    backend: Union[Backend, str],
    language: Union[Language, str],
    platform: Union[Platform, str],
) -> List[str]:
    if isinstance(distributions, str):
        distributions = distributions.split(",")
    if isinstance(backend, str):
        backend = Backend(backend)
    if isinstance(language, str):
        language = Language(language)
    if isinstance(platform, str):
        platform = Platform(platform)

    urls = extract_whl_files()
    whls = parse_whl_files(urls)

    return [
        select_whl(whls, distribution, backend, language, platform).url
        for distribution in distributions
    ]


def extract_whl_files(
    base: str = "https://download.pytorch.org/whl/", html: str = "torch_stable.html",
) -> List[str]:
    content = urlopen(urljoin(base, html)).read().decode("utf-8")
    pattern = re.compile('^<a href="[^"]*">(?P<file>[^<]*)</a><br>$')
    files = []
    for html_group in content.split("\n"):
        match = pattern.match(html_group)
        if match is not None:
            files.append(match.group("file"))
    return files


def parse_whl_files(
    files: Iterable[str], base: str = "https://download.pytorch.org/whl/"
) -> List[Whl]:
    whls = []
    for file in files:
        match = FILE_PATTERN.match(file)
        if match is not None:
            whls.append(
                Whl(
                    distribution=match.group("distribution"),
                    version=match.group("version"),
                    backend=Backend(match.group("backend")),
                    language=Language(match.group("language")),
                    platform=Platform(match.group("platform")),
                    url=urljoin(base, file),
                )
            )
    return whls


def select_whl(
    whls: Iterable[Whl],
    distribution: str,
    backend: Backend,
    language: Language,
    platform: Platform,
) -> Whl:
    def select(whls: Iterable[Whl], attr: str, val: Any) -> List[Whl]:
        selected_whls = [whl for whl in whls if getattr(whl, attr) == val]
        if selected_whls:
            return selected_whls

        valid_vals = {getattr(whl, attr) for whl in whls}
        msg = (
            f"'{val}' is invalid for attribute '{attr}'. "
            f"Valid values are ({', '.join(valid_vals)})"
        )
        raise RuntimeError(msg)

    whls = select(whls, "distribution", distribution)
    whls = select(whls, "backend", backend)
    whls = select(whls, "language", language)
    whls = select(whls, "platform", platform)

    return sorted(whls, key=lambda whl: whl.version)[-1]
