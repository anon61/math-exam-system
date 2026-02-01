import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.build_exam import generate_exam, render_node_preview
from scripts.models import Question

class TestBuildExam(unittest.TestCase):
    def setUp(self):
        # Create a dummy project structure in memory if needed, but for now, mocking is enough.
        self.project_root = Path(__file__).resolve().parent.parent
        # A sample question node to be used in tests.
        self.sample_question = Question(id="qn-test", topic="Calculus", year=2023, lecturer="Dr. Gemini")

    @patch("scripts.build_exam.subprocess.run")
    @patch("scripts.build_exam.open", new_callable=unittest.mock.mock_open)
    @patch("scripts.build_exam.DBManager")
    def test_generate_exam_logic(self, mock_db_manager, mock_open_file, mock_subprocess):
        """
        Test the logic of generate_exam without touching the filesystem or running Typst.
        """
        # Arrange
        # 1. Mock DBManager to return our sample question
        mock_db_instance = MagicMock()
        mock_db_instance.questions = {"qn-test": self.sample_question}
        mock_db_manager.return_value = mock_db_instance

        # 2. Mock subprocess.run to simulate successful Typst compilation
        mock_subprocess.return_value = MagicMock(returncode=0)

        # Act
        # Call the function to be tested
        result_paths = generate_exam(specific_ids=["qn-test"], filename="test_exam")
        path_student, path_teacher = result_paths

        # Assert
        # 1. Check if it returned the correct paths
        self.assertEqual(path_student, self.project_root / "test_exam.pdf")
        self.assertEqual(path_teacher, self.project_root / "test_exam_key.pdf")

        # 2. Check if the .typ files were written with the correct content
        # We expect two calls to open: one for student, one for teacher's key
        self.assertEqual(mock_open_file.call_count, 2)
        
        # The mock_open().write method will have been called twice.
        write_calls = mock_open_file().write.call_args_list
        self.assertEqual(len(write_calls), 2)

        student_typ_content = write_calls[0][0][0]
        teacher_typ_content = write_calls[1][0][0]

        self.assertIn("#show_solutions.update(false)", student_typ_content)
        self.assertIn("#show_solutions.update(true)", teacher_typ_content)

        # 3. Check if Typst was called twice
        self.assertEqual(mock_subprocess.call_count, 2)
        
        # Check the compilation commands
        expected_calls = [
            call(['typst', 'compile', '--root', str(self.project_root), str(self.project_root / 'test_exam.typ')], check=True, encoding='utf-8'),
            call(['typst', 'compile', '--root', str(self.project_root), str(self.project_root / 'test_exam_key.typ')], check=True, encoding='utf-8')
        ]
        mock_subprocess.assert_has_calls(expected_calls, any_order=False)

    @patch("scripts.build_exam.subprocess.run")
    @patch("scripts.build_exam.open", new_callable=unittest.mock.mock_open)
    def test_render_node_preview_logic(self, mock_open_file, mock_subprocess):
        """
        Test the logic of render_node_preview.
        """
        # Arrange
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Act
        img_path, error_msg = render_node_preview(self.sample_question)

        # Assert
        # 1. Check returned path and error
        self.assertIsNotNone(img_path)
        self.assertIsNone(error_msg)
        self.assertTrue(img_path.endswith(".png"))

        # 2. Check content of the .typ file
        self.assertEqual(mock_open_file.call_count, 1)
        
        write_calls = mock_open_file().write.call_args_list
        self.assertEqual(len(write_calls), 1)
        preview_typ_content = write_calls[0][0][0]

        self.assertIn("#show_solutions.update(true)", preview_typ_content)
        self.assertIn('#question("qn-test")', preview_typ_content)

        # 3. Check if Typst was called for PNG compilation
        self.assertEqual(mock_subprocess.call_count, 1)
        mock_subprocess.assert_called_once()


if __name__ == "__main__":
    unittest.main()
