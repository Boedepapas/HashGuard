import os
import time
import re
import sqlite3
import queue
import threading
import requests
import shutil
import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from dotenv import load_dotenv

# Global IPC server reference for broadcasting updates
IPC_SERVER = None

def set_ipc_server(server):
    """Set the IPC server for broadcasting updates."""
    global IPC_SERVER
    IPC_SERVER = server

#-------------------------------------------------------------------------------
# Configuration Loader
#-------------------------------------------------------------------------------

import yaml

# Load environment variables from .env file
load_dotenv()

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    CFG = yaml.safe_load(f)

# Initialize paths - use HashGuard root folder (parent of backend) for shared data
def get_hashguard_root():
    """Get the HashGuard root directory (parent of backend folder)."""
    backend_dir = Path(__file__).parent
    return backend_dir.parent

HASHGUARD_ROOT = get_hashguard_root()

# Watch path - user sets via UI, defaults to user's Downloads if empty
watch_path_config = CFG.get("watch_path", "").strip()
if watch_path_config:
    WATCH_PATH = os.path.abspath(watch_path_config)
else:
    # Default to user's Downloads folder
    WATCH_PATH = os.path.join(os.path.expanduser("~"), "Downloads")

# Quarantine path - in HashGuard root folder (shared with frontend)
quarantine_path_config = CFG.get("quarantine_path", "").strip()
if quarantine_path_config:
    QUARANTINE_PATH = os.path.abspath(quarantine_path_config)
else:
    QUARANTINE_PATH = str(HASHGUARD_ROOT / "quarantine")

# Logs path - in HashGuard root folder (shared with frontend)
logs_path_config = CFG.get("logs_path", "").strip()
if logs_path_config:
    LOGS_PATH = os.path.abspath(logs_path_config)
else:
    LOGS_PATH = str(HASHGUARD_ROOT / "logs")

# Cache database - in backend folder
cache_db_config = CFG.get("cache_db", "").strip()
if cache_db_config:
    CACHE_DB = os.path.abspath(cache_db_config)
else:
    CACHE_DB = str(Path(__file__).parent / "cache.sqlite")

# Create directories if they don't exist
os.makedirs(QUARANTINE_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)

# Print paths for debugging
print(f"[Monitor] HASHGUARD_ROOT: {HASHGUARD_ROOT}")
print(f"[Monitor] WATCH_PATH: {WATCH_PATH}")
print(f"[Monitor] QUARANTINE_PATH: {QUARANTINE_PATH}")
print(f"[Monitor] LOGS_PATH: {LOGS_PATH}")
print(f"[Monitor] CACHE_DB: {CACHE_DB}")

DEBOUNCE_MS = int(CFG.get("debounce_ms", 500))
STABILITY_SECONDS = int(CFG.get("stability_seconds", 3))
MIN_SIZE = int(CFG.get("min_size_bytes", 1))
MAX_SIZE = int(CFG.get("max_size_bytes", 2_147_483_648))
ALLOWED_EXTS = set(x.lower() for x in CFG.get("allowed_extensions", []))
BLOCKED_PATHS = [os.path.abspath(p) for p in CFG.get("blocked_paths", [])]
IGNORE_NAME_REGEX = [re.compile(r) for r in CFG.get("ignore_name_regex", [])]
PRIORITY_MAP = CFG.get("priority_map", {})
WORKER_COUNT = int(CFG.get("worker_count", 4))
WORKER_THROTTLE_MS = int(CFG.get("worker_throttle_ms", 0))

#-------------------------------------------------------------------------------
# Local Cache
#-------------------------------------------------------------------------------

def init_cache(db_path: str):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cache (
        hash TEXT PRIMARY KEY,
        verdict TEXT,
        ts INTEGER
    )""")
    conn.commit()
    return conn

CACHE_CONN = init_cache(CACHE_DB)
CACHE_LOCK = threading.Lock()

def cache_lookup(hash_hex: str) -> Optional[str]:
    with CACHE_LOCK:
        cur = CACHE_CONN.cursor()
        cur.execute("SELECT verdict FROM cache WHERE hash=?;", (hash_hex,))
        row = cur.fetchone()
        return row[0] if row else None

def cache_store(hash_hex: str, verdict: str):
    with CACHE_LOCK:
        ts = int(time.time())
        cur = CACHE_CONN.cursor()
        cur.execute("INSERT OR REPLACE INTO cache (hash, verdict, ts) VALUES (?, ?, ?);", (hash_hex, verdict, ts))
        CACHE_CONN.commit()

# ----------------------------
# Helper utilities

# ----------------------------
def normalize_path(path: str) -> str:
    return os.path.abspath(os.path.realpath(path))

def path_is_blocked(path: str) -> bool:
    for bp in BLOCKED_PATHS:
        if path.startswith(bp):
            return True
    return False

def name_matches_ignore(name: str) -> bool:
    return any(r.search(name) for r in IGNORE_NAME_REGEX)

def extension_allowed(path: str) -> bool:
    _, ext = os.path.splitext(path)
    if not ext:
        return False
    return ext.lower() in ALLOWED_EXTS

def size_ok(path: str) -> bool:
    try:
        size = os.path.getsize(path)
    except OSError:
        return False
    return MIN_SIZE <= size <= MAX_SIZE

def compute_sha256(path: str, chunk_size: int = 1024*64) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def priority_for_path(path: str) -> int:
    _, ext = os.path.splitext(path)
    return int(PRIORITY_MAP.get(ext.lower(), 1))

def Quarantine(path: str):
    """Move a file to quarantine and create metadata."""
    if not QUARANTINE_PATH:
        print(f"No quarantine path set; cannot quarantine {path}")
        return False
    
    path_obj = Path(path)
    quarantine_dir = Path(QUARANTINE_PATH)
    
    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique quarantine filename
        basename = path_obj.name
        quarantine_file = quarantine_dir / basename
        
        # If file exists, add timestamp to make unique
        if quarantine_file.exists():
            timestamp = int(time.time())
            name_parts = basename.rsplit('.', 1)
            if len(name_parts) == 2:
                quarantine_file = quarantine_dir / f"{name_parts[0]}.{timestamp}.{name_parts[1]}"
            else:
                quarantine_file = quarantine_dir / f"{basename}.{timestamp}"
        
        # Move file to quarantine
        try:
            path_obj.replace(quarantine_file)
        except OSError:
            shutil.move(str(path_obj), str(quarantine_file))
        
        # Set read-only permissions (owner only)
        try:
            quarantine_file.chmod(0o600)
        except Exception as e:
            print(f"Warning: Failed to set permissions on {quarantine_file}: {e}")
        
        # Broadcast quarantine update to frontend
        if IPC_SERVER:
            try:
                IPC_SERVER.broadcast({"type": "quarantine_updated", "action": "added", "filename": str(quarantine_file.name)})
            except Exception as e:
                print(f"Failed to broadcast quarantine update: {e}")
        
        # Create metadata file
        timestamp = time.time()
        meta = {
            "original_path": str(path_obj),
            "quarantined_path": str(quarantine_file),
            "timestamp": timestamp,
            "action": "quarantine",
            "filename": basename,
        }
        meta_path = quarantine_file.with_suffix(quarantine_file.suffix + ".meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        
        print(f"Quarantined {path_obj} to {quarantine_file}")
        return True
        
    except Exception as e:
        print(f"Error quarantining {path}: {e}")
        return False
#-------------------------------------------------------------------------------
# Debounce and Stability
#-------------------------------------------------------------------------------

@dataclass
class PendingItem:
    path: str
    last_seen: float
    last_size: int

PENDING: Dict[str, PendingItem] = {}
PENDING_LOCK = threading.Lock()

def schedule_stability_check(filepath: str):
    """
    Checks if a file is stable (not changing size) for STABILITY_SECONDS before processing.
    """
    now = time.time()
    try:
        size = os.path.getsize(filepath)
    except OSError:
        size = -1
    with PENDING_LOCK:
        PENDING[filepath] = PendingItem(path=filepath, last_seen=now, last_size=size)

def stability_worker_loop(out_queue: "queue.PriorityQueue", stop_event: threading.Event = None):
    """
    Background thread that periodically scans pending items and moves stable files
    into the worker queue. Stability defined as unchanged size for STABILITY_SECONDS.
    """
    while True:
        if stop_event and stop_event.is_set():
            return
        time.sleep(DEBOUNCE_MS / 1000.0)
        now = time.time()
        to_process = []
        with PENDING_LOCK:
            for pth, item in list(PENDING.items()):
                try:
                    current_size = os.path.getsize(pth)
                except OSError:
                    # file gone or unreachable; drop
                    PENDING.pop(pth, None)
                    continue
                # size unchanged and enough time passed
                if current_size == item.last_size and (now - item.last_seen) >= STABILITY_SECONDS:
                    to_process.append(pth)
                    PENDING.pop(pth, None)
                else:
                    # update last_seen/last_size if size changed
                    if current_size != item.last_size:
                        PENDING[pth].last_size = current_size
                        PENDING[pth].last_seen = now
        for pth in to_process:
            enqueue_if_passes_filters(pth, out_queue)

#-------------------------------------------------------------------------------
# Filesystem Event Handler
#-------------------------------------------------------------------------------

class FilterHandler(FileSystemEventHandler):
    """
    Watchdog handler that debounces file events and schedules stability checks.
    Only 'created' and 'modified' events are considered.
    """

    def __init__(self, out_queue: "queue.PriorityQueue"):
        self.out_queue = out_queue

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            handle_fs_event(event.src_path, self.out_queue)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            handle_fs_event(event.src_path, self.out_queue)

def handle_fs_event(filepath: str, out_queue: "queue.PriorityQueue"):
    filepath = normalize_path(filepath)
    if path_is_blocked(filepath):
        return
    if name_matches_ignore(os.path.basename(filepath)):
        return
    # Drop early if extension is not allowed
    if not extension_allowed(filepath):
        return
    schedule_stability_check(filepath)


def enqueue_if_passes_filters(pth: str, out_queue: "queue.PriorityQueue"):
    """
    Called after stability checks succeed. Performs final content sniffing, whitelist check,
    and then places the path into the prioritized out_queue for worker hashing.
    """
    p = normalize_path(pth)
    name = os.path.basename(p)

    # Final existence and permission check
    if not os.path.exists(p):
        print(f"DROP missing {p}")
        return
    if path_is_blocked(p):
        print(f"DROP blocked on final check {p}")
        return
    if name_matches_ignore(name):
        print(f"DROP ignore name final {p}")
        return
    if not extension_allowed(p):
        print(f"DROP extension final {p}")
        return
    if not size_ok(p):
        print(f"DROP size rule final {p}")
        return
    try:
        h = compute_sha256(p)
    except Exception as e:
        print(f"DROP error hashing {p}: {e}")
        return
    verdict = cache_lookup(h)
    if verdict == "clean":
        print(f"CACHE HIT clean {p}")
        return
    if verdict == "malicious":
        print(f"CACHE HIT malicious {p}")
        Quarantine(p)
        return
     # Push into worker queue with priority
    prio = -priority_for_path(p)  # PriorityQueue returns smallest first; invert to get high-prio first
    out_queue.put((prio, time.time(), p, h))
    print(f"ENQUEUE {p} prio={-prio}")

#-------------------------------------------------------------------------------
# Worker Process Items
#-------------------------------------------------------------------------------

def worker_process_item(item):
    """
    Worker function to process a single item from the queue.
    Tries premium APIs first, falls back to free APIs if keys not available.
    Combines verdicts from multiple sources.
    """
    from logger import write_scan_log, write_quarantine_log, write_event_log
    from ipc import IPCServer
    
    prio, ts, path, hash_hex = item
    print(f"WORKER START {path} hash={hash_hex}")
    
    # Try to get verdicts from available APIs (in order of preference)
    verdicts = []
    sources_used = []
    
    # Try MalwareBazaar (premium)
    mb_verdict = MB_API_lookup_hash(hash_hex)
    if mb_verdict:
        verdicts.append(mb_verdict)
        sources_used.append("MalwareBazaar")
        print(f"  MalwareBazaar: {mb_verdict}")
    
    # Try VirusTotal (premium)
    vt_verdict = VT_API_lookup_hash(hash_hex)
    if vt_verdict:
        verdicts.append(vt_verdict)
        sources_used.append("VirusTotal")
        print(f"  VirusTotal: {vt_verdict}")
    
    # Try custom API
    cp_verdict = CP_API_lookup_hash(hash_hex)
    if cp_verdict:
        verdicts.append(cp_verdict)
        sources_used.append("CustomAPI")
        print(f"  Custom API: {cp_verdict}")
    
    # Fallback to free API if no results
    if not verdicts:
        free_verdict = free_API_lookup_hash(hash_hex)
        if free_verdict:
            verdicts.append(free_verdict)
            sources_used.append("FreeAPI")
            print(f"  Free API (fallback): {free_verdict}")
    
    # Combine verdicts: if ANY says malicious, mark as malicious
    if not verdicts:
        # No API results available - mark as unknown (do not assume clean)
        verdict = "unknown"
        print(f"  WARNING: No APIs available, marking unknown")
    elif "malicious" in verdicts:
        verdict = "malicious"
    else:
        verdict = "clean"
    
    cache_store(hash_hex, verdict)
    
    # Write log file
    import os as os_module
    filename = os_module.path.basename(path)
    write_scan_log(filename, verdict, hash_hex, path, sources_used)
    
    if verdict == "malicious":
        print(f"VERDICT malicious {path}")
        write_quarantine_log(filename, hash_hex, path)
        Quarantine(path)
    elif verdict == "clean":
        print(f"VERDICT clean {path}")
    else:
        print(f"VERDICT unknown {path}")
        write_event_log("unknown_verdict", {"path": path, "hash": hash_hex})
        write_quarantine_log(filename, hash_hex, path)
        Quarantine(path)

    # Throttle to reduce CPU spikes
    if WORKER_THROTTLE_MS > 0:
        time.sleep(WORKER_THROTTLE_MS / 1000.0)
    
    
def MB_API_lookup_hash(hash_hex: str) -> Optional[str]:
    """
    MalwareBazaar API lookup for hash reputation.
    Returns 'malicious', 'clean', or None (unknown/error).
    Requires MalwareBazaar_Auth_KEY (preferred) or MALWAREBAZAAR_API_KEY environment variable.
    """
    auth_key = os.getenv("MalwareBazaar_Auth_KEY") or os.getenv("MALWAREBAZAAR_API_KEY")
    if not auth_key:
        return None  # API key not configured, skip this service
    
    url = "https://mb-api.abuse.ch/api/v1/"
    headers = {"Auth-Key": auth_key}
    data = {"query": "get_info", "hash": hash_hex}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 401:
            print("MalwareBazaar API error: unauthorized (check API key)")
            return None
        response.raise_for_status()
        result = response.json()
        if result.get("data"):
            return "malicious"
        else:
            return "clean"
    except requests.RequestException as e:
        print(f"MalwareBazaar API error: {e}")
        return None


def VT_API_lookup_hash(hash_hex: str) -> Optional[str]:
    """
    VirusTotal API lookup for hash reputation.
    Returns 'malicious', 'clean', or None (unknown/error).
    Requires VIRUSTOTAL_API_KEY environment variable.
    """
    auth_key = os.getenv("VIRUSTOTAL_API_KEY")
    if not auth_key:
        return None  # API key not configured, skip this service
    
    url = f"https://www.virustotal.com/api/v3/files/{hash_hex}"
    headers = {"x-apikey": auth_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {})
        attributes = data.get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        
        malicious_count = stats.get("malicious", 0)
        if malicious_count > 0:
            return "malicious"
        else:
            return "clean"
    except requests.RequestException as e:
        print(f"VirusTotal API error: {e}")
        return None


def free_API_lookup_hash(hash_hex: str) -> Optional[str]:
    """
    ThreatFox lookup (requires THREATFOX_API_KEY).
    Returns 'malicious' if hash is found, 'clean' otherwise, None on error/missing key.
    """
    try:
        tf_key = os.getenv("THREATFOX_API_KEY")
        if not tf_key:
            print("Free API fallback disabled: THREATFOX_API_KEY not set.")
            return None
        headers = {"API-KEY": tf_key}
        resp = requests.post(
            "https://threatfox-api.abuse.ch/api/v1/",
            json={"query": "search_hash", "hash": hash_hex},
            headers=headers,
            timeout=8,
        )
        if resp.status_code == 401:
            print("Free API fallback unauthorized (ThreatFox). Skipping.")
            return None
        resp.raise_for_status()
        data = resp.json()
        if data.get("data"):
            return "malicious"
        return "clean"
    except requests.RequestException as e:
        print(f"Free API fallback unavailable: {e}")
        return None


def CP_API_lookup_hash(hash_hex: str) -> Optional[str]:
    """
    Placeholder for second API lookup.
    Replace with your actual API call logic.
    """
    # TODO: Implement your second API here
    return None


