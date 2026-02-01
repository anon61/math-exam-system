import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def debug():
    print("DIAGNOSTIC MODE: Testing Preview Generation...")
    
    # 1. Setup paths
    preview_dir = PROJECT_ROOT / "temp_previews"
    preview_dir.mkdir(exist_ok=True)
    
    typ_file = preview_dir / "debug_test.typ"
    png_file = preview_dir / "debug_test.png"
    
    # 2. Write a minimal test file
    content = """
    #import "src/lib.typ": *
    #set page(width: auto, height: auto, margin: 1cm)
    #question("qn-limit-proof")
    """
    
    with open(typ_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"   -> Created test file: {typ_file}")
    
    # 3. Run Typst explicitly with UTF-8 ENFORCED
    cmd = [
        "typst", "compile", 
        "--root", str(PROJECT_ROOT), 
        "--format", "png", 
        str(typ_file), 
        str(png_file)
    ]
    
    print(f"   -> Executing: {' '.join(cmd)}")
    
    try:
        # FIX IS HERE: encoding="utf-8"
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding="utf-8"  
        )
        
        print("\n--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print("--------------")
        
        if result.returncode == 0:
            print("SUCCESS! Preview generated.")
        else:
            print("FAILURE! See the error message above.")
            
    except FileNotFoundError:
        print("CRITICAL: 'typst' executable not found in PATH.")

if __name__ == "__main__":
    debug()