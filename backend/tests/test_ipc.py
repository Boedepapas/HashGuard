"""
Tests for HashGuard IPC module.
Tests basic IPC functionality without conflicting with running service.
"""
import pytest
import socket
import json
import threading
import time
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipc import IPCServer, IPCClient, LOCALHOST, IPC_PORT


class TestIPCServerBasics:
    """Test IPC server basic functionality."""
    
    def test_server_initializes(self):
        """Server should initialize without errors."""
        server = IPCServer()
        
        assert server.running is False
        assert server.command_handler is None
    
    def test_server_with_handler(self):
        """Server should accept a command handler."""
        def handler(cmd):
            return {"status": "ok"}
        
        server = IPCServer(command_handler=handler)
        
        assert server.command_handler == handler
    
    def test_server_start_stop_flags(self):
        """Server should set running flag correctly."""
        server = IPCServer()
        
        assert server.running is False
        
        server.running = True  # Simulate start
        assert server.running is True
        
        server.running = False  # Simulate stop
        assert server.running is False


class TestIPCClientBasics:
    """Test IPC client basic functionality."""
    
    def test_client_initializes(self):
        """Client should initialize with default settings."""
        client = IPCClient()
        
        assert client.host == LOCALHOST
        assert client.port == IPC_PORT
        assert client.socket is None
    
    def test_client_custom_settings(self):
        """Client should accept custom host and port."""
        client = IPCClient(host="192.168.1.1", port=12345)
        
        assert client.host == "192.168.1.1"
        assert client.port == 12345
    
    def test_client_handles_no_server(self):
        """Client should handle connection failure gracefully."""
        client = IPCClient(port=54399)  # Unused port
        
        result = client.connect()
        
        assert result is False
    
    def test_client_send_without_connection(self):
        """Client should return None when sending without connection."""
        client = IPCClient()
        
        result = client.send_command({"type": "test"})
        
        assert result is None
    
    def test_client_close_without_connection(self):
        """Client should handle close without connection."""
        client = IPCClient()
        
        # Should not raise exception
        client.close()


class TestIPCProtocol:
    """Test IPC protocol details."""
    
    def test_json_message_format(self):
        """Messages should be valid JSON."""
        test_cmd = {"type": "test", "data": {"nested": "value"}}
        encoded = json.dumps(test_cmd).encode('utf-8')
        decoded = json.loads(encoded.decode('utf-8'))
        
        assert decoded == test_cmd
    
    def test_unicode_in_messages(self):
        """Should handle unicode characters in messages."""
        test_cmd = {"type": "test", "data": "test\u00e9\u00e0\u00f1"}
        encoded = json.dumps(test_cmd).encode('utf-8')
        decoded = json.loads(encoded.decode('utf-8'))
        
        assert decoded["data"] == "test\u00e9\u00e0\u00f1"
    
    def test_large_message(self):
        """Should handle large messages."""
        large_data = "x" * 10000
        test_cmd = {"type": "test", "data": large_data}
        encoded = json.dumps(test_cmd).encode('utf-8')
        decoded = json.loads(encoded.decode('utf-8'))
        
        assert decoded["data"] == large_data
    
    def test_command_types(self):
        """Valid command types should be serializable."""
        command_types = [
            {"type": "start_scan"},
            {"type": "stop_scan"},
            {"type": "get_status"},
            {"type": "set_watch_path", "path": "/some/path"},
            {"type": "get_monthly_reports"},
            {"type": "get_monthly_report", "month": "12-2025"},
        ]
        
        for cmd in command_types:
            encoded = json.dumps(cmd).encode('utf-8')
            decoded = json.loads(encoded.decode('utf-8'))
            assert decoded == cmd


class TestIPCIntegration:
    """Integration tests that test against actual running service."""
    
    @pytest.fixture
    def running_service(self):
        """Check if service is running and skip if not."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((LOCALHOST, IPC_PORT))
            if result != 0:
                pytest.skip("HashGuard service not running")
        finally:
            sock.close()
        yield
    
    def test_connect_to_service(self, running_service):
        """Should connect to running HashGuard service."""
        client = IPCClient()
        
        result = client.connect()
        
        assert result is True
        client.close()
    
    def test_get_status_from_service(self, running_service):
        """Should get status from running service."""
        client = IPCClient()
        client.connect()
        
        response = client.send_command({"type": "get_status"})
        
        assert response is not None
        assert "status" in response
        
        client.close()
