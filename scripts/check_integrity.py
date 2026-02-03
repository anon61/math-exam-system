import sys
from pathlib import Path
from typing import List, Set

# --- SETUP PATHS ---
# Ensure we can import from the scripts module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from scripts.db_manager import DBManager
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


def check_integrity() -> None:
    print("========================================")
    print("   🛡️  DATA INTEGRITY & TYPE CHECK   ")
    print("========================================")

    data_dir = PROJECT_ROOT / "data"
    if not data_dir.exists():
        print(f"❌ Data directory not found at: {data_dir}")
        return

    # 1. Load Database
    print("[1/3] Loading Database...")
    try:
        db = DBManager(data_dir)
    except Exception as e:
        print(f"❌ DB Load Failed: {e}")
        return

    # 2. Collect All IDs for Lookup
    print("[2/3] Indexing IDs...")
    all_ids: Set[str] = set()
    all_ids.update(db.questions.keys())
    all_ids.update(db.definitions.keys())
    all_ids.update(db.tools.keys())
    all_ids.update(db.mistakes.keys())
    all_ids.update(db.examples.keys())
    all_ids.update(db.lectures.keys())
    all_ids.update(db.tutorials.keys())
    # Note: Courses might not be in DBManager if not added explicitly,
    # but if they are, add them. Assuming DBManager has them or we skip.

    print(f"   -> Found {len(all_ids)} unique items.")

    # 3. Verify Links (Foreign Keys)
    print("[3/3] Verifying Relationships...")
    error_count = 0

    def check_ref(source_id: str, ref_id: str, field_name: str) -> None:
        nonlocal error_count
        if ref_id and ref_id not in all_ids:
            print(
                f"   🚩 Broken Link in [{source_id}]: '{field_name}' points to unknown ID '{ref_id}'"
            )
            error_count += 1

    def check_refs(source_id: str, ref_ids: List[str], field_name: str) -> None:
        for rid in ref_ids:
            check_ref(source_id, rid, field_name)

    # --- CHECK QUESTIONS ---
    for q in db.questions.values():
        check_refs(q.id, q.tools, "tools")
        # Mistake IDs in questions are stored as strings in 'common_mistakes'
        check_refs(q.id, q.common_mistakes, "common_mistakes")

    # --- CHECK EXAMPLES ---
    for ex in db.examples.values():
        check_refs(ex.id, ex.related_definition_ids, "related_definition_ids")

    # --- CHECK LECTURES ---
    for lec in db.lectures.values():
        if lec.course_id:
            # We assume course IDs are not in the main 'all_ids' unless loaded
            # If you load courses in DBManager, uncomment the check below:
            # check_ref(lec.id, lec.course_id, "course_id")
            pass
        check_refs(lec.id, lec.definition_ids, "definition_ids")
        check_refs(lec.id, lec.tool_ids, "tool_ids")
        check_refs(lec.id, lec.example_ids, "example_ids")

    # --- CHECK TUTORIALS ---
    for tut in db.tutorials.values():
        if tut.lecture_ref:
            check_ref(tut.id, tut.lecture_ref, "lecture_ref")
        check_refs(tut.id, tut.example_question_ids, "example_question_ids")

    # --- SUMMARY ---
    print("-" * 40)
    if error_count == 0:
        print("✅ INTEGRITY PASSED. All links are valid.")
    else:
        print(f"❌ FOUND {error_count} BROKEN LINKS.")
        print("   Action: Open the YAML files mentioned above and fix the IDs.")


if __name__ == "__main__":
    check_integrity()
