import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import sys
import yaml

# Add scripts to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.models import (
    KnowledgeNode, Definition, Tool, Example, Mistake, Course, Lecture, 
    Tutorial, Question, Homework, ExampleType, Severity, AnswerStep
)
from scripts.db_manager import DBManager

class TestModels(unittest.TestCase):
    """Tests for the data models in scripts/models.py"""

    def test_knowledge_node_instantiation(self):
        """Verify standard nodes can be instantiated."""
        node = KnowledgeNode(id="node-1")
        self.assertEqual(node.id, "node-1")
        
        # Test Definition
        d = Definition(id="def-1", term="T", content="C")
        self.assertEqual(d.term, "T")

    def test_enums(self):
        """Verify Enum constraints."""
        self.assertEqual(ExampleType("Standard"), ExampleType.STANDARD)
        with self.assertRaises(ValueError):
            Severity("Super-Critical")

class TestAssessmentEngine(unittest.TestCase):
    """Specific tests for Phase 5 (Questions, Answers, Homework)."""

    def test_answer_step_structure(self):
        """Verify AnswerStep dataclass works as expected."""
        step = AnswerStep(type="Proof", title="Step 1", content="x=y")
        self.assertEqual(step.type, "Proof")
        self.assertIsNone(step.proof)

    def test_question_parsing(self):
        """
        Critical: Verify DBManager can parse nested AnswerStep objects inside Questions.
        This mocks the YAML load process specifically for questions.
        """
        mock_yaml = """
        - id: "qn-test"
          topic: "Limits"
          answer_steps:
            - type: "Calculation"
              title: "Find Delta"
              content: "delta = epsilon/3"
        """
        
        # Mock the file system
        with patch("builtins.open", mock_open(read_data=mock_yaml)):
            with patch("pathlib.Path.exists", return_value=True):
                # Prevent automatic DB load on init
                with patch("scripts.db_manager.DBManager.load_db", lambda self: None):
                    db = DBManager(data_path=Path("/fake"))

                # We mock the _type_map iteration to only load questions for this test
                db._type_map = { "questions.yaml": (Question, db.questions) }
                db.load_db()
                
                # Check if the Question was loaded
                self.assertIn("qn-test", db.questions)
                q = db.questions["qn-test"]
                
                # Check if nested AnswerSteps were parsed into Objects, not left as Dicts
                self.assertTrue(hasattr(q, "answer_steps"))
                self.assertEqual(len(q.answer_steps), 1)
                first_step = q.answer_steps[0]
                
                self.assertIsInstance(first_step, AnswerStep, "Nested list should be converted to AnswerStep objects")
                self.assertEqual(first_step.title, "Find Delta")

class TestDatabaseManager(unittest.TestCase):
    """General DBManager logic."""

    @patch("pathlib.Path.exists", return_value=True)
    def test_add_node_uniqueness(self, mock_exists):
        """Test that add_node raises error for duplicate IDs."""
        # Setup empty DB
        with patch("scripts.db_manager.DBManager.load_db", lambda self: None):
            db = DBManager(Path("/fake"))
            node = Definition(id="d1", term="t", content="c")
            db.add_node(node)
            with self.assertRaises(ValueError):
                db.add_node(node)

if __name__ == "__main__":
    unittest.main()