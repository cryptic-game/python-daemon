from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from daemon import environment


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
