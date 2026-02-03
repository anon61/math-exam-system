import subprocess
import time
import sys
from pathlib import Path

# Define project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_stability_test(duration=5):
    print(f"🚀 Launching Streamlit for {duration}-second Stability Test...")
    print("   (This runs headless, so no browser window will open)")

    # Start Streamlit in a subprocess
    # --headless prevents it from trying to open a browser tab
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"]

    process = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",  # Force UTF-8 to avoid Hebrew locale crashes
    )

    start_time = time.time()

    try:
        # Loop for 'duration' seconds checking if it crashed
        while time.time() - start_time < duration:
            return_code = process.poll()

            if return_code is not None:
                # CRASH DETECTED!
                print(
                    f"\n❌ App CRASHED after {round(time.time() - start_time, 2)} seconds!"
                )
                stdout, stderr = process.communicate()
                print("\n--- 📜 ERROR LOG (STDERR) ---")
                print(stderr)
                print("-----------------------------")
                return False

            time.sleep(0.5)
            print(".", end="", flush=True)

        # SURVIVED!
        print(f"\n\n✅ App is STABLE (ran for {duration}s without crashing).")
        print("   Killing process...")
        process.terminate()
        return True

    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user.")
        process.terminate()
        return None


if __name__ == "__main__":
    success = run_stability_test(5)
    if not success:
        sys.exit(1)
