"""
Tests for HashGuard database module.
"""
import pytest
import tempfile
import os
import time
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import (
    initialize_database,
    write_scan_log,
    get_scan_by_hash,
    get_monthly_reports,
    get_monthly_report,
    get_statistics,
    get_report_by_date_range,
    DB_CONNECTION,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
        db_path = f.name
    
    initialize_database(db_path)
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


class TestDatabaseInitialization:
    """Test database initialization."""
    
    def test_initialize_creates_tables(self, temp_db):
        """Database initialization should create required tables."""
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='scan_logs'"
        )
        tables = cursor.fetchall()
        conn.close()
        
        assert len(tables) == 1
        assert tables[0][0] == 'scan_logs'
    
    def test_initialize_creates_indexes(self, temp_db):
        """Database initialization should create indexes."""
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'idx_timestamp' in indexes
        assert 'idx_verdict' in indexes
        assert 'idx_hash' in indexes


class TestScanLogWriting:
    """Test writing scan logs."""
    
    def test_write_scan_log_success(self, temp_db):
        """Should successfully write a scan log entry."""
        result = write_scan_log(
            filename="test.exe",
            verdict="clean",
            hash_hex="abc123def456",
            original_path="/path/to/test.exe",
            sources=["MalwareBazaar"],
            error=None
        )
        
        assert result is True
    
    def test_write_scan_log_malicious(self, temp_db):
        """Should write malicious scan log entry."""
        result = write_scan_log(
            filename="malware.exe",
            verdict="malicious",
            hash_hex="bad123hash456",
            original_path="/path/to/malware.exe",
            sources=["MalwareBazaar"],
            error=None
        )
        
        assert result is True
    
    def test_write_scan_log_with_error(self, temp_db):
        """Should write scan log with error message."""
        result = write_scan_log(
            filename="failed.exe",
            verdict="error",
            hash_hex="error123hash",
            original_path="/path/to/failed.exe",
            sources=[],
            error="Connection timeout"
        )
        
        assert result is True
    
    def test_write_scan_log_replaces_duplicate_hash(self, temp_db):
        """Writing same hash should replace existing entry."""
        hash_hex = "duplicate123hash"
        
        # First write
        write_scan_log(
            filename="first.exe",
            verdict="clean",
            hash_hex=hash_hex,
            original_path="/path/first.exe"
        )
        
        # Second write with same hash
        write_scan_log(
            filename="second.exe",
            verdict="malicious",
            hash_hex=hash_hex,
            original_path="/path/second.exe"
        )
        
        # Should have updated entry
        entry = get_scan_by_hash(hash_hex)
        assert entry is not None
        assert entry['filename'] == 'second.exe'
        assert entry['verdict'] == 'malicious'


class TestScanLogQuerying:
    """Test querying scan logs."""
    
    def test_get_scan_by_hash_found(self, temp_db):
        """Should find scan log by hash."""
        hash_hex = "findme123hash"
        write_scan_log(
            filename="findme.exe",
            verdict="clean",
            hash_hex=hash_hex,
            original_path="/path/findme.exe",
            sources=["MalwareBazaar"]
        )
        
        result = get_scan_by_hash(hash_hex)
        
        assert result is not None
        assert result['filename'] == 'findme.exe'
        assert result['verdict'] == 'clean'
        assert result['hash'] == hash_hex
    
    def test_get_scan_by_hash_not_found(self, temp_db):
        """Should return None for unknown hash."""
        result = get_scan_by_hash("nonexistent123hash")
        
        assert result is None


class TestMonthlyReports:
    """Test monthly report functionality."""
    
    def test_get_monthly_reports_empty(self, temp_db):
        """Should return empty list when no logs exist."""
        result = get_monthly_reports()
        
        assert result == []
    
    def test_get_monthly_reports_with_data(self, temp_db):
        """Should return list of months with scan data."""
        # Add some scan logs
        write_scan_log(
            filename="test1.exe",
            verdict="clean",
            hash_hex="hash1",
            original_path="/path/test1.exe"
        )
        write_scan_log(
            filename="test2.exe",
            verdict="malicious",
            hash_hex="hash2",
            original_path="/path/test2.exe"
        )
        
        result = get_monthly_reports()
        
        assert len(result) >= 1
        # Should be in format MM-YYYY
        assert '-' in result[0]
    
    def test_get_monthly_report_content(self, temp_db):
        """Should return formatted report for a month."""
        # Add a scan log
        write_scan_log(
            filename="report_test.exe",
            verdict="malicious",
            hash_hex="reporthash123",
            original_path="/path/report_test.exe",
            sources=["MalwareBazaar"]
        )
        
        # Get the month for this entry
        months = get_monthly_reports()
        if months:
            report = get_monthly_report(months[0])
            assert isinstance(report, list)


class TestRecentDetections:
    """Test statistics and date range functionality."""
    
    def test_get_statistics_empty(self, temp_db):
        """Should return zero counts when no logs exist."""
        result = get_statistics()
        
        assert result["total"] == 0
        assert result["malicious"] == 0
        assert result["clean"] == 0
    
    def test_get_statistics_with_data(self, temp_db):
        """Should return correct counts with data."""
        # Add some entries
        write_scan_log("clean1.exe", "clean", "hash1", "/path/clean1.exe")
        write_scan_log("clean2.exe", "clean", "hash2", "/path/clean2.exe")
        write_scan_log("malware.exe", "malicious", "hash3", "/path/malware.exe")
        
        result = get_statistics()
        
        assert result["total"] == 3
        assert result["malicious"] == 1
        assert result["clean"] == 2
    
    def test_get_report_by_date_range(self, temp_db):
        """Should return scans within date range."""
        # Add some entries
        for i in range(5):
            write_scan_log(
                filename=f"test{i}.exe",
                verdict="clean",
                hash_hex=f"rangehash{i}",
                original_path=f"/path/test{i}.exe"
            )
        
        # Get all entries (wide date range)
        start = time.time() - 3600  # 1 hour ago
        end = time.time() + 3600  # 1 hour from now
        
        result = get_report_by_date_range(start, end)
        
        assert len(result) == 5
