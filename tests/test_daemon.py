from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from fastapi import HTTPException

from daemon import daemon
from tests._utils import import_module, AsyncMock, mock_dict


class TestDaemon(IsolatedAsyncioTestCase):
    def get_decorated_function(self, fastapi_patch: MagicMock, decorator_name, *decorator_args, **decorator_kwargs):
        functions = []
        decorator = MagicMock(side_effect=functions.append)
        getattr(fastapi_patch(), decorator_name).side_effect = (
            lambda *args, **kwargs: decorator if (args, kwargs) == (decorator_args, decorator_kwargs) else MagicMock()
        )
        fastapi_patch.reset_mock()

        module = import_module("daemon.daemon")

        decorator.assert_called_once()
        self.assertEqual(1, len(functions))
        return module, functions[0]

    @patch("daemon.endpoints.register_collections")
    @patch("fastapi.FastAPI")
    async def test__global_vars(self, fastapi_patch: MagicMock, register_collections_patch: MagicMock):
        module = import_module("daemon.daemon")

        fastapi_patch.assert_called_once_with(title="Python Daemon")
        self.assertEqual(fastapi_patch(), module.app)
        register_collections_patch.assert_called_once_with(fastapi_patch())
        self.assertEqual(register_collections_patch(), module.endpoints)

    @patch("daemon.database.db")
    @patch("fastapi.FastAPI")
    async def test__db_session(self, fastapi_patch: MagicMock, db_patch: MagicMock):
        _, db_session = self.get_decorated_function(fastapi_patch, "middleware", "http")

        events = []
        db_patch.create_session.side_effect = lambda: events.append(0)
        expected = MagicMock()
        call_next = AsyncMock(side_effect=lambda _: events.append(1) or expected)
        request = MagicMock()
        db_patch.commit = AsyncMock(side_effect=lambda: events.append(2))
        db_patch.close = AsyncMock(side_effect=lambda: events.append(3))

        result = await db_session(request, call_next)

        self.assertEqual([0, 1, 2, 3], events)
        call_next.assert_called_once_with(request)
        self.assertEqual(expected, result)

    @patch("fastapi.FastAPI")
    async def test__on_startup__no_tables(self, fastapi_patch: MagicMock):
        module, on_startup = self.get_decorated_function(fastapi_patch, "on_event", "startup")

        module.SQL_CREATE_TABLES = False
        db = module.db = AsyncMock()

        await on_startup()

        db.create_tables.assert_not_called()

    @patch("fastapi.FastAPI")
    async def test__on_startup__create_tables(self, fastapi_patch: MagicMock):
        module, on_startup = self.get_decorated_function(fastapi_patch, "on_event", "startup")

        module.SQL_CREATE_TABLES = True
        db = module.db = AsyncMock()

        await on_startup()

        db.create_tables.assert_called_once_with()

    @patch("daemon.endpoint_collection.format_docs")
    @patch("daemon.schemas.daemon.EndpointCollectionModel")
    @patch("daemon.utils.responses")
    @patch("daemon.authorization.HTTPAuthorization")
    @patch("fastapi.params.Depends")
    @patch("fastapi.FastAPI")
    async def test__daemon_endpoints(
        self,
        fastapi_patch: MagicMock,
        depends_patch: MagicMock,
        httpauthorization_patch: MagicMock,
        responses_patch: MagicMock,
        endpoint_collection_model_patch: MagicMock,
        format_docs_patch: MagicMock,
    ):
        format_docs_patch.side_effect = lambda f: setattr(f, "docs_formatted", True) or f  # noqa: B010
        module, daemon_endpoints = self.get_decorated_function(
            fastapi_patch,
            "get",
            "/daemon/endpoints",
            name="List Daemon Endpoints",
            tags=["daemon"],
            dependencies=[[depends_patch(), depends_patch.reset_mock()][0]],
            responses=[responses_patch(), responses_patch.reset_mock()][0],
        )

        httpauthorization_patch.assert_called_once_with()
        depends_patch.assert_called_once_with(httpauthorization_patch())
        responses_patch.assert_called_once_with(list[endpoint_collection_model_patch])
        self.assertEqual(True, daemon_endpoints.docs_formatted)

        module.endpoints = MagicMock()
        self.assertEqual(module.endpoints, await daemon_endpoints())

    @patch("daemon.daemon.JSONResponse")
    @patch("daemon.daemon.HTTPException")
    async def test__make_exception(self, httpexception_patch: MagicMock, jsonresponse_patch: MagicMock):
        status_code = MagicMock()
        kwargs = mock_dict(5, True)

        result = daemon._make_exception(status_code, **kwargs)

        httpexception_patch.assert_called_once_with(status_code)
        jsonresponse_patch.assert_called_once_with(
            {**kwargs, "error": f"{status_code} {httpexception_patch().detail}"},
            status_code,
        )
        self.assertEqual(jsonresponse_patch(), result)

    @patch("daemon.exceptions.api_exception.APIException")
    @patch("fastapi.FastAPI")
    async def test__handle_api_exception(self, fastapi_patch: MagicMock, apiexception_patch: MagicMock):
        _, handle_api_exception = self.get_decorated_function(fastapi_patch, "exception_handler", apiexception_patch)
        exception = MagicMock()

        result = await handle_api_exception(..., exception)

        exception.make_response.assert_called_once_with()
        self.assertEqual(exception.make_response(), result)

    @patch("fastapi.exceptions.HTTPException")
    @patch("fastapi.FastAPI")
    async def test__handle_http_exception(self, fastapi_patch: MagicMock, httpexception_patch: MagicMock):
        module, handle_http_exception = self.get_decorated_function(
            fastapi_patch,
            "exception_handler",
            httpexception_patch,
        )
        exception = MagicMock()
        _make_exception, module._make_exception = module._make_exception, MagicMock()

        result = await handle_http_exception(..., exception)

        module._make_exception.assert_called_once_with(exception.status_code)
        self.assertEqual(module._make_exception(), result)
        module._make_exception = _make_exception

    @patch("fastapi.exceptions.RequestValidationError")
    @patch("fastapi.FastAPI")
    async def test__handle_unprocessable_entity(
        self,
        fastapi_patch: MagicMock,
        request_validation_error_patch: MagicMock,
    ):
        module, handle_unprocessable_entity = self.get_decorated_function(
            fastapi_patch,
            "exception_handler",
            request_validation_error_patch,
        )
        exception = MagicMock()
        _make_exception, module._make_exception = module._make_exception, MagicMock()

        result = await handle_unprocessable_entity(..., exception)

        exception.errors.assert_called_once_with()
        module._make_exception.assert_called_once_with(422, detail=exception.errors())
        self.assertEqual(module._make_exception(), result)
        module._make_exception = _make_exception

    @patch("fastapi.FastAPI")
    async def test__handle_internal_server_error(self, fastapi_patch: MagicMock):
        module, handle_internal_server_error = self.get_decorated_function(
            fastapi_patch,
            "exception_handler",
            Exception,
        )
        exception = MagicMock()
        _make_exception, module._make_exception = module._make_exception, MagicMock()

        result = await handle_internal_server_error(..., exception)

        module._make_exception.assert_called_once_with(500)
        self.assertEqual(module._make_exception(), result)
        module._make_exception = _make_exception

    @patch("fastapi.FastAPI")
    async def test__handle_not_found(self, fastapi_patch: MagicMock):
        module, handle_not_found = self.get_decorated_function(
            fastapi_patch,
            "get",
            "/{_:path}",
            include_in_schema=False,
        )

        with self.assertRaises(HTTPException) as context:
            await handle_not_found()

        self.assertEqual(404, context.exception.status_code)
