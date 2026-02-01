import argparse
import random
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager

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

def generate_exam(topic=None, count=3, filename="generated_exam", specific_ids=None):
    """
    Generates a PDF exam.
    :param topic: Filter questions by topic (ignored if specific_ids is provided)
    :param count: Number of random questions (ignored if specific_ids is provided)
    :param specific_ids: A list of strings (Question IDs) to include exactly.
    """
    print(f"🏗️  Building Exam...")
    
    # 1. Load Database
    try:
        db = DBManager(PROJECT_ROOT / "data")
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return None

    selected = []

    # 2. Selection Logic
    if specific_ids:
        # Manual Selection Mode (from GUI)
        print(f"   -> Mode: Manual Selection ({len(specific_ids)} items)")
        for qid in specific_ids:
            if qid in db.questions:
                selected.append(db.questions[qid])
            else:
                print(f"⚠️  Warning: Question ID '{qid}' not found.")
    else:
        # Random Mode (from CLI)
        print(f"   -> Mode: Random Sampling (Topic: {topic or 'Any'}, Count: {count})")
        candidates = list(db.questions.values())
        if topic:
            candidates = [q for q in candidates if q.topic and topic.lower() in q.topic.lower()]
        
        if not candidates:
            print(f"❌ No questions found for topic '{topic}'.")
            return None

        if len(candidates) < count:
            print(f"⚠️  Warning: Requested {count} questions, but only found {len(candidates)}.")
            selected = candidates
        else:
            selected = random.sample(candidates, count)

    # 3. Build Typst Content
    typst_body = ""
    for i, q in enumerate(selected, 1):
        typst_body += f"== Question {i}\n"
        typst_body += f"#question(\"{q.id}\")\n\n"

    # 4. Fill Template
    full_source = TEMPLATE.format(
        title=f"Exam: {topic or 'General Mathematics'}",
        content=typst_body
    )

    # 5. Write File
    output_typ = PROJECT_ROOT / f"{filename}.typ"
    with open(output_typ, "w", encoding="utf-8") as f:
        f.write(full_source)
    
    print(f"✅ Generated Typst file: {output_typ.name}")

    # 6. Compile PDF
    print("⚙️  Compiling PDF...")
    output_pdf = PROJECT_ROOT / f"{filename}.pdf"
    try:
        subprocess.run(["typst", "compile", "--root", ".", str(output_typ)], check=True)
        print(f"🎉 Success! Exam ready: {output_pdf.name}")
        return output_pdf # Return path for the GUI to download
    except subprocess.CalledProcessError:
        print("❌ Error: Typst compilation failed.")
        return None
    except FileNotFoundError:
        print("❌ Error: Typst CLI not found. Is it installed?")
        return None

def render_preview(question, project_root):
    """Compiles a single question to SVG for the UI."""
    preview_dir = project_root / "temp_previews"
    preview_dir.mkdir(exist_ok=True)
    
    # Small template just for the snippet
    typ_content = f"""
#import "src/lib.typ": *
#set page(width: auto, height: auto, margin: 1cm)
#question("{question.id}")
"""
    
    typ_file = preview_dir / f"{question.id}.typ"
    svg_file = preview_dir / f"{question.id}.svg"
    
    with open(typ_file, "w", encoding="utf-8") as f:
        f.write(typ_content)
        
    try:
        # Use capture_output to get stderr
        result = subprocess.run(
            ["typst", "compile", "--format", "svg", "--root", str(project_root), str(typ_file), str(svg_file)],
            check=True, capture_output=True, text=True
        )
        return svg_file, None
    except subprocess.CalledProcessError as e:
        # Return the error message from stderr
        return None, e.stderr
    except FileNotFoundError:
        return None, "Typst CLI not found. Is it installed on your system PATH?"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random math exam.")
    parser.add_argument("--topic", help="Filter by topic (e.g. 'Limits')")
    parser.add_argument("--count", type=int, default=3, help="Number of questions")
    parser.add_argument("--name", default="generated_exam", help="Output filename")
    
    args = parser.parse_args()
    
    generate_exam(topic=args.topic, count=args.count, filename=args.name)