# HashGuard Backend Setup Guide

## Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/Boedepapas/HashGuard.git
   cd HashGuard/backend
   ```

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

## Configuration

### Step 1: Copy the environment template
```powershell
Copy-Item .env.example .env
```

### Step 2: Configure API Keys (Required)

All external lookups require user-provided API keys. Without them, files without cached verdicts will be treated as unknown and quarantined.

- **MalwareBazaar** (required for MB lookups)
  1. Visit https://malwarebazaar.abuse.ch/
  2. Sign up for an account
  3. Navigate to the API section and copy your key
  4. Edit `.env`:
     ```
     MALWAREBAZAAR_API_KEY=your-actual-key-here
     ```

- **VirusTotal** (required for VT lookups)
  1. Visit https://www.virustotal.com/
  2. Sign up for an account
  3. Go to Settings → API Key and copy it
  4. Edit `.env`:
     ```
     VIRUSTOTAL_API_KEY=your-actual-key-here
     ```

- **ThreatFox** (optional)
  1. Visit https://threatfox.abuse.ch/
  2. Sign up for an account
  3. Copy the API key
  4. Edit `.env`:
     ```
     THREATFOX_API_KEY=your-actual-key-here
     ```

Add both MalwareBazaar and VirusTotal keys for best coverage. ThreatFox is additive.

### Step 3: Configure Scan Settings

Edit `config.yaml` to customize:
- `watch_path`: Directory to monitor for downloads (default: `./downloads`)
- `quarantine_path`: Where to isolate suspicious files (default: `./quarantine`)
- `allowed_extensions`: File types to scan (executables, archives, docs, etc.)
- `stability_seconds`: Wait time to ensure file is fully written before scanning
- `worker_count`: Number of parallel scan workers

## Running the Backend

### Standalone Mode
```powershell
python main.py
```

### As Windows Service
```powershell
python hashguard_service.py install
python hashguard_service.py start
```

## How API Scanning Works

### Verdict Logic:
1. **Queries configured APIs**: MalwareBazaar → VirusTotal → ThreatFox → Custom API
2. **If ANY API says malicious** → File is quarantined
3. **If all say clean** → File is allowed
4. **If unknown/no response** → File is quarantined (no anonymous fallback)
5. **Results are cached** → Same file hash checked again uses cached result

### API Priority:
| API | Requires Auth | Accuracy | Speed |
|-----|---------------|----------|-------|
| MalwareBazaar | Yes | ★★★★★ | Fast |
| VirusTotal | Yes | ★★★★★ | Medium |
| ThreatFox | Yes | ★★★★☆ | Fast |
| Custom API | Maybe | Varies | Varies |

## Important Security Notes

⚠️ **Never commit `.env` to version control!**
- `.env` is in `.gitignore` and should stay local
- Each user/machine has their own API keys
- If a key is leaked, rotate it immediately in your API provider's dashboard

## Troubleshooting

### "MALWAREBAZAAR_API_KEY environment variable not set"
- Copy `.env.example` to `.env`
- Add your actual API key (required for lookups)

### "No APIs available"
- Either no API keys configured OR
- All APIs are unreachable (network issues)
- Files without cached verdicts will be quarantined until keys are added or services recover
- Check internet connection and API status pages

### Files not being scanned
- Check `config.yaml`: `watch_path` points to correct directory
- Verify `allowed_extensions` includes the file types you want
- Check `stability_seconds`: may need to wait longer for large files

## Next Steps

See the frontend documentation to connect the backend with the HashGuard UI.
