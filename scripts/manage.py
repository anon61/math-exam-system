
import argparse
import sys
from pathlib import Path
from dataclasses import fields, is_dataclass, MISSING
from enum import Enum
import yaml

# Add project root to sys.path to allow importing from 'scripts'
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from scripts.db_manager import DBManager
from scripts.models import (
    Definition, Tool, Example, Mistake, Course, Lecture, Tutorial, Question, Homework,
    ExampleType, Severity, AnswerStep, KnowledgeNode, Assessment
)

# A map from type names (strings) to the actual model classes
NODE_TYPE_MAP = {
    "definition": Definition,
    "tool": Tool,
    "example": Example,
    "mistake": Mistake,
    "course": Course,
    "lecture": Lecture,
    "tutorial": Tutorial,
    "question": Question,
    "homework": Homework,
}

# This is a simplified version of the map in DBManager, used for saving.
# A better long-term solution would be a public `save()` method on DBManager itself.
TYPE_TO_FILENAME_MAP = {
    Definition: "definitions.yaml",
    Tool: "tools.yaml",
    Example: "examples.yaml",
    Mistake: "mistakes.yaml",
    Course: "courses.yaml",
    Lecture: "lectures.yaml",
    Tutorial: "tutorials.yaml",
    Question: "questions.yaml",
    Homework: "homework.yaml",
}

def get_multiline_input(prompt):
    """Captures multi-line input from the user."""
    print(f"{prompt} (Press Enter on an empty line to finish):")
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def save_changes(db_manager: DBManager):
    """Saves all in-memory data back to the respective YAML files."""
    # Group nodes by their type
    nodes_by_type = {}
    for node in db_manager.nodes.values():
        node_type = type(node)
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)

    # Write each type to its corresponding file
    for node_type, filename in TYPE_TO_FILENAME_MAP.items():
        file_path = db_manager.data_path / filename
        nodes_to_save = nodes_by_type.get(node_type, [])
        
        if not nodes_to_save:
            # If no nodes of this type exist, ensure the file is removed
            if file_path.exists():
                file_path.unlink()
            continue

        list_of_dicts = []
        for node in sorted(nodes_to_save, key=lambda n: n.id): # Sort for consistency
            node_dict = {}
            for f in fields(node):
                value = getattr(node, f.name)
                if value is None or (isinstance(value, list) and not value):
                    continue # Don't write empty fields
                
                if isinstance(value, Enum):
                    node_dict[f.name] = value.value
                elif isinstance(value, list) and value and is_dataclass(value[0]):
                    node_dict[f.name] = [item.__dict__ for item in value]
                else:
                    node_dict[f.name] = value
            list_of_dicts.append(node_dict)

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(list_of_dicts, f, sort_keys=False, indent=2, default_flow_style=False)


def handle_add(args, db: DBManager):
    """Interactively adds a new node to the database."""
    node_type_str = args.type
    if node_type_str not in NODE_TYPE_MAP:
        print(f"Error: Unknown type '{node_type_str}'. Choices are: {list(NODE_TYPE_MAP.keys())}")
        return

    node_class = NODE_TYPE_MAP[node_type_str]
    print(f"--- Adding new {node_type_str} ---")

    data = {}
    # The corrected logic iterates over all fields returned by `dataclasses.fields`,
    # which correctly includes inherited fields in the proper order (parents first).
    for f in fields(node_class):
        prompt = f"Enter {f.name} ({f.type.__name__})"
        
        # Handle default values
        default_prompt = ""
        if f.default is not MISSING:
            default_prompt = f" [default: {f.default}]"
        elif f.default_factory is not MISSING:
            default_prompt = f" [default: {f.default_factory()}]"

        prompt = f"Enter {f.name} ({f.type.__name__}){default_prompt}: "

        # Special handling for different types
        if f.type is str and f.name in ('content', 'description', 'statement', 'given', 'to_prove', 'remedy', 'hint'):
            data[f.name] = get_multiline_input(prompt.strip())
        elif 'List' in str(f.type):
             val_str = input(prompt + "(comma-separated): ")
             data[f.name] = [item.strip() for item in val_str.split(',') if item.strip()] if val_str else []
        elif issubclass(f.type, Enum):
            enum_choices = [e.value for e in f.type]
            print(prompt + f"Choices: {', '.join(enum_choices)}")
            while True:
                val_str = input("> ")
                if val_str in enum_choices:
                    data[f.name] = f.type(val_str)
                    break
                else:
                    print(f"Invalid choice. Please select from: {', '.join(enum_choices)}")
        else: # Handles str, int, etc.
            while True:
                val_str = input(prompt)
                if val_str:
                    try:
                        data[f.name] = f.type(val_str)
                        break
                    except ValueError:
                        print(f"Error: Invalid type. Please enter a {f.type.__name__}.")
                elif f.default is not MISSING or f.default_factory is not MISSING:
                    break # Allow empty input to use default
                else:
                     # ID is always required
                    if f.name == 'id':
                        print("Error: ID is a required field.")
                    else: # Other fields can be empty if no default
                        data[f.name] = None
                        break

    try:
        # Filter out keys with None values unless they don't have a default
        final_data = {}
        for f in fields(node_class):
            field_name = f.name
            if field_name in data:
                final_data[field_name] = data[field_name]
            elif f.default is MISSING and f.default_factory is MISSING:
                 # This will likely cause an error below, which is what we want
                 # for missing required fields.
                 pass
        
        new_node = node_class(**final_data)
        db.add_node(new_node)
        save_changes(db)
        print(f"\n[Success] Added {node_type_str} '{new_node.id}'.")
    except (ValueError, TypeError) as e:
        print(f"\n[Error] Could not create {node_type_str}: {e}")

def handle_list(args, db: DBManager):
    """Lists all nodes of a specific type."""
    node_type_str = args.type
    if node_type_str not in NODE_TYPE_MAP:
        print(f"Error: Unknown type '{node_type_str}'. Choices are: {list(NODE_TYPE_MAP.keys())}")
        return

    node_class = NODE_TYPE_MAP[node_type_str]
    
    count = 0
    # Iterate through the main nodes dictionary
    for node_id, node in sorted(db.nodes.items()):
        if isinstance(node, node_class):
            if count == 0:
                print(f"--- Listing all {node_type_str}s ---")
            print(f"- ID: {node.id}")
            # Print a couple of key fields for context
            if hasattr(node, 'name'):
                print(f"  Name: {node.name}")
            elif hasattr(node, 'term'):
                print(f"  Term: {node.term}")
            elif hasattr(node, 'topic'):
                print(f"  Topic: {node.topic}")
            count += 1
            
    if count == 0:
        print(f"No {node_type_str}s found.")


def handle_delete(args, db: DBManager):
    """Deletes a node by its ID."""
    node_id = args.id
    try:
        db.delete_node(node_id)
        save_changes(db)
        print(f"[Success] Deleted node '{node_id}'.")
    except ValueError as e:
        print(f"[Error] {e}")


def main():
    parser = argparse.ArgumentParser(description="Math Exam System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'add' command
    parser_add = subparsers.add_parser("add", help="Add a new node (question, definition, etc.)")
    parser_add.add_argument("type", help=f"The type of node to add. Choices: {list(NODE_TYPE_MAP.keys())}")
    parser_add.set_defaults(func=handle_add)

    # 'list' command
    parser_list = subparsers.add_parser("list", help="List all nodes of a certain type")
    parser_list.add_argument("type", help=f"The type of node to list. Choices: {list(NODE_TYPE_MAP.keys())}")
    parser_list.set_defaults(func=handle_list)

    # 'delete' command
    parser_delete = subparsers.add_parser("delete", help="Delete a node by its ID")
    parser_delete.add_argument("id", help="The ID of the node to delete")
    parser_delete.set_defaults(func=handle_delete)

    args = parser.parse_args()

    # Initialize DBManager
    data_path = project_root / "data"
    try:
        db = DBManager(data_path)
    except Exception as e:
        print(f"Failed to load database: {e}")
        sys.exit(1)

    # Execute the appropriate function
    args.func(args, db)


if __name__ == "__main__":
    main()
