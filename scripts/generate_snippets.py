import json
from pathlib import Path
import sys

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.db_manager import DBManager  # noqa: E402


def generate_vscode_snippets():
    """
    Generates a VS Code snippet file from the database content.
    """
    data_path = Path("data")
    db_manager = DBManager(data_path)

    definitions = db_manager.definitions
    tools = db_manager.tools
    examples = db_manager.examples
    mistakes = db_manager.mistakes

    snippets = {}

    # Definitions
    for def_id, definition in definitions.items():
        label = f"Ref: {definition.term} ({def_id})"
        snippets[label] = {
            "prefix": "def",
            "body": [f'#def("{def_id}")'],
            "description": definition.content[:100]
            + ("..." if len(definition.content) > 100 else ""),
        }

    # Tools
    for tool_id, tool in tools.items():
        label = f"Ref: {tool.name} ({tool_id})"
        snippets[label] = {
            "prefix": "tool",
            "body": [f'#tool("{tool_id}")'],
            "description": tool.statement,
        }

    # Examples
    for ex_id, example in examples.items():
        label = f"Ref: {example.name} ({ex_id})"
        snippets[label] = {
            "prefix": "ex",
            "body": [f'#ex("{ex_id}")'],
        }

    # Mistakes
    for mistake_id, mistake in mistakes.items():
        label = f"Ref: {mistake.name} ({mistake_id})"
        snippets[label] = {
            "prefix": "mistake",
            "body": [f'#mistake("{mistake_id}")'],
        }

    output_dir = Path(".vscode")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "typst.code-snippets"

    with open(output_path, "w") as f:
        json.dump(snippets, f, indent=2)

    print(f"✅ Generated {len(snippets)} snippets for VS Code.")


if __name__ == "__main__":
    generate_vscode_snippets()
