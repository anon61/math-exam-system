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

# --- 3. TEMPLATE ---
# FIX: We add a toggle at the top to control visibility
TEMPLATE = """
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

{content}

#v(2em)
#align(center)[*End of Examination*]
"""

# --- 4. PREVIEW RENDERER (Unchanged) ---
def render_node_preview(node):
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
        return None, "Preview not supported."

    # Force Solutions to be visible in Preview
    typ_content = f"""
    #import "/src/lib.typ": *
    #show_solutions.update(true) 
    #set page(width: 14cm, height: auto, margin: 0.5cm, header: none, footer: none)
    #set text(font: "Times New Roman", size: 11pt)
    
    {typ_call}
    """
    
    typ_file = preview_dir / f"{node.id}.typ"
    img_file = preview_dir / f"{node.id}.png"
    
    with open(typ_file, "w", encoding="utf-8") as f:
        f.write(typ_content)
        
    try:
        result = subprocess.run(
            ["typst", "compile", "--root", str(PROJECT_ROOT), "--format", "png", "--ppi", "144", str(typ_file), str(img_file)],
            capture_output=True, text=True, encoding="utf-8"
        )
        return str(img_file) if result.returncode == 0 else None, result.stderr if result.returncode != 0 else None
    except Exception as e:
        return None, str(e)

# --- 5. EXAM GENERATOR (Double Compilation) ---
def generate_exam(topic=None, count=3, filename="generated_exam", specific_ids=None):
    print(f"[INFO] Building Exam Pairs...")
    
    try:
        db = DBManager(PROJECT_ROOT / "data")
    except Exception as e:
        return None, None # Return tuple

    selected = []
    if specific_ids:
        for qid in specific_ids:
            if qid in db.questions: selected.append(db.questions[qid])
    else:
        candidates = list(db.questions.values())
        if topic: candidates = [q for q in candidates if topic.lower() in (q.topic or "").lower()]
        selected = random.sample(candidates, min(len(candidates), count)) if candidates else []

    typst_body = ""
    for i, q in enumerate(selected, 1):
        typst_body += f"== Question {i}\n#question(\"{q.id}\")\n\n"

    # --- COMPILE 1: STUDENT VERSION (No Solutions) ---
    src_student = TEMPLATE.format(title=f"Exam: {topic or 'General'}", content=typst_body, show_sol="false")
    path_student = PROJECT_ROOT / f"{filename}.pdf"
    
    with open(PROJECT_ROOT / f"{filename}.typ", "w", encoding="utf-8") as f:
        f.write(src_student)
    
    try:
        subprocess.run(["typst", "compile", "--root", str(PROJECT_ROOT), str(PROJECT_ROOT / f"{filename}.typ")], check=True, encoding="utf-8")
    except: return None, None

    # --- COMPILE 2: TEACHER VERSION (With Solutions) ---
    src_teacher = TEMPLATE.format(title=f"Exam: {topic or 'General'} (KEY)", content=typst_body, show_sol="true")
    path_teacher = PROJECT_ROOT / f"{filename}_key.pdf"
    
    with open(PROJECT_ROOT / f"{filename}_key.typ", "w", encoding="utf-8") as f:
        f.write(src_teacher)
        
    try:
        subprocess.run(["typst", "compile", "--root", str(PROJECT_ROOT), str(PROJECT_ROOT / f"{filename}_key.typ")], check=True, encoding="utf-8")
        print(f"[SUCCESS] Generated Pair: {path_student.name} & {path_teacher.name}")
        return path_student, path_teacher
    except: return None, None
