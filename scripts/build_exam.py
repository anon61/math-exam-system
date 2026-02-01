import argparse
import random
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager

# Template using standard Windows fonts
TEMPLATE = """
#import "src/lib.typ": *

#set page(
  paper: "a4", 
  margin: 2cm,
  header: align(right)[
    *Math Exam Generated on #datetime.today().display()*
  ]
)
#set text(font: "Times New Roman", size: 11pt)

= {title}

{content}

#v(2em)
#align(center)[*End of Examination*]
"""

def generate_exam(topic=None, count=3, filename="generated_exam"):
    print(f"Building Exam (Topic: {topic or 'Any'}, Questions: {count})...")
    
    # 1. Load Database
    try:
        db = DBManager(PROJECT_ROOT / "data")
    except Exception as e:
        print(f"Error loading database: {e}")
        return

    # 2. Filter Questions
    candidates = list(db.questions.values())
    if topic:
        # Case-insensitive topic matching
        candidates = [q for q in candidates if q.topic and topic.lower() in q.topic.lower()]
    
    if not candidates:
        print(f"No questions found for topic '{topic}'.")
        return

    # Select random questions
    if len(candidates) < count:
        print(f"Warning: Requested {count} questions, but only found {len(candidates)}.")
        selected = candidates
    else:
        selected = random.sample(candidates, count)

    # 3. Build Typst Content
    typst_body = ""
    for i, q in enumerate(selected, 1):
        typst_body += f"== Question {i}\n"
        typst_body += f'#question("{q.id}")\n\n'

    # 4. Fill Template
    full_source = TEMPLATE.format(
        title=f"Exam: {topic or 'General Mathematics'}",
        content=typst_body
    )

    # 5. Write File
    output_typ = PROJECT_ROOT / f"{filename}.typ"
    with open(output_typ, "w", encoding="utf-8") as f:
        f.write(full_source)
    
    print(f"Generated Typst file: {output_typ.name}")

    # 6. Compile PDF
    print("Compiling PDF...")
    try:
        # We enforce root=. to allow imports from src/
        subprocess.run(["typst", "compile", "--root", ".", str(output_typ)], check=True)
        print(f"Success! Exam ready: {filename}.pdf")
    except subprocess.CalledProcessError:
        print("Error: Typst compilation failed.")
    except FileNotFoundError:
        print("Error: Typst CLI not found. Is it installed?")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random math exam.")
    parser.add_argument("--topic", help="Filter by topic (e.g. 'Limits')")
    parser.add_argument("--count", type=int, default=3, help="Number of questions")
    parser.add_argument("--name", default="generated_exam", help="Output filename")
    
    args = parser.parse_args()
    
    generate_exam(topic=args.topic, count=args.count, filename=args.name)
