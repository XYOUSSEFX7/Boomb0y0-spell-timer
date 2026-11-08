@echo off
<<<<<<< HEAD
setlocal
chcp 65001 >nul
cd /d "%~dp0"

=======
chcp 65001 >nul
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
echo ============================================
echo   Boomb0y0 spell timer - build EXE (PyQt6)
echo ============================================
echo.
<<<<<<< HEAD
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
=======

if not exist "lol_timer.py" (
    echo ERROR: lol_timer.py not found in this folder.
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
    pause
    exit /b 1
)

<<<<<<< HEAD
REM ---- make sure Python is available ----
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found in PATH.
    echo        Install Python 3 from python.org and tick "Add python.exe to PATH".
=======
echo [1/3] Installing tools (needs internet)...
python -m pip install --upgrade pyinstaller PyQt6
if errorlevel 1 (
    echo ERROR: pip install failed.
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
    pause
    exit /b 1
)

<<<<<<< HEAD
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
=======
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM  build.bat         = lite build (smaller exe, uses Boomb0y0.spec)
REM  build.bat safe    = safe build (bigger exe, use it if the lite one won't open)
if /i "%~1"=="safe" goto SAFE
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
if not exist "Boomb0y0.spec" (
    echo NOTE: Boomb0y0.spec not found, using the safe build.
    goto SAFE
)

echo.
<<<<<<< HEAD
echo [3/3] Building the LITE version...
=======
echo [2/3] Building the LITE version...
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
python -m PyInstaller --noconfirm --clean Boomb0y0.spec
if errorlevel 1 (
    echo.
    echo The lite build failed. Trying the safe build instead...
    goto SAFE
)
goto DONE

:SAFE
echo.
<<<<<<< HEAD
echo [3/3] Building the SAFE version...
set "EXCL=--exclude-module tkinter --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib --exclude-module PIL"
set "EXCL=%EXCL% --exclude-module PyQt6.QtNetwork --exclude-module PyQt6.QtQml --exclude-module PyQt6.QtQuick --exclude-module PyQt6.QtSvg"
set "EXCL=%EXCL% --exclude-module PyQt6.QtMultimedia --exclude-module PyQt6.QtSql --exclude-module PyQt6.QtTest --exclude-module PyQt6.QtXml"
set "EXCL=%EXCL% --exclude-module PyQt6.QtOpenGL --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPrintSupport --exclude-module PyQt6.QtBluetooth"
set "EXCL=%EXCL% --exclude-module unittest --exclude-module doctest --exclude-module pydoc --exclude-module sqlite3"
set "EXCL=%EXCL% --exclude-module setuptools --exclude-module pkg_resources --exclude-module distutils"
=======
echo [2/3] Building the SAFE version...
set EXCL=--exclude-module tkinter --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module matplotlib --exclude-module PIL
set EXCL=%EXCL% --exclude-module PyQt6.QtNetwork --exclude-module PyQt6.QtQml --exclude-module PyQt6.QtQuick --exclude-module PyQt6.QtSvg
set EXCL=%EXCL% --exclude-module PyQt6.QtMultimedia --exclude-module PyQt6.QtSql --exclude-module PyQt6.QtTest --exclude-module PyQt6.QtXml
set EXCL=%EXCL% --exclude-module PyQt6.QtOpenGL --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPrintSupport --exclude-module PyQt6.QtBluetooth
set EXCL=%EXCL% --exclude-module unittest --exclude-module doctest --exclude-module pydoc --exclude-module sqlite3
set EXCL=%EXCL% --exclude-module setuptools --exclude-module pkg_resources --exclude-module distutils
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
if exist "spell_icons" (
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% --add-data "spell_icons;spell_icons" lol_timer.py
) else (
    echo NOTE: spell_icons folder not found, building without bundled icons.
    python -m PyInstaller --noconfirm --clean --onefile --noconsole --name Boomb0y0 %EXCL% lol_timer.py
)
if errorlevel 1 (
    echo.
<<<<<<< HEAD
    echo ERROR: build failed. Read the error text above.
=======
    echo ERROR: build failed. Send me the error text above.
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
    pause
    exit /b 1
)

:DONE
echo.
<<<<<<< HEAD
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
=======
echo [3/3] Done!
echo Your program is here:  dist\Boomb0y0.exe
for %%A in (dist\Boomb0y0.exe) do echo Size: %%~zA bytes
echo.
echo Open it and make sure everything works. If it does not open, run:  build.bat safe
>>>>>>> a21bc005b57982a9a50fbf2030225ba676a0dba5
echo.
pause
