# HashGuard Backend - Quick Reference

## Start the Backend
```powershell
cd C:\Users\jaket\Dev\SchoolProjects\HashGuard\backend
python main.py
```

Expected output:
```
[IPC] Server started on 127.0.0.1:54321
```

## Configure API Keys
```powershell
# Copy template
Copy-Item .env.example .env

# Edit .env and add your keys
notepad .env
```

Without API keys, external lookups are unavailable and unknown files are quarantined by default.

## Main Directories
| Path | Purpose |
|------|---------|
| `./downloads` | Watch directory (configurable) |
| `./quarantine/` | Quarantined files |
| `./logs/` | Scan results (JSON + monthly text) |
| `./cache.sqlite` | Hash verdict cache |

## IPC Commands
```python
# Import client
from ipc import IPCClient
client = IPCClient()
client.connect()

# Start/Stop scanning
client.send_command({"type": "start_scan"})
client.send_command({"type": "stop_scan"})

# Pause/Resume
client.send_command({"type": "pause_scan"})
client.send_command({"type": "resume_scan"})

# Set watch path
client.send_command({"type": "set_watch_path", "path": "C:\\Downloads"})

# Get status
status = client.send_command({"type": "get_status"})
```

## Verdict Logic
```
Query APIs → If ANY malicious → QUARANTINE
            → If all clean → ALLOW
            → If unknown/no response → QUARANTINE
```

## File Structure
```
backend/
├── main.py              ← Start here
├── monitor.py           ← File watching & scanning
├── ipc.py              ← Frontend communication
├── logger.py           ← Logging to ~/HashGuardDemo/logs/
├── config.yaml         ← Configuration
├── .env                ← API keys (user's local)
├── requirements.txt    ← Dependencies
├── README.md           ← Full documentation
├── SETUP.md            ← Setup guide
└── FRONTEND_INTEGRATION.md ← For frontend devs
```

## Key Files
| File | What It Does |
|------|-------------|
| `main.py` | Backend entry point, scan control |
| `monitor.py` | File monitoring, hashing, API calls |
| `ipc.py` | Socket IPC for frontend commands |
| `logger.py` | Write results to JSON logs |
| `config.yaml` | Scan settings (extensions, paths, etc) |
| `.env` | Secret API keys |

## API Keys

### MalwareBazaar
```
Sign up: https://malwarebazaar.abuse.ch/
Add to .env: MALWAREBAZAAR_API_KEY=your-key
```

### VirusTotal
```
Sign up: https://www.virustotal.com/
Add to .env: VIRUSTOTAL_API_KEY=your-key
```

### ThreatFox (optional)
```
Sign up: https://threatfox.abuse.ch/
Add to .env: THREATFOX_API_KEY=your-key
```

## Config Settings
```yaml
watch_path: ./downloads              # Directory to monitor
quarantine_path: ./quarantine        # Where to isolate files
allowed_extensions: [.exe, .zip]     # File types to scan
stability_seconds: 3                 # Wait before scanning
debounce_ms: 500                     # Event debounce
worker_count: 4                      # Parallel workers
```

## Logging
Scan results saved as JSON in `~/HashGuardDemo/logs/`:
```json
{
  "timestamp": 1733446234.5678,
  "filename": "file.exe",
  "verdict": "malicious",
  "hash": "sha256hex...",
  "sources": ["MalwareBazaar"],
  "path": "C:\\Downloads\\file.exe"
}
```

## Troubleshooting

### Backend won't start
```powershell
# Check dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Need 3.7+
```

### Port 54321 in use
```powershell
# Find what's using the port
netstat -ano | findstr 54321

# Kill the process
taskkill /PID <pid> /F
```

### No API results
```
Check:
1. Internet connection
2. API key configured (.env file)
3. API endpoint status
4. Check backend logs
```

## Documentation
- **Full docs**: `README.md`
- **Setup**: `SETUP.md`
- **Frontend integration**: `FRONTEND_INTEGRATION.md`
- **What changed**: `IMPLEMENTATION_SUMMARY.md`
- **Deployment checklist**: `CHECKLIST.md`

## Status
✅ Backend ready for integration
✅ IPC server listening on 127.0.0.1:54321
✅ API keys required (no anonymous fallback)
✅ All logging implemented
✅ Frontend integration guide complete

## Next: Frontend Integration
1. Update frontend to use `IPCClient` from `ipc.py`
2. Replace `MockBackend` with real backend calls
3. Connect start/stop buttons to IPC commands
4. Read logs from `~/HashGuardDemo/logs/`
5. Test full integration

See `FRONTEND_INTEGRATION.md` for code examples.
