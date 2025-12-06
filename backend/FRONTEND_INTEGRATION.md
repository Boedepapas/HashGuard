# Frontend-Backend Integration Guide

## Overview

The backend now runs as a Windows service (`HashGuardService`) separate from the frontend. The frontend can automatically start the service if it's not already running, then communicate via Socket IPC.

## Quick Start - Minimal Changes Needed

### Step 1: Import Backend Helper

Add this to your frontend code:

```python
import sys
sys.path.insert(0, r"C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend")

from backend_helper import ensure_backend_running
from ipc import IPCClient
```

### Step 2: Start Backend on App Launch

In your app's `main()` function or window initialization:

```python
# Before creating your GUI, ensure backend is running
if not ensure_backend_running(verbose=True):
    sg.popup_error(
        "Backend Error",
        "Failed to start HashGuard backend service.\n\n"
        "Please run as Administrator and try again."
    )
    return
```

### Step 3: Replace MockBackend with Real Backend

Replace your current `MockBackend` class with this real implementation:

```python
class HashGuardBackend:
    """Real backend implementation using IPC."""
    
    def __init__(self, window):
        self.window = window
        self.client = IPCClient()
        self.running = False
        self.connected = False
        
        # Try to connect
        if not self.client.connect():
            print("[Backend] Failed to connect to IPC server")
            return
        self.connected = True
    
    def start_scan(self):
        if not self.connected:
            return
        response = self.client.send_command({"type": "start_scan"})
        if response and response.get("status") == "ok":
            self.running = True
            self.window.write_event_value("-BACKEND-STATUS-", "started")
    
    def stop_scan(self):
        if not self.connected:
            return
        response = self.client.send_command({"type": "stop_scan"})
        if response and response.get("status") == "ok":
            self.running = False
            self.window.write_event_value("-BACKEND-STATUS-", "stopped")
    
    def pause_scan(self):
        if not self.connected:
            return
        self.client.send_command({"type": "pause_scan"})
        self.window.write_event_value("-BACKEND-STATUS-", "paused")
    
    def resume_scan(self):
        if not self.connected:
            return
        self.client.send_command({"type": "resume_scan"})
    
    def set_downloads_folder(self, folder_path):
        """Set the watch path."""
        if not self.connected:
            return
        response = self.client.send_command({
            "type": "set_watch_path",
            "path": folder_path
        })
        if response and response.get("status") == "ok":
            self.window.write_event_value("-BACKEND-UPDATE-", "path_changed")
    
    def delete_quarantine(self, filename):
        """Files are deleted via system commands, not backend."""
        # Frontend can delete directly from quarantine folder
        return True, ""
    
    def shutdown(self):
        if self.client:
            self.client.close()
```

Then in your main event loop:

```python
# Replace:
# backend = MockBackend(window)

# With:
backend = HashGuardBackend(window)
```

## Service Details

### Installation
The Windows service is installed during application setup:
```powershell
python hashguard_service.py install
```

### Service Information
- **Service Name**: `HashGuardService`
- **Display Name**: `HashGuard File Monitor Service`  
- **IPC Endpoint**: `127.0.0.1:54321`
- **Data Location**: `C:\Program Files\HashGuard\`

### Service Management
Frontend users don't need to do anything - the backend helper will automatically:
1. Check if service is installed
2. Start the service if not running
3. Connect the frontend

## Available IPC Commands

### start_scan
```python
client.send_command({"type": "start_scan"})
# Response: {"status": "ok", "message": "Scan started"}
```

### stop_scan
```python
client.send_command({"type": "stop_scan"})
```

### pause_scan
```python
client.send_command({"type": "pause_scan"})
```

### resume_scan
```python
client.send_command({"type": "resume_scan"})
```

### set_watch_path
```python
client.send_command({
    "type": "set_watch_path",
    "path": "C:\\Users\\Username\\Downloads"
})
```

### get_status
```python
response = client.send_command({"type": "get_status"})
# Response: {
#   "status": "ok",
#   "scanning": true/false,
#   "paused": true/false,
#   "watch_path": "C:\\..."
# }
```

## Handling Errors

### Backend not responding

```python
from backend_helper import check_backend_status

status = check_backend_status()

if not status['reachable']:
    if not status['service_running']:
        # Try to start
        if not ensure_backend_running():
            show_error("Backend Error", "Could not start backend service")
    else:
        show_error("Connection Error", "Service running but not responding")
```

### Required Administrator Privileges

The service installation requires admin rights. If your app is being run without admin:

```python
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    sg.popup_error(
        "Administrator Required",
        "HashGuard requires administrator privileges to start.\n\n"
        "Please run as Administrator."
    )
    return
```

## Reading Scan Results

Scan logs are written to: `C:\Program Files\HashGuard\logs\`

Each scan result is a JSON file:
```json
{
  "timestamp": 1733446234.5678,
  "iso_time": "2024-12-05T10:30:34.567",
  "filename": "file.exe",
  "verdict": "malicious",
  "hash": "abc123...",
  "path": "C:\\Downloads\\file.exe",
  "sources": ["MalwareBazaar"],
  "error": null
}
```

Read logs like this:

```python
from pathlib import Path
import json

logs_dir = Path("C:\\Program Files\\HashGuard\\logs")

def read_latest_logs(count=10):
    """Read the most recent log files."""
    log_files = sorted(logs_dir.glob("*.json"), reverse=True)[:count]
    results = []
    
    for log_file in log_files:
        try:
            with open(log_file) as f:
                results.append(json.load(f))
        except:
            pass
    
    return results
```

## Quarantine Files

Quarantined files are stored in: `C:\Program Files\HashGuard\quarantine\`

Each file has a `.meta.json` metadata file containing original path and timestamp.

To restore a quarantine file:
```python
from pathlib import Path
import shutil

def restore_quarantine_file(filename):
    """Restore a quarantined file to its original location."""
    quarantine_dir = Path("C:\\Program Files\\HashGuard\\quarantine")
    quarantine_file = quarantine_dir / filename
    meta_file = quarantine_file.with_suffix(quarantine_file.suffix + ".meta.json")
    
    if not quarantine_file.exists():
        return False, "File not found"
    
    # Read original path
    try:
        import json
        with open(meta_file) as f:
            meta = json.load(f)
        original_path = meta["original_path"]
    except:
        original_path = filename
    
    # Restore
    try:
        shutil.move(str(quarantine_file), original_path)
        meta_file.unlink()  # Delete metadata
        return True, "File restored"
    except Exception as e:
        return False, str(e)
```

## Complete Frontend Example

See your updated `hashguardFrontendv4.py` - replace the `MockBackend` class with `HashGuardBackend` and add the startup code.

The changes are minimal - just the backend initialization and class replacement!
client.send_command({"type": "resume_scan"})
```

#### Set Watch Path (for Downloads folder)
```python
client.send_command({
    "type": "set_watch_path",
    "path": "C:\\Users\\username\\Downloads"
})
```

#### Get Status
```python
status = client.send_command({"type": "get_status"})
print(status)
# {
#   "status": "ok",
#   "scanning": True,
#   "paused": False,
#   "watch_path": "./downloads"
# }
```

### 4. Close Connection
```python
client.close()
```

## Integration Points in Your Frontend

### Start/Stop Button (Graph Element)
Your current code does:
```python
if not scanning:
    backend.start_scan()
else:
    backend.stop_scan()
```

Replace with:
```python
if not scanning:
    client.send_command({"type": "start_scan"})
    # Update UI
else:
    client.send_command({"type": "stop_scan"})
    # Update UI
```

### Downloads Folder Selection
Your current code has:
```python
if event == "-DOWNLOADS-":
    folder = sg.popup_get_folder("Select Downloads Folder", no_window=True)
    if folder:
        # TODO: Tell backend to set this path
```

Replace with:
```python
if event == "-DOWNLOADS-":
    folder = sg.popup_get_folder("Select Downloads Folder", no_window=True)
    if folder:
        response = client.send_command({
            "type": "set_watch_path",
            "path": folder
        })
        if response and response.get("status") == "ok":
            window["-DLNAME-"].update(os.path.basename(folder))
            # Success!
```

### Polling for Updates
Instead of using `MockBackend`, read from the backend logs:

```python
from pathlib import Path
import json

LOGS_DIR = Path.home() / "HashGuardDemo" / "logs"

def get_latest_scan_results(count=5):
    """Get the latest N scan results."""
    if not LOGS_DIR.exists():
        return []
    
    # Get all log files, sorted by name (newest last)
    logs = sorted(LOGS_DIR.glob("*.json"))[-count:]
    
    results = []
    for log_file in logs:
        try:
            with open(log_file) as f:
                results.append(json.load(f))
        except:
            pass
    
    return results
```

## File Organization

### Backend
```
C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend\
├── main.py          <- Start the backend
├── monitor.py       <- File watching & scanning
├── ipc.py          <- Communication module
├── logger.py       <- Logging
├── config.yaml     <- Configuration
└── .env            <- API keys (user's local)
```

### Frontend
```
C:\Users\jaket\Dev\PersonalProjects\pyfrontend\
└── hashguardFrontendv4.py
```

### Shared Data
```
C:\Users\<username>\HashGuardDemo\
├── logs/           <- Scan results (read by frontend)
├── quarantine/     <- Quarantined files
└── cache.sqlite    <- Backend's file hash cache
```

## Running Both Backend and Frontend

### Terminal 1 - Backend
```powershell
cd C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend
python main.py
```

You should see:
```
[IPC] Server started on 127.0.0.1:54321
```

### Terminal 2 - Frontend
```powershell
cd C:\Users\jaket\Dev\PersonalProjects\pyfrontend
python hashguardFrontendv4.py
```

## Handling Disconnections

```python
client = IPCClient()

def send_safe_command(command):
    """Send command, reconnect if needed."""
    if not client.socket:
        if not client.connect():
            print("Backend is not running")
            return None
    
    response = client.send_command(command)
    if response is None:
        # Connection lost, try to reconnect
        client.close()
        client.connect()
    return response
```

## Example: Complete Frontend Integration

```python
import sys
sys.path.insert(0, r"C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend")
from ipc import IPCClient

class FrontendBackendBridge:
    def __init__(self):
        self.client = IPCClient()
        self.connected = False
        self.scanning = False
    
    def connect(self):
        if self.client.connect():
            self.connected = True
            return True
        return False
    
    def start_scan(self):
        if self.connect():
            response = self.client.send_command({"type": "start_scan"})
            if response and response.get("status") == "ok":
                self.scanning = True
                return True
        return False
    
    def stop_scan(self):
        if self.connected:
            response = self.client.send_command({"type": "stop_scan"})
            if response and response.get("status") == "ok":
                self.scanning = False
                return True
        return False
    
    def set_watch_path(self, path):
        if self.connected:
            return self.client.send_command({
                "type": "set_watch_path",
                "path": path
            })
        return None
    
    def get_status(self):
        if self.connected:
            return self.client.send_command({"type": "get_status"})
        return None
    
    def disconnect(self):
        self.client.close()
        self.connected = False

# Usage in your frontend code:
backend = FrontendBackendBridge()
backend.connect()

# When user clicks start button
if backend.start_scan():
    # Update UI
    set_status("scanning")
else:
    sg.popup_error("Failed to connect to backend")
```

## Troubleshooting

### "Connection refused" on port 54321
- Backend not running
- Start backend: `python main.py` in backend directory

### "No such module 'ipc'"
- Python path issue
- Add backend directory to path:
  ```python
  import sys
  sys.path.insert(0, r"C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend")
  ```

### Commands not working
- Check backend logs - is it processing files?
- Verify `config.yaml` watch path is correct
- Check `allowed_extensions` includes test file types

### Files not appearing in logs
- Backend may still be scanning (check with `get_status`)
- Verify files match `allowed_extensions`
- Wait for `stability_seconds` (default 3 seconds)

## API Reference

### Message Format
All messages are JSON objects sent as UTF-8 encoded strings.

### Request
```json
{
  "type": "command_name",
  "param1": "value1",
  "param2": "value2"
}
```

### Response
```json
{
  "status": "ok|error",
  "message": "Human readable message",
  "data": {}
}
```

## Performance Tips

1. **Don't poll too frequently** - Check status every 2-5 seconds max
2. **Use file watching** - Read `~/HashGuardDemo/logs/` for updates
3. **Batch commands** - Send multiple commands together when possible
4. **Close when done** - Always call `client.close()` when exiting

## Next Steps

1. ✅ Backend is ready
2. ⬜ Update frontend to use IPC client
3. ⬜ Replace MockBackend with real backend calls
4. ⬜ Read logs from `~/HashGuardDemo/logs/` instead of polling
5. ⬜ Test full integration
