import os
import sys
import re
import yaml

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "questions.yaml")

def load_file_lines():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found.")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return f.readlines()

def find_question_blocks(lines):
    """
    Scans the file for lines starting with '- id:'.
    Returns a dict mapping ID -> (start_line_index, end_line_index)
    """
    blocks = {}
    current_id = None
    start_idx = -1
    
    id_pattern = re.compile(r'^- id: "(.+?)"')

    for i, line in enumerate(lines):
        match = id_pattern.match(line)
        if match:
            # If we were tracking a previous block, close it
            if current_id:
                blocks[current_id] = (start_idx, i)
            
            # Start new block
            current_id = match.group(1)
            start_idx = i
            
    # Close the last block
    if current_id:
        blocks[current_id] = (start_idx, len(lines))
        
    return blocks

def get_multiline_edit(prompt, current_val):
    print(f"\n📘 {prompt}")
    print("   -------------------------------------------------")
    print(f"   CURRENT: \n{current_val}")
    print("   -------------------------------------------------")
    print("   (Type new content. Press ENTER twice to finish.)")
    print("   (Press ENTER immediately to keep current value.)")
    
    lines = []
    first_enter = False
    
    while True:
        try:
            line = input()
            # If empty line on first input, user wants to keep current
            if line.strip() == "" and not lines and not first_enter:
                return current_val
            
            # Double enter to finish
            if line.strip() == "" and len(lines) > 0:
                break
            
            # Allow one empty line logic or just capturing input
            if line.strip() != "":
                lines.append(line)
                
            first_enter = True
        except EOFError:
            break
            
    return "\n".join(lines) if lines else current_val

def get_single_edit(prompt, current_val):
    print(f"\n🔹 {prompt}")
    user_input = input(f"   Current: [{current_val}] \n   New (Enter to keep): ").strip()
    return user_input if user_input else current_val

def main():
    print("==========================================")
    print("   TYPST EXAM SYSTEM - QUESTION EDITOR    ")
    print("==========================================")

    lines = load_file_lines()
    blocks = find_question_blocks(lines)

    if not blocks:
        print("No questions found in database.")
        return

    # 1. Select Question
    print(f"Found {len(blocks)} questions:")
    sorted_ids = sorted(blocks.keys())
    for idx, q_id in enumerate(sorted_ids):
        print(f"  {idx + 1}. {q_id}")

    selection = input("\nSelect number or type ID to edit: ").strip()
    
    target_id = None
    if selection in blocks:
        target_id = selection
    elif selection.isdigit() and 1 <= int(selection) <= len(sorted_ids):
        target_id = sorted_ids[int(selection) - 1]
    else:
        print("❌ Invalid selection.")
        return

    # 2. Extract and Parse the Block
    start, end = blocks[target_id]
    block_lines = lines[start:end]
    block_text = "".join(block_lines)
    
    # We parse just this block to a dict
    # Note: 'yaml.safe_load' might treat the list item as a list of 1 dict
    try:
        data = yaml.safe_load(block_text)
        if isinstance(data, list):
            data = data[0]
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML block: {e}")
        return

    print(f"\n📝 Editing: {target_id} ({data.get('topic', 'Unknown Topic')})")

    # 3. Edit Loop
    # Editable fields map: Display Name -> Key
    fields = [
        ("Year", "year"),
        ("Lecturer", "lecturer"),
        ("Topic", "topic"),
        ("Tools", "tools"),
        ("Common Mistakes", "common_mistakes")
    ]

    # Edit Simple Fields
    for label, key in fields:
        current = data.get(key, "")
        data[key] = get_single_edit(label, current)

    # Edit Multiline Fields
    data['given'] = get_multiline_edit("GIVEN (Setup)", data.get('given', ''))
    data['to_prove'] = get_multiline_edit("TO PROVE (Goal)", data.get('to_prove', ''))
    data['hint'] = get_multiline_edit("HINT", data.get('hint', ''))

    # 4. Reconstruct YAML Block
    # We manually reconstruct to preserve the nice block scalars (|) for Typst math
    # standard yaml.dump often messes up the format required for the Typst parser logic
    
    new_block = f"""- id: "{data['id']}"
  year: {data['year']}
  lecturer: "{data['lecturer']}"
  topic: "{data['topic']}"
  given: |
    {str(data['given']).strip().replace(chr(10), chr(10) + '    ')}
  to_prove: |
    {str(data['to_prove']).strip().replace(chr(10), chr(10) + '    ')}
  tools: "{data['tools']}"
  common_mistakes: "{data['common_mistakes']}"
  hint: |
    {str(data['hint']).strip().replace(chr(10), chr(10) + '    ')}
  answer_steps:
"""
    # Note: We preserve answer_steps from the original text because editing complex nested lists 
    # via terminal is error-prone. We grab the answer_steps part from the original block.
    
    # Find where answer_steps starts in the original block text
    step_start_index = -1
    for i, line in enumerate(block_lines):
        if line.strip().startswith("answer_steps:"):
            step_start_index = i
            break
            
    if step_start_index != -1:
        # Append the original answer_steps lines to our new block
        steps_text = "".join(block_lines[step_start_index:])
        new_block += steps_text
    else:
        # If no steps existed, just close the block (rare)
        new_block += "    []\n"

    # 5. Save Changes
    print("\n------------------------------------------")
    print(new_block)
    print("------------------------------------------")
    confirm = input("💾 Save these changes? (y/n): ").lower()
    
    if confirm == 'y':
        # Rebuild full file content
        new_file_lines = lines[:start] + [new_block] + lines[end:]
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_file_lines)
        print(f"✅ Successfully updated {target_id} in {DATA_FILE}")
    else:
        print("❌ Changes discarded.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled.")