import yaml
from pathlib import Path
from typing import Dict, Type, List

from scripts.models import (
    KnowledgeNode,
    Definition,
    Tool,
    Example,
    Mistake,
    Course,
    Lecture,
    Tutorial,
    Question,
    Homework,
    ExampleType,
    Severity,
    AnswerStep,
)

class DBManager:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.nodes: Dict[str, KnowledgeNode] = {}

        # Type-specific storage
        self.definitions: Dict[str, Definition] = {}
        self.tools: Dict[str, Tool] = {}
        self.examples: Dict[str, Example] = {}
        self.mistakes: Dict[str, Mistake] = {}
        self.courses: Dict[str, Course] = {}
        self.lectures: Dict[str, Lecture] = {}
        self.tutorials: Dict[str, Tutorial] = {}
        self.questions: Dict[str, Question] = {}
        self.homeworks: Dict[str, Homework] = {}

        self._type_map = {
            "definitions.yaml": (Definition, self.definitions),
            "tools.yaml": (Tool, self.tools),
            "examples.yaml": (Example, self.examples),
            "mistakes.yaml": (Mistake, self.mistakes),
            "courses.yaml": (Course, self.courses),
            "lectures.yaml": (Lecture, self.lectures),
            "tutorials.yaml": (Tutorial, self.tutorials),
            "questions.yaml": (Question, self.questions),
            "homework.yaml": (Homework, self.homeworks),
        }
        self.load_db()

    def load_db(self):
        for filename, (cls, storage_dict) in self._type_map.items():
            file_path = self.data_path / filename
            if not file_path.exists():
                continue

            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if not data:
                    continue
                
                for item_data in data:
                    # Handle Enums
                    if "type" in item_data and "type" in Example.__annotations__:
                        item_data["type"] = ExampleType(item_data["type"])
                    if "severity" in item_data and "severity" in Mistake.__annotations__:
                        item_data["severity"] = Severity(item_data["severity"])

                    # Handle nested Question data
                    if cls is Question and "answer_steps" in item_data:
                        raw_steps = item_data.get("answer_steps") or []
                        item_data["answer_steps"] = [AnswerStep(**step) for step in raw_steps if step]


                    node = cls(**item_data)
                    if node.id in self.nodes:
                        raise ValueError(f"Duplicate ID found: {node.id}")
                    
                    self.nodes[node.id] = node
                    storage_dict[node.id] = node

    def add_node(self, node: KnowledgeNode):
        if node.id in self.nodes:
            raise ValueError(f"Node with ID '{node.id}' already exists.")
        
        self.nodes[node.id] = node
        for _, (cls, storage_dict) in self._type_map.items():
            if isinstance(node, cls):
                storage_dict[node.id] = node
                break

    def delete_node(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"Node with ID '{node_id}' not found.")

        # Check for referential integrity
        for existing_node in self.nodes.values():
            for field_name, field_value in existing_node.__dict__.items():
                if isinstance(field_value, list) and node_id in field_value:
                    raise ValueError(
                        f"Cannot delete node '{node_id}' because it is referenced by node '{existing_node.id}' in field '{field_name}'."
                    )
                if field_name.endswith("_ref") and field_value == node_id:
                     raise ValueError(
                        f"Cannot delete node '{node_id}' because it is referenced by node '{existing_node.id}' in field '{field_name}'."
                    )

        node_to_delete = self.nodes.pop(node_id)
        for _, (cls, storage_dict) in self._type_map.items():
            if isinstance(node_to_delete, cls):
                if node_id in storage_dict:
                    del storage_dict[node_id]
                break

    def update_node_id(self, old_id: str, new_id: str):
        if old_id not in self.nodes:
            raise ValueError(f"Node with ID '{old_id}' not found.")
        if new_id in self.nodes:
            raise ValueError(f"Node with ID '{new_id}' already exists.")

        # Update the node's ID itself
        node_to_update = self.nodes.pop(old_id)
        node_to_update.id = new_id
        self.nodes[new_id] = node_to_update

        # Update the type-specific dictionary
        for _, (cls, storage_dict) in self._type_map.items():
            if isinstance(node_to_update, cls):
                if old_id in storage_dict:
                    del storage_dict[old_id]
                    storage_dict[new_id] = node_to_update
                break

        # Update all references to the old ID
        for node in self.nodes.values():
            for field_name, field_value in node.__dict__.items():
                if isinstance(field_value, list):
                    if old_id in field_value:
                        # Replace all occurrences
                        node.__dict__[field_name] = [new_id if item == old_id else item for item in field_value]
                elif field_name.endswith("_ref") and field_value == old_id:
                    node.__dict__[field_name] = new_id
