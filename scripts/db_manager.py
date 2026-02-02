from pathlib import Path
import yaml
from scripts.models import Question, Definition, Tool, Mistake, Example, Lecture, Tutorial

class DBManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        # Initialize storage
        self.questions = {}
        self.definitions = {}
        self.tools = {}
        self.mistakes = {}
        self.examples = {}
        self.lectures = {}
        self.tutorials = {}
        
        self.load_all()

    def _load_file(self, filename, model_class, storage_dict):
        path = self.data_dir / filename
        if not path.exists():
            return # Silent skip if missing
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or []
                
            for item in data:
                if "id" not in item: continue
                
                # Filter valid fields only
                valid_keys = model_class.__annotations__.keys()
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