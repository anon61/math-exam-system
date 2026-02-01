from pathlib import Path
import sys

from scripts.db_manager import DBManager

def check_integrity():
    """
    Loads the entire database and checks for broken references.
    """
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data"
    
    print("Initializing DBManager...")
    try:
        db = DBManager(data_path)
    except ValueError as e:
        print(f"Error during database loading: {e}")
        sys.exit(1)
    
    print(f"Database loaded. Found {len(db.nodes)} nodes.")
    
    errors = []
    
    for node in db.nodes.values():
        for field_name, field_value in node.__dict__.items():
            if not field_value:
                continue

            # Check fields that are single ID references
            if field_name.endswith("_ref") or field_name.endswith("_id"):
                if isinstance(field_value, str) and field_value not in db.nodes:
                    errors.append(
                        f"Broken reference in {node.id} -> {field_name}: "
                        f"ID '{field_value}' not found."
                    )
            
            # Check fields that are lists of IDs
            if field_name.endswith("_ids") or field_name.endswith("_sequence"):
                 if isinstance(field_value, list):
                    for item_id in field_value:
                        if item_id not in db.nodes:
                            errors.append(
                                f"Broken reference in {node.id} -> {field_name}: "
                                f"ID '{item_id}' not found."
                            )

    if errors:
        print("\n--- Integrity Check Failed ---")
        for error in errors:
            print(error)
        print(f"\nFound {len(errors)} errors.")
        sys.exit(1)
    else:
        print("\n--- Integrity Check Passed ---")
        print("All references are valid.")
        sys.exit(0)

if __name__ == "__main__":
    check_integrity()
