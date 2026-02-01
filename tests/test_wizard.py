import unittest
import subprocess
import sys
import os
from pathlib import Path
import yaml

# --- Config ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIZARD_SCRIPT = PROJECT_ROOT / "scripts" / "add_question.py"
DATA_FILE = PROJECT_ROOT / "data" / "questions.yaml"

class TestQuestionWizard(unittest.TestCase):
    
    def setUp(self):
        """Backup questions.yaml"""
        self.backup_created = False
        if DATA_FILE.exists():
            self.backup_path = DATA_FILE.with_suffix(".yaml.bak")
            DATA_FILE.rename(self.backup_path)
            self.backup_created = True

    def tearDown(self):
        """Restore questions.yaml"""
        if DATA_FILE.exists():
            os.remove(DATA_FILE)
        
        if self.backup_created and self.backup_path.exists():
            self.backup_path.rename(DATA_FILE)

    def run_wizard(self, inputs):
        """Runs the wizard script with mocked inputs."""
        input_str = "\n".join(inputs) + "\n"
        return subprocess.run(
            [sys.executable, str(WIZARD_SCRIPT)],
            input=input_str,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

    def test_add_question_flow(self):
        """
        Simulate a user adding a question via the wizard.
        Inputs correspond to the prompts in add_question.py
        """
        inputs = [
            "qn-auto-test", # ID
            "2025",         # Year
            "Prof. AI",     # Lecturer
            "Calculus",     # Topic
            "Given x",      # Given (Line 1)
            "",             # Given (End)
            "Prove y",      # To Prove (Line 1)
            "",             # To Prove (End)
            "Theorem A",    # Tools
            "-",            # Mistakes
            "Use logic",    # Hint (Line 1)
            ""              # Hint (End)
        ]

        result = self.run_wizard(inputs)
        
        # 1. Check Script Success
        self.assertEqual(result.returncode, 0, f"Wizard failed: {result.stderr}")
        self.assertIn("Success!", result.stdout)

        # 2. Check File Output
        self.assertTrue(DATA_FILE.exists(), "questions.yaml was not created")
        
        with open(DATA_FILE, "r") as f:
            data = yaml.safe_load(f)
        
        # 3. Verify Content
        self.assertIsInstance(data, list)
        entry = data[0]
        self.assertEqual(entry['id'], "qn-auto-test")
        self.assertEqual(entry['lecturer'], "Prof. AI")
        # Check block scalar handling (strip newlines)
        self.assertEqual(entry['given'].strip(), "Given x")

if __name__ == "__main__":
    unittest.main()

