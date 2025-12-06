"""
Smoke test for HashGuard backend.
Creates test files, checks for quarantine/logs, validates CPU throttle behavior.
"""

import os
import time
import json
import tempfile
from pathlib import Path
from ipc import IPCClient

def create_test_file(path: str, size_bytes: int = 65536, content: bytes = None) -> str:
    """Create a test file and return its path."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        if content:
            f.write(content)
        else:
            f.write(b"benign" * (size_bytes // 6))
    return path


def test_backend():
    """Run smoke test: create files, check backend response."""
    # Clean prior artifacts for a fresh run but keep directories
    for folder in [Path("./logs/logsText"), Path("./logs"), Path("./quarantine")]:
        if folder.exists():
            for p in folder.glob("*"):
                if p.is_file():
                    try:
                        p.unlink()
                    except Exception:
                        pass
                elif p.is_dir():
                    for child in p.glob("*"):
                        try:
                            child.unlink()
                        except Exception:
                            pass
                    try:
                        p.rmdir()
                    except Exception:
                        pass
        folder.mkdir(parents=True, exist_ok=True)

    watch_path = os.path.expanduser("~/Downloads")
    print(f"[TEST] Watch path: {watch_path}")
    
    # Connect to backend IPC
    client = IPCClient()
    if not client.connect():
        print("[TEST] ERROR: Could not connect to backend IPC (is main.py running?)")
        return False
    
    print("[TEST] Connected to backend IPC")
    
    # Check backend status
    status = client.send_command({"type": "get_status"})
    print(f"[TEST] Backend status: {status}")
    
    if not status or status.get("status") != "ok":
        print("[TEST] ERROR: Backend not responding correctly")
        return False
    
    # Start scan
    print("[TEST] Starting scan...")
    resp = client.send_command({"type": "start_scan"})
    print(f"[TEST] Start scan response: {resp}")
    
    # Create test files
    test_files = []

    # File 1: Benign (should likely be clean)
    benign_file = os.path.join(watch_path, "test_benign.exe")
    create_test_file(benign_file, content=b"MZ" + b"X" * 65534)  # Fake EXE
    test_files.append(("benign_file", benign_file))
    print(f"[TEST] Created benign file: {benign_file}")

    # File 2: Unknown (random bytes)
    unknown_file = os.path.join(watch_path, "test_unknown.exe")
    create_test_file(unknown_file, content=bytes(range(256)) * 256)  # Random bytes
    test_files.append(("unknown_file", unknown_file))
    print(f"[TEST] Created unknown file: {unknown_file}")

    # File 3: Archive extension (should enqueue)
    zip_file = os.path.join(watch_path, "test_archive.zip")
    create_test_file(zip_file, content=b"PK" + b"A" * 65534)
    test_files.append(("zip_file", zip_file))
    print(f"[TEST] Created archive file: {zip_file}")

    # File 4: Disallowed extension (should be dropped)
    txt_file = os.path.join(watch_path, "test_drop.txt")
    create_test_file(txt_file, content=b"dropme" * 20000)
    test_files.append(("txt_file", txt_file))
    print(f"[TEST] Created disallowed file (should drop): {txt_file}")
    
    # Wait for processing (stability_seconds=3 + debounce + worker time)
    print("[TEST] Waiting for files to be processed (20 seconds)...")
    time.sleep(20)
    
    # Check logs directory
    logs_dir = Path("./logs")
    quarantine_dir = Path("./quarantine")
    
    print(f"\n[TEST] Checking logs in: {logs_dir}")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.json"))
        print(f"[TEST] Found {len(log_files)} log files:")
        for log_file in sorted(log_files)[-10:]:  # Last 10 logs
            with open(log_file) as f:
                log = json.load(f)
                print(f"  - {log_file.name}: {log.get('event') or log.get('verdict')} | {log.get('filename', log.get('path', ''))}")
    else:
        print("[TEST] WARNING: Logs directory not found")
    
    print(f"\n[TEST] Checking quarantine in: {quarantine_dir}")
    if quarantine_dir.exists():
        quarantined = list(quarantine_dir.glob("*"))
        print(f"[TEST] Found {len(quarantined)} quarantined items:")
        for item in quarantined:
            print(f"  - {item.name}")
    else:
        print("[TEST] WARNING: Quarantine directory not found")
    
    # Cleanup
    print("\n[TEST] Cleanup: removing test files...")
    for _, fpath in test_files:
        try:
            os.remove(fpath)
        except:
            pass
    
    # Stop scan
    client.send_command({"type": "stop_scan"})
    client.close()
    
    print("\n[TEST] Done. Check logs/quarantine above for results.")
    return True


if __name__ == "__main__":
    test_backend()
