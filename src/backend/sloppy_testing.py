import unittest
import os
import sys
import importlib.util
import traceback

class TestScriptRuns(unittest.TestCase):
    folder_path = ""

    @classmethod
    def setUpClass(cls):
        # Validate that the folder path was provided
        if not cls.folder_path:
            raise ValueError("Folder path must be set before running tests.")

    def test_scripts(self):
        # Iterate over files in the specified folder
        for filename in os.listdir(self.folder_path):
            # Check if the file name starts with "test" and ends with ".py"
            if filename.startswith("test") and filename.endswith(".py"):
                file_path = os.path.join(self.folder_path, filename)
                module_name = filename[:-3]  # Remove the ".py" extension

                # Attempt to import the file as a module
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                except Exception as e:
                    # Capture the full traceback for the error
                    detailed_error = traceback.format_exc()
                    self.fail(f"Script {filename} threw an error:\n{detailed_error}")

if __name__ == '__main__':
    # Ensure a folder path argument is passed
    if len(sys.argv) > 1:
        TestScriptRuns.folder_path = sys.argv.pop(1)
    else:
        print("Please provide a folder path as an argument.")
        sys.exit(1)

    unittest.main()
