import subprocess
import sys
import time
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "latest_crash.log"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_error(stderr_text):
    if not stderr_text:
        return "No error captured", "N/A"
    lines = stderr_text.strip().split('\n')
    last_line = lines[-1] if lines else "Unknown Error"
    
    file_info = "Unknown Location"
    for line in reversed(lines):
        if 'File "' in line:
            match = re.search(r'File "(.*?)", line (\d+)', line)
            if match:
                file_info = f"{match.group(1)} at line {match.group(2)}"
                break
    return last_line, file_info

def main_loop():
    while True:
        clear_screen()
        print("WATCHDOG: Starting Streamlit...")
        
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )

        try:
            # Wait for process to exit or be stable
            while process.poll() is None:
                time.sleep(1)
            
            # Use communicate to safely get streams without "None" attribute errors
            stdout, stderr_output = process.communicate()
            
            if stderr_output:
                error_msg, location = parse_error(stderr_output)
                
                print("\nCRASH SUMMARY")
                print(f"Error: {error_msg}")
                print(f"Location: {location}")
                print("-" * 60)
                
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write(f"AI CONTEXT: DIAGNOSTIC REPORT\n{'='*30}\n")
                    f.write(f"ERROR TYPE: {error_msg}\n")
                    f.write(f"DETECTED AT: {location}\n{'='*30}\n\n")
                    f.write(f"FULL STACK TRACE:\n{stderr_output}")
                
                print(f"Report written to {LOG_FILE.name}")
            else:
                print("\nApp closed normally with no errors.")

        except KeyboardInterrupt:
            process.terminate()
            sys.exit(0)

        print("\nReview report in VS Code, fix code, and press ENTER to retry...")
        input()

if __name__ == "__main__":
    main_loop()