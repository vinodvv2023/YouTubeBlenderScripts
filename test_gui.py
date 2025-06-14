import unittest
import os

class TestFolders(unittest.TestCase):
    def test_source_folder_exists(self):
        self.assertTrue(os.path.exists("videos"))
    def test_output_folder_exists(self):
        self.assertTrue(os.path.exists("output"))

if __name__ == "__main__":
    unittest.main()
