import sys
from io import StringIO

import pytest

from pytorch_wheel_installer import __version__, cli, computation_backend


@pytest.fixture
def patch_argv(mocker):
    def patch(*args):
        return mocker.patch.object(sys, "argv", ["pwi", *args])

    return patch


def test_parse_input_smoke(subtests, patch_argv):
    distributions = ("torch", "torchvision")
    patch_argv(*distributions)

    args = cli.parse_input()

    with subtests.test("distributions"):
        assert "distributions" in args
        assert distributions == tuple(args.distributions)

    with subtests.test("computation_backend"):
        assert "computation_backend" in args
        assert isinstance(args.computation_backend, (type(None), str))

    with subtests.test("no_install"):
        assert "no_install" in args
        assert isinstance(args.no_install, bool)

    with subtests.test("install_cmd"):
        assert "install_cmd" in args
        assert isinstance(args.install_cmd, str)


def test_parse_input_computation_backend(subtests, patch_argv):
    for arg in ("-b", "--computation-backend"):
        with subtests.test(arg=arg):
            patch_argv(arg, "cu42", "foo")

            args = cli.parse_input()

            assert isinstance(
                args.computation_backend, computation_backend.ComputationBackend
            )


def test_entry_point_help_smoke(subtests, mocker, patch_argv):
    for arg in ("-h", "--help"):
        with subtests.test(arg=arg):
            patch_argv(arg)
            stdout = mocker.patch.object(sys, "stdout", StringIO())

            with pytest.raises(SystemExit) as info:
                cli.entry_point()

            code = info.value.code
            assert code is None or code == 0

            assert stdout.getvalue().strip()


def test_entry_point_version(subtests, mocker, patch_argv):
    for arg in ("-v", "--version"):
        with subtests.test(arg=arg):
            patch_argv(arg)
            stdout = mocker.patch.object(sys, "stdout", StringIO())

            with pytest.raises(SystemExit) as info:
                cli.entry_point()

            code = info.value.code
            assert code is None or code == 0

            out = stdout.getvalue().strip()
            assert out == f"pytorch_wheel_installer=={__version__}"


def test_entry_point_no_distributions(mocker, patch_argv):
    patch_argv()
    mocker.patch("pytorch_wheel_installer.cli.find_links", side_effect=RuntimeError)

    with pytest.raises(SystemExit) as info:
        cli.entry_point()

    code = info.value.code
    assert code is None or code == 0


def test_entry_point_no_install(subtests, mocker, patch_argv):
    links = [
        "https://download.pytorch.org/foo.whl",
        "https://download.pytorch.org/bar.whl",
    ]
    mocker.patch("pytorch_wheel_installer.cli.find_links", return_value=links)

    for arg in ("-n", "--no-install"):
        with subtests.test(arg=arg):
            patch_argv(arg, "baz")
            stdout = mocker.patch.object(sys, "stdout", StringIO())

            with pytest.raises(SystemExit) as info:
                cli.entry_point()

            code = info.value.code
            assert code is None or code == 0

            out = stdout.getvalue().strip()
            assert "\n".join(links) == out


def test_entry_point_install_cmd(subtests, mocker, patch_argv):
    links = [
        "https://download.pytorch.org/foo.whl",
        "https://download.pytorch.org/bar.whl",
    ]
    mocker.patch("pytorch_wheel_installer.cli.find_links", return_value=links)

    install_cmd = "custom install cmd"

    for arg in ("-c", "--install-cmd"):
        with subtests.test(arg=arg):
            patch_argv(arg, install_cmd, "baz")
            check_call_mock = mocker.patch(
                "pytorch_wheel_installer.cli.subprocess.check_call"
            )

            cli.entry_point()

            cmd = check_call_mock.call_args[0][0]
            assert cmd == " ".join((install_cmd, *links))


def test_get_help_no_help():
    with pytest.raises(RuntimeError):
        cli.get_help("no_help_available")
