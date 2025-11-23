import unittest
from sw_api.solidworks_connector import SolidWorksConnector

class TestSolidWorksExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = SolidWorksConnector()
        cls.doc_path = "C:/path/to/test_part.sldprt"  # Update with actual test file

    def test_check_connection(self):
        self.assertTrue(self.connector.is_connected(), "Should connect to SolidWorks")

    def test_get_active_document(self):
        if self.connector.is_connected():
            path = self.connector.get_active_document_path()
            self.assertIsInstance(path, str)

    def test_get_dimensions(self):
        if self.connector.is_connected():
            dimensions = self.connector.get_dimensions()
            self.assertIsInstance(dimensions, list)

    def test_get_features(self):
        if self.connector.is_connected():
            features = self.connector.get_features()
            self.assertIsInstance(features, list)

    def test_get_components(self):
        if self.connector.is_connected():
            components = self.connector.get_components()
            self.assertIsInstance(components, list)

if __name__ == "__main__":
    unittest.main()