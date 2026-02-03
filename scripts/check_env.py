import sys
import shutil
import importlib.util


def check_step(name, check_func, fail_msg):
    print(f"Checking {name:<20} ...", end=" ")
    if check_func():
        print("✅ OK")
        return True
    else:
        print("❌ MISSING")
        print(f"   -> FIX: {fail_msg}")
        return False


def main():
    print("\n--- SYSTEM HEALTH CHECK ---")
    all_good = True

    # 1. Python
    if not check_step(
        "Python Version", lambda: sys.version_info >= (3, 8), "Install Python 3.10+"
    ):
        all_good = False

    # 2. Typst
    if not check_step(
        "Typst CLI",
        lambda: shutil.which("typst") is not None,
        "Run 'install.bat' again to install Typst",
    ):
        all_good = False

    # 3. Libraries
    if not check_step(
        "PyYAML Library",
        lambda: importlib.util.find_spec("yaml") is not None,
        "Run 'pip install -r requirements.txt'",
    ):
        all_good = False

    print("---------------------------")
    if all_good:
        print("🎉 READY! You can now start developing.")
        print("   Try running: python scripts/add_question.py")
    else:
        print("⚠️  Issues found. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
