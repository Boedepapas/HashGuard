# hashguard_test_files.py
# Quick smoke test for Logs and Quarantine functionality.
# Usage: python filegenerator.py
# Generates test files in the backend's quarantine and logs directories.

import os
import sys
import time
import json
import platform
import subprocess
from pathlib import Path

# Point to shared HashGuard root directories
HASHGUARD_ROOT = Path(__file__).parent.parent
QUARANTINE_DIR = HASHGUARD_ROOT / "quarantine"
LOGS_DIR = HASHGUARD_ROOT / "logs" / "logsText"  # Monthly text logs for UI display

def ensure_dirs():
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    print("Using:")
    print("  LOGS_DIR      =", LOGS_DIR)
    print("  QUARANTINE_DIR=", QUARANTINE_DIR)

def create_dummy_files():
    now = time.time()
    dt = time.localtime(now)
    
    # Create monthly text log (e.g., 12-2025.txt)
    month_str = f"{dt.tm_mon:02d}-{dt.tm_year}"
    log_path = LOGS_DIR / f"{month_str}.txt"
    
    with open(log_path, "w", encoding="utf-8") as f:
        # Create 5 test log entries in backend format: [MM-DD-YYYY] Filename: X Verdict: Y Hash: Z
        for i in range(1, 6):
            entry_time = now + (i * 3600)  # Space entries 1 hour apart
            entry_dt = time.localtime(entry_time)
            date_str = f"{entry_dt.tm_mon:02d}-{entry_dt.tm_mday:02d}-{entry_dt.tm_year}"
            
            filename = f"test_file_{i}.exe"
            verdict = ["malicious", "clean", "unknown"][i % 3]
            hash_val = f"a1b2c3d4e5f6{'0' * (64 - 12)}"
            
            entry = f"[{date_str}] Filename: {filename}\tVerdict: {verdict}\tHash: {hash_val}\n"
            f.write(entry)
    
    print(f"Created monthly log: {log_path.name}")

    # Create 3 quarantine files with metadata
    for i in range(1, 4):
        qfile_name = f"suspicious_{i}.exe"
        qfile_path = QUARANTINE_DIR / qfile_name
        meta_path = QUARANTINE_DIR / f"{qfile_name}.meta.json"
        
        # Create dummy binary
        with open(qfile_path, "wb") as f:
            f.write(b"MZ" + b"X" * 65534)  # Fake EXE
        
        # Create metadata
        meta_data = {
            "original_path": f"C:\\Downloads\\{qfile_name}",
            "quarantined_at": now,
            "hash": f"deadbeef{'0' * 56}",
            "reason": "Test quarantine file"
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)
        
        print(f"Created quarantine: {qfile_name}")

def list_dir_names(dirpath):
    try:
        return sorted([f for f in os.listdir(dirpath) if not f.endswith(".meta.json")])
    except Exception as e:
        print("Error listing", dirpath, ":", e)
        return []

def main():
    ensure_dirs()
    create_dummy_files()

    print("\nCurrent logs:", list_dir_names(LOGS_DIR))
    print("Current quarantine:", list_dir_names(QUARANTINE_DIR))
    print("\nDone! Launch the frontend to see these files in the UI.")

if __name__ == "__main__":
    main()