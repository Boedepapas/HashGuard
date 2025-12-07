"""SQLite database for scan logs and cache."""
import sqlite3
import threading
from pathlib import Path
from datetime import datetime
import json

# Thread-safe database access
DB_LOCK = threading.Lock()
DB_CONNECTION = None
DB_PATH = None

def initialize_database(db_path: str):
    """Initialize the SQLite database with schema."""
    global DB_CONNECTION, DB_PATH
    DB_PATH = db_path
    
    with DB_LOCK:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                filename TEXT NOT NULL,
                verdict TEXT NOT NULL,
                hash TEXT UNIQUE,
                path TEXT,
                sources TEXT,
                error TEXT
            )
        """)
        
        # Create indexes for fast queries
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON scan_logs(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_verdict ON scan_logs(verdict)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON scan_logs(hash)")
        
        conn.commit()
        DB_CONNECTION = conn

def write_scan_log(filename: str, verdict: str, hash_hex: str, original_path: str, sources: list = None, error: str = None):
    """Write a scan result to the database."""
    if DB_CONNECTION is None:
        print("[Database] ERROR: Database not initialized")
        return False
    
    timestamp = datetime.now().timestamp()
    sources_json = json.dumps(sources or [])
    
    with DB_LOCK:
        try:
            DB_CONNECTION.execute("""
                INSERT OR REPLACE INTO scan_logs 
                (timestamp, filename, verdict, hash, path, sources, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, filename, verdict, hash_hex, original_path, sources_json, error))
            DB_CONNECTION.commit()
            return True
        except Exception as e:
            print(f"[Database] Error writing scan log: {e}")
            return False

def get_scan_by_hash(hash_hex: str):
    """Get scan details by hash."""
    if DB_CONNECTION is None:
        return None
    
    with DB_LOCK:
        try:
            row = DB_CONNECTION.execute(
                "SELECT * FROM scan_logs WHERE hash = ?",
                (hash_hex,)
            ).fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[Database] Error querying by hash: {e}")
            return None

def get_monthly_reports():
    """Get list of months that have scan logs (for UI listbox)."""
    if DB_CONNECTION is None:
        return []
    
    with DB_LOCK:
        try:
            rows = DB_CONNECTION.execute("""
                SELECT DISTINCT strftime('%m-%Y', datetime(timestamp, 'unixepoch')) as month
                FROM scan_logs
                ORDER BY month DESC
            """).fetchall()
            return [row['month'] for row in rows]
        except Exception as e:
            print(f"[Database] Error getting monthly reports: {e}")
            return []

def get_monthly_report(month_str: str):
    """Get formatted report for a specific month (e.g., '12-2025')."""
    if DB_CONNECTION is None:
        return []
    
    with DB_LOCK:
        try:
            # Parse month string (MM-YYYY format)
            month, year = month_str.split('-')
            
            rows = DB_CONNECTION.execute("""
                SELECT timestamp, filename, verdict, hash
                FROM scan_logs
                WHERE strftime('%m', datetime(timestamp, 'unixepoch')) = ?
                  AND strftime('%Y', datetime(timestamp, 'unixepoch')) = ?
                ORDER BY timestamp DESC
            """, (month, year)).fetchall()
            
            # Format as: [MM-DD-YYYY] Filename: X Verdict: Y Hash: Z
            report_lines = []
            for row in rows:
                dt = datetime.fromtimestamp(row['timestamp'])
                date_str = dt.strftime("%m-%d-%Y")
                line = f"[{date_str}] Filename: {row['filename']}\tVerdict: {row['verdict']}\tHash: {row['hash']}"
                report_lines.append(line)
            
            return report_lines
        except Exception as e:
            print(f"[Database] Error getting monthly report: {e}")
            return []

def get_statistics():
    """Get scan statistics."""
    if DB_CONNECTION is None:
        return {
            "total": 0,
            "malicious": 0,
            "clean": 0,
            "unknown": 0
        }
    
    with DB_LOCK:
        try:
            total = DB_CONNECTION.execute("SELECT COUNT(*) FROM scan_logs").fetchone()[0]
            malicious = DB_CONNECTION.execute("SELECT COUNT(*) FROM scan_logs WHERE verdict = 'malicious'").fetchone()[0]
            clean = DB_CONNECTION.execute("SELECT COUNT(*) FROM scan_logs WHERE verdict = 'clean'").fetchone()[0]
            unknown = DB_CONNECTION.execute("SELECT COUNT(*) FROM scan_logs WHERE verdict = 'unknown'").fetchone()[0]
            
            return {
                "total": total,
                "malicious": malicious,
                "clean": clean,
                "unknown": unknown
            }
        except Exception as e:
            print(f"[Database] Error getting statistics: {e}")
            return {"total": 0, "malicious": 0, "clean": 0, "unknown": 0}

def get_report_by_date_range(start_timestamp: float, end_timestamp: float):
    """Get scans within a date range."""
    if DB_CONNECTION is None:
        return []
    
    with DB_LOCK:
        try:
            rows = DB_CONNECTION.execute("""
                SELECT * FROM scan_logs
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            """, (start_timestamp, end_timestamp)).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[Database] Error querying date range: {e}")
            return []

def close_database():
    """Close database connection."""
    global DB_CONNECTION
    if DB_CONNECTION:
        with DB_LOCK:
            DB_CONNECTION.close()
            DB_CONNECTION = None
