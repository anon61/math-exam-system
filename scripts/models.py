from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


# --- 1. ENUMS & TYPES ---
class ExampleType(str, Enum):
    CALCULATION = "calculation"
    PROOF = "proof"
    CONCEPTUAL = "conceptual"
    CODE = "code"
    STANDARD = "Standard"
    COUNTER_EXAMPLE = "Counter-Example"  # Added to match YAML


class RelationshipType(str, Enum):
    RELIES_ON = "relies_on"
    RELATED_TO = "related_to"
    PREREQUISITE = "prerequisite"


class Severity(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"
    # Fallback for case sensitivity
    Critical = "Critical"
    Minor = "Minor"
    Moderate = "Moderate"


# --- 2. CORE GRAPH PRIMITIVES ---
@dataclass
class KnowledgeNode:
    """Base class for all nodes. Ensures every object has an ID."""

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
    proof: Optional[str] = None  # Added to match YAML (some steps have 'proof: null')


# --- 3. UNIVERSITY STRUCTURES ---
@dataclass
class Course(KnowledgeNode):
    name: str
    # Added fields found in audit
    definition_sequence: List[str] = field(default_factory=list)
    tool_sequence: List[str] = field(default_factory=list)
    example_sequence: List[str] = field(default_factory=list)


@dataclass
class Lecture(KnowledgeNode):
    # 'name' replaced by 'title' to match YAML
    title: str
    course_id: Optional[str] = None
    # Added fields found in audit
    date: Optional[str] = None
    sequence: Optional[int] = None
    definition_ids: List[str] = field(default_factory=list)
    tool_ids: List[str] = field(default_factory=list)
    example_ids: List[str] = field(default_factory=list)


@dataclass
class Tutorial(KnowledgeNode):
    # Made optional because YAML doesn't always have them
    title: Optional[str] = None
    week: Optional[int] = None
    content: Optional[str] = None
    # Added fields found in audit
    sequence: Optional[int] = None
    lecture_ref: Optional[str] = None
    example_question_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.title:
            self.title = (
                f"Tutorial {self.sequence}" if self.sequence else "Untitled Tutorial"
            )


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
    # Added fields found in audit
    tools: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)

    def __post_init__(self):
            # Handle nested AnswerStep objects if they come in as dicts from YAML
            if self.answer_steps and isinstance(self.answer_steps[0], dict):
                # FIX: Explicitly cast to list of dicts to satisfy Pylance/MyPy
                from typing import cast, Dict, Any
                steps_data = cast(List[Dict[str, Any]], self.answer_steps)
                self.answer_steps = [AnswerStep(**step) for step in steps_data]


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
        if not self.description:
            self.description = "No description provided."


@dataclass
class Mistake(KnowledgeNode):
    description: str
    severity: Optional[str] = (
        None  # Changed to str to be lenient with "Critical" vs "critical"
    )
    correction: Optional[str] = None
    # Added fields found in audit
    name: Optional[str] = None
    remedy: Optional[str] = None

    def __post_init__(self):
        # Normalize remedy/correction
        if not self.correction and self.remedy:
            self.correction = self.remedy


@dataclass
class Example(KnowledgeNode):
    name: str  # Renamed from 'title' to match YAML
    content: str
    type: Optional[str] = (
        "Standard"  # Changed to str to accept "Counter-Example" easily
    )
    # Added fields found in audit
    related_definition_ids: List[str] = field(default_factory=list)
