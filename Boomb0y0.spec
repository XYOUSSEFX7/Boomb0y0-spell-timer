# -*- mode: python ; coding: utf-8 -*-
# ملف البناء النحيف: بيشيل ملفات Qt اللي البرنامج مش بيستخدمها.
# البرنامج بيرسم بدون OpenGL ومن غير شبكة Qt ومن غير SVG أو PDF،
# وأيقونات PNG بتتقرا من Qt نفسه من غير مكتبات صور إضافية.
import os

datas = []
if os.path.isdir('spell_icons'):
    datas.append(('spell_icons', 'spell_icons'))

excludes = [
    'tkinter', 'numpy', 'scipy', 'pandas', 'matplotlib', 'PIL',
    'PyQt6.QtNetwork', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtSvg',
    'PyQt6.QtMultimedia', 'PyQt6.QtSql', 'PyQt6.QtTest', 'PyQt6.QtXml',
    'PyQt6.QtOpenGL', 'PyQt6.QtPdf', 'PyQt6.QtPrintSupport',
    'PyQt6.QtBluetooth', 'PyQt6.QtDBus', 'PyQt6.QtDesigner', 'PyQt6.QtHelp',
    'PyQt6.QtNfc', 'PyQt6.QtPositioning', 'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'unittest', 'doctest', 'pydoc', 'sqlite3',
    'setuptools', 'pkg_resources', 'distutils',
]

a = Analysis(
    ['lol_timer.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

# أجزاء مش محتاجينها (الاسم بيتطابق على أي جزء من مسار الملف)
DROP = (
    'opengl32sw',          # محرك OpenGL برمجي (الأكبر، حوالي 15-20 ميجا)
    'd3dcompiler',
    'qt6pdf', 'qt6svg', 'qt6network', 'qt6quick', 'qt6qml',
    'qt6virtualkeyboard',
    '/imageformats/',      # PNG مدمج في Qt، مش محتاج plugin
    '/iconengines/',
    '/generic/',
    '/tls/',
    '/networkinformation/',
    '/platforminputcontexts/',
    '/translations/',
)


def keep(name):
    n = name.replace('\\', '/').lower()
    return not any(s in n for s in DROP)


a.binaries = [b for b in a.binaries if keep(b[0])]
a.datas = [d for d in a.datas if keep(d[0])]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Boomb0y0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
