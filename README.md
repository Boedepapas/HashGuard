# HashGuard

Real-time malware detection system using hash-based threat intelligence

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

HashGuard is a Windows application that monitors file system activity in real-time and checks file hashes against the MalwareBazaar malware intelligence database. Suspicious files are automatically quarantined and logged for review.

## Features

- **Real-time File Monitoring** - Watches your Downloads folder (or custom path) for new files
- **MalwareBazaar Integration** - Checks file hashes against abuse.ch's malware database
- **Windows Service** - Runs in the background as a system service
- **Automatic Quarantine** - Suspicious files are moved to an isolated directory
- **GUI Frontend** - Easy-to-use interface for control and monitoring
- **Smart Caching** - SQLite-based cache prevents redundant API calls
- **Monthly Logs** - Organized scan history with detailed reports

---

## Installation

### Step 1: Download

Download the latest `HashGuard_Package.zip` from [GitHub Releases](https://github.com/Boedepapas/HashGuard/releases).

### Step 2: Extract

Extract the ZIP file to a permanent location (e.g., `C:\HashGuard` or `C:\Program Files\HashGuard`).

**Contents of HashGuard_Package:**
```
HashGuard_Package/
    HashGuardBackend.exe    # Backend service executable
    HashGuard.exe           # GUI application
    install_service.bat     # Service installer (run as Admin)
    uninstall_service.bat   # Service uninstaller (run as Admin)
    config.yaml             # Configuration file (edit this)
    .env.example            # API key template
    logs/                   # Scan logs directory
    quarantine/             # Quarantined files directory
```

### Step 3: Configure API Key (Required)

HashGuard requires a MalwareBazaar API key to check file hashes.

1. **Get a free API key:**
   - Visit [https://bazaar.abuse.ch/](https://bazaar.abuse.ch/)
   - Create a free account
   - Go to your account settings and copy your Auth Key

2. **Add the key to HashGuard:**
   - In the `HashGuard_Package` folder, rename `.env.example` to `.env`
   - Open `.env` in a text editor
   - Replace `your-api-key-here` with your actual API key:
     ```
     MALWAREBAZAAR_API_KEY=your-actual-api-key
     ```
   - Save the file

### Step 4: Install the Windows Service

The backend runs as a Windows service so it can monitor files even when the GUI is closed.

1. **Right-click** on `install_service.bat`
2. Select **"Run as administrator"**
3. You should see "Service installed successfully" and "Service started"

**Alternative (Command Prompt):**
```powershell
# Open Command Prompt as Administrator
cd C:\path\to\HashGuard_Package
.\install_service.bat
```

### Step 5: Launch the GUI

Double-click `HashGuard.exe` to open the graphical interface.

---

## Usage

### Starting and Stopping Scans

1. Open `HashGuard.exe`
2. Click **Connect** to connect to the backend service
3. Click the **Start** button (play icon) to begin monitoring
4. Click the **Stop** button to pause monitoring

### Setting the Watch Folder

By default, HashGuard monitors your Downloads folder. To change this:

1. Click **"Set Downloads Path"** in the Settings tab
2. Select the folder you want to monitor
3. The backend will automatically start watching the new folder

### Viewing Scan History

1. Go to the **Logs** tab
2. Select a month from the list
3. Click **"Open Report"** to view detailed scan results

### Managing Quarantined Files

1. Go to the **Quarantine** tab
2. View files that were flagged as suspicious
3. Select a file and click **"Delete"** to permanently remove it

---

## Configuration

Edit `config.yaml` to customize HashGuard's behavior:

```yaml
# Watch path - leave empty to use Downloads folder
watch_path: ""

# File size limits
min_size_bytes: 65536      # 64 KB minimum (skip tiny files)
max_size_bytes: 2147483648 # 2 GB maximum

# File types to scan
allowed_extensions:
  - .exe
  - .msi
  - .zip
  - .7z
  - .pdf
  - .docx
  - .js

# Paths to ignore
blocked_paths:
  - C:\Windows\Temp

# Performance tuning
worker_count: 2           # Parallel scan workers
stability_seconds: 3      # Wait for file to finish writing
debounce_ms: 500          # Ignore rapid duplicate events
worker_throttle_ms: 75    # CPU throttling between scans
```

**After editing, restart the service:**
```powershell
net stop HashGuardService
net start HashGuardService
```

---

## Service Management

### Check Service Status
```powershell
sc query HashGuardService
```

### Start/Stop Service
```powershell
net start HashGuardService
net stop HashGuardService
```

### Uninstall Service
Right-click `uninstall_service.bat` and select "Run as administrator"

Or via command line:
```powershell
.\HashGuardBackend.exe remove
```

---

## Building from Source

### Prerequisites

- Python 3.8 or higher
- Windows 10/11
- pip (Python package manager)

### Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/Boedepapas/HashGuard.git
   cd HashGuard
   ```

2. **Create virtual environments and install dependencies:**
   ```powershell
   # Backend
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ..\frontend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   
   # PyInstaller (for building)
   pip install pyinstaller
   ```

3. **Build the executables:**
   ```powershell
   cd ..
   .\build_all.bat
   ```

4. **Output location:**
   ```
   dist\HashGuard_Package\
   ```

### Running Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

---

## Troubleshooting

### "Service failed to start"

- Ensure you ran `install_service.bat` as Administrator
- Check Windows Event Viewer > Application logs for errors
- Verify `config.yaml` has valid syntax

### "Cannot connect to backend"

- Check if service is running: `sc query HashGuardService`
- Try restarting the service: `net stop HashGuardService` then `net start HashGuardService`
- Make sure port 54321 isn't blocked by firewall

### "No files being detected"

- Verify the watch path is set correctly in Settings
- Check that the file extension is in `allowed_extensions` in `config.yaml`
- Files under 64KB are skipped by default (adjust `min_size_bytes`)

### "API returns no results"

- Verify your `.env` file contains a valid API key
- Check your internet connection
- MalwareBazaar only returns results for known malware hashes

### High CPU usage

- Reduce `worker_count` to 1 in `config.yaml`
- Increase `worker_throttle_ms` (e.g., to 150)
- Add frequently-changing folders to `blocked_paths`

---

## Project Structure

```
HashGuard/
├── backend/
│   ├── main.py                 # Backend entry point
│   ├── hashguard_service.py    # Windows service wrapper
│   ├── monitor.py              # File monitoring and API calls
│   ├── ipc.py                  # Frontend-backend communication
│   ├── database.py             # SQLite scan log storage
│   ├── service_manager.py      # Service management utilities
│   ├── backend_helper.py       # Auto-start helper for frontend
│   ├── config.yaml             # Configuration
│   ├── requirements.txt        # Python dependencies
│   └── tests/                  # Unit tests
│
├── frontend/
│   ├── hashguardFrontendv5.py  # GUI application
│   ├── graphics/               # Icons and images
│   └── requirements.txt        # Python dependencies
│
├── backend_service.spec        # PyInstaller build spec (backend)
├── frontend_gui.spec           # PyInstaller build spec (frontend)
├── build_all.bat               # Build script
├── pytest.ini                  # Test configuration
├── LICENSE
└── README.md
```

---

## How It Works

1. **File Detection** - Watchdog monitors the watch folder for new/modified files
2. **Filtering** - Files are checked against extension whitelist and size limits
3. **Hashing** - SHA-256 hash is computed for each file
4. **Cache Check** - Database is checked for previous scan results
5. **API Query** - Hash is sent to MalwareBazaar API
6. **Verdict** - File is marked as CLEAN, MALICIOUS, or UNKNOWN
7. **Action** - Malicious files are moved to quarantine
8. **Logging** - Result is saved to database and shown in GUI

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MalwareBazaar](https://bazaar.abuse.ch/) by abuse.ch for malware hash intelligence
- [Watchdog](https://github.com/gorakhargosh/watchdog) for file system monitoring
- [PySimpleGUI](https://www.pysimplegui.org/) for the GUI framework
- [pywin32](https://github.com/mhammond/pywin32) for Windows service support

---

**HashGuard** - A cybersecurity education project
