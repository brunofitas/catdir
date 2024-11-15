import unittest
import os
import shutil
from catdir.catdir import CatDir
from unittest.mock import patch
from io import StringIO


class TestCatDir(unittest.TestCase):

    def setUp(self):
        # Set up a temporary test directory
        self.test_dir = "test_data"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a .catignore file
        with open(os.path.join(self.test_dir, ".catignore"), "w") as f:
            f.write("*.ignore\n")

        # Create test files
        self.create_file("test.txt", "This is a test file.")
        self.create_file("ignore.ignore", "This file should be ignored.")
        self.create_file("nested/nested.txt", "This is a nested file.")
        self.create_file("nested/ignore.ignore", "Nested ignored file.")

    def tearDown(self):
        # Clean up the test directory after each test
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_file(self, file_path, content):
        full_path = os.path.join(self.test_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    def test_load_ignore_patterns(self):
        catdir = CatDir(target=self.test_dir, recursive=True)
        self.assertIn("*.ignore", catdir.ignore_patterns)

    def test_should_ignore(self):
        catdir = CatDir(target=self.test_dir, recursive=True)
        self.assertTrue(catdir.should_ignore("file.ignore"))
        self.assertFalse(catdir.should_ignore("test.txt"))

    def test_create_tree(self):
        catdir = CatDir(target=self.test_dir, recursive=True)
        catdir.create_tree()
        self.assertIn(os.path.join(self.test_dir, "test.txt"), catdir.file_tree)
        self.assertIn(os.path.join(self.test_dir, "nested/nested.txt"), catdir.file_tree)
        self.assertNotIn(os.path.join(self.test_dir, "ignore.ignore"), catdir.file_tree)
        self.assertNotIn(os.path.join(self.test_dir, "nested/ignore.ignore"), catdir.file_tree)

    def test_render_tree(self):
        catdir = CatDir(target=self.test_dir, recursive=True)
        catdir.create_tree()

        # Use patch to safely mock sys.stdout
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            catdir.render_tree()
            output_str = mock_stdout.getvalue()

        # Verify that the output contains expected file names
        self.assertIn("test.txt", output_str)
        self.assertIn("nested/nested.txt", output_str)
        self.assertNotIn("ignore.ignore", output_str)

    def test_reconstruct_tree(self):
        # Prepare input text for reconstruction
        input_text = """
####################################################################################################
TREE:
####################################################################################################
test_data/test.txt
test_data/nested/nested.txt
####################################################################################################
# FILES
####################################################################################################
File: test_data/test.txt
Type: text
----------------------------------------------------------------------------------------------------
This is a test file.
====================================================================================================
File: test_data/nested/nested.txt
Type: text
----------------------------------------------------------------------------------------------------
This is a nested file.
====================================================================================================
        """

        # Create a new directory for reconstruction
        reconstruct_dir = "reconstruct_data"
        os.makedirs(reconstruct_dir, exist_ok=True)

        # Initialize CatDir for reconstruction
        catdir = CatDir(target=reconstruct_dir, recursive=True, reconstruct=True)
        catdir.reconstruct_tree(input_text)

        # Verify files were reconstructed correctly
        with open(os.path.join(reconstruct_dir, "test_data/test.txt"), "r") as f:
            self.assertEqual(f.read(), "This is a test file.")

        with open(os.path.join(reconstruct_dir, "test_data/nested/nested.txt"), "r") as f:
            self.assertEqual(f.read(), "This is a nested file.")

        # Clean up reconstructed directory
        shutil.rmtree(reconstruct_dir, ignore_errors=True)

    def test_end_to_end(self):
        catdir = CatDir(target=self.test_dir, recursive=True)
        catdir.create_tree()

        # Capture rendered output using patch
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            catdir.render_tree()
            rendered_output = mock_stdout.getvalue()

        # Reconstruct in a new directory
        reconstruct_dir = "end_to_end_data"
        os.makedirs(reconstruct_dir, exist_ok=True)
        catdir_reconstruct = CatDir(target=reconstruct_dir, recursive=True, reconstruct=True)
        catdir_reconstruct.reconstruct_tree(rendered_output)

        # Check if files were successfully reconstructed
        for file_path in ["test.txt", "nested/nested.txt"]:
            original_file = os.path.join(self.test_dir, file_path)
            reconstructed_file = os.path.join(reconstruct_dir, "test_data", file_path)
            with open(original_file, "r") as original, open(reconstructed_file, "r") as reconstructed:
                self.assertEqual(original.read(), reconstructed.read())

        # Clean up the reconstructed directory
        shutil.rmtree(reconstruct_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
