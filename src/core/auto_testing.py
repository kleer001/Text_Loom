import unittest
import os
import sys
import importlib.util
import traceback

"""
    Auto Testing Framework: A script runner for automated testing with progress tracking and continuation support.

    This utility provides a systematic way to execute test scripts in a directory, tracking their execution status
    and supporting continuation from previous runs. It's particularly useful for large test suites where
    maintaining execution state between runs is important.

    Command Line Usage:
    Basic run:
        python auto_testing.py <folder_path>
    
    Continue from previous run:
        python auto_testing.py -c <folder_path>
        python auto_testing.py --continue <folder_path>

    Features:
    1. Progress Tracking:
        - Maintains a log file (continue.test.log) tracking test execution
        - Uses status markers: [ ] (not run), [?] (running), [x] (completed)
        - Preserves execution history between runs
    
    2. Test Execution:
        - Runs files in reverse chronological order (newest first)
        - Only processes files starting with "test" and ending in ".py"
        - Provides detailed error traces on failure
        
    3. Continuation Support:
        - Can resume from previous partial runs
        - Skips previously completed tests when in continue mode
        - Maintains execution state across multiple sessions

    Status File Format:
    Each line in continue.test.log follows the format:
    [status] filename.py
    
    Status markers:
    [ ] - Test not yet run
    [?] - Test currently running
    [x] - Test completed successfully

    Error Handling:
    - Provides full stack traces for test failures
    - Maintains log file integrity even on failure
    - Preserves partial progress on interruption

    Example Log File:
    [x] test_basic_operations.py
    [?] test_advanced_features.py
    [ ] test_edge_cases.py
    [ ] test_performance.py

    Notes:
    - Test files must be valid Python modules
    - Tests are executed in the same Python environment as the runner
    - The log file is created in the current working directory
    - Required folder path argument must be provided
    """

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