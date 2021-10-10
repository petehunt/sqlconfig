import tempfile
import unittest
from .lib import load, dump
import os

class RoundtripTest(unittest.TestCase):
  def compare_dirs(self, expected, received):
    expected_files = set(os.listdir(expected))
    received_files = set(os.listdir(received))
    self.assertEqual(expected_files, received_files, "Directories had different sets of files")
    for filename in expected_files:
      with open(os.path.join(expected, filename), "r") as expected_f:
        with open(os.path.join(received, filename), "r") as received_f:
          self.assertMultiLineEqual(expected_f.read(), received_f.read(), "File " + filename + " did not match")

  def test_roundtrip(self):
    test_data = os.path.join(os.path.dirname(__file__), "testdata")
    db_truth = os.path.join(test_data, "db", "Chinook_Sqlite.sqlite")
    files_truth = os.path.join(test_data, "files")
    with tempfile.TemporaryDirectory() as tempdir:
      # Export the DB and make sure that they match the source of truth in the repo
      files_temp = os.path.join(tempdir, "files")
      dump(db_truth, files_temp)
      self.compare_dirs(files_truth, files_temp)

    with tempfile.TemporaryDirectory() as tempdir:
      # Import and re-export the db and make sure it matches the source of truth
      db_temp = os.path.join(tempdir, "db.sqlite")
      files_temp = os.path.join(tempdir, "files")
      load(db_temp, files_truth)
      dump(db_temp, files_temp)
      self.compare_dirs(files_truth, files_temp)


if __name__ == "__main__":
  unittest.main()