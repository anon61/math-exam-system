import os
from pathlib import Path

# Project path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_PATH = PROJECT_ROOT / "scripts" / "models.py"

def apply_master_schema():
    """Applies the comprehensive model schema to prevent ImportErrors."""
    master_code = """from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

# --- 1. ENUMS & TYPES ---
class ExampleType(str, Enum):
    CALCULATION = "calculation"
    PROOF = "proof"
    CONCEPTUAL = "conceptual"
    CODE = "code"
    STANDARD = "Standard" 

class RelationshipType(str, Enum):
    RELIES_ON = "relies_on"
    RELATED_TO = "related_to"
    PREREQUISITE = "prerequisite"

class Severity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"

# --- 2. CORE GRAPH PRIMITIVES ---
@dataclass
class KnowledgeNode:
    id: str

@dataclass
class Relationship:
    source: str
    target: str
    type: str

@dataclass
class AnswerStep:
    type: str  
    title: str
    content: str

# --- 3. UNIVERSITY STRUCTURES ---
@dataclass
class Course(KnowledgeNode):
    name: str

@dataclass
class Lecture(KnowledgeNode):
    name: str
    course_id: Optional[str] = None 

@dataclass
class Tutorial(KnowledgeNode):
    title: str
    week: int
    content: Optional[str] = None

@dataclass
class Homework(KnowledgeNode):
    title: str
    week: int
    content: Optional[str] = None

# --- 4. EXAM CONTENT MODELS ---
@dataclass
class Question(KnowledgeNode):
    year: int
    lecturer: str
    topic: str
    given: str
    to_prove: str
    hint: Optional[str] = None
    image: Optional[str] = None 
    answer_steps: List[AnswerStep] = field(default_factory=list)

@dataclass
class Definition(KnowledgeNode):
    content: str
    term: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not self.term and self.name:
            self.term = self.name
        if not self.term:
            self.term = "Untitled Definition"

@dataclass
class Tool(KnowledgeNode):
    description: Optional[str] = None
    usage: Optional[str] = None
    short_name: Optional[str] = None
    name: Optional[str] = None
    statement: Optional[str] = None

    def __post_init__(self):
        if not self.short_name and self.name:
            self.short_name = self.name
        if not self.short_name:
            self.short_name = "Untitled Tool"
        if not self.description and self.statement:
            self.description = self.statement

@dataclass
class Mistake(KnowledgeNode):
    description: str
    correction: str
    severity: Optional[Severity] = None

@dataclass
class Example(KnowledgeNode):
    title: str
    content: str
    type: Optional[ExampleType] = None
"""
    
    print(f"Applying Master Schema to {MODELS_PATH}...")
    try:
        with open(MODELS_PATH, "w", encoding="utf-8") as f:
            f.write(master_code)
        print("Success: Schema synchronized.")
    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    apply_master_schema()