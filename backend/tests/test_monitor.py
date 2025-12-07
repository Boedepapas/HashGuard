"""
Tests for HashGuard monitor module.
Tests core file monitoring and hash checking functionality.
"""
import pytest
import os
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHashComputation:
    """Test SHA256 hash computation."""
    
    def test_compute_sha256_empty_file(self):
        """Should compute correct hash for empty file."""
        from monitor import compute_sha256
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"")
            temp_path = f.name
        
        try:
            result = compute_sha256(temp_path)
            # SHA256 of empty string
            expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            assert result == expected
        finally:
            os.unlink(temp_path)
    
    def test_compute_sha256_known_content(self):
        """Should compute correct hash for known content."""
        from monitor import compute_sha256
        
        test_content = b"Hello, HashGuard!"
        expected = hashlib.sha256(test_content).hexdigest()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = compute_sha256(temp_path)
            assert result == expected
        finally:
            os.unlink(temp_path)
    
    def test_compute_sha256_large_file(self):
        """Should handle large files correctly."""
        from monitor import compute_sha256
        
        # Create a 1MB file
        test_content = b"x" * (1024 * 1024)
        expected = hashlib.sha256(test_content).hexdigest()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = compute_sha256(temp_path)
            assert result == expected
        finally:
            os.unlink(temp_path)


class TestPathFiltering:
    """Test path filtering functions."""
    
    def test_normalize_path(self):
        """Should normalize paths correctly."""
        from monitor import normalize_path
        
        # Test with relative path
        result = normalize_path("./test/path")
        assert os.path.isabs(result)
        
        # Test with absolute path
        abs_path = os.path.abspath("/test/path")
        result = normalize_path(abs_path)
        assert result == abs_path
    
    def test_extension_allowed_exe(self):
        """Should allow .exe extension."""
        from monitor import extension_allowed
        
        result = extension_allowed("test.exe")
        assert result is True
    
    def test_extension_allowed_msi(self):
        """Should allow .msi extension."""
        from monitor import extension_allowed
        
        result = extension_allowed("test.msi")
        assert result is True
    
    def test_extension_allowed_case_insensitive(self):
        """Extension check should be case insensitive."""
        from monitor import extension_allowed
        
        assert extension_allowed("test.EXE") is True
        assert extension_allowed("test.Exe") is True
        assert extension_allowed("test.MSI") is True
    
    def test_extension_not_allowed_txt(self):
        """Should not allow .txt extension."""
        from monitor import extension_allowed
        
        result = extension_allowed("test.txt")
        assert result is False
    
    def test_extension_not_allowed_no_extension(self):
        """Should not allow files without extension."""
        from monitor import extension_allowed
        
        result = extension_allowed("testfile")
        assert result is False


class TestSizeFiltering:
    """Test file size filtering."""
    
    def test_size_ok_normal_file(self):
        """Should accept file above minimum size."""
        from monitor import size_ok, MIN_SIZE
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Write more than MIN_SIZE bytes (config has 64KB minimum)
            f.write(b"x" * (MIN_SIZE + 1000))
            temp_path = f.name
        
        try:
            result = size_ok(temp_path)
            assert result is True
        finally:
            os.unlink(temp_path)
    
    def test_size_ok_empty_file(self):
        """Should reject empty file (below minimum)."""
        from monitor import size_ok, MIN_SIZE
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            result = size_ok(temp_path)
            # Empty files (0 bytes) should be rejected if MIN_SIZE > 0
            assert result is (MIN_SIZE <= 0)
        finally:
            os.unlink(temp_path)
    
    def test_size_ok_nonexistent_file(self):
        """Should return False for nonexistent file."""
        from monitor import size_ok
        
        result = size_ok("/nonexistent/path/file.exe")
        assert result is False


class TestCacheFunctions:
    """Test local cache functionality."""
    
    def test_cache_lookup_miss(self):
        """Should return None for uncached hash."""
        from monitor import cache_lookup
        
        result = cache_lookup("nonexistent_hash_12345")
        assert result is None
    
    def test_cache_store_and_lookup(self):
        """Should store and retrieve cached verdicts."""
        from monitor import cache_store, cache_lookup
        
        test_hash = "test_cache_hash_67890"
        test_verdict = "clean"
        
        cache_store(test_hash, test_verdict)
        result = cache_lookup(test_hash)
        
        assert result == test_verdict
    
    def test_cache_store_updates_existing(self):
        """Should update existing cache entry."""
        from monitor import cache_store, cache_lookup
        
        test_hash = "update_cache_hash_11111"
        
        cache_store(test_hash, "clean")
        assert cache_lookup(test_hash) == "clean"
        
        cache_store(test_hash, "malicious")
        assert cache_lookup(test_hash) == "malicious"


class TestMalwareBazaarAPI:
    """Test MalwareBazaar API lookup."""
    
    @patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": ""}, clear=True)
    def test_mb_api_no_key(self):
        """Should return None when no API key is set."""
        from monitor import MB_API_lookup_hash
        
        # Clear the env var for this test
        with patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": "", "MALWAREBAZAAR_API_KEY": ""}, clear=False):
            # Force reload to pick up new env
            result = MB_API_lookup_hash("test_hash")
            # Without API key, should return None
            assert result is None
    
    @patch('monitor.requests.post')
    @patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": "test_key"})
    def test_mb_api_malicious_response(self, mock_post):
        """Should return 'malicious' when hash found in database."""
        from monitor import MB_API_lookup_hash
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"sha256_hash": "test"}]}
        mock_post.return_value = mock_response
        
        result = MB_API_lookup_hash("test_hash")
        
        assert result == "malicious"
    
    @patch('monitor.requests.post')
    @patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": "test_key"})
    def test_mb_api_clean_response(self, mock_post):
        """Should return 'clean' when hash not found in database."""
        from monitor import MB_API_lookup_hash
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"query_status": "hash_not_found"}
        mock_post.return_value = mock_response
        
        result = MB_API_lookup_hash("test_hash")
        
        assert result == "clean"
    
    @patch('monitor.requests.post')
    @patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": "test_key"})
    def test_mb_api_unauthorized(self, mock_post):
        """Should return None on unauthorized response."""
        from monitor import MB_API_lookup_hash
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = MB_API_lookup_hash("test_hash")
        
        assert result is None
    
    @patch('monitor.requests.post')
    @patch.dict(os.environ, {"MalwareBazaar_Auth_KEY": "test_key"})
    def test_mb_api_network_error(self, mock_post):
        """Should return None on network error."""
        from monitor import MB_API_lookup_hash
        import requests
        
        mock_post.side_effect = requests.RequestException("Network error")
        
        result = MB_API_lookup_hash("test_hash")
        
        assert result is None


class TestQuarantine:
    """Test quarantine functionality."""
    
    def test_quarantine_file(self):
        """Should move file to quarantine and create metadata."""
        from monitor import Quarantine, QUARANTINE_PATH
        
        # Create a temp file to quarantine
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as f:
            f.write(b"test malware content")
            temp_path = f.name
        
        try:
            result = Quarantine(temp_path)
            
            assert result is True
            # Original file should be moved
            assert not os.path.exists(temp_path)
            
            # Check quarantine directory for the file
            quarantine_dir = Path(QUARANTINE_PATH)
            quarantine_files = list(quarantine_dir.glob("*.exe"))
            assert len(quarantine_files) >= 1
            
            # Check metadata file exists
            meta_files = list(quarantine_dir.glob("*.meta.json"))
            assert len(meta_files) >= 1
            
        finally:
            # Cleanup
            for f in Path(QUARANTINE_PATH).glob("*.exe"):
                try:
                    os.unlink(f)
                except:
                    pass
            for f in Path(QUARANTINE_PATH).glob("*.meta.json"):
                try:
                    os.unlink(f)
                except:
                    pass
    
    def test_quarantine_nonexistent_file(self):
        """Should handle nonexistent file gracefully."""
        from monitor import Quarantine
        
        result = Quarantine("/nonexistent/path/malware.exe")
        
        assert result is False
