import subprocess
import shutil
import os
import time
import random
import sys

# CONFIGURATION
DATA_DIR = "data"
BACKUP_DIR = "data_backup"
CLI_SCRIPT = ["python", "scripts/manage.py"]
ITERATIONS = 50  # How many items to add

def setup_backup():
    """Safety First: Back up the Golden Dataset."""
    print(f"📦 Creating backup of '{DATA_DIR}' to '{BACKUP_DIR}'...", end=" ")
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(DATA_DIR, BACKUP_DIR)
    print("Done.")

def restore_backup():
    """Restore the Golden Dataset."""
    print(f"\n♻️  Restoring backup from '{BACKUP_DIR}'...", end=" ")
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    shutil.copytree(BACKUP_DIR, DATA_DIR)
    shutil.rmtree(BACKUP_DIR)
    print("Done.")

def run_cli(args, input_str=None):
    """Run the CLI and return success/fail."""
    try:
        result = subprocess.run(
            CLI_SCRIPT + args,
            input=input_str,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )
        return result
    except Exception as e:
        print(f"\n❌ CRITICAL EXECUTION ERROR: {e}")
        sys.exit(1)

def stress_test():
    start_time = time.time()
    
    print(f"🚀 Starting STRESS TEST ({ITERATIONS} iterations)")
    print("-" * 60)

    # 1. BATCH ADD DEFINITIONS
    print("1️⃣  Adding 50 Definitions...", end=" ", flush=True)
    for i in range(ITERATIONS):
        def_id = f"def-stress-{i}"
        # Inputs: ID, Term, Content (note the extra \n to finish content)
        inputs = f"{def_id}\nStress Term {i}\nStress Content {i}\n\n"
        res = run_cli(["add", "definition"], inputs)
        
        if res.returncode != 0:
            print(f"\n❌ Failed to add {def_id}: {res.stderr}")
            return
        
        if i % 10 == 0:
            print(".", end="", flush=True)
    print(" ✅")

    # 2. BATCH ADD EXAMPLES (LINKING)
    print("2️⃣  Adding 50 Examples (Linking)...", end=" ", flush=True)
    for i in range(ITERATIONS):
        ex_id = f"ex-stress-{i}"
        def_id = f"def-stress-{i}"
        # Inputs: ID, Name, Type, Content, Def_IDs
        inputs = f"{ex_id}\nStress Ex {i}\nStandard\nContent {i}\n\n{def_id}\n"
        res = run_cli(["add", "example"], inputs)
        
        if res.returncode != 0:
            print(f"\n❌ Failed to add {ex_id}: {res.stderr}")
            return
            
        if i % 10 == 0:
            print(".", end="", flush=True)
    print(" ✅")

    # 3. VERIFICATION
    print("3️⃣  Verifying Database Size...", end=" ")
    res = run_cli(["list", "definition"])
    line_count = len(res.stdout.splitlines())
    # We expect original count + 50 (approx)
    if line_count > ITERATIONS:
        print(f"✅ (Found {line_count} definitions)")
    else:
        print(f"❌ ERROR: Only found {line_count} definitions!")

    # 4. CHAOS MONKEY (Integrity Check)
    print("4️⃣  Running Chaos Monkey (Random Deletes)...")
    
    # Try to delete a definition that has an example (Should FAIL)
    target_idx = random.randint(0, ITERATIONS - 1)
    target_def = f"def-stress-{target_idx}"
    print(f"   🔸 Attempting to delete linked node '{target_def}'...", end=" ")
    
    # FIX: Removed "definition" from args. It's just `delete <id>`
    res = run_cli(["delete", target_def]) 
    
    # The CLI prints errors to stdout and exits 0, so we check stdout for the error message.
    if "[Error]" in res.stdout and "referenced by" in res.stdout:
        print("✅ BLOCKED (Integrity Check Passed)")
    else:
        print(f"❌ FAILED! It allowed deletion or gave wrong error.\nOutput: {res.stdout}\nError: {res.stderr}")

    # Clean up correctly (Delete Example first, then Definition)
    target_ex = f"ex-stress-{target_idx}"
    print(f"   🔸 Cleanup: Deleting child '{target_ex}'...", end=" ")
    
    # FIX: Removed "example" from args
    run_cli(["delete", target_ex])
    print("Done.")
    
    print(f"   🔸 Retry: Deleting parent '{target_def}'...", end=" ")
    # FIX: Removed "definition" from args
    res = run_cli(["delete", target_def])
    if res.returncode == 0:
        print("✅ SUCCESS")
    else:
        print(f"❌ FAILED to delete unlinked node. Error: {res.stderr}")

    # SUMMARY
    duration = time.time() - start_time
    print("-" * 60)
    print(f"🏁 Stress Test Completed in {duration:.2f} seconds.")
    print(f"⚡ Speed: {ITERATIONS * 2 / duration:.2f} ops/sec")

if __name__ == "__main__":
    try:
        setup_backup()
        stress_test()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted! Restoring backup...")
    finally:
        restore_backup()