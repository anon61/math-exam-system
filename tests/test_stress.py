
import os
import shutil
import subprocess
import time
import random
import atexit
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_SCRIPT = PROJECT_ROOT / "scripts" / "manage.py"
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "data_backup"
PYTHON_EXEC = "python"  # Use "python3" if that's your command

# --- State ---
initial_def_count = 0

# --- Helper Functions ---
def run_cli_command(command, input_data=None):
    """Runs a CLI command as a subprocess, optionally with stdin."""
    process = subprocess.run(
        [PYTHON_EXEC, str(CLI_SCRIPT)] + command,
        input=input_data,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return process

def get_definition_count():
    """Gets the current number of definitions using the CLI."""
    result = run_cli_command(["list", "definition"])
    if result.returncode != 0:
        print("Error getting definition count:")
        print(result.stderr)
        return -1
    
    # Count occurrences of '- ID:' which indicates a listed item
    return result.stdout.count("- ID:")

# --- Test Setup and Teardown ---
def backup_data():
    """Creates a backup of the data directory."""
    print(f"\n--- Backing up '{DATA_DIR}' to '{BACKUP_DIR}' ---")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(DATA_DIR, BACKUP_DIR)

def restore_data():
    """Restores the data directory from the backup."""
    print(f"\n--- Restoring data from '{BACKUP_DIR}' ---")
    if BACKUP_DIR.exists():
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR)
        shutil.copytree(BACKUP_DIR, DATA_DIR)
        shutil.rmtree(BACKUP_DIR)
        print("--- Restore complete ---")
    else:
        print("--- No backup found, skipping restore ---")

def setup_module():
    """Pytest setup function, runs before all tests in this module."""
    backup_data()
    # Ensure cleanup happens even if the script crashes
    atexit.register(restore_data)
    global initial_def_count
    initial_def_count = get_definition_count()
    if initial_def_count == -1:
        # If we can't get the initial count, we must stop.
        # Restore will be called by atexit.
        raise RuntimeError("Could not determine initial definition count. Aborting tests.")
    print(f"Initial definition count: {initial_def_count}")

# We don't need teardown_module because atexit handles the restore

# --- Test Cases ---

def test_stress_batch_add_and_link():
    """
    Tests batch adding of definitions and linking examples to them.
    Verifies the final count and measures performance.
    """
    print("\n--- Running: test_stress_batch_add_and_link ---")
    num_operations = 50

    # 1. Batch Add Definitions
    print(f"Adding {num_operations} definitions...")
    start_time = time.time()
    for i in range(num_operations):
        def_id = f"def-stress-{i}"
        term = f"Stress Term {i}"
        content = f"Content for stress test definition {i}."
        
        # Multiple newlines are important to satisfy all prompts
        input_data = f"{def_id}\n{term}\n{content}\n\n" 
        
        result = run_cli_command(["add", "definition"], input_data=input_data)
        assert result.returncode == 0, f"Failed to add definition {def_id}:\n{result.stderr}"
        assert f"Added definition '{def_id}'" in result.stdout
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Batch Add completed in {duration:.2f} seconds.")
    print(f"Time per operation: {duration / num_operations:.4f} seconds.")

    # 2. Batch Link Examples
    print(f"Adding and linking {num_operations} examples...")
    for i in range(num_operations):
        ex_id = f"ex-stress-{i}"
        def_id = f"def-stress-{i}"
        name = f"Stress Example {i}"
        ex_type = "Standard"
        content = f"Content linking to {def_id}."
        
        # Input for: id, name, type, content, related_definition_ids
        input_data = f"{ex_id}\n{name}\n{ex_type}\n{content}\n\n{def_id}\n"
        
        result = run_cli_command(["add", "example"], input_data=input_data)
        assert result.returncode == 0, f"Failed to add example {ex_id}:\n{result.stderr}"
        assert f"Added example '{ex_id}'" in result.stdout

    # 3. Verification
    print("Verifying final definition count...")
    final_def_count = get_definition_count()
    expected_count = initial_def_count + num_operations
    assert final_def_count == expected_count, \
        f"Expected {expected_count} definitions, but found {final_def_count}."
    print(f"Verification successful: Found {final_def_count} definitions.")


def test_chaos_monkey_deletion():
    """
    Randomly attempts to delete definitions that are linked to examples,
    verifying that the integrity check prevents it. Then deletes the example
    and successfully deletes the definition.
    """
    print("\n--- Running: test_chaos_monkey_deletion ---")
    num_to_delete = 10
    total_defs_added = 50 # from the previous test

    # Get a random sample of the definitions we just added
    indices_to_test = random.sample(range(total_defs_added), num_to_delete)
    
    for i in indices_to_test:
        def_id = f"def-stress-{i}"
        ex_id = f"ex-stress-{i}"
        print(f"Testing deletion logic for {def_id}...")

        # 1. Attempt to delete definition while it's linked -> MUST FAIL
        print(f"  Attempting to delete linked definition {def_id} (should fail)...")
        fail_result = run_cli_command(["delete", def_id])
        assert fail_result.returncode != 0, f"CLI should have failed to delete linked def {def_id}, but it succeeded."
        # Check for the specific error message from DBManager's integrity check
        assert f"is referenced by other nodes" in fail_result.stdout
        print("  ...Failed as expected.")

        # 2. Delete the example first -> MUST SUCCEED
        print(f"  Deleting example {ex_id} first...")
        delete_ex_result = run_cli_command(["delete", ex_id])
        assert delete_ex_result.returncode == 0, f"Failed to delete example {ex_id}:\n{delete_ex_result.stderr}"
        assert f"Deleted node '{ex_id}'" in delete_ex_result.stdout
        print("  ...Success.")

        # 3. Attempt to delete definition again -> MUST SUCCEED
        print(f"  Attempting to delete unlinked definition {def_id} (should succeed)...")
        success_result = run_cli_command(["delete", def_id])
        assert success_result.returncode == 0, f"Failed to delete unlinked definition {def_id}:\n{success_result.stderr}"
        assert f"Deleted node '{def_id}'" in success_result.stdout
        print("  ...Success.")
        
    print("\nChaos monkey testing completed successfully.")
