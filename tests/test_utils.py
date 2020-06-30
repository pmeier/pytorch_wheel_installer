import pytest

from pytorch_wheel_installer import utils


def test_get_public_or_private_attr(subtests):
    with subtests.test("public attribute"):

        class ObjWithPublicAttribute:
            attr = None

        obj = ObjWithPublicAttribute()
        assert utils.get_public_or_private_attr(obj, "attr") is None

    with subtests.test("private attribute"):

        class ObjWithPrivateAttribute:
            _attr = None

        obj = ObjWithPrivateAttribute()
        assert utils.get_public_or_private_attr(obj, "attr") is None

    with subtests.test("no attribute"):

        class ObjWithoutAttribute:
            pass

        obj = ObjWithoutAttribute()

        with pytest.raises(AttributeError):
            utils.get_public_or_private_attr(obj, "attr")
