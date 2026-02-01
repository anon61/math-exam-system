# Project State Log

## 📅 Status: Phase 1 (The Pilot)
**Goal:** Prove the system works by implementing the "Examples" layer.

### 🏗️ Active Tasks (Todo)
- [x] Create `data/examples.yaml` with 3 dummy entries (Standard, Counter, Non-Example).
- [x] Update `scripts/models.py` to include the `Example` class and `ExampleType` Enum.
- [x] Update `src/lib.typ` to load `examples.yaml` into `KB`.
- [x] Implement `#ex(id)` function in `src/lib.typ` with color coding.
- [x] Create a test PDF `test_examples.typ` to verify rendering.

### 🛑 Current Blockers
- None.

### 🧠 Context Log
- **[2025-Start]**: Architecture finalized. Decided to use 8 layers. "Non-Example" type added for pedagogical clarity.