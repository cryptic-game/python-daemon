from unittest import TestCase
from unittest.mock import patch

from utils import run_module


class TestMain(TestCase):
    @patch("bootstrap.bootstrap")
    def test__main(self, bootstrap_patch):
        run_module("main")
        bootstrap_patch.assert_called_with()
