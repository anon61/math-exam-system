import os
import sys
import datetime

# CONFIGURATION
# Detects the project root relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "questions.yaml")

def get_multiline_input(prompt):
    """
    Captures multi-line input from the user.
    """
    print(f"\n* {prompt}")
    print("   (Type your text. Press ENTER twice to finish.)")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and len(lines) > 0:
                break
            if line.strip() != "":
                lines.append(line)
        except EOFError:
            break
            
    # Join and indent for YAML block scalar
    return "\n    ".join(lines)

def get_single_input(prompt, default=None):
    """
    Captures a single line of input.
    """
    if default:
        user_input = input(f"\n* {prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"\n* {prompt}: ").strip()
            if user_input:
                return user_input

def append_to_yaml(data):
    """
    Appends the structured data to the YAML file.
    """
    # We construct the string manually to ensure the nice block format (|)
    # that Typst prefers for math content.
    
    entry = f"""
- id: "{data['id']}"
  year: {data['year']}
  lecturer: "{data['lecturer']}"
  topic: "{data['topic']}"
  given: |
    {data['given']}
  to_prove: |
    {data['to_prove']}
  tools: "{data['tools']}"
  common_mistakes: "{data['mistakes']}"
  hint: |
    {data['hint']}
"""
    
    try:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"\nSuccess! Question '{data['id']}' added to:")
        print(f"   {DATA_FILE}")
    except Exception as e:
        print(f"\nError writing file: {e}")

def main():
    print("==========================================")
    print("   TYPST EXAM SYSTEM - QUESTION WIZARD    ")
    print("==========================================")
    print("This tool will guide you through adding a new question.")
    print("You can use commas, quotes, and math symbols freely.")

    # 1. Gather Metadata
    current_year = datetime.datetime.now().year
    
    data = {}
    data['id'] = get_single_input("Question ID (e.g. CALC-005)")
    data['year'] = get_single_input("Year", default=str(current_year))
    data['lecturer'] = get_single_input("Lecturer Name")
    data['topic'] = get_single_input("Topic (e.g. Limits, Groups)")

    # 2. Gather Content (Multiline)
    data['given'] = get_multiline_input("GIVEN (The setup/context):")
    data['to_prove'] = get_multiline_input("TO PROVE (The goal):")
    
    # 3. Gather Pedagogy
    data['tools'] = get_single_input("Tools/Theorems required")
    data['mistakes'] = get_single_input("Common Mistakes (optional)", default="-")
    data['hint'] = get_multiline_input("HINT (Pedagogical nudge):")

    # 4. Save
    print("\n------------------------------------------")
    append_to_yaml(data)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled.")
        sys.exit(0)