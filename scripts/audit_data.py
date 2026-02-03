import sys
import yaml
from pathlib import Path
from dataclasses import fields

# --- SETUP PATHS ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.models import (  # noqa: E402
    Question,
    Definition,
    Tool,
    Mistake,
    Example,
    Course,
    Lecture,
    Tutorial,
)

# --- CONFIGURATION ---
# Map filename to the Class it should match
DATA_MAP = {
    "questions.yaml": Question,
    "definitions.yaml": Definition,
    "tools.yaml": Tool,
    "examples.yaml": Example,
    "mistakes.yaml": Mistake,
    "courses.yaml": Course,
    "lectures.yaml": Lecture,
    "tutorials.yaml": Tutorial,
}


def audit_file(filename, model_class):
    file_path = PROJECT_ROOT / "data" / filename
    if not file_path.exists():
        print(f"⚠️  MISSING: {filename}")
        return

    print(f"🔎 Scanning {filename}...")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"   ❌ FATAL: Could not read YAML file. {e}")
        return

    if not data:
        print("   ⚠️  Empty file.")
        return

    error_count = 0

    # Get the list of valid fields for this Class
    valid_fields = {f.name for f in fields(model_class)}

    for i, item in enumerate(data):
        item_id = item.get("id", f"Index {i}")

        # 1. Check for UNKNOWN fields (arguments that shouldn't be there)
        item_keys = set(item.keys())
        unknown_fields = item_keys - valid_fields

        # 2. Check for MISSING fields (arguments that must be there)
        #    (We create a dummy instance to see what Python complains about)
        try:
            model_class(**item)
        except TypeError as e:
            msg = str(e)
            error_count += 1
            print(f"   ❌ ID [{item_id}]: {msg}")

            # Helper: If it's an unexpected argument, tell us which one
            if "unexpected keyword argument" in msg:
                print(f"      -> FOUND: {list(unknown_fields)}")
                print(f"      -> EXPECTED: {list(valid_fields)}")

            # Helper: If it's missing arguments
            if "missing" in msg and "argument" in msg:
                print(f"      -> DATA HAS: {list(item_keys)}")

    if error_count == 0:
        print("   ✅ Perfect Match.")
    else:
        print(f"   🚩 Found {error_count} errors in this file.")
    print("-" * 40)


if __name__ == "__main__":
    print("========================================")
    print("   DATA SCHEMA AUDIT (SOFT LOAD)")
    print("========================================")

    for fname, cls in DATA_MAP.items():
        audit_file(fname, cls)

    print("\nAudit Complete.")
