"""
Tests for HashGuard backend helper module.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend_helper import (
    get_backend_path,
    ensure_backend_running,
    check_backend_status,
)


class TestGetBackendPath:
    """Test backend path detection."""
    
    def test_get_backend_path_returns_path(self):
        """Should return a Path object."""
        result = get_backend_path()
        
        assert isinstance(result, Path)
    
    def test_get_backend_path_finds_backend(self):
        """Should find the backend directory."""
        result = get_backend_path()
        
        # The backend_helper.py is in backend/, so it should find it
        assert result.name == "backend" or result.exists()


class TestEnsureBackendRunning:
    """Test ensure_backend_running function."""
    
    @patch('service_manager.is_backend_reachable')
    def test_already_running(self, mock_reachable):
        """Should return True if backend already reachable."""
        mock_reachable.return_value = True
        
        result = ensure_backend_running(verbose=False)
        
        assert result is True
    
    @patch('service_manager.is_backend_reachable')
    @patch('service_manager.ensure_service_running')
    def test_starts_service(self, mock_ensure, mock_reachable):
        """Should try to start service if not reachable."""
        mock_reachable.return_value = False
        mock_ensure.return_value = (True, "Service started")
        
        result = ensure_backend_running(verbose=False)
        
        # Should have tried to ensure service is running
        mock_ensure.assert_called_once()
    
    @patch('service_manager.is_backend_reachable')
    @patch('service_manager.ensure_service_running')
    def test_returns_false_on_failure(self, mock_ensure, mock_reachable):
        """Should return False if service fails to start."""
        mock_reachable.return_value = False
        mock_ensure.return_value = (False, "Failed to start")
        
        result = ensure_backend_running(verbose=False)
        
        assert result is False


class TestCheckBackendStatus:
    """Test check_backend_status function."""
    
    @patch('service_manager.is_backend_reachable')
    @patch('service_manager.is_service_installed')
    @patch('service_manager.is_service_running')
    def test_status_reachable(self, mock_running, mock_installed, mock_reachable):
        """Should return correct status when backend is reachable."""
        mock_reachable.return_value = True
        mock_installed.return_value = True
        mock_running.return_value = True
        
        result = check_backend_status()
        
        assert result["reachable"] is True
        assert result["status"] == "Backend is running"
    
    @patch('service_manager.is_backend_reachable')
    @patch('service_manager.is_service_installed')
    @patch('service_manager.is_service_running')
    def test_status_not_installed(self, mock_running, mock_installed, mock_reachable):
        """Should return correct status when service not installed."""
        mock_reachable.return_value = False
        mock_installed.return_value = False
        mock_running.return_value = False
        
        result = check_backend_status()
        
        assert result["reachable"] is False
        assert result["service_installed"] is False
        assert result["status"] == "Service not installed"
    
    @patch('service_manager.is_backend_reachable')
    @patch('service_manager.is_service_installed')
    @patch('service_manager.is_service_running')
    def test_status_service_running_not_responding(self, mock_running, mock_installed, mock_reachable):
        """Should detect when service is running but not responding."""
        mock_reachable.return_value = False
        mock_installed.return_value = True
        mock_running.return_value = True
        
        result = check_backend_status()
        
        assert result["reachable"] is False
        assert result["service_running"] is True
        assert "not responding" in result["status"]
