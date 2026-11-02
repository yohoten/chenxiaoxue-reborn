@echo off
:: ============================================================
::  ChenXiaoXue Reborn - launcher.bat v3.0 (thin shim)
::  All logic moved to launcher.py (no cmd encoding/escape issues)
::  Usage: launcher.bat [setup^|dev^|backend^|frontend^|tauri^|test^|prod^|stop]
:: ============================================================
setlocal
set "SCRIPT=%~dp0launcher.py"
if not exist "%SCRIPT%" (
    echo [ERROR] launcher.py not found next to launcher.bat
    pause
    exit /b 1
)

where py >nul 2>&1
if not errorlevel 1 (
    py -3 "%SCRIPT%" %*
    goto :done
)
where python >nul 2>&1
if not errorlevel 1 (
    python "%SCRIPT%" %*
    goto :done
)
echo [ERROR] Python not found. Install Python 3.10+ from https://www.python.org/downloads/
pause
exit /b 1

:done
endlocal
