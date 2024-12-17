import unittest
import os
import sys
import importlib.util
import traceback

class TestScriptRuns(unittest.TestCase):
    folder_path = ""
    continue_from = False
    log_file = "continue.test.log"

    @classmethod
    def setUpClass(cls):
        if not cls.folder_path:
            raise ValueError("Folder path must be set before running tests.")
        
        test_files = sorted(
            [(f, os.path.getctime(os.path.join(cls.folder_path, f))) 
             for f in os.listdir(cls.folder_path) 
             if f.startswith("test") and f.endswith(".py")],
            key=lambda x: x[1],
            reverse=True
        )
        
        if cls.continue_from and not os.path.exists(cls.log_file):
            cls.continue_from = False
            
        if not cls.continue_from:
            with open(cls.log_file, 'w') as f:
                for filename, _ in test_files:
                    f.write(f"[ ] {filename}\n")

    def update_log_status(self, filename, status):
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        with open(self.log_file, 'w') as f:
            for line in lines:
                if filename in line:
                    f.write(f"{status} {filename}\n")
                else:
                    f.write(line)

    def test_scripts(self):
        test_files = sorted(
            [(f, os.path.getctime(os.path.join(self.folder_path, f))) 
             for f in os.listdir(self.folder_path) 
             if f.startswith("test") and f.endswith(".py")],
            key=lambda x: x[1],
            reverse=True
        )

        if self.continue_from:
            with open(self.log_file, 'r') as f:
                completed = {line.split()[-1] for line in f if '[x]' in line}
        else:
            completed = set()

        for filename, _ in test_files:
            if filename in completed:
                continue

            self.update_log_status(filename, '[?]')
            
            file_path = os.path.join(self.folder_path, filename)
            module_name = filename[:-3]

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.update_log_status(filename, '[x]')
            except Exception as e:
                detailed_error = traceback.format_exc()
                self.fail(f"Script {filename} threw an error:\n{detailed_error}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-c', '--continue']:
            TestScriptRuns.continue_from = True
            TestScriptRuns.folder_path = sys.argv[2]
            sys.argv.pop(1)
        else:
            TestScriptRuns.folder_path = sys.argv[1]
        sys.argv.pop(1)
    else:
        print("Usage: python auto_testing.py [-c] <folder_path>")
        sys.exit(1)

    unittest.main()