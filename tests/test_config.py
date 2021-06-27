from unittest.case import TestCase
from unittest.mock import patch

from environment import get_bool
from utils import import_module


class TestConfig(TestCase):
    @patch("os.getenv")
    def test__get_bool(self, get_env_patch):
        for k in ("true", "t", "yes", "y", "1"):
            get_env_patch.return_value = k
            self.assertEqual(True, get_bool("test", False))
        for k in ("false", "f", "no", "n", "0"):
            get_env_patch.return_value = k
            self.assertEqual(False, get_bool("test", True))

    @patch("os.getenv")
    def test__env_vars(self, get_env_patch):
        get_env_patch.side_effect = lambda k, d=None: d
        config = import_module("config")

        for key, default in [
            ("API_TOKEN", None),
            ("HOST", "0.0.0.0"),  # noqa: S104
            ("PORT", 8000),
            ("DEBUG", False),
            ("SQL_SERVER_LOCATION", "postgresql://localhost:5432"),
            ("SQL_SERVER_DATABASE", "cryptic"),
            ("SQL_SERVER_USERNAME", "cryptic"),
            ("SQL_SERVER_PASSWORD", "cryptic"),
            ("SQL_SHOW_STATEMENTS", False),
            ("SQL_CREATE_TABLES", False),
            ("SENTRY_DSN", None),
        ]:
            self.assertEqual(default, getattr(config, key))
