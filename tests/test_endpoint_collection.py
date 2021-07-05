from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

from daemon import endpoint_collection


class TestEndpointCollection(IsolatedAsyncioTestCase):
    async def test__format_docs(self):
        # noinspection PyUnusedLocal
        @endpoint_collection.format_docs
        def func(param1, param2):
            """
            description

            foo bar
            baz

            :param param1: asdf
            :param param2: qwerty
            :return: something
            """

            pass

        self.assertEqual(
            "description\n\nfoo bar\nbaz\n\n"
            "**Parameters:**\n- **param1:** asdf\n- **param2:** qwerty\n\n"
            "**Returns:** something",
            func.__doc__,
        )

    async def test__default_parameter(self):
        default = MagicMock()

        @endpoint_collection.default_parameter(default)
        def func(foo, bar, baz, xy=42, test=True):
            return foo, bar, baz, xy, test

        result = func()

        self.assertEqual((default, default, default, 42, True), result)

    @patch("daemon.endpoint_collection.Body")
    @patch("daemon.endpoint_collection.default_parameter")
    @patch("daemon.endpoint_collection.Depends")
    async def test__dependency(
        self,
        depends_patch: MagicMock,
        default_parameter_patch: MagicMock,
        body_patch: MagicMock,
    ):
        f = MagicMock()

        result = endpoint_collection.dependency(f)

        body_patch.assert_called_once_with(...)
        default_parameter_patch.assert_called_once_with(body_patch())
        default_parameter_patch().assert_called_once_with(f)
        depends_patch.assert_called_once_with(default_parameter_patch()())
        self.assertEqual(depends_patch(), result)
