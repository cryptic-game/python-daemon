from unittest import TestCase
from unittest.mock import patch, MagicMock

from daemon import endpoints
from daemon.endpoints import counter_collection, device_collection


class TestEndpoints(TestCase):
    def test__endpoint_collections(self):
        self.assertEqual([device_collection, counter_collection], endpoints.ENDPOINT_COLLECTIONS)

    @patch("daemon.endpoints.ENDPOINT_COLLECTIONS")
    def test__register_collections(self, endpoint_collections_patch):
        app = MagicMock()
        collections = []
        for i in range(5):
            collections.append(collection := MagicMock())
            collection.register.return_value = MagicMock() if i % 2 else None
        endpoint_collections_patch.__iter__.return_value = collections

        result = endpoints.register_collections(app)

        for collection in collections:
            collection.register.assert_called_once_with(app)

        self.assertEqual([collection.register(app) for collection in collections[1::2]], result)
