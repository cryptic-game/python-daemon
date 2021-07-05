from unittest import IsolatedAsyncioTestCase

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
