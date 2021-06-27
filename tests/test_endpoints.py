from unittest import TestCase
from unittest.mock import patch, MagicMock

import endpoints


class TestEndpoints(TestCase):
    @patch("endpoints.ENDPOINT_COLLECTIONS")
    def test__register_collections(self, endpoint_collections_patch):
        app = MagicMock()
        endpoint_collections_patch.__iter__.return_value = collections = [MagicMock() for _ in range(5)]

        result = endpoints.register_collections(app)

        for collection in collections:
            collection.register.assert_called_once_with(app)

        self.assertEqual([collection.register(app) for collection in collections], result)
