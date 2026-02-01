from dataclasses import dataclass, field
from typing import List, Optional

# --- CORE GRAPH MODELS ---
@dataclass
class KnowledgeNode:
    """Base class for all knowledge items to ensure compatibility with DBManager."""
    id: str

@dataclass
class Relationship:
    """Represents a link between two nodes (e.g., Question -> relies_on -> Definition)."""
    source: str
    target: str
    type: str

@dataclass
class AnswerStep:
    type: str  # e.g., "Calculation", "Reasoning", "Proof"
    title: str
    content: str

# --- CONTENT MODELS ---
@dataclass
class Course(KnowledgeNode):
    """Represents a specific university course."""
    name: str
    # Add other fields if your original had them, but this satisfies the import.

@dataclass
class Question(KnowledgeNode):
    year: int
    lecturer: str
    topic: str
    given: str
    to_prove: str
    hint: Optional[str] = None
    # IMAGE FIELD (The new feature)
    image: Optional[str] = None 
    answer_steps: List[AnswerStep] = field(default_factory=list)

@dataclass
class Definition(KnowledgeNode):
    name: str
    content: str

@dataclass
class Tool(KnowledgeNode):
    name: str
    description: str
    usage: str

@dataclass
class Mistake(KnowledgeNode):
    description: str
    correction: str

@dataclass
class Example(KnowledgeNode):
    title: str
    content: str