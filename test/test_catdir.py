import unittest
import os
import shutil
from catdir.catdir import CatDir
from unittest.mock import patch
from io import StringIO


class TestCatDir(unittest.TestCase):

    def setUp(self):
        # Create test directory with files and .catignore
        self.test_dir = "test_data"
        os.makedirs(self.test_dir, exist_ok=True)

        with open(os.path.join(self.test_dir, ".catignore"), "w") as f:
            f.write("*.ignore\n")

        self.create_file("test.txt", "This is a test file.")
        self.create_file("ignore.ignore", "This file should be ignored.")
        self.create_file("nested/nested.txt", "This is a nested file.")
        self.create_file("nested/ignore.ignore", "Nested ignored file.")

    def tearDown(self):
        # Delete test directory after each test
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_file(self, file_path, content):
        # Utility to create a test file
        full_path = os.path.join(self.test_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def test_load_ignore_patterns(self):
        # Test if ignore patterns are loaded correctly
        cat_dir = CatDir(target=self.test_dir, recursive=True)
        self.assertIn("*.ignore", cat_dir.ignore_patterns)

    def test_should_ignore(self):
        # Validate ignore logic
        cat_dir = CatDir(target=self.test_dir, recursive=True)
        self.assertTrue(cat_dir.should_ignore("file.ignore"))
        self.assertFalse(cat_dir.should_ignore("test.txt"))

    def test_create_tree(self):
        # Test if file_tree only includes allowed files
        cat_dir = CatDir(target=self.test_dir, recursive=True)
        cat_dir.create_tree()

        self.assertIn("test.txt", cat_dir.file_tree)
        self.assertIn("nested/nested.txt", cat_dir.file_tree)
        self.assertNotIn("ignore.ignore", cat_dir.file_tree)
        self.assertNotIn("nested/ignore.ignore", cat_dir.file_tree)

    def test_render_tree(self):
        # Test output from render_tree
        cat_dir = CatDir(target=self.test_dir, recursive=True)
        cat_dir.create_tree()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cat_dir.render_tree()
            output_str = mock_stdout.getvalue()

        self.assertIn("test.txt", output_str)
        self.assertIn("nested/nested.txt", output_str)
        self.assertNotIn("ignore.ignore", output_str)

    def test_reconstruct_tree(self):
        # Test full reconstruction of a rendered tree
        input_text = """
####################################################################################################
# TREE:
####################################################################################################
test_data/test.txt
test_data/nested/nested.txt
####################################################################################################
# FILES
####################################################################################################
>> File: test_data/test.txt
>> Type: text
----------------------------------------------------------------------------------------------------
This is a test file.
====================================================================================================
>> File: test_data/nested/nested.txt
>> Type: text
----------------------------------------------------------------------------------------------------
This is a nested file.
====================================================================================================
        """

        reconstruct_dir = "reconstruct_data"
        os.makedirs(reconstruct_dir, exist_ok=True)

        cat_dir = CatDir(target=reconstruct_dir, recursive=True, reconstruct=True)
        cat_dir.reconstruct_tree(input_text)

        with open(os.path.join(reconstruct_dir, "test_data/test.txt"), "r") as f:
            self.assertEqual(f.read(), "This is a test file.")

        with open(os.path.join(reconstruct_dir, "test_data/nested/nested.txt"), "r") as f:
            self.assertEqual(f.read(), "This is a nested file.")

        shutil.rmtree(reconstruct_dir, ignore_errors=True)

    def test_end_to_end(self):
        # End-to-end test: dump + reconstruct + validate equality
        cat_dir = CatDir(target=self.test_dir, recursive=True)
        cat_dir.create_tree()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            cat_dir.render_tree()
            rendered_output = mock_stdout.getvalue()

        reconstruct_dir = "end_to_end_data"
        os.makedirs(reconstruct_dir, exist_ok=True)

        cat_dir_reconstruct = CatDir(target=reconstruct_dir, recursive=True, reconstruct=True)
        cat_dir_reconstruct.reconstruct_tree(rendered_output)

        for file_path in ["test.txt", "nested/nested.txt"]:
            original_file = os.path.join(self.test_dir, file_path)
            reconstructed_file = os.path.join(reconstruct_dir, file_path)
            with open(original_file, "r") as original, open(reconstructed_file, "r") as reconstructed:
                self.assertEqual(original.read(), reconstructed.read())

        shutil.rmtree(reconstruct_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
