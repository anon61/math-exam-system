import os
import sys

# CONFIG
MAIN_DB = "data/questions.yaml"
TEMP_FILE = "new.yaml"

def merge_yaml():
    print(f"--- Typst Question Merger ---")
    
    # 1. Read the new content
    if not os.path.exists(TEMP_FILE):
        print(f"❌ Error: Create a file named '{TEMP_FILE}' and paste your YAML there first.")
        return

    with open(TEMP_FILE, "r", encoding="utf-8") as f:
        new_content = f.read().strip()

    if not new_content:
        print("❌ Error: 'new.yaml' is empty.")
        return

    # 2. Validation (Basic)
    if "- id:" not in new_content:
        print("⚠️ Warning: This doesn't look like a valid list entry (missing '- id:').")
        print("   Make sure Gemini outputted a list item starting with dash (-).")
        confirm = input("   Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return

    # 3. Append to Main DB
    # We prepend a newline to ensure separation
    with open(MAIN_DB, "a", encoding="utf-8") as f:
        f.write("\n\n" + new_content)

    print(f"✅ Successfully appended to {MAIN_DB}")
    
    # 4. Clear the temp file
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        f.write("")
    print("🧹 Cleared new.yaml")

if __name__ == "__main__":
    merge_yaml()