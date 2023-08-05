import unittest

from app import app


class IndexViewTest(unittest.TestCase):
    """
    Index View Integration Tests
    """

    def setUp(self):
        self.test_client = app.test_client()

    def test_success(self):
        response = self.test_client.get("/")
        assert response.status_code == 200
