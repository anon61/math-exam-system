import argparse
import random
import subprocess
import sys
import os
from pathlib import Path

# --- 1. SETUP PATHS ---
# Robustly find the project root regardless of where script is run
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager
from scripts.models import Question, Definition, Tool, Mistake, Example, Lecture, Tutorial

# --- 2. TEMPLATE ---
# The template explicitly uses the boolean passed from python
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

# --- 3. PREVIEW RENDERER ---
def render_node_preview(node):
    """
    Renders a single node (Question, Def, etc.) to a PNG.
    """
    preview_dir = PROJECT_ROOT / "temp_previews"
    preview_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate Typst Call
    if isinstance(node, Question):
        typ_call = f'#question("{node.id}")'
    elif isinstance(node, Definition):
        typ_call = f'#def("{node.id}")'
    elif isinstance(node, Tool):
        typ_call = f'#tool("{node.id}")'
    elif isinstance(node, Mistake):
        typ_call = f'#mistake("{node.id}")' 
    elif isinstance(node, Example):
         typ_call = f'#ex("{node.id}")'
    elif isinstance(node, Lecture):
         typ_call = f'#lecture("{node.id}")'
    elif isinstance(node, Tutorial):
         typ_call = f'#tutorial("{node.id}")'
    else:
        return None, f"Node type '{type(node).__name__}' not supported for preview."

    # Preview Template: Force solutions ON, simplified page
    typ_content = f"""
    #import "/src/lib.typ": *
    #show_solutions.update(true) 
    #set page(width: 14cm, height: auto, margin: 0.5cm, header: none, footer: none)
    #set text(font: "Times New Roman", size: 11pt)
    
    {typ_call}
    """
    
    typ_file = preview_dir / f"{node.id}.typ"
    img_file = preview_dir / f"{node.id}.png"
    
    # Write source file
    with open(typ_file, "w", encoding="utf-8") as f:
        f.write(typ_content)
        
    # Compile
    # CRITICAL: --root must be PROJECT_ROOT for absolute imports like "/src/lib.typ" to work
    cmd = [
        "typst", "compile", 
        "--root", str(PROJECT_ROOT), 
        "--format", "png", 
        "--ppi", "144", 
        str(typ_file), 
        str(img_file)
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True, 
            encoding="utf-8"
        )
        
        if result.returncode == 0:
            return str(img_file), None
        else:
            return None, f"Typst Error:\n{result.stderr}"
            
    except Exception as e:
        return None, f"Subprocess Failed: {str(e)}"

# --- 4. EXAM GENERATOR ---
def generate_exam(topic=None, count=3, filename="generated_exam", specific_ids=None):
    """
    Generates PDF pair (Student + Key).
    """
    print(f"[INFO] Initializing DB from {PROJECT_ROOT / 'data'}")
    
    try:
        db = DBManager(PROJECT_ROOT / "data")
    except Exception as e:
        print(f"[ERROR] DB Init Failed: {e}")
        return None, None

    # Select Questions
    selected = []
    if specific_ids:
        for qid in specific_ids:
            if qid in db.questions: 
                selected.append(db.questions[qid])
            else:
                print(f"[WARN] ID {qid} not found in DB.")
    else:
        candidates = list(db.questions.values())
        if topic: 
            candidates = [q for q in candidates if topic.lower() in (q.topic or "").lower()]
        
        count = min(len(candidates), count)
        if count > 0:
            selected = random.sample(candidates, count)

    if not selected:
        print("[WARN] No questions selected.")
        return None, None

    # Build Body
    typst_body = ""
    for i, q in enumerate(selected, 1):
        typst_body += f"== Question {i}\n#question(\"{q.id}\")\n\n"

    # --- COMPILE 1: STUDENT VERSION (No Solutions) ---
    # Passing "false" (Typst boolean) to the template
    src_student = TEMPLATE.format(title=f"Exam: {topic or 'General'}", content=typst_body, show_sol="false")
    path_student = PROJECT_ROOT / f"{filename}.pdf"
    
    with open(PROJECT_ROOT / f"{filename}.typ", "w", encoding="utf-8") as f:
        f.write(src_student)
    
    print(f"[INFO] Compiling Student Version...")
    res_std = subprocess.run(["typst", "compile", "--root", str(PROJECT_ROOT), str(PROJECT_ROOT / f"{filename}.typ")], capture_output=True)
    if res_std.returncode != 0:
        print(f"[ERROR] Student Compile Failed:\n{res_std.stderr.decode()}")
        return None, None

    # --- COMPILE 2: TEACHER VERSION (With Solutions) ---
    # Passing "true" to the template
    src_teacher = TEMPLATE.format(title=f"Exam: {topic or 'General'} (KEY)", content=typst_body, show_sol="true")
    path_teacher = PROJECT_ROOT / f"{filename}_key.pdf"
    
    with open(PROJECT_ROOT / f"{filename}_key.typ", "w", encoding="utf-8") as f:
        f.write(src_teacher)
        
    print(f"[INFO] Compiling Teacher Version...")
    res_key = subprocess.run(["typst", "compile", "--root", str(PROJECT_ROOT), str(PROJECT_ROOT / f"{filename}_key.typ")], capture_output=True)
    
    if res_key.returncode == 0:
        return path_student, path_teacher
    else:
        print(f"[ERROR] Key Compile Failed:\n{res_key.stderr.decode()}")
        return None, None
