# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for HashGuard Backend Service
Creates HashGuardBackend.exe that can run as Windows service
"""
import os

block_cipher = None

# Backend data files
backend_datas = [
    ('backend/config.yaml', 'backend'),
    ('.env.example', '.') if os.path.exists('.env.example') else None,
]
backend_datas = [d for d in backend_datas if d is not None]

# Hidden imports for backend
backend_hiddenimports = [
    # Windows Service
    'win32serviceutil',
    'win32service',
    'win32event',
    'servicemanager',
    'win32timezone',
    'win32file',
    'win32con',
    'win32api',
    'pywintypes',
    # Watchdog
    'watchdog.observers',
    'watchdog.observers.winapi',
    'watchdog.observers.read_directory_changes',
    'watchdog.events',
    # Standard library
    'yaml',
    'dotenv',
    'sqlite3',
    'requests',
    'queue',
    'threading',
    'json',
    'hashlib',
    'shutil',
    're',
    'dataclasses',
    'concurrent.futures',
]

a = Analysis(
    ['backend/hashguard_service.py'],
    pathex=['backend'],
    binaries=[],
    datas=backend_datas,
    hiddenimports=backend_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['service_runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HashGuardBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for service
    disable_windowing_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/graphics/app_icon.ico',
)
