import itertools

import pytest

from pytorch_wheel_installer import utils

from .utils import cycle_over


# TODO: use fixtures
def test_Language_parse():
    desireds = {
        "cp36": (3, 6),
        "cp37": (3, 7),
        "cp38": (3, 8),
        "py3": (3, None),
        "py36": (3, 6),
        "py37": (3, 7),
        "py38": (3, 8),
    }
    for language_str, desired in desireds.items():
        actual = utils.Language.parse(language_str)
        assert actual == desired


# TODO: use fixtures
def test_Language_eq():
    py3s_with_minor = tuple(utils.Language(f"py3{minor}") for minor in (6, 7, 8))
    py2 = utils.Language("py2")
    py3 = utils.Language("py3")

    for language, other_languages in cycle_over(py3s_with_minor):
        for other_language in other_languages:
            assert language != other_language

    for language in py3s_with_minor:
        assert language != py2
        assert language == py3


# TODO: use fixtures
def test_Language_eq_str():
    language_strs = ("cp36", "cp37", "cp38", "py3", "py36", "py37", "py38")
    for language_str in language_strs:
        language = utils.Language(language_str)
        assert language == language_str


# TODO: use fixtures
def test_Language_str():
    desireds = {
        "cp36": "3.6",
        "cp37": "3.7",
        "cp38": "3.8",
        "py3": "3",
        "py36": "3.6",
        "py37": "3.7",
        "py38": "3.8",
    }
    for language_str, desired in desireds.items():
        assert str(utils.Language(language_str)) == desired


@pytest.fixture(scope="module")
def linux_platform_strs():
    return ("Linux", "linux_x86_64")


@pytest.fixture(scope="module")
def linux_platforms(linux_platform_strs):
    return tuple(utils.Platform(platform_str) for platform_str in linux_platform_strs)


@pytest.fixture(scope="module")
def windows_platform_strs():
    return ("Windows", "win_amd64")


@pytest.fixture(scope="module")
def windows_platforms(windows_platform_strs):
    return tuple(utils.Platform(platform_str) for platform_str in windows_platform_strs)


@pytest.fixture(scope="module")
def macos_platform_strs():
    return ("Darwin", "macosx_10_6_x86_64", "macosx_10_9_x86_64")


@pytest.fixture(scope="module")
def macos_platforms(macos_platform_strs):
    return tuple(utils.Platform(platform_str) for platform_str in macos_platform_strs)


@pytest.fixture(scope="module")
def platform_strs(linux_platform_strs, windows_platform_strs, macos_platform_strs):
    return (*linux_platform_strs, *windows_platform_strs, *macos_platform_strs)


@pytest.fixture(scope="module")
def platforms(platform_strs):
    return tuple(utils.Platform(platform_str) for platform_str in platform_strs)


def test_Platform_parse_linux(linux_platform_strs):
    for platform_str in linux_platform_strs:
        assert utils.Platform.parse(platform_str) == "linux"


def test_Platform_parse_windows(windows_platform_strs):
    for platform_str in windows_platform_strs:
        assert utils.Platform.parse(platform_str) == "windows"


def test_Platform_parse_macos(macos_platform_strs):
    for platform_str in macos_platform_strs:
        assert utils.Platform.parse(platform_str) == "macos"


def test_Platform_parse_other():
    assert utils.Platform.parse("any") is None


def test_Platform_eq(linux_platforms, windows_platforms, macos_platforms):
    for platforms in (linux_platforms, windows_platforms, macos_platforms):
        for platform, other_platforms in cycle_over(platforms):
            for other_platform in other_platforms:
                assert platform == other_platform

    platform = utils.Platform("any")
    for other_platform in itertools.chain(
        linux_platforms, windows_platforms, macos_platforms
    ):
        assert platform == other_platform


def test_Platform_neq(linux_platforms, windows_platforms, macos_platforms):
    platforms = (linux_platforms[0], windows_platforms[0], macos_platforms[0])
    for platform, other_platforms in cycle_over(platforms):
        for other_platform in other_platforms:
            assert platform != other_platform


def test_Platform_eq_str(platform_strs):
    for platform_str in platform_strs:
        platform = utils.Platform(platform_str)
        assert platform == platform_str


def test_Platform_str_linux(linux_platform_strs):
    for platform_str in linux_platform_strs:
        assert str(utils.Platform(platform_str)) == "linux"


def test_Platform_str_windows(windows_platform_strs):
    for platform_str in windows_platform_strs:
        assert str(utils.Platform(platform_str)) == "windows"


def test_Platform_str_macos(macos_platform_strs):
    for platform_str in macos_platform_strs:
        assert str(utils.Platform(platform_str)) == "macos"


def test_Platform_str_other():
    assert str(utils.Platform("any")) == "None"
