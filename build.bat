@echo off
chcp 65001 >nul
echo ============================================
echo   Boomb0y0 spell timer - build EXE (PyQt6)
echo ============================================
echo.

if not exist "lol_timer.py" (
    echo ERROR: lol_timer.py not found in this folder.
    pause
    exit /b 1
)

echo [1/3] Installing tools (needs internet)...
python -m pip install --upgrade pyinstaller PyQt6
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM  build.bat         = lite build (smaller exe, uses Boomb0y0.spec)
REM  build.bat safe    = safe build (bigger exe, use it if the lite one won't open)
if /i "%~1"=="safe" goto SAFE
if not exist "Boomb0y0.spec" (
    echo NOTE: Boomb0y0.spec not found, using the safe build.
    goto SAFE
)

echo.
echo [2/3] Building the LITE version...
python -m PyInstaller --noconfirm --clean Boomb0y0.spec
if errorlevel 1 (
    echo.
    echo The lite build failed. Trying the safe build instead...
    goto SAFE
)
goto DONE

:SAFE
echo.
echo [2/3] Building the SAFE version...
set EXCL=--exclude-module tkinter --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib --exclude-module PIL
set EXCL=%EXCL% --exclude-module PyQt6.QtNetwork --exclude-module PyQt6.QtQml --exclude-module PyQt6.QtQuick --exclude-module PyQt6.QtSvg
set EXCL=%EXCL% --exclude-module PyQt6.QtMultimedia --exclude-module PyQt6.QtSql --exclude-module PyQt6.QtTest --exclude-module PyQt6.QtXml
set EXCL=%EXCL% --exclude-module PyQt6.QtOpenGL --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPrintSupport --exclude-module PyQt6.QtBluetooth
set EXCL=%EXCL% --exclude-module unittest --exclude-module doctest --exclude-module pydoc --exclude-module sqlite3
set EXCL=%EXCL% --exclude-module setuptools --exclude-module pkg_resources --exclude-module distutils
if exist "spell_icons" (
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% --add-data "spell_icons;spell_icons" lol_timer.py
) else (
    echo NOTE: spell_icons folder not found, building without bundled icons.
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% lol_timer.py
)
if errorlevel 1 (
    echo.
    echo ERROR: build failed. Send me the error text above.
    pause
    exit /b 1
)

:DONE
echo.
echo [3/3] Done!
echo Your program is here:  dist\Boomb0y0.exe
for %%A in (dist\Boomb0y0.exe) do echo Size: %%~zA bytes
echo.
echo Open it and make sure everything works. If it does not open, run:  build.bat safe
echo.
pause
