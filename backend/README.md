# HashGuard Backend

A real-time file monitoring and threat detection service for Windows. Scans downloads and other directories using multiple threat intelligence APIs.

## Features

✅ **Real-time file monitoring** - Watches folders for new/modified files
✅ **Multi-API threat detection** - Uses MalwareBazaar, VirusTotal, and free fallback APIs
✅ **Hybrid approach** - Works with or without API keys
✅ **Automatic quarantine** - Isolates detected threats
✅ **Logging** - Detailed scan results in `~/HashGuardDemo/logs/`
✅ **IPC communication** - Integrates with frontend via socket IPC
✅ **Scan control** - Start/stop/pause/resume from frontend
✅ **Thread-safe** - Handles concurrent file processing

## Architecture

```
main.py
  ├─ BackendController: Manages scan state and IPC commands
  ├─ IPCServer: Handles frontend communication
  ├─ Observer: Filesystem event monitoring (watchdog)
  ├─ FilterHandler: Debounces and filters filesystem events
  ├─ stability_worker_loop: Ensures files are fully written
  └─ ThreadPoolExecutor: Parallel hash computation and API queries

monitor.py
  ├─ MB_API_lookup_hash(): MalwareBazaar queries
  ├─ VT_API_lookup_hash(): VirusTotal queries
  ├─ CP_API_lookup_hash(): Custom API placeholder
  ├─ free_API_lookup_hash(): Free fallback
  ├─ cache_*(): Local SQLite caching
  └─ Quarantine(): Moves suspicious files to ~/HashGuardDemo/quarantine/

logger.py
  ├─ write_scan_log(): Records scan results
  ├─ write_quarantine_log(): Records quarantine events
  └─ write_event_log(): Records backend events

ipc.py
  ├─ IPCServer: Listens on 127.0.0.1:54321
  └─ IPCClient: For frontend to send commands
```

## Getting Started

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

Edit `.env` with your API keys (optional):
```
MALWAREBAZAAR_API_KEY=your-key-here
VIRUSTOTAL_API_KEY=your-key-here
```

### 3. Run the Backend

#### As Windows Service (Recommended for Production)
```powershell
# Install service (one-time, requires admin)
python hashguard_service.py install

# Start the service
net start HashGuardService

# Stop the service
net stop HashGuardService
```

#### Standalone (Development)
```powershell
python main.py
```

You should see:
```
[IPC] Server started on 127.0.0.1:54321
```

The frontend will automatically start the service if needed.

## IPC Protocol

The backend listens on port **54321** for JSON commands from the frontend.

### Commands

#### Start Scanning
```json
{"type": "start_scan"}
```
Response: `{"status": "ok", "message": "Scan started"}`

#### Stop Scanning
```json
{"type": "stop_scan"}
```
Response: `{"status": "ok", "message": "Scan stopped"}`

#### Pause Scanning
```json
{"type": "pause_scan"}
```
Response: `{"status": "ok", "message": "Scan paused"}`

#### Resume Scanning
```json
{"type": "resume_scan"}
```
Response: `{"status": "ok", "message": "Scan resumed"}`

#### Set Watch Path
```json
{"type": "set_watch_path", "path": "C:\\Downloads"}
```
Response: `{"status": "ok", "message": "Watch path changed to C:\\Downloads"}`

#### Get Status
```json
{"type": "get_status"}
```
Response:
```json
{
  "status": "ok",
  "scanning": true,
  "paused": false,
  "watch_path": "./downloads"
}
```

## Verdict Logic

When a file is scanned:

1. **Check cache** - If hash was recently analyzed, use cached verdict
2. **Query APIs** (in order):
   - MalwareBazaar (if API key configured)
   - VirusTotal (if API key configured)
   - Custom API (placeholder)
   - Free Fallback (always available)
3. **Combine verdicts**:
   - If ANY API says "malicious" → quarantine the file
   - If all say "clean" → allow the file
   - If no APIs respond → treat as "clean" (safe default)
4. **Cache result** - Store verdict for faster future lookups

## File Paths

- **Watch directory**: Configured in `config.yaml` (default: `./downloads`)
- **Quarantine**: `~/HashGuardDemo/quarantine/`
- **Logs**: `~/HashGuardDemo/logs/`
- **Cache DB**: `./cache.sqlite`
- **Config**: `config.yaml`

## Log Files

Scan results are written to `~/HashGuardDemo/logs/` as JSON files:

```json
{
  "timestamp": 1733446234.5678,
  "iso_time": "2024-12-05T10:30:34.567",
  "filename": "suspicious.exe",
  "verdict": "malicious",
  "hash": "abc123...",
  "path": "C:\\Downloads\\suspicious.exe",
  "sources": ["MalwareBazaar"],
  "error": null
}
```

## Configuration

Edit `config.yaml`:

```yaml
watch_path: ./downloads              # Directory to monitor
quarantine_path: ./quarantine        # Quarantine directory
allowed_extensions: [.exe, .zip]     # Only scan these types
stability_seconds: 3                 # Wait before scanning (let file finish writing)
debounce_ms: 500                     # Event debounce interval
worker_count: 4                      # Parallel scan threads
cache_db: ./cache.sqlite             # Cache database path
```

## API Keys

### MalwareBazaar
1. Visit https://malwarebazaar.abuse.ch/
2. Sign up for free account
3. Copy API key from dashboard
4. Add to `.env`:
   ```
   MALWAREBAZAAR_API_KEY=your-key
   ```

### VirusTotal
1. Visit https://www.virustotal.com/
2. Sign up for free account (higher quota than free tier)
3. Go to Settings → API Key
4. Add to `.env`:
   ```
   VIRUSTOTAL_API_KEY=your-key
   ```

## Environment Variables

All optional - backend works without any configured:

```powershell
$env:MALWAREBAZAAR_API_KEY = "your-key"
$env:VIRUSTOTAL_API_KEY = "your-key"
```

Or create `.env` file (recommended).

## Troubleshooting

### "No APIs available, defaulting to clean"
All configured APIs are returning errors. Check:
- Internet connection
- API endpoint status
- Rate limiting (if you've scanned many files)

### Port 54321 already in use
Another instance of HashGuard is running, or another application is using the port.

### Quarantine permission denied
The file may be locked by another process. Windows will retry when the file is released.

## Development

### Adding a New API

1. Create function in `monitor.py`:
```python
def MY_API_lookup_hash(hash_hex: str) -> Optional[str]:
    api_key = os.getenv("MY_API_KEY")
    if not api_key:
        return None  # Not configured
    # ... query API ...
    return "malicious" or "clean" or None
```

2. Add to `worker_process_item()`:
```python
my_verdict = MY_API_lookup_hash(hash_hex)
if my_verdict:
    verdicts.append(my_verdict)
```

3. Update `config.yaml` and `.env.example` with documentation.

## Performance

- **Memory**: ~50MB baseline + cache size
- **CPU**: Minimal when idle, ~20% per scan worker when active
- **Disk I/O**: Depends on file sizes and scan frequency
- **Network**: Only when querying APIs (minimal bandwidth)

## Security Considerations

- API keys should never be in source code
- Use `.env` file (local, not version controlled)
- Files are moved (not copied) to quarantine
- Quarantine files are set to read-only (0o600)
- All operations logged with timestamps
- IPC uses localhost only (127.0.0.1:54321)

## License

[Add your license here]

## Support

For issues or questions, see: https://github.com/Boedepapas/HashGuard
