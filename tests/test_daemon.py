from unittest import TestCase
from unittest.mock import patch, Mock

from fastapi import HTTPException

from utils import import_module


def import_daemon():
    return import_module("daemon")


class TestDaemon(TestCase):
    @patch("endpoints.register_collections")
    @patch("fastapi.FastAPI")
    def test__app(self, fastapi_patch, register_collections_patch):
        daemon = import_daemon()

        fastapi_patch.assert_called_with()
        self.assertEqual(fastapi_patch(), daemon.app)

        register_collections_patch.assert_called_with(daemon.app)
        self.assertEqual(register_collections_patch(), daemon.endpoints)

    def test__daemon_endpoints(self):
        daemon = import_daemon()

        result = daemon.daemon_endpoints()
        self.assertEqual(daemon.endpoints, result)

    @patch("fastapi.responses.JSONResponse")
    def test__make_exception(self, json_response_patch):
        daemon = import_daemon()

        result = daemon._make_exception(418, foo="bar", test=42)
        json_response_patch.assert_called_with({"foo": "bar", "test": 42, "error": "418 I'm a Teapot"}, 418)
        self.assertEqual(json_response_patch(), result)

    def test__handle_http_exception(self):
        daemon = import_daemon()
        daemon._make_exception = make_exception = Mock()

        result = daemon.handle_http_exception(None, exception := Mock())
        make_exception.assert_called_with(exception.status_code)
        self.assertEqual(make_exception(), result)

    def test__handle_unprocessable_entity(self):
        daemon = import_daemon()
        daemon._make_exception = make_exception = Mock()

        result = daemon.handle_unprocessable_entity(None, exception := Mock())
        make_exception.assert_called_with(422, detail=exception.errors())
        self.assertEqual(make_exception(), result)

    def test__handle_internal_server_error(self):
        daemon = import_daemon()
        daemon._make_exception = make_exception = Mock()

        result = daemon.handle_internal_server_error(None, None)
        make_exception.assert_called_with(500)
        self.assertEqual(make_exception(), result)

    def test__handle_not_found(self):
        daemon = import_daemon()

        with self.assertRaises(HTTPException) as exc:
            daemon.handle_not_found()
        self.assertEqual(404, exc.exception.status_code)

    @patch("uvicorn.run")
    def test__run_daemon(self, uvicorn_run_patch):
        daemon = import_daemon()
        daemon.HOST = host = Mock()
        daemon.PORT = port = Mock()
        daemon.DEBUG = debug = Mock()

        daemon.run_daemon()

        uvicorn_run_patch.assert_called_with("daemon:app", host=host, port=port, reload=debug)
