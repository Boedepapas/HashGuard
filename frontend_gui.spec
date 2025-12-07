# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for HashGuard Frontend GUI
Creates HashGuard.exe that connects to backend service
"""
import os

block_cipher = None

# Frontend data files
frontend_datas = [
    ('frontend/graphics', 'frontend/graphics'),
]

# Hidden imports for frontend
frontend_hiddenimports = [
    # GUI
    'PySimpleGUI4',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.font',
    'tkinter.ttk',
    # PIL/Pillow - all submodules
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageOps',
    'PIL.ImageFilter',
    'Pillow',
    # Backend modules used by frontend
    'backend_helper',
    'ipc',
    'service_manager',  # For backend_helper to check service status
    # Other
    'pkg_resources.py2_warn',
    'threading',
    'json',
    'subprocess',
    'io',
]

# Collect all PIL data
from PyInstaller.utils.hooks import collect_all
pil_datas, pil_binaries, pil_hiddenimports = collect_all('PIL')
frontend_hiddenimports.extend(pil_hiddenimports)

a = Analysis(
    ['frontend/hashguardFrontendv5.py'],
    pathex=['frontend', 'backend'],  # Include backend in path for imports
    binaries=pil_binaries,
    datas=frontend_datas + pil_datas,
    hiddenimports=frontend_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='HashGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console for GUI app
    disable_windowing_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/graphics/app_icon.ico' if os.path.exists('frontend/graphics/app_icon.ico') else None,
)
