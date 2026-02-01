import argparse
import random
import subprocess
import sys
from pathlib import Path

# --- 1. SETUP PATHS ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# --- 2. IMPORTS ---
from scripts.db_manager import DBManager
from scripts.models import Question, Definition, Tool, Mistake, Example

# --- 3. TEMPLATE (For PDF) ---
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

# --- 4. PREVIEW RENDERER ---
def render_node_preview(node):
    """
    Compiles a single node to PNG.
    Returns: (image_path_string, error_message_string)
    """
    preview_dir = PROJECT_ROOT / "temp_previews"
    preview_dir.mkdir(exist_ok=True)
    
    if isinstance(node, Question):
        typ_call = f'#question("{node.id}")'
    elif isinstance(node, Definition):
        typ_call = f'#def("{node.id}")'
    elif isinstance(node, Tool):
        typ_call = f'#tool("{node.id}")'
    elif isinstance(node, Mistake):
        typ_call = f'== Mistake: {node.id}\n{node.description}' 
    elif isinstance(node, Example):
         typ_call = f'#ex("{node.id}")'
    else:
        return None, "Preview not supported for this type"

    # FIX: Set FIXED width (14cm) to prevent "Billboard" scaling effect
    typ_content = f"""
    #import "/src/lib.typ": *
    #set page(width: 14cm, height: auto, margin: 0.5cm, header: none, footer: none)
    #set text(font: "Times New Roman", size: 11pt)
    
    {typ_call}
    """
    
    typ_file = preview_dir / f"{node.id}.typ"
    img_file = preview_dir / f"{node.id}.png"
    
    with open(typ_file, "w", encoding="utf-8") as f:
        f.write(typ_content)
        
    try:
        # 144 PPI is standard for crisp screen reading
        result = subprocess.run(
            ["typst", "compile", "--root", str(PROJECT_ROOT), "--format", "png", "--ppi", "144", str(typ_file), str(img_file)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        if result.returncode != 0:
            return None, f"Typst Error: {result.stderr}"
            
        return str(img_file), None
        
    except FileNotFoundError:
        return None, "Error: 'typst' executable not found."
    except Exception as e:
        return None, f"System Error: {str(e)}"

# --- 5. EXAM GENERATOR ---
def generate_exam(topic=None, count=3, filename="generated_exam", specific_ids=None):
    print(f"[INFO] Building Exam...")
    
    try:
        db = DBManager(PROJECT_ROOT / "data")
    except Exception as e:
        print(f"[ERROR] Error loading database: {e}")
        return None

    selected = []

    if specific_ids:
        for qid in specific_ids:
            if qid in db.questions:
                selected.append(db.questions[qid])
    else:
        candidates = list(db.questions.values())
        if topic:
            candidates = [q for q in candidates if q.topic and topic.lower() in q.topic.lower()]
        
        if not candidates:
            return None
        selected = random.sample(candidates, min(len(candidates), count)) if candidates else []

    typst_body = ""
    for i, q in enumerate(selected, 1):
        typst_body += f"== Question {i}\n"
        typst_body += f"#question(\"{q.id}\")\n\n"

    full_source = TEMPLATE.format(
        title=f"Exam: {topic or 'General Mathematics'}",
        content=typst_body
    )

    output_typ = PROJECT_ROOT / f"{filename}.typ"
    with open(output_typ, "w", encoding="utf-8") as f:
        f.write(full_source)
    
    output_pdf = PROJECT_ROOT / f"{filename}.pdf"
    
    try:
        subprocess.run(
            ["typst", "compile", "--root", str(PROJECT_ROOT), str(output_typ)], 
            check=True,
            encoding="utf-8"
        )
        print(f"[SUCCESS] Exam ready: {output_pdf.name}")
        return output_pdf
    except Exception as e:
        print(f"[ERROR] Compilation failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random math exam.")
    parser.add_argument("--topic", help="Filter by topic")
    parser.add_argument("--count", type=int, default=3, help="Number of questions")
    parser.add_argument("--name", default="generated_exam", help="Output filename")
    
    args = parser.parse_args()
    generate_exam(topic=args.topic, count=args.count, filename=args.name)