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

# --- 1. CONFIGURATION ---
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

# --- 2. YAML FORMATTER (THE FIX) ---
def str_presenter(dumper, data):
    """
    Configures YAML to use the Block Style (|) for strings containing
    math symbols like $, \, {, }, or newlines.
    This prevents PyYAML from escaping characters (e.g. changing '\' to '\\').
    """
    if len(data.splitlines()) > 1 or any(c in data for c in "$[]{}\\"):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

# --- 3. CORE LOGIC ---
def get_multiline_input(prompt):
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
    """Saves all in-memory data back to YAML with the new formatter."""
    nodes_by_type = {}
    for node in db_manager.nodes.values():
        node_type = type(node)
        if node_type not in nodes_by_type:
            nodes_by_type[node_type] = []
        nodes_by_type[node_type].append(node)

    for node_type, filename in TYPE_TO_FILENAME_MAP.items():
        file_path = db_manager.data_path / filename
        nodes_to_save = nodes_by_type.get(node_type, [])
        
        if not nodes_to_save:
            if file_path.exists():
                file_path.unlink()
            continue

        list_of_dicts = []
        for node in sorted(nodes_to_save, key=lambda n: n.id):
            node_dict = {}
            for f in fields(node):
                value = getattr(node, f.name)
                if value is None or (isinstance(value, list) and not value):
                    continue
                
                if isinstance(value, Enum):
                    node_dict[f.name] = value.value
                elif isinstance(value, list) and value and is_dataclass(value[0]):
                    node_dict[f.name] = [item.__dict__ for item in value]
                else:
                    node_dict[f.name] = value
            list_of_dicts.append(node_dict)

        with open(file_path, 'w', encoding='utf-8') as f:
            # allow_unicode=True is CRITICAL for math symbols
            yaml.dump(list_of_dicts, f, sort_keys=False, indent=2, 
                      default_flow_style=False, allow_unicode=True)

def handle_add(args, db: DBManager):
    node_type_str = args.type
    if node_type_str not in NODE_TYPE_MAP:
        print(f"Error: Unknown type '{node_type_str}'")
        return

    node_class = NODE_TYPE_MAP[node_type_str]
    print(f"--- Adding new {node_type_str} ---")

    data = {}
    for f in fields(node_class):
        # ... (Same input logic as before, abbreviated for brevity but keep original logic)
        prompt = f"Enter {f.name}"
        if f.default is not MISSING:
             prompt += f" [default: {f.default}]"
        
        prompt += ": "

        if f.type is str and f.name in ('content', 'description', 'statement', 'given', 'to_prove', 'remedy', 'hint'):
            data[f.name] = get_multiline_input(prompt.strip())
        elif 'List' in str(f.type):
             val_str = input(prompt + "(comma-separated): ")
             data[f.name] = [item.strip() for item in val_str.split(',') if item.strip()] if val_str else []
        elif issubclass(f.type, Enum):
            enum_choices = [e.value for e in f.type]
            while True:
                val_str = input(prompt + f"Choices: {enum_choices} > ")
                if val_str in enum_choices:
                    data[f.name] = f.type(val_str)
                    break
        else:
            val_str = input(prompt)
            if val_str:
                data[f.name] = val_str
            elif f.name == 'id':
                print("ID is required!")
                return

    try:
        # Filter None values
        final_data = {k: v for k, v in data.items() if v is not None}
        new_node = node_class(**final_data)
        db.add_node(new_node)
        save_changes(db) # This now uses the smart dumper
        print(f"\n[Success] Added {node_type_str} '{new_node.id}'.")
    except Exception as e:
        print(f"\n[Error] {e}")

def handle_list(args, db: DBManager):
    node_type_str = args.type
    node_class = NODE_TYPE_MAP.get(node_type_str)
    if not node_class: return

    for node in sorted(db.nodes.values(), key=lambda x: x.id):
        if isinstance(node, node_class):
            print(f"- {node.id}")

def handle_delete(args, db: DBManager):
    try:
        db.delete_node(args.id)
        save_changes(db)
        print(f"[Success] Deleted node '{args.id}'.")
    except ValueError as e:
        print(f"[Error] {e}")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add")
    p_add.add_argument("type")
    p_add.set_defaults(func=handle_add)

    p_list = subparsers.add_parser("list")
    p_list.add_argument("type")
    p_list.set_defaults(func=handle_list)

    p_del = subparsers.add_parser("delete")
    p_del.add_argument("id")
    p_del.set_defaults(func=handle_delete)

    args = parser.parse_args()
    data_path = project_root / "data"
    try:
        db = DBManager(data_path)
        args.func(args, db)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()