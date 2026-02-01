from dataclasses import dataclass
from enum import Enum
from typing import List

class ExampleType(Enum):
    STANDARD = "Standard"
    COUNTER_EXAMPLE = "Counter-Example"
    NON_EXAMPLE = "Non-Example"

@dataclass
class Example:
    id: str
    name: str
    type: ExampleType
    content: str
    related_definition_ids: List[str]
