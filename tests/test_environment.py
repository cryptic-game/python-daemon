from collections import namedtuple
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from daemon import environment
from tests._utils import import_module

EnvironmentVariable = namedtuple("EnvironmentVariable", ["dtype", "name", "default"])

VARIABLES: dict[str, EnvironmentVariable] = {
    "LOG_LEVEL": EnvironmentVariable(str, "LOG_LEVEL", "INFO"),
    "HOST": EnvironmentVariable(str, "HOST", "0.0.0.0"),  # noqa: S104
    "PORT": EnvironmentVariable(int, "PORT", 8000),
    "RELOAD": EnvironmentVariable(bool, "RELOAD", False),
    "DEBUG": EnvironmentVariable(bool, "DEBUG", False),
    "API_TOKEN": EnvironmentVariable(str, "API_TOKEN", None),
    "DB_DRIVER": EnvironmentVariable(str, "SQL_DRIVER", "postgresql+asyncpg"),
    "DB_HOST": EnvironmentVariable(str, "SQL_HOST", "localhost"),
    "DB_PORT": EnvironmentVariable(int, "SQL_PORT", 5432),
    "DB_DATABASE": EnvironmentVariable(str, "SQL_DATABASE", "cryptic"),
    "DB_USERNAME": EnvironmentVariable(str, "SQL_USERNAME", "cryptic"),
    "DB_PASSWORD": EnvironmentVariable(str, "SQL_PASSWORD", "cryptic"),
    "POOL_RECYCLE": EnvironmentVariable(int, "POOL_RECYCLE", 300),
    "POOL_SIZE": EnvironmentVariable(int, "POOL_SIZE", 20),
    "MAX_OVERFLOW": EnvironmentVariable(int, "MAX_OVERFLOW", 20),
    "SQL_SHOW_STATEMENTS": EnvironmentVariable(bool, "SQL_SHOW_STATEMENTS", False),
    "SQL_CREATE_TABLES": EnvironmentVariable(bool, "SQL_CREATE_TABLES", False),
    "REDIS_HOST": EnvironmentVariable(str, "REDIS_HOST", "redis"),
    "REDIS_PORT": EnvironmentVariable(int, "REDIS_PORT", 6379),
    "REDIS_DB": EnvironmentVariable(int, "REDIS_DB", 0),
    "SENTRY_DSN": EnvironmentVariable(str, "SENTRY_DSN", None),
}


class TestEnvironment(IsolatedAsyncioTestCase):
    @patch("daemon.environment.getenv")
    async def test__get_bool(self, getenv_part: MagicMock):
        key = MagicMock()

        for default in [False, True]:
            for i, value in enumerate(["false", "true", "f", "t", "no", "yes", "n", "y", "0", "1"]):
                value = "".join([c.lower, c.upper][j % 2]() for j, c in enumerate(value))
                getenv_part.reset_mock()

                with self.subTest(default=default, key=value):
                    getenv_part.return_value = value

                    result = environment.get_bool(key, default)

                    self.assertEqual(bool(i % 2), result)
                    getenv_part.assert_called_once_with(key, str(default))

    @patch("os.getenv")
    async def test__environment_variables(self, getenv_patch: MagicMock):
        def getenv(a, b=None):
            var = next(v for v in VARIABLES.values() if v.name == a)
            if var.default is None:
                self.assertEqual(None, b)
                return

            self.assertEqual(str(var.default), b)

            return str(var.default)

        getenv_patch.side_effect = getenv

        env = import_module("daemon.environment")

        for name, variable in VARIABLES.items():
            self.assertEqual(variable.default, getattr(env, name))
