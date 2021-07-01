from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from daemon import utils


class TestUtils(IsolatedAsyncioTestCase):
    async def test__responses(self):
        default = MagicMock()

        def make_exception(status_code):
            out = MagicMock()
            out.__name__ = MagicMock()
            out.status_code = status_code
            return out

        args = [a := make_exception(401), b := make_exception(403), c := make_exception(403), d := make_exception(404)]

        # noinspection PyTypeChecker
        result = utils.responses(default, *args)

        a.assert_called_once_with()
        a().make_dict.assert_called_once_with()
        b.assert_called_once_with()
        b().make_dict.assert_called_once_with()
        c.assert_called_once_with()
        c().make_dict.assert_called_once_with()
        d.assert_called_once_with()
        d().make_dict.assert_called_once_with()
        self.assertEqual(
            {
                200: {"model": default},
                401: {
                    "description": b"Unauthorized",
                    "content": {
                        "application/json": {
                            "examples": {a.__name__: {"description": a.description, "value": a().make_dict()}},
                        },
                    },
                },
                403: {
                    "description": b"Forbidden",
                    "content": {
                        "application/json": {
                            "examples": {
                                f"{b.__name__} (1/2)": {"description": b.description, "value": b().make_dict()},
                                f"{c.__name__} (2/2)": {"description": c.description, "value": c().make_dict()},
                            },
                        },
                    },
                },
                404: {
                    "description": b"Not Found",
                    "content": {
                        "application/json": {
                            "examples": {d.__name__: {"description": d.description, "value": d().make_dict()}},
                        },
                    },
                },
            },
            result,
        )

    async def test__get_example(self):
        arg = MagicMock()
        arg.Config.schema_extra = {"example": (expected := MagicMock())}

        result = utils.get_example(arg)

        self.assertEqual(expected, result)
