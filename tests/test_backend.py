import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import sys

# Add scripts to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.models import (
    KnowledgeNode,
    Definition,
    Example,
    ExampleType,
    Severity,
    AnswerStep,
)
from scripts.db_manager import DBManager


class TestModels(unittest.TestCase):
    """Tests for the data models in scripts/models.py"""

    def test_knowledge_node_instantiation(self):
        node = KnowledgeNode(id="node-1")
        self.assertEqual(node.id, "node-1")

        d = Definition(id="def-1", term="T", content="C")
        self.assertEqual(d.term, "T")

    def test_enums(self):
        self.assertEqual(ExampleType("Standard"), ExampleType.STANDARD)
        with self.assertRaises(ValueError):
            Severity("Super-Critical")


class TestAssessmentEngine(unittest.TestCase):
    """Specific tests for Phase 5 (Questions, Answers)."""

    def test_question_parsing(self):
        """Verify DBManager can parse nested AnswerStep objects."""
        mock_question_yaml = """
        - id: "qn-test"
          topic: "Limits"
          answer_steps:
            - type: "Calculation"
              title: "Find Delta"
              content: "delta = epsilon/3"
        """

        # This custom side effect will return the correct mock data based on the file being opened.
        def custom_open_side_effect(file_path, *args, **kwargs):
            if "questions.yaml" in str(file_path):
                return mock_open(read_data=mock_question_yaml)()
            else:
                # Return an empty file for all other yaml files to avoid TypeErrors
                return mock_open(read_data="")()

        # The DBManager uses explicit filenames, so we patch `builtins.open`.
        with patch("builtins.open", side_effect=custom_open_side_effect):
            with patch("pathlib.Path.exists", return_value=True):
                db = DBManager(data_path=Path("/fake"))

                self.assertIn("qn-test", db.questions)
                q = db.questions["qn-test"]
                self.assertTrue(hasattr(q, "answer_steps"))
                self.assertIsInstance(q.answer_steps[0], AnswerStep)
                self.assertEqual(q.answer_steps[0].title, "Find Delta")


class TestDatabaseManager(unittest.TestCase):
    """Core Database Logic & Integrity Tests."""

    @patch("scripts.db_manager.DBManager.load_db", lambda self: None)
    def setUp(self):
        self.db = DBManager(Path("/fake"))

    def test_add_node_uniqueness(self):
        """Prevent duplicate IDs."""
        node = Definition(id="d1", term="t", content="c")
        self.db.add_node(node)
        with self.assertRaises(ValueError):
            self.db.add_node(node)

    def test_delete_integrity_protection(self):
        """CRITICAL: Ensure nodes cannot be deleted if referenced."""
        # 1. Create a dependency chain: Example -&gt; Definition
        defi = Definition(id="def-root", term="Root", content="...")
        ex = Example(
            id="ex-child",
            name="Child",
            type=ExampleType.STANDARD,
            content="...",
            related_definition_ids=["def-root"],
        )

        self.db.add_node(defi)
        self.db.add_node(ex)

        # 2. Try to delete the Definition (Should Fail)
        with self.assertRaisesRegex(ValueError, "referenced by node 'ex-child'"):
            self.db.delete_node("def-root")

        # 3. Delete the Child first
        self.db.delete_node("ex-child")
        self.assertNotIn("ex-child", self.db.nodes)

        # 4. Now delete the Parent (Should Succeed)
        self.db.delete_node("def-root")
        self.assertNotIn("def-root", self.db.nodes)

    def test_update_id_cascading(self):
        """Verify changing an ID updates all references to it."""
        defi = Definition(id="def-old", term="Root", content="...")
        ex = Example(
            id="ex-child",
            name="Child",
            type=ExampleType.STANDARD,
            content="...",
            related_definition_ids=["def-old"],
        )

        self.db.add_node(defi)
        self.db.add_node(ex)

        # Rename def-old -&gt; def-new
        self.db.update_node_id("def-old", "def-new")

        # Check Definition
        self.assertNotIn("def-old", self.db.nodes)
        self.assertIn("def-new", self.db.nodes)

        # Check Reference in Example
        updated_ex = self.db.nodes["ex-child"]
        self.assertIn("def-new", updated_ex.related_definition_ids)
        self.assertNotIn("def-old", updated_ex.related_definition_ids)


if __name__ == "__main__":
    unittest.main()
