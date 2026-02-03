from pathlib import Path
import yaml
from dataclasses import fields  # <--- CRITICAL IMPORT
from scripts.models import (
    Question,
    Definition,
    Tool,
    Mistake,
    Example,
    Lecture,
    Tutorial,
)


class DBManager:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir
        # Initialize storage
        self.nodes = {}
        self.questions = {}
        self.definitions = {}
        self.tools = {}
        self.mistakes = {}
        self.examples = {}
        self.lectures = {}
        self.tutorials = {}

        if self.data_dir:
            self.load_all()

    def add_node(self, node):
        """Adds a node to the appropriate dictionary."""
        self.nodes[node.id] = node
        if isinstance(node, Question):
            self.questions[node.id] = node
        elif isinstance(node, Definition):
            self.definitions[node.id] = node
        elif isinstance(node, Tool):
            self.tools[node.id] = node
        elif isinstance(node, Mistake):
            self.mistakes[node.id] = node
        elif isinstance(node, Example):
            self.examples[node.id] = node
        elif isinstance(node, Lecture):
            self.lectures[node.id] = node
        elif isinstance(node, Tutorial):
            self.tutorials[node.id] = node

    def delete_node(self, node_id):
        """Deletes a node from all dictionaries."""
        if node_id in self.nodes:
            node = self.nodes.pop(node_id)
            if isinstance(node, Question):
                self.questions.pop(node_id, None)
            elif isinstance(node, Definition):
                self.definitions.pop(node_id, None)
            elif isinstance(node, Tool):
                self.tools.pop(node_id, None)
            elif isinstance(node, Mistake):
                self.mistakes.pop(node_id, None)
            elif isinstance(node, Example):
                self.examples.pop(node_id, None)
            elif isinstance(node, Lecture):
                self.lectures.pop(node_id, None)
            elif isinstance(node, Tutorial):
                self.tutorials.pop(node_id, None)
        else:
            raise ValueError(f"Node with id '{node_id}' not found.")

    def _load_file(self, filename, model_class, storage_dict):
        path = self.data_dir / filename
        if not path.exists():
            return  # Silent skip if missing

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or []

            # CRITICAL FIX: Use 'fields()' to get inherited fields (like 'id')
            valid_keys = {f.name for f in fields(model_class)}

            for item in data:
                if "id" not in item:
                    continue

                # Filter valid fields only
                clean_item = {k: v for k, v in item.items() if k in valid_keys}

                try:
                    obj = model_class(**clean_item)
                    storage_dict[obj.id] = obj
                except Exception as e:
                    print(f"[WARN] Skipping {item.get('id')} in {filename}: {e}")

        except Exception as e:
            print(f"[ERROR] Could not load {filename}: {e}")

    def load_all(self):
        self._load_file("questions.yaml", Question, self.questions)
        self._load_file("definitions.yaml", Definition, self.definitions)
        self._load_file("tools.yaml", Tool, self.tools)
        self._load_file("mistakes.yaml", Mistake, self.mistakes)
        self._load_file("examples.yaml", Example, self.examples)
        self._load_file("lectures.yaml", Lecture, self.lectures)
        self._load_file("tutorials.yaml", Tutorial, self.tutorials)
