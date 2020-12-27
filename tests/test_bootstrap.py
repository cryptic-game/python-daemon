from unittest import TestCase
from unittest.mock import patch

import bootstrap


class TestBootstrap(TestCase):
    @patch("sentry_sdk.init")
    @patch("bootstrap.SENTRY_DSN", None)
    def test__setup_sentry__skip(self, sentry_init_patch):
        bootstrap.setup_sentry()
        sentry_init_patch.assert_not_called()

    @patch("sentry_sdk.init")
    @patch("bootstrap.SENTRY_DSN")
    def test__setup_sentry__setup(self, sentry_dsn_patch, sentry_init_patch):
        bootstrap.setup_sentry()
        sentry_init_patch.assert_called_with(dsn=sentry_dsn_patch, attach_stacktrace=True, shutdown_timeout=5)

    @patch("sys.exit")
    @patch("bootstrap.print")
    @patch("bootstrap.API_TOKEN", "something")
    def test__check_api_token__skip(self, print_patch, exit_patch):
        bootstrap.check_api_token()
        print_patch.assert_not_called()
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("bootstrap.print")
    @patch("bootstrap.API_TOKEN", None)
    @patch("bootstrap.DEBUG", True)
    def test__check_api_token__debug(self, print_patch, exit_patch):
        print_calls = []
        print_patch.side_effect = print_calls.append

        bootstrap.check_api_token()
        output = print_calls.pop().lower()
        self.assertIn("no api token specified", output)
        self.assertIn("endpoints can be accessed without authentication", output)
        self.assertFalse(print_calls)
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("bootstrap.print")
    @patch("bootstrap.API_TOKEN", None)
    @patch("bootstrap.DEBUG", False)
    def test__check_api_token__production(self, print_patch, exit_patch):
        print_calls = []
        print_patch.side_effect = print_calls.append

        bootstrap.check_api_token()
        output = print_calls.pop().lower()
        self.assertIn("no api token specified", output)
        self.assertFalse(print_calls)
        exit_patch.assert_called_with(1)

    @patch("database.db.Base.metadata.create_all")
    @patch("bootstrap.SQL_CREATE_TABLES", False)
    def test__create_tables__skip(self, create_all_patch):
        bootstrap.create_tables()
        create_all_patch.assert_not_called()

    @patch("database.db.Base.metadata.create_all")
    @patch("database.db.engine")
    @patch("bootstrap.SQL_CREATE_TABLES", True)
    def test__create_tables__create(self, engine_patch, create_all_patch):
        bootstrap.create_tables()
        create_all_patch.assert_called_with(engine_patch)

    @patch("bootstrap.run_daemon")
    @patch("bootstrap.create_tables")
    @patch("bootstrap.check_api_token")
    @patch("bootstrap.setup_sentry")
    def test__bootstrap(self, *args):
        calls = []
        for func in args:
            func.side_effect = lambda f=func: calls.append(f)

        bootstrap.bootstrap()

        for func in args:
            self.assertEqual(func, calls.pop(0))
        self.assertFalse(calls)
