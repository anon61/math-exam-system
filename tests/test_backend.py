import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add scripts to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from scripts.models import (
    KnowledgeNode,
    Definition,
    Tool,
    Example,
    Mistake,
    Course,
    Lecture,
    Tutorial,
    Question,
    Homework,
    ExampleType,
    Severity,
    AnswerStep,
)
from scripts.db_manager import DBManager


class TestModels(unittest.TestCase):
    """Tests for the data models in scripts/models.py"""

    def test_knowledge_node_instantiation(self):
        """Verify that KnowledgeNode and its subclasses can be instantiated."""
        node = KnowledgeNode(id="node-1")
        self.assertEqual(node.id, "node-1")

        definition = Definition(id="def-1", term="Test Term", content="Test Content")
        self.assertEqual(definition.id, "def-1")
        self.assertEqual(definition.term, "Test Term")

        tool = Tool(id="tool-1", name="Test Tool", short_name="TT", statement="Do this.")
        self.assertEqual(tool.name, "Test Tool")

        example = Example(
            id="ex-1",
            name="Test Example",
            type=ExampleType.STANDARD,
            content="An example.",
            related_definition_ids=["def-1"],
        )
        self.assertEqual(example.type, ExampleType.STANDARD)
        self.assertIn("def-1", example.related_definition_ids)

        mistake = Mistake(
            id="mistake-1",
            name="Common Mistake",
            severity=Severity.MINOR,
            description="A mistake.",
            remedy="Fix it.",
        )
        self.assertEqual(mistake.severity, Severity.MINOR)

        course = Course(
            id="course-1",
            name="Test Course",
            definition_sequence=["def-1"],
            tool_sequence=[],
            example_sequence=[],
        )
        self.assertIn("def-1", course.definition_sequence)

        lecture = Lecture(
            id="lec-1",
            sequence=1,
            title="Test Lecture",
            date="2024-01-01",
            definition_ids=["def-1"],
            tool_ids=[],
            example_ids=[],
        )
        self.assertEqual(lecture.sequence, 1)

        tutorial = Tutorial(
            id="tut-1",
            sequence=1,
            lecture_ref="lec-1",
            example_question_ids=["ex-1"],
        )
        self.assertEqual(tutorial.lecture_ref, "lec-1")

        question = Question(id="q-1", topic="Test Topic")
        self.assertEqual(question.topic, "Test Topic")
        
        homework = Homework(id="hw-1")
        self.assertTrue(isinstance(homework, Homework))


    def test_enums(self):
        """Verify that Severity and ExampleType Enums enforce valid values."""
        # Test valid values
        self.assertEqual(ExampleType("Standard"), ExampleType.STANDARD)
        self.assertEqual(ExampleType("Counter-Example"), ExampleType.COUNTER_EXAMPLE)
        self.assertEqual(Severity("Critical"), Severity.CRITICAL)
        self.assertEqual(Severity("Minor"), Severity.MINOR)

        # Test invalid values
        with self.assertRaises(ValueError):
            ExampleType("Invalid-Type")
        with self.assertRaises(ValueError):
            Severity("Invalid-Severity")


class TestDatabaseManager(unittest.TestCase):
    """Tests for the DBManager in scripts/db_manager.py"""

    @patch("pathlib.Path.exists", return_value=True)
    def test_load_db(self, mock_exists):
        """Test that the manager correctly loads data using a robust mocking strategy."""
        # Data to be returned by the mocked yaml files
        mock_definitions_data = [{"id": "def-1", "term": "Term1", "content": "Content1"}]
        mock_lectures_data = [{
            "id": "lec-1", "sequence": 1, "title": "Lec1", "date": "2024-01-01",
            "definition_ids": ["def-1"], "tool_ids": [], "example_ids": []
        }]

        # Create a dictionary mapping filenames to their mock YAML content
        # We need to import yaml for this to work
        import yaml
        mock_file_content = {
            "definitions.yaml": yaml.dump(mock_definitions_data),
            "lectures.yaml": yaml.dump(mock_lectures_data),
        }

        # This side effect for 'open' returns a mock file handle with the correct content
        def open_side_effect(path, mode='r'):
            filename = Path(path).name
            content = mock_file_content.get(filename, "")
            return mock_open(read_data=content).return_value

        with patch("builtins.open", side_effect=open_side_effect):
            # Instantiate the manager within the patch context
            db = DBManager(data_path=Path("/fake/path"))

            # Verify that nodes were loaded into the main dictionary
            self.assertIn("def-1", db.nodes)
            self.assertIn("lec-1", db.nodes)

            # Verify that nodes were loaded into type-specific dictionaries
            self.assertIn("def-1", db.definitions)
            self.assertIn("lec-1", db.lectures)
            self.assertEqual(db.definitions["def-1"].term, "Term1")
            self.assertIn("def-1", db.lectures["lec-1"].definition_ids)

    @patch("scripts.db_manager.DBManager.load_db", lambda self: None)
    def setUp(self):
        """Setup an empty DB for tests that don't involve loading."""
        self.db = DBManager(data_path=Path("/fake/path"))

    def test_add_node_uniqueness(self):
        """Test that add_node raises an error for duplicate IDs."""
        node1 = Definition(id="def-1", term="Term1", content="Content1")
        node2 = Definition(id="def-1", term="Term2", content="Content2")
        
        self.db.add_node(node1)
        with self.assertRaisesRegex(ValueError, "Node with ID 'def-1' already exists."):
            self.db.add_node(node2)

    def test_delete_node_referential_integrity(self):
        """Test that delete_node is blocked by existing references."""
        definition = Definition(id="def-1", term="Term1", content="Content1")
        lecture = Lecture(
            id="lec-1", sequence=1, title="Lec1", date="2024-01-01",
            definition_ids=["def-1"], tool_ids=[], example_ids=[]
        )
        
        self.db.add_node(definition)
        self.db.add_node(lecture)

        with self.assertRaisesRegex(ValueError, "Cannot delete node 'def-1' because it is referenced by node 'lec-1'"):
            self.db.delete_node("def-1")

        self.db.delete_node("lec-1")
        self.assertNotIn("lec-1", self.db.nodes)

        self.db.delete_node("def-1")
        self.assertNotIn("def-1", self.db.nodes)

    def test_update_node_id(self):
        """Test that update_node_id correctly updates references."""
        definition = Definition(id="def-1", term="Term1", content="Content1")
        lecture = Lecture(
            id="lec-1", sequence=1, title="Lec1", date="2024-01-01",
            definition_ids=["def-1", "def-other"], tool_ids=[], example_ids=[]
        )
        
        self.db.add_node(definition)
        self.db.add_node(lecture)

        self.db.update_node_id("def-1", "def-new")

        self.assertNotIn("def-1", self.db.nodes)
        self.assertIn("def-new", self.db.nodes)
        self.assertIn("def-new", self.db.definitions)
        
        updated_lecture = self.db.lectures["lec-1"]
        self.assertIn("def-new", updated_lecture.definition_ids)
        self.assertNotIn("def-1", updated_lecture.definition_ids)

        another_def = Definition(id="def-2", term="Term2", content="Content2")
        self.db.add_node(another_def)
        with self.assertRaisesRegex(ValueError, "Node with ID 'def-2' already exists."):
            self.db.update_node_id("def-new", "def-2")


if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
