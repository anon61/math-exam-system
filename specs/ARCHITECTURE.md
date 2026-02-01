# Project Architecture: 8-Layer Math Knowledge Engine

## 1. Goal
To build a relational knowledge base for mathematics that links Definitions, Tools, Examples, Mistakes, Lectures, and Assessments, rendering them via Typst.

## 2. Data Topology (The 8 YAML Layers)
All data resides in `data/`.

### Zone A: Source of Truth
1. **`definitions.yaml`**: Vocabulary.
   - Schema: `{id: str, term: str, content: str}`
2. **`tools.yaml`**: Theorems and Lemmas.
   - Schema: `{id: str, name: str, short_name: str, statement: str}`
3. **`examples.yaml`**: Illustrations.
   - Schema: `{id: str, name: str, type: [Standard, Counter-Example, Non-Example], content: str, related_definition_ids: [id]}`
4. **`mistakes.yaml`**: Common anti-patterns.
   - Schema: `{id: str, name: str, severity: [Critical, Minor], description: str, remedy: str}`

### Zone B: Context
5. **`courses.yaml`**: Playlist/Map.
   - Schema: `{id: str, name: str, definition_sequence: [id], tool_sequence: [id], example_sequence: [id]}`
6. **`lectures.yaml`**: Narrative.
   - Schema: `{id: str, sequence: int, title: str, date: str, definition_ids: [id], tool_ids: [id], example_ids: [id]}`
7. **`tutorials.yaml`**: Practice.
   - Schema: `{id: str, sequence: int, lecture_ref: id, example_question_ids: [id]}`

### Zone C: Assessment
8. **`questions.yaml`** (Exams) & **`homework.yaml`** (HW).
   - Schema: `{id: str, ..., tool_ids: [id], mistake_ids: [id], example_ids: [id]}`

## 3. Python Backend (Strict MVC)
Located in `scripts/`.
1. **`models.py`**: Python `dataclasses` for all 8 layers.
   - `ExampleType` Enum: `STANDARD`, `COUNTER_EXAMPLE`, `NON_EXAMPLE`.
2. **`db_manager.py`**:
   - `add_node()`: Check ID uniqueness.
   - `delete_node()`: Check Referential Integrity (Block delete if used).
3. **`check_integrity.py`**: Verify all IDs point to real objects.

## 4. Typst Frontend
Located in `src/`.
1. **`lib.typ`**:
   - Loads all 8 YAMLs into global `KB`.
   - `#ref(id)`: Polymorphic linker (detects prefix).
   - `#ex(id)`: Renders with color (Green=Standard, Red=Counter, Orange=Non).