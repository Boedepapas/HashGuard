import os
import time
import re
import sqlite3
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

#-------------------------------------------------------------------------------
# Configuration Loader
#-------------------------------------------------------------------------------

import yaml

CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    CFG = yaml.safe_load(f)

WATCH_PATH = os.path.abspath(CFG["watch_path"])
STABILITY_SECONDS = float(CFG.get("stability_seconds", 3))
DEBOUNCE_MS = int(CFG.get("debounce_ms", 500))
MIN_SIZE = int(CFG.get("min_size_bytes", 1))
MAX_SIZE = int(CFG.get("max_size_bytes", 2_147_483_648))
ALLOWED_EXTS = set(x.lower() for x in CFG.get("allowed_extensions", []))
BLOCKED_PATHS = [os.path.abspath(p) for p in CFG.get("blocked_paths", [])]
IGNORE_NAME_REGEX = [re.compile(r) for r in CFG.get("ignore_name_regex", [])]
PRIORITY_MAP = CFG.get("priority_map", {})
WORKER_COUNT = int(CFG.get("worker_count", 4))
CACHE_DB = os.path.abspath(CFG.get("cache_db", "cache.sqlite"))

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
    import hashlib
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

def stability_worker_loop(out_queue: "queue.PriorityQueue"):
    """
    Background thread that periodically scans pending items and moves stable files
    into the worker queue. Stability defined as unchanged size for STABILITY_SECONDS.
    """
    while True:
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
    schedule_stability_check(filepath)
    if not extension_allowed(filepath):
        schedule_stability_check(filepath)
        return


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
        # Add quarantine logic here later
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
    Computes hash, checks cache, and simulates external scan.
    """
    prio, ts, path, hash = item
    print(f"WORKER START {path} hash= {hash}")
    verdict = API_lookup_hash(hash)
    cache_store(hash, verdict)
    if verdict == "malicious":
        print(f"VERDICT malicious {path}")
        # Add quarantine logic here later
    if verdict == "clean":
        print(f"VERDICT clean {path}")
    
def API_lookup_hash(hash_hex: str) -> str:
    """
    Placeholder for external API hash lookup.
    Replace with actual API call logic.
    """
    # Simulate network delay
    time.sleep(1)
    # For demo purposes, randomly decide verdict
    import random
    return "clean" if random.random() > 0.1 else "malicious"

#-------------------------------------------------------------------------------
# Main Monitoring Loop
# need to make a main.py file
#-------------------------------------------------------------------------------

def main():
    out_queue = queue.PriorityQueue()
    observer = Observer()
    handler = FilterHandler(out_queue)
    observer.schedule(handler, WATCH_PATH, recursive=True)
    observer.start()

    # Start stability worker thread
    stability_thread = threading.Thread(target=stability_worker_loop, args=(out_queue,), daemon=True)
    stability_thread.start()

    # Start thread pool to process items from queue
    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as exe:
        try:
            while True:
                try:
                    item = out_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                # Submit to pool for processing
                exe.submit(worker_process_item, item)
        #-------------------------------------------------------------------------------
        # Change with GUI story
        except KeyboardInterrupt:
            print("Shutting down")
        #-------------------------------------------------------------------------------
        finally:
            observer.stop()
            observer.join()
