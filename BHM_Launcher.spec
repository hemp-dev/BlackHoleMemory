# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    [os.path.join('scripts', 'bhm_launcher.py')],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('scripts', 'scripts'),
        ('plugins', 'plugins'),
        ('infra', 'infra'),
        ('config', 'config'),
        ('pyproject.toml', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = os.path.join('assets', 'bhm-control-panel.ico')
if sys.platform == 'darwin' and os.path.exists(os.path.join('assets', 'bhm-control-panel.icns')):
    icon_path = os.path.join('assets', 'bhm-control-panel.icns')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BHM_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[icon_path],
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='BlackHoleMemory.app',
        icon=icon_path,
        bundle_identifier='io.blackholememory.launcher',
    )
