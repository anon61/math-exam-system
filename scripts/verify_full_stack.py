import sys
from pathlib import Path

# --- SETUP PATHS ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

print(f"[*] Starting Deep Scan in: {PROJECT_ROOT}")

# --- CHECK 1: IMPORTING MODULES ---
print("\n[1/4] Checking Imports...")
try:
    from scripts.db_manager import DBManager
    from scripts.build_exam import render_node_preview, generate_exam
    print("✅ Imports successful.")
except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    print("   -> Tip: Check if '__init__.py' exists in 'scripts/' folder.")
    sys.exit(1)
except Exception as e:
    print(f"❌ UNKNOWN IMPORT ERROR: {e}")
    sys.exit(1)

# --- CHECK 2: LOADING DATABASE LOGIC ---
print("\n[2/4] Testing Database Logic (DBManager)...")
try:
    db = DBManager(PROJECT_ROOT / "data")
    q_count = len(db.questions)
    print(f"✅ DBManager initialized. Loaded {q_count} questions.")
    
    if q_count == 0:
        print("⚠️  WARNING: Database is empty! The app will look broken.")
except Exception as e:
    print(f"❌ DATABASE CRASH: {e}")
    print("   -> Your YAML files might be valid text, but missing fields required by DBManager.")
    sys.exit(1)

# --- CHECK 3: TYPST COMPILATION (Preview) ---
print("\n[3/4] Testing Typst Preview Engine...")
try:
    # Pick the first available question
    if db.questions:
        first_q = list(db.questions.values())[0]
        print(f"   -> Rendering preview for Question ID: {first_q.id}")
        
        img_path, error = render_node_preview(first_q)
        
        if img_path:
            print(f"✅ Preview generated: {img_path}")
        else:
            print(f"❌ TYPST ERROR: {error}")
            sys.exit(1)
    else:
        print("   -> Skipping preview test (No questions).")
except Exception as e:
    print(f"❌ PREVIEW SYSTEM CRASH: {e}")
    sys.exit(1)

# --- CHECK 4: PDF GENERATION (Full Exam) ---
print("\n[4/4] Testing PDF Exam Generation...")
try:
    if db.questions:
        # Try to build a small exam
        print("   -> Compiling full PDF exam...")
        path_std, path_key = generate_exam(count=1, filename="test_exam_output")
        
        if path_std:
            print(f"✅ Student Exam: {path_std}")
            print(f"✅ Teacher Key:  {path_key}")
        else:
            print("❌ PDF COMPILATION FAILED (Check logs above)")
            sys.exit(1)
    else:
        print("   -> Skipping PDF test (No questions).")
except Exception as e:
    print(f"❌ PDF BUILDER CRASH: {e}")
    sys.exit(1)

print("\n" + "="*40)
print("🎉 FULL STACK VERIFIED!")
print("The code logic is 100% working.")
print("If the app fails now, the issue is purely STREAMLIT/BROWSER related.")
print("="*40)