import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager

def check_integrity():
    print("🔍 Starting Database Integrity Check...")
    data_path = PROJECT_ROOT / "data"
    
    try:
        db = DBManager(data_path)
    except Exception as e:
        print(f"❌ CRITICAL: Could not load database. {e}")
        sys.exit(1)

    print(f"   Loaded {len(db.nodes)} nodes.")
    errors = []

    for node_id, node in db.nodes.items():
        # 1. Check 'related_definition_ids' (Examples)
        if hasattr(node, 'related_definition_ids'):
            for target in node.related_definition_ids:
                if target not in db.definitions:
                    errors.append(f"[{node_id}] refers to unknown Definition '{target}'")

        # 2. Check 'lecture_ref' (Tutorials)
        if hasattr(node, 'lecture_ref') and node.lecture_ref:
            if node.lecture_ref not in db.lectures:
                errors.append(f"[{node_id}] refers to unknown Lecture '{node.lecture_ref}'")

        # 3. Check Assessment Lists (Questions/Homework)
        # Fields: tool_ids, mistake_ids, example_ids
        if hasattr(node, 'tool_ids'):
            for target in node.tool_ids:
                if target not in db.tools:
                    errors.append(f"[{node_id}] refers to unknown Tool '{target}'")
        
        if hasattr(node, 'mistake_ids'):
            for target in node.mistake_ids:
                if target not in db.mistakes:
                    errors.append(f"[{node_id}] refers to unknown Mistake '{target}'")

        # 4. Check Sequence Lists (Courses)
        if hasattr(node, 'definition_sequence'):
            for target in node.definition_sequence:
                if target not in db.definitions:
                    errors.append(f"[{node_id}] Broken definition_sequence link '{target}'")

    if errors:
        print(f"\n❌ FAILED: Found {len(errors)} integrity errors:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    else:
        print("\n✅ SUCCESS: Database integrity verified. No broken links.")
        sys.exit(0)

if __name__ == "__main__":
    check_integrity()