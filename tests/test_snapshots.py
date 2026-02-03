import sys
from pathlib import Path
import pytest

# --- SETUP PATHS ---
# Ensure we can import from the scripts module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager  # noqa: E402
from scripts.build_exam import generate_exam  # noqa: E402
from scripts.models import Question, AnswerStep  # noqa: E402


@pytest.fixture
def mock_db():
    """
    Provides a DBManager with a fixed, in-memory set of mock data
    instead of loading from YAML files. This ensures tests are deterministic.
    """
    db = DBManager()  # Initialize with no data path

    # Create Mock Data
    mock_questions = [
        Question(
            id="q1",
            topic="Algebra",
            year=2023,
            lecturer="Dr. PyTest",
            given="Let $x = 3$.",
            to_prove="Find $x^2$.",
            answer_steps=[
                AnswerStep(type="Calculation", title="Step 1", content="$3^2 = 9$")
            ],
        ),
        Question(
            id="q2",
            topic="Calculus",
            year=2023,
            lecturer="Dr. PyTest",
            given="Let $f(x) = x^2$.",
            to_prove="Find the derivative.",
            answer_steps=[
                AnswerStep(
                    type="Calculation", title="Step 1", content="$f'(x) = 2x$."
                )
            ],
        ),
    ]

    for q in mock_questions:
        db.add_node(q)

    return db


def test_exam_generation_snapshot(mock_db, monkeypatch):
    """
    Tests that the generated Typst content matches a 'golden' snapshot.
    This ensures that changes to build_exam.py logic are detected.
    """
    # 1. Arrange
    # Use monkeypatch to replace the DBManager instance used in generate_exam
    monkeypatch.setattr("scripts.build_exam.DBManager", lambda path: mock_db)

    # 2. Act
    # Generate the exam using a fixed set of questions
    generate_exam(filename="test_exam_output", specific_ids=["q1", "q2"])

    # 3. Assert
    # Define the "Golden String" - the exact output we expect.
    # Note: Whitespace and newlines are important!
    golden_snapshot = """
#import "/src/lib.typ": *

#show_solutions.update({show_sol})

#set page(
  paper: "a4", 
  margin: 2cm,
  header: align(right)[
    *Math Exam Generated on #datetime.today().display()*
  ]
)
#set text(font: "Times New Roman", size: 11pt)

= {title}

== Question 1
#question("q1")

== Question 2
#question("q2")



#v(2em)
#align(center)[*End of Examination*]
"""

    # Compare the actual generated content against the golden snapshot
    generated_file_path = PROJECT_ROOT / "test_exam_output.typ"
    with open(generated_file_path, "r", encoding="utf-8") as f:
        generated_content = f.read()

    # We format the title and show_sol out of the snapshot, as they are dynamic
    golden_student = golden_snapshot.format(
        title="Exam: General", show_sol="false"
    )
    assert generated_content.strip() == golden_student.strip()

    # Now check the key
    generated_key_path = PROJECT_ROOT / "test_exam_output_key.typ"
    with open(generated_key_path, "r", encoding="utf-8") as f:
        generated_key_content = f.read()

    golden_key = golden_snapshot.format(
        title="Exam: General (KEY)", show_sol="true"
    )
    assert generated_key_content.strip() == golden_key.strip()
