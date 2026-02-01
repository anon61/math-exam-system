from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, Dict

@dataclass
class KnowledgeNode:
    id: str

class ExampleType(Enum):
    STANDARD = "Standard"
    COUNTER_EXAMPLE = "Counter-Example"
    NON_EXAMPLE = "Non-Example"

class Severity(Enum):
    CRITICAL = "Critical"
    MINOR = "Minor"

@dataclass
class Definition(KnowledgeNode):
    term: str
    content: str

@dataclass
class Tool(KnowledgeNode):
    name: str
    short_name: str
    statement: str

@dataclass
class Example(KnowledgeNode):
    name: str
    type: ExampleType
    content: str
    related_definition_ids: List[str] = field(default_factory=list)

@dataclass
class Mistake(KnowledgeNode):
    name: str
    severity: Severity
    description: str
    remedy: str

@dataclass
class Course(KnowledgeNode):
    name: str
    definition_sequence: List[str]
    tool_sequence: List[str]
    example_sequence: List[str]

@dataclass
class Lecture(KnowledgeNode):
    sequence: int
    title: str
    date: str
    definition_ids: List[str]
    tool_ids: List[str]
    example_ids: List[str]

@dataclass
class Tutorial(KnowledgeNode):
    sequence: int
    lecture_ref: str
    example_question_ids: List[str]

@dataclass
class Assessment(KnowledgeNode):
    tool_ids: List[str] = field(default_factory=list)
    mistake_ids: List[str] = field(default_factory=list)
    example_ids: List[str] = field(default_factory=list)

@dataclass
class AnswerStep:
    type: str
    title: str
    content: str
    proof: Optional[str] = None

@dataclass
class Question(Assessment):
    year: Optional[int] = None
    lecturer: Optional[str] = None
    topic: Optional[str] = None
    given: Optional[str] = None
    to_prove: Optional[str] = None
    tools: Optional[str] = None
    common_mistakes: Optional[str] = None
    hint: Optional[str] = None
    answer_steps: List[AnswerStep] = field(default_factory=list)

@dataclass
class Homework(Assessment):
    pass
