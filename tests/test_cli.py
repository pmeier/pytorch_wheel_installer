import sys

from pytorch_wheel_installer import cli


def test_parse_input_smoke(subtests, mocker):
    distributions = ("torch", "torchvision")
    mocker.patch.object(sys, "argv", ["pwi", *distributions])

    args = cli.parse_input()

    with subtests.test("distributions"):
        assert "distributions" in args
        assert distributions == tuple(args.distributions)

    with subtests.test("computation_backend"):
        assert "computation_backend" in args
        assert isinstance(args.computation_backend, (None, str))

    with subtests.test("no_install"):
        assert "no_install" in args
        assert isinstance(args.no_install, bool)

    with subtests.test("install_cmd"):
        assert "install_cmd" in args
        assert isinstance(args.install_cmd, str)
