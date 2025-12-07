"""
Tests for HashGuard service manager module.
"""
import pytest
import socket
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from service_manager import (
    is_service_installed,
    is_service_running,
    is_backend_reachable,
    get_service_status,
)


class TestServiceStatus:
    """Test service status checking."""
    
    @patch('service_manager.subprocess.run')
    def test_is_service_installed_true(self, mock_run):
        """Should return True when service is installed."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = is_service_installed()
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('service_manager.subprocess.run')
    def test_is_service_installed_false(self, mock_run):
        """Should return False when service is not installed."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        
        result = is_service_installed()
        
        assert result is False
    
    @patch('service_manager.subprocess.run')
    def test_is_service_running_true(self, mock_run):
        """Should return True when service is running."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SERVICE_NAME: HashGuardService\nSTATE: 4  RUNNING",
            stderr=""
        )
        
        result = is_service_running()
        
        assert result is True
    
    @patch('service_manager.subprocess.run')
    def test_is_service_running_false_stopped(self, mock_run):
        """Should return False when service is stopped."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SERVICE_NAME: HashGuardService\nSTATE: 1  STOPPED",
            stderr=""
        )
        
        result = is_service_running()
        
        assert result is False
    
    @patch('service_manager.subprocess.run')
    def test_is_service_running_false_not_installed(self, mock_run):
        """Should return False when service is not installed."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        
        result = is_service_running()
        
        assert result is False


class TestBackendReachability:
    """Test backend reachability checking."""
    
    @patch('service_manager.socket.socket')
    def test_is_backend_reachable_true(self, mock_socket_class):
        """Should return True when backend is reachable."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        result = is_backend_reachable()
        
        assert result is True
        mock_socket.connect_ex.assert_called_once_with(("127.0.0.1", 54321))
        mock_socket.close.assert_called_once()
    
    @patch('service_manager.socket.socket')
    def test_is_backend_reachable_false(self, mock_socket_class):
        """Should return False when backend is not reachable."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 10061  # Connection refused
        mock_socket_class.return_value = mock_socket
        
        result = is_backend_reachable()
        
        assert result is False
    
    @patch('service_manager.socket.socket')
    def test_is_backend_reachable_exception(self, mock_socket_class):
        """Should return False on socket exception."""
        mock_socket_class.side_effect = socket.error("Connection failed")
        
        result = is_backend_reachable()
        
        assert result is False


class TestGetServiceStatus:
    """Test get_service_status function."""
    
    @patch('service_manager.is_service_installed')
    @patch('service_manager.is_service_running')
    def test_status_running(self, mock_running, mock_installed):
        """Should return 'running' when service is running."""
        mock_installed.return_value = True
        mock_running.return_value = True
        
        result = get_service_status()
        
        assert result == "running"
    
    @patch('service_manager.is_service_installed')
    @patch('service_manager.is_service_running')
    def test_status_stopped(self, mock_running, mock_installed):
        """Should return 'stopped' when service is installed but not running."""
        mock_installed.return_value = True
        mock_running.return_value = False
        
        result = get_service_status()
        
        assert result == "stopped"
    
    @patch('service_manager.is_service_installed')
    def test_status_not_installed(self, mock_installed):
        """Should return 'not_installed' when service is not installed."""
        mock_installed.return_value = False
        
        result = get_service_status()
        
        assert result == "not_installed"
