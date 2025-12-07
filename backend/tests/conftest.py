"""
Pytest configuration and fixtures for HashGuard tests.
"""
import pytest
import sys
import os
from pathlib import Path

# Add backend to path for imports
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before running tests."""
    # Ensure we're not using real API keys in tests
    os.environ.setdefault("MalwareBazaar_Auth_KEY", "")
    os.environ.setdefault("MALWAREBAZAAR_API_KEY", "")
    
    yield
    
    # Cleanup after tests


@pytest.fixture
def mock_config():
    """Provide mock configuration for tests."""
    return {
        "watch_path": "",
        "quarantine_path": "",
        "logs_path": "",
        "cache_db": "",
        "debounce_ms": 500,
        "stability_seconds": 3,
        "min_size_bytes": 1,
        "max_size_bytes": 2147483648,
        "allowed_extensions": [".exe", ".dll", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".js"],
        "blocked_paths": [],
        "ignore_name_regex": [],
        "priority_map": {".exe": 2, ".dll": 2, ".msi": 1},
        "worker_count": 4,
        "worker_throttle_ms": 0,
    }
