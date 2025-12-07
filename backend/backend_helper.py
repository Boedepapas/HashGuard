"""
HashGuard Backend Connection Helper for Frontend

Import this in your frontend to automatically manage the backend service.

Example usage:
    from backend_helper import ensure_backend_running, connect_to_backend
    
    # Ensure backend is running
    success = ensure_backend_running()
    if not success:
        show_error_dialog("Backend failed to start")
    
    # Connect to backend
    from ipc import IPCClient
    client = IPCClient()
    if client.connect():
        client.send_command({"type": "start_scan"})
"""

import sys
import os
from pathlib import Path
import subprocess
import time


def get_backend_path() -> Path:
    """Get path to backend directory."""
    # If backend_helper.py is in the backend directory, return parent dir
    backend_helper_dir = Path(__file__).parent
    if backend_helper_dir.name == "backend":
        return backend_helper_dir
    
    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent / "backend",  # Same directory as this file
        Path("C:/Program Files/HashGuard/backend"),
        Path("C:/Program Files (x86)/HashGuard/backend"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Default to relative path
    return Path(__file__).parent / "backend"


def ensure_backend_running(backend_path: Path = None, verbose: bool = False) -> bool:
    """
    Ensure HashGuard backend service is running.
    
    Args:
        backend_path: Path to backend directory (auto-detected if None)
        verbose: Print status messages
    
    Returns:
        True if backend is running, False otherwise
    """
    # Try direct import first (works when bundled with PyInstaller)
    try:
        from service_manager import (
            is_backend_reachable,
            is_service_running,
            is_service_installed,
            ensure_service_running
        )
        if verbose:
            print("[BackendHelper] Using bundled service_manager")
    except ImportError:
        # Fall back to dynamic path import (for development)
        if backend_path is None:
            backend_path = get_backend_path()
        
        if not backend_path.exists():
            if verbose:
                print(f"[BackendHelper] Backend path not found: {backend_path}")
            return False
        
        # Add backend to path so we can import service_manager
        sys.path.insert(0, str(backend_path))
        
        try:
            from service_manager import (
                is_backend_reachable,
                is_service_running,
                is_service_installed,
                ensure_service_running
            )
            if verbose:
                print(f"[BackendHelper] Using service_manager from: {backend_path}")
        except ImportError as e:
            if verbose:
                print(f"[BackendHelper] Failed to import service_manager: {e}")
            return False
    
    try:
        # Quick check if already reachable
        if is_backend_reachable():
            if verbose:
                print("[BackendHelper] Backend already reachable")
            return True
        
        if verbose:
            print("[BackendHelper] Backend not reachable, checking service...")
        
        # Try to ensure service is running
        success, message = ensure_service_running()
        
        if verbose:
            print(f"[BackendHelper] {message}")
        
        return success
        
    except Exception as e:
        if verbose:
            print(f"[BackendHelper] Error: {e}")
        return False


def check_backend_status(backend_path: Path = None) -> dict:
    """
    Check current backend status.
    
    Args:
        backend_path: Path to backend directory (auto-detected if None)
    
    Returns:
        Dict with keys:
        - reachable: bool - Is backend IPC reachable
        - service_installed: bool - Is service installed
        - service_running: bool - Is service running
        - status: str - Human readable status
    """
    # Try direct import first (works when bundled with PyInstaller)
    try:
        from service_manager import (
            is_backend_reachable,
            is_service_running,
            is_service_installed
        )
    except ImportError:
        # Fall back to dynamic path import
        if backend_path is None:
            backend_path = get_backend_path()
        
        sys.path.insert(0, str(backend_path))
        
        try:
            from service_manager import (
                is_backend_reachable,
                is_service_running,
                is_service_installed
            )
        except ImportError:
            return {
                "reachable": False,
                "service_installed": False,
                "service_running": False,
                "status": "Error: Could not import service_manager",
            }
    
    try:
        reachable = is_backend_reachable()
        installed = is_service_installed()
        running = is_service_running()
        
        if reachable:
            status = "Backend is running"
        elif running:
            status = "Service running but backend not responding"
        elif installed:
            status = "Service installed but not running"
        else:
            status = "Service not installed"
        
        return {
            "reachable": reachable,
            "service_installed": installed,
            "service_running": running,
            "status": status,
        }
    except Exception as e:
        return {
            "reachable": False,
            "service_installed": False,
            "service_running": False,
            "status": f"Error checking status: {e}",
        }


def install_backend_service(backend_path: Path = None, verbose: bool = False) -> bool:
    """
    Install HashGuard backend as a Windows service.
    Requires administrator privileges.
    
    Args:
        backend_path: Path to backend directory (auto-detected if None)
        verbose: Print status messages
    
    Returns:
        True if installation successful, False otherwise
    """
    # Try direct import first (works when bundled with PyInstaller)
    try:
        from service_manager import install_service
    except ImportError:
        if backend_path is None:
            backend_path = get_backend_path()
        
        sys.path.insert(0, str(backend_path))
        
        try:
            from service_manager import install_service
        except ImportError as e:
            if verbose:
                print(f"[BackendHelper] Could not import service_manager: {e}")
            return False
    
    try:
        if backend_path is None:
            backend_path = get_backend_path()
            
        service_script = backend_path / "hashguard_service.py"
        success, message = install_service(str(service_script))
        
        if verbose:
            print(f"[BackendHelper] {message}")
        
        return success
    except Exception as e:
        if verbose:
            print(f"[BackendHelper] Error installing: {e}")
        return False
