
import unittest
import subprocess
import sys
from pathlib import Path
import os

# --- Test Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANAGE_PY_PATH = PROJECT_ROOT / "scripts" / "manage.py"
DATA_PATH = PROJECT_ROOT / "data"

# Test data will be cleaned up automatically
DEF_ID = "def-auto-test"
EX_ID = "ex-auto-test"

DEFINITION_YAML = DATA_PATH / "definitions.yaml"
EXAMPLE_YAML = DATA_PATH / "examples.yaml"
# ---

class TestCliE2e(unittest.TestCase):

    def setUp(self):
        """
        Back up production data files before the test runs.
        This prevents the test from destroying existing data.
        """
        self.backed_up_files = {}
        files_to_manage = [DEFINITION_YAML, EXAMPLE_YAML]
        
        print("\nChecking for existing data files to back up...")
        for f_path in files_to_manage:
            if f_path.exists():
                backup_path = f_path.with_suffix(f_path.suffix + '.bak')
                print(f"  - Backing up '{f_path.name}' to '{backup_path.name}'")
                f_path.rename(backup_path)
                self.backed_up_files[f_path] = backup_path

    def tearDown(self):
        """
        Clean up any created test files and restore backups.
        This runs even if the test fails.
        """
        print("\nCleaning up test data and restoring backups...")
        
        # Remove files created by the test
        if DEFINITION_YAML.exists():
            os.remove(DEFINITION_YAML)
            print(f"  - Removed test file: {DEFINITION_YAML.name}")
        if EXAMPLE_YAML.exists():
            os.remove(EXAMPLE_YAML)
            print(f"  - Removed test file: {EXAMPLE_YAML.name}")

        # Restore backups
        for original_path, backup_path in self.backed_up_files.items():
            if backup_path.exists():
                print(f"  - Restoring backup '{backup_path.name}' to '{original_path.name}'")
                backup_path.rename(original_path)

    def run_cli_command(self, command, input_text=None):
        """Helper function to run a CLI command and return the result."""
        return subprocess.run(
            [sys.executable, str(MANAGE_PY_PATH)] + command,
            input=input_text,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

    def test_referential_integrity_scenario(self):
        """
        Tests the full referential integrity scenario:
        1. Add a definition.
        2. Add an example referencing it.
        3. Fail to delete the definition.
        4. Delete the example.
        5. Succeed in deleting the definition.
        """
        # 1. Add a definition
        print("Step 1: Adding definition...")
        add_def_input = f"{DEF_ID}\nAuto Term\nA test definition.\n\n"
        result = self.run_cli_command(["add", "definition"], input_text=add_def_input)
        self.assertEqual(result.returncode, 0, f"Failed to add definition. Stderr: {result.stderr}")
        self.assertIn(f"[Success] Added definition '{DEF_ID}'", result.stdout)
        print("-> Success")

        # 2. Add an example that references the definition
        print("Step 2: Adding example...")
        add_ex_input = f"{EX_ID}\nAuto Example\nStandard\nSome content.\n\n{DEF_ID}\n"
        result = self.run_cli_command(["add", "example"], input_text=add_ex_input)
        self.assertEqual(result.returncode, 0, f"Failed to add example. Stderr: {result.stderr}")
        self.assertIn(f"[Success] Added example '{EX_ID}'", result.stdout)
        print("-> Success")

        # 3. Attempt to delete the definition (should fail)
        print("Step 3: Attempting to delete definition (expect failure)...")
        result = self.run_cli_command(["delete", DEF_ID])
        # Successful execution, but with a business logic error message
        self.assertEqual(result.returncode, 0)
        self.assertIn(f"[Error] Cannot delete node '{DEF_ID}'", result.stdout)
        print("-> Correctly failed")

        # 4. Delete the example
        print("Step 4: Deleting example...")
        result = self.run_cli_command(["delete", EX_ID])
        self.assertEqual(result.returncode, 0, f"Failed to delete example. Stderr: {result.stderr}")
        self.assertIn(f"[Success] Deleted node '{EX_ID}'", result.stdout)
        print("-> Success")

        # 5. Attempt to delete the definition again (should succeed)
        print("Step 5: Attempting to delete definition again (expect success)...")
        result = self.run_cli_command(["delete", DEF_ID])
        self.assertEqual(result.returncode, 0, f"Failed to delete definition. Stderr: {result.stderr}")
        self.assertIn(f"[Success] Deleted node '{DEF_ID}'", result.stdout)
        print("-> Success")


if __name__ == "__main__":
    print("Running End-to-End CLI Integration Test...")
    # Using TestLoader to run a specific test class
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCliE2e)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Exit with a non-zero code if tests failed
    if result.wasSuccessful():
        print("\nAll Integration Tests Passed!")
        sys.exit(0)
    else:
        print("\nSome Integration Tests Failed.")
        sys.exit(1)
