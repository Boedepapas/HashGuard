# hashguard_test_files.py
# Quick smoke test for Logs and Quarantine functionality.
# Usage: python hashguard_test_files.py
# Run while your HashGuard UI is running, then refresh the UI lists.

import os
import sys
import time
import platform
import subprocess
from pathlib import Path

# Configure these to match your app's directories if different
BASE_DIR = Path.home() / "HashGuardDemo"
QUARANTINE_DIR = BASE_DIR / "quarantine"
LOGS_DIR = BASE_DIR / "logs"
UI_CONFIG = BASE_DIR / "ui_config.json"
POLL_INTERVAL = 1.0

def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    print("Using:")
    print("  LOGS_DIR      =", LOGS_DIR)
    print("  QUARANTINE_DIR=", QUARANTINE_DIR)

def create_dummy_files():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create 3 text logs
    for i in range(1, 4):
        path = os.path.join(LOGS_DIR, f"test_log_{i}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Test log {i}\nCreated: {now}\nThis is a dummy log for UI testing.\n")
        print("Created log:", path)

    # Create 2 quarantine binaries
    for i in range(1, 3):
        path = os.path.join(QUARANTINE_DIR, f"quarantine_{i}.bin")
        with open(path, "wb") as f:
            f.write(b"dummy quarantine content\n")
        print("Created quarantine file:", path)

def open_file_with_default_app(path):
    print("Attempting to open:", path)
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        print("Opened successfully (or OS launched default app).")
    except Exception as e:
        print("Failed to open file:", e)

def delete_quarantine_file(filename):
    path = os.path.join(QUARANTINE_DIR, filename)
    print("Attempting to delete:", path)
    try:
        if os.path.exists(path):
            os.remove(path)
            print("Deleted:", path)
            return True, None
        else:
            print("File not found:", path)
            return False, "not found"
    except Exception as e:
        print("Error deleting file:", e)
        return False, str(e)

def list_dir_names(dirpath):
    try:
        return sorted(os.listdir(dirpath))
    except Exception as e:
        print("Error listing", dirpath, ":", e)
        return []

def main():
    ensure_dirs()
    create_dummy_files()

    print("\nCurrent logs:", list_dir_names(LOGS_DIR))
    print("Current quarantine:", list_dir_names(QUARANTINE_DIR))

    # Pause so you can switch to the UI and refresh lists if needed
    print("\nWaiting 1.5s before opening a log (switch to your UI and refresh lists)...")
    time.sleep(1.5)

    # Try opening the first log
    logs = list_dir_names(LOGS_DIR)
    if logs:
        open_file_with_default_app(os.path.join(LOGS_DIR, logs[0]))
    else:
        print("No logs to open.")

    # Pause then delete a quarantine file
    print("\nWaiting 1.5s before deleting a quarantine file...")
    time.sleep(1.5)
    q = list_dir_names(QUARANTINE_DIR)
    if q:
        ok, err = delete_quarantine_file(q[0])
        print("Delete result:", ok, err)
    else:
        print("No quarantine files to delete.")

    print("\nFinal logs:", list_dir_names(LOGS_DIR))
    print("Final quarantine:", list_dir_names(QUARANTINE_DIR))
    print("\nDone. If your UI didn't auto-refresh, trigger your poll/refresh handler now.")

if __name__ == "__main__":
    main()