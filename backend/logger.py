"""
Logging module for HashGuard backend.
Writes scan results and events to the configured logs directory.
Also maintains monthly aggregated text logs for frontend display.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import os


def init_logs(logs_dir: str):
    """Initialize logs directory. Called by main.py with configured path."""
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    return logs_dir


# Will be set by main.py
LOGS_DIR = None
LOGS_LOCK = threading.Lock()
IPC_SERVER = None

def set_ipc_server(server):
    """Set the IPC server for broadcasting updates."""
    global IPC_SERVER
    IPC_SERVER = server


def set_logs_dir(logs_dir: str):
    """Set the logs directory path. Called by main.py during initialization."""
    global LOGS_DIR
    LOGS_DIR = logs_dir
    init_logs(logs_dir)


def get_monthly_log_path(logs_dir: str, timestamp: float = None) -> Path:
    """Get the monthly log file path for a given timestamp (e.g., logsText/12-2025.txt)."""
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    month_str = f"{dt.month:02d}-{dt.year}"
    logs_text_dir = Path(logs_dir) / "logsText"
    logs_text_dir.mkdir(parents=True, exist_ok=True)
    return logs_text_dir / f"{month_str}.txt"


def append_to_monthly_log(logs_dir: str, filename: str, verdict: str, hash_hex: str, timestamp: float):
    """Append a scan entry to the monthly text log in the format: [MM-DD-YYYY] Filename: X Verdict: Y Hash: Z"""
    log_path = get_monthly_log_path(logs_dir, timestamp)
    
    dt = datetime.fromtimestamp(timestamp)
    date_str = dt.strftime("%m-%d-%Y")
    
    entry = f"[{date_str}] Filename: {filename}\tVerdict: {verdict}\tHash: {hash_hex}\n"
    
    with LOGS_LOCK:
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"Error appending to monthly log: {e}")


def write_scan_log(filename: str, verdict: str, hash_hex: str, 
                   original_path: str, sources: list = None, error: str = None):
    """
    Write a scan result to the logs directory.
    Creates both a JSON log and appends to monthly text log.
    
    Args:
        filename: Name of the scanned file
        verdict: 'malicious', 'clean', or 'unknown'
        hash_hex: SHA256 hash of the file
        original_path: Original path of the file
        sources: List of APIs that were consulted
        error: Any error message from scanning
    """
    if LOGS_DIR is None:
        print("[Logger] WARNING: LOGS_DIR not initialized")
        return None
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    timestamp = time.time()
    iso_time = datetime.fromtimestamp(timestamp).isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "iso_time": iso_time,
        "filename": filename,
        "verdict": verdict,
        "hash": hash_hex,
        "path": original_path,
        "sources": sources or [],
        "error": error,
    }
    
    # Create JSON log file with timestamp
    log_filename = f"scan_{int(timestamp)}.json"
    log_path = Path(LOGS_DIR) / log_filename
    
    with LOGS_LOCK:
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2)
            
            # Also append to monthly text log
            append_to_monthly_log(LOGS_DIR, filename, verdict, hash_hex, timestamp)
            
            # Broadcast log update to frontend
            if IPC_SERVER:
                try:
                    IPC_SERVER.broadcast({"type": "log_updated", "action": "added", "filename": filename, "verdict": verdict})
                except Exception as e:
                    print(f"Failed to broadcast log update: {e}")
            
            return log_path
        except Exception as e:
            print(f"Error writing scan log: {e}")
            return None


def write_quarantine_log(filename: str, hash_hex: str, original_path: str):
    """Write a quarantine event to logs."""
    if LOGS_DIR is None:
        print("[Logger] WARNING: LOGS_DIR not initialized")
        return None
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    timestamp = time.time()
    iso_time = datetime.fromtimestamp(timestamp).isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "iso_time": iso_time,
        "event": "quarantine",
        "filename": filename,
        "hash": hash_hex,
        "original_path": original_path,
    }
    
    log_filename = f"quarantine_{int(timestamp)}.json"
    log_path = Path(LOGS_DIR) / log_filename
    
    with LOGS_LOCK:
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2)
            return log_path
        except Exception as e:
            print(f"Error writing quarantine log: {e}")
            return None


def write_event_log(event_type: str, details: Dict[str, Any]):
    """Write a generic event to logs."""
    if LOGS_DIR is None:
        print("[Logger] WARNING: LOGS_DIR not initialized")
        return None
    Path(LOGS_DIR).mkdir(parents=True, exist_ok=True)
    
    timestamp = time.time()
    iso_time = datetime.fromtimestamp(timestamp).isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "iso_time": iso_time,
        "event": event_type,
        **details
    }
    
    log_filename = f"event_{event_type}_{int(timestamp)}.json"
    log_path = Path(LOGS_DIR) / log_filename
    
    with LOGS_LOCK:
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2)
            return log_path
        except Exception as e:
            print(f"Error writing event log: {e}")
            return None
