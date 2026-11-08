@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Boomb0y0 spell timer - build EXE (PyQt6)
echo ============================================
echo.
echo   build.bat              - lite build (smaller exe)     [default]
echo   build.bat safe         - safe build (bigger exe)
echo   build.bat nopip        - skip the pip update step (faster / offline)
echo   (you can combine them:  build.bat safe nopip)
echo.

REM ---- read the switches (any order) ----
set "MODE=lite"
set "SKIP_PIP="
for %%A in (%*) do (
    if /i "%%~A"=="safe"  set "MODE=safe"
    if /i "%%~A"=="nopip" set "SKIP_PIP=1"
)

if not exist "lol_timer.py" (
    echo ERROR: lol_timer.py not found next to build.bat.
    pause
    exit /b 1
)

REM ---- make sure Python is available ----
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo        Install Python 3 from python.org and tick "Add python.exe to PATH".
    pause
    exit /b 1
)

REM ---- install build tools (skippable) ----
if defined SKIP_PIP (
    echo [1/3] Skipping pip update ^(nopip^).
) else (
    echo [1/3] Installing / updating build tools ^(needs internet^)...
    python -m pip install --upgrade --disable-pip-version-check -q pyinstaller PyQt6
    if errorlevel 1 echo    WARN: pip failed - continuing if PyInstaller is already installed.
)

python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed.
    echo        Run:  python -m pip install pyinstaller PyQt6
    pause
    exit /b 1
)

echo [2/3] Cleaning old build...
if exist "build" rmdir /s /q build
if exist "dist"  rmdir /s /q dist

REM  lite  = smaller exe, uses Boomb0y0.spec
REM  safe  = bigger exe, use it if the lite one will not open
if /i "%MODE%"=="safe" goto SAFE
if not exist "Boomb0y0.spec" (
    echo NOTE: Boomb0y0.spec not found, using the safe build.
    goto SAFE
)

echo.
echo [3/3] Building the LITE version...
python -m PyInstaller --noconfirm --clean Boomb0y0.spec
if errorlevel 1 (
    echo.
    echo The lite build failed. Trying the safe build instead...
    goto SAFE
)
goto DONE

:SAFE
echo.
echo [3/3] Building the SAFE version...
set "EXCL=--exclude-module tkinter --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib --exclude-module PIL"
set "EXCL=%EXCL% --exclude-module PyQt6.QtNetwork --exclude-module PyQt6.QtQml --exclude-module PyQt6.QtQuick --exclude-module PyQt6.QtSvg"
set "EXCL=%EXCL% --exclude-module PyQt6.QtMultimedia --exclude-module PyQt6.QtSql --exclude-module PyQt6.QtTest --exclude-module PyQt6.QtXml"
set "EXCL=%EXCL% --exclude-module PyQt6.QtOpenGL --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPrintSupport --exclude-module PyQt6.QtBluetooth"
set "EXCL=%EXCL% --exclude-module unittest --exclude-module doctest --exclude-module pydoc --exclude-module sqlite3"
set "EXCL=%EXCL% --exclude-module setuptools --exclude-module pkg_resources --exclude-module distutils"
if exist "spell_icons" (
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% --add-data "spell_icons;spell_icons" lol_timer.py
) else (
    echo NOTE: spell_icons folder not found, building without bundled icons.
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% lol_timer.py
)
if errorlevel 1 (
    echo.
    echo ERROR: build failed. Read the error text above.
    pause
    exit /b 1
)

:DONE
echo.
if not exist "dist\Boomb0y0.exe" (
    echo ERROR: dist\Boomb0y0.exe was not created.
    pause
    exit /b 1
)
echo ============================================
echo   Done!  Your program is here:
echo   %CD%\dist\Boomb0y0.exe
echo ============================================
for %%A in (dist\Boomb0y0.exe) do echo Size: %%~zA bytes
echo.
echo Open it and make sure everything works.
echo If it does not open, run:  build.bat safe
echo.
pause
