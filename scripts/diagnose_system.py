import shutil
import subprocess
import importlib.util
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REQUIRED_PKGS = ["streamlit", "yaml", "watchdog"]
REQUIRED_BINS = ["typst", "git"]

# --- REPORT STORAGE ---
# We store errors here instead of crashing
REPORT = {"CRITICAL": [], "MISSING_FILES": [], "DATA_CORRUPTION": [], "WARNINGS": []}


def check_python_packages():
    """Phase 1: Check if pip packages are installed."""
    print("[1/4] Checking Python Packages...")
    for pkg in REQUIRED_PKGS:
        if pkg == "yaml":  # Special case for PyYAML
            spec = importlib.util.find_spec("yaml")
        else:
            spec = importlib.util.find_spec(pkg)

        if spec is None:
            REPORT["CRITICAL"].append(
                f"Missing Python Package: '{pkg}' (Run: pip install {pkg})"
            )


def check_system_binaries():
    """Phase 2: Check if Typst and Git are in PATH."""
    print("[2/4] Checking System Tools...")
    for tool in REQUIRED_BINS:
        if shutil.which(tool) is None:
            REPORT["CRITICAL"].append(
                f"Missing System Tool: '{tool}' (Install via 'winget install {tool}')"
            )


def check_data_integrity():
    """Phase 3: Validate YAML files without crashing."""
    print("[3/4] Validating Data Integrity...")

    # We try to import yaml strictly for this check
    try:
        import yaml
    except ImportError:
        REPORT["WARNINGS"].append("Skipping Data Check: PyYAML not installed.")
        return

    if not DATA_DIR.exists():
        REPORT["MISSING_FILES"].append(f"Data Directory not found: {DATA_DIR}")
        return

    yaml_files = list(DATA_DIR.glob("*.yaml"))
    if not yaml_files:
        REPORT["WARNINGS"].append("No .yaml files found in data/ directory.")

    for f in yaml_files:
        try:
            with open(f, "r", encoding="utf-8") as stream:
                content = yaml.safe_load(stream)
                if content is None:
                    REPORT["DATA_CORRUPTION"].append(f"{f.name}: File is empty")
                elif not isinstance(content, (list, dict)):
                    REPORT["DATA_CORRUPTION"].append(
                        f"{f.name}: Invalid structure (must be list or dict)"
                    )
        except yaml.YAMLError as e:
            # We catch the specific syntax error line
            if hasattr(e, "problem_mark"):
                mark = e.problem_mark
                REPORT["DATA_CORRUPTION"].append(
                    f"{f.name}: Syntax Error at line {mark.line+1}, col {mark.column+1}"
                )
            else:
                REPORT["DATA_CORRUPTION"].append(f"{f.name}: Corrupt YAML - {str(e)}")
        except Exception as e:
            REPORT["DATA_CORRUPTION"].append(f"{f.name}: Read Error - {str(e)}")


def check_compilation_dry_run():
    """Phase 4: Attempt a minimal Typst compilation."""
    print("[4/4] Testing Compilation Engine...")

    if shutil.which("typst") is None:
        return  # Already logged in Phase 2

    # Create a dummy test file
    test_file = PROJECT_ROOT / "temp_diagnose.typ"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("#set page(width: auto, height: auto)\n*Diagnostics Check*")

    try:
        # Run typst and CAPTURE stderr instead of crashing
        result = subprocess.run(
            ["typst", "compile", str(test_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0:
            REPORT["CRITICAL"].append(
                f"Typst Compilation Failed:\n{result.stderr.strip()}"
            )
    except Exception as e:
        REPORT["CRITICAL"].append(f"Typst Execution Error: {str(e)}")
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()
        pdf = test_file.with_suffix(".pdf")
        if pdf.exists():
            pdf.unlink()


def print_report():
    print("\n" + "=" * 60)
    print("DIAGNOSTIC REPORT (ALL ERRORS A-Z)")
    print("=" * 60)

    has_errors = False

    for category, errors in REPORT.items():
        if errors:
            has_errors = True
            print(f"\n[{category}]")
            for e in errors:
                print(f" ❌ {e}")

    if not has_errors:
        print("\n✅ SYSTEM HEALTHY. No errors found.")
    else:
        print("\n" + "-" * 60)
        print("ACTION PLAN:")
        if REPORT["CRITICAL"]:
            print("1. Fix CRITICAL issues first (Pip/Winget).")
        if REPORT["DATA_CORRUPTION"]:
            print("2. Fix YAML syntax errors in data/ folder.")
        print("-" * 60)


if __name__ == "__main__":
    check_python_packages()
    check_system_binaries()
    check_data_integrity()
    check_compilation_dry_run()
    print_report()
