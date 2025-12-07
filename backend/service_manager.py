"""
Windows service management for HashGuard backend.
Handles service installation, starting, stopping, and checking status.
"""

import subprocess
import time
import socket
from typing import Tuple


def is_service_installed() -> bool:
    """Check if HashGuardService is installed."""
    try:
        result = subprocess.run(
            ["sc", "query", "HashGuardService"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[ServiceManager] Error checking service: {e}")
        return False


def is_service_running() -> bool:
    """Check if HashGuardService is currently running."""
    try:
        result = subprocess.run(
            ["sc", "query", "HashGuardService"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return False
        return "RUNNING" in result.stdout
    except Exception as e:
        print(f"[ServiceManager] Error checking service status: {e}")
        return False


def is_backend_reachable() -> bool:
    """Check if backend IPC server is reachable on localhost:54321"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 54321))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"[ServiceManager] Error connecting to backend: {e}")
        return False


def install_service(service_script_path: str) -> Tuple[bool, str]:
    """
    Install HashGuardService.
    
    Args:
        service_script_path: Path to hashguard_service.py
    
    Returns:
        (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [service_script_path, "install"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Service installed successfully"
        else:
            return False, f"Installation failed: {result.stderr}"
    except Exception as e:
        return False, f"Error installing service: {str(e)}"


def start_service() -> Tuple[bool, str]:
    """
    Start HashGuardService.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            ["net", "start", "HashGuardService"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Wait for service to actually start and be reachable
            for attempt in range(5):
                time.sleep(1)
                if is_backend_reachable():
                    return True, "Service started successfully"
            return True, "Service started (waiting for backend)"
        else:
            return False, f"Failed to start: {result.stderr}"
    except Exception as e:
        return False, f"Error starting service: {str(e)}"


def stop_service() -> Tuple[bool, str]:
    """
    Stop HashGuardService.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            ["net", "stop", "HashGuardService"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Service stopped successfully"
        else:
            return False, f"Failed to stop: {result.stderr}"
    except Exception as e:
        return False, f"Error stopping service: {str(e)}"


def get_service_status() -> str:
    """
    Get current service status.
    
    Returns:
        Status string: "running", "stopped", "not_installed", or "unknown"
    """
    if not is_service_installed():
        return "not_installed"
    
    if is_service_running():
        return "running"
    
    return "stopped"


def ensure_service_running() -> Tuple[bool, str]:
    """
    Ensure HashGuardService is running.
    Will install and/or start the service as needed.
    
    Returns:
        (success: bool, message: str)
    """
    # Check if backend is already reachable
    if is_backend_reachable():
        return True, "Backend already running"
    
    # Check if service is installed
    if not is_service_installed():
        print("[ServiceManager] Service not installed, installing...")
        # Try to install - this may fail if not admin
        success, msg = install_service("hashguard_service.py")
        if not success:
            return False, f"Failed to install service: {msg}"
    
    # Check if service is running
    if not is_service_running():
        print("[ServiceManager] Service not running, starting...")
        success, msg = start_service()
        if not success:
            return False, f"Failed to start service: {msg}"
    
    # Give it a moment to start up
    time.sleep(2)
    
    # Check if backend is reachable now
    if is_backend_reachable():
        return True, "Service started and backend is reachable"
    
    return False, "Service started but backend not reachable"
