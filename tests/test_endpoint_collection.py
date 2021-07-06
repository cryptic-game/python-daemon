import itertools
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

from fastapi import APIRouter
from fastapi.params import Depends

from daemon import endpoint_collection
from tests._utils import mock_list, mock_dict


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

    @patch("daemon.endpoint_collection.str")
    async def test__get_user(self, str_patch: MagicMock):
        user_id = MagicMock()

        result = await endpoint_collection.get_user.dependency(user_id)

        str_patch.assert_called_once_with(user_id)
        self.assertEqual(str_patch(), result)
        self.assertIsInstance(endpoint_collection.get_user, Depends)

    @patch("daemon.endpoint_collection.HTTPAuthorization")
    @patch("daemon.endpoint_collection.Depends")
    @patch("daemon.endpoint_collection.super")
    async def test__constructor(
        self,
        super_patch: MagicMock,
        depends_patch: MagicMock,
        httpauthorization_patch: MagicMock,
    ):
        super_patch.return_value = type("", (), {"__init__": MagicMock(return_value=None)})

        self.assertTrue(issubclass(endpoint_collection.EndpointCollection, APIRouter))

        for disabled, test, debug in itertools.product([False, True], repeat=3):
            super_patch().__init__.reset_mock()
            super_patch.reset_mock()
            httpauthorization_patch.reset_mock()
            depends_patch.reset_mock()

            with self.subTest(disabled=disabled, test=test, debug=debug):
                name = MagicMock()
                description = MagicMock()
                endpoint_collection.DEBUG = debug

                result = endpoint_collection.EndpointCollection(name, description, disabled=disabled, test=test)

                httpauthorization_patch.assert_called_once_with()
                depends_patch.assert_called_once_with(httpauthorization_patch())
                super_patch.assert_called_once_with()
                super_patch().__init__.assert_called_once_with(
                    prefix=f"/{name}",
                    tags=[f"[TEST] {name}" if test else name],
                    dependencies=[depends_patch()],
                )
                self.assertEqual(name, result._name)
                self.assertEqual(description, result._description)
                self.assertEqual(test, result._test)
                self.assertEqual(disabled or test and not debug, result._disabled)
                self.assertEqual([], result._endpoints)

    @patch("daemon.endpoint_collection.Body")
    @patch("daemon.endpoint_collection.default_parameter")
    @patch("daemon.endpoint_collection.format_docs")
    async def test__endpoint(
        self,
        format_docs_patch: MagicMock,
        default_parameter_patch: MagicMock,
        body_patch: MagicMock,
    ):
        for disabled, collection_test, test, debug, name_from_func in itertools.product([False, True], repeat=5):
            format_docs_patch.reset_mock()
            default_parameter_patch.reset_mock()
            body_patch.reset_mock()

            with self.subTest(
                disabled=disabled,
                collection_test=collection_test,
                test=test,
                debug=debug,
                name_from_func=name_from_func,
            ):

                collection = MagicMock(_test=collection_test)
                name = MagicMock()
                args = mock_list(5)
                kwargs = mock_dict(5, True)
                func = MagicMock()
                func.__name__ = MagicMock()
                func.__doc__ = """
                foo bar baz
                hello world

                asdf
                xyz

                42 1337
                """
                func.__doc__ = func.__doc__.replace("\n\n", "\n    \n")
                default_parameter_patch()().__name__ = str(MagicMock())
                default_parameter_patch.reset_mock()
                endpoint_collection.DEBUG = debug

                result = endpoint_collection.EndpointCollection.endpoint(
                    collection,
                    None if name_from_func else name,
                    *args,
                    disabled=disabled,
                    test=test,
                    **kwargs,
                )(func)

                if disabled or (test or collection_test) and not debug:
                    self.assertIs(result, func)
                    collection._endpoints.append.assert_not_called()
                    collection.post.assert_not_called()
                    continue

                if name_from_func:
                    name = func.__name__

                collection._endpoints.append.assert_called_once_with(
                    endpoint_collection.Endpoint(name, "foo bar baz hello world"),
                )

                format_docs_patch.assert_called_once_with(func)
                body_patch.assert_called_once_with(...)
                default_parameter_patch.assert_called_once_with(body_patch())
                default_parameter_patch().assert_called_once_with(format_docs_patch())
                collection.post.assert_called_once_with(
                    f"/{name}",
                    name="[TEST] " * (test or collection_test) + default_parameter_patch()().__name__,
                    *args,
                    **kwargs,
                )
                collection.post().assert_called_once_with(default_parameter_patch()())
                self.assertEqual(collection.post()(), result)

    async def test__name(self):
        collection = MagicMock()
        # noinspection PyArgumentList
        self.assertEqual(collection._name, endpoint_collection.EndpointCollection.name.fget(collection))

    async def test__description(self):
        collection = MagicMock()
        # noinspection PyArgumentList
        self.assertEqual(collection._description, endpoint_collection.EndpointCollection.description.fget(collection))

    async def test__register__disabled(self):
        app = MagicMock()
        collection = MagicMock(_disabled=True)

        result = endpoint_collection.EndpointCollection.register(collection, app)

        app.include_router.assert_not_called()
        self.assertIs(result, None)

    async def test__register__enabled(self):
        app = MagicMock()
        collection = MagicMock(_disabled=False, _endpoints=mock_list(5))

        result = endpoint_collection.EndpointCollection.register(collection, app)

        app.include_router.assert_called_once_with(collection)
        self.assertEqual(
            {
                "id": collection.name,
                "description": collection.description,
                "disabled": False,
                "endpoints": [
                    {"id": endpoint.name, "description": endpoint.description, "disabled": False}
                    for endpoint in collection._endpoints
                ],
            },
            result,
        )
