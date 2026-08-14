@echo off
setlocal enabledelayedexpansion
title 陈筱雪 Reborn - 启动器

:: ============================================================
::  陈筱雪 Reborn — 统一启动器 v2.2
::  用法: launcher.bat [mode]
::    mode: setup | dev | backend | frontend | tauri | test | prod
::  兼容: 支持路径含 &、空格等特殊字符（先 cd 再以相对路径启动）
:: ============================================================

:: 获取脚本所在目录（处理包含特殊字符的路径）
for %%i in ("%~dp0.") do set "ROOT=%%~fi"
if not defined ROOT set "ROOT=%CD%"

set "BACKEND=%ROOT%\backend"
set "FRONTEND=%ROOT%\frontend"
set "VENV=%ROOT%\backend\.venv"
set "TITLE=陈筱雪 Reborn"

:: -- 参数直通模式 --------------------------------------------
if "%~1"=="" goto :menu
if /i "%~1"=="setup"    goto :do_setup
if /i "%~1"=="dev"      goto :do_dev
if /i "%~1"=="backend"  goto :do_backend
if /i "%~1"=="frontend" goto :do_frontend
if /i "%~1"=="tauri"    goto :do_tauri
if /i "%~1"=="test"     goto :do_test
if /i "%~1"=="prod"     goto :do_prod
echo [错误] 未知模式: %~1
echo 可用模式: setup, dev, backend, frontend, tauri, test, prod
goto :menu

:: -- 菜单 ----------------------------------------------------
:menu
cls
echo.
echo   ========================================
echo     陈筱雪 Reborn - 统一启动器 v2.2
echo   ========================================
echo.
echo   [1] 环境安装     (首次使用请先执行)
echo   [2] 开发模式     (后端 + 前端，双窗口)
echo   [3] 仅后端       (FastAPI :8000)
echo   [4] 仅前端       (Vite :5173)
echo   [5] Tauri 桌面   (Rust 原生窗口)
echo   [6] 测试模式     (Humanizer + 浏览器)
echo   [7] 生产模式     (后端生产配置)
echo.
echo   [Q] 退出
echo.
set /p "CHOICE=  输入选择 [1-7/Q]: "

if "%CHOICE%"=="1" goto :do_setup
if "%CHOICE%"=="2" goto :do_dev
if "%CHOICE%"=="3" goto :do_backend
if "%CHOICE%"=="4" goto :do_frontend
if "%CHOICE%"=="5" goto :do_tauri
if "%CHOICE%"=="6" goto :do_test
if "%CHOICE%"=="7" goto :do_prod
if /i "%CHOICE%"=="q" goto :quit
echo   [错误] 无效选择，请重试
call :wait_seconds 2
goto :menu

:: ============================================================
::  [1] 环境安装
:: ============================================================
:do_setup
cls
echo.
echo   ====== 环境安装 ======
echo.

echo   [1/6] 检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 Python，请安装 Python 3.10+
    echo          下载: https://www.python.org/downloads/
    goto :end
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
echo   [ OK ] Python %PY_VER%

echo   [2/6] 检查 Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 Node.js，请安装 Node.js 18+
    echo          下载: https://nodejs.org/
    goto :end
)
for /f "tokens=1 delims=v" %%i in ('node --version 2^>^&1') do set "NODE_VER=%%i"
echo   [ OK ] Node.js v%NODE_VER%

echo   [3/6] 创建虚拟环境...
cd /d "%BACKEND%"
if not exist ".venv" (
    echo        创建虚拟环境...
    python -m venv .venv
) else (
    echo        虚拟环境已存在
)

echo   [4/6] 安装后端依赖...
call .venv\Scripts\activate.bat
echo        升级 pip...
python -m pip install --upgrade pip -q 2>nul
echo        安装 Python 包...
python -m pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo   [错误] 后端依赖安装失败
    goto :end
)
echo   [ OK ] 后端依赖安装完成

echo   [5/6] 配置环境变量...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo   [注意] 已从 .env.example 创建 .env，请编辑填入 API Key
    )
) else (
    echo        .env 已存在，跳过
)

echo   [6/6] 安装前端依赖...
cd /d "%FRONTEND%"
if not exist "node_modules" (
    echo        安装 npm 包...
    call npm install
    if %errorlevel% neq 0 (
        echo   [错误] 前端依赖安装失败
        goto :end
    )
) else (
    echo        node_modules 已存在，跳过
)
echo   [ OK ] 前端依赖安装完成

echo.
echo   ====== 安装完成！ ======
echo.
echo   提示: 运行 launcher.bat dev 启动开发模式
goto :end

:: ============================================================
::  [2] 开发模式
:: ============================================================
:do_dev
cls
echo.
echo   ====== 开发模式 ======
echo.

call :check_venv
if %errorlevel% neq 0 goto :end

echo   [1/2] 启动后端 (端口 8000)...
cd /d "%BACKEND%"
start "陈筱雪 - 后端 (8000)" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo   等待后端就绪 (5 秒)...
call :wait_seconds 5

echo   [2/2] 启动前端 (端口 5173)...
cd /d "%FRONTEND%"
start "陈筱雪 - 前端 (5173)" cmd /k "node node_modules/vite/bin/vite.js"

echo.
echo   [ OK ] 开发模式已启动 (双窗口)
echo     后端: http://localhost:8000
echo     前端: http://localhost:5173
echo     文档: http://localhost:8000/docs
echo     健康: http://localhost:8000/health
echo.
echo   关闭对应的 CMD 窗口即可停止服务
goto :end

:: ============================================================
::  [3] 仅后端
:: ============================================================
:do_backend
cls
echo.
echo   ====== 仅后端 ======
echo.

call :check_venv
if %errorlevel% neq 0 goto :end

echo   启动 FastAPI (端口 8000)...
cd /d "%BACKEND%"
start "陈筱雪 - 后端 (8000)" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

echo.
echo   [ OK ] 后端已启动
echo     API:  http://localhost:8000
echo     文档: http://localhost:8000/docs
echo     健康: http://localhost:8000/health
goto :end

:: ============================================================
::  [4] 仅前端
:: ============================================================
:do_frontend
cls
echo.
echo   ====== 仅前端 ======
echo.

if not exist "%FRONTEND%\node_modules" (
    echo   [错误] 请先执行 [1] 环境安装
    goto :end
)

echo   启动 Vite (端口 5173)...
cd /d "%FRONTEND%"
start "陈筱雪 - 前端 (5173)" cmd /k "node node_modules/vite/bin/vite.js"

echo.
echo   [ OK ] 前端已启动
echo     地址: http://localhost:5173
goto :end

:: ============================================================
::  [5] Tauri 桌面模式
:: ============================================================
:do_tauri
cls
echo.
echo   ====== Tauri 桌面模式 ======
echo.

rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [错误] 未找到 Rust，请安装 Rust
    echo          下载: https://rustup.rs/
    goto :end
)

call :check_venv
if %errorlevel% neq 0 goto :end

echo   启动后端 (后台)...
cd /d "%BACKEND%"
start "陈筱雪 - 后端 (8000)" cmd /c ".venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

echo   等待后端就绪...
call :wait_seconds 3

echo   启动 Tauri 桌面应用...
cd /d "%FRONTEND%"
start "陈筱雪 - Tauri" cmd /k "npm run tauri dev"

echo.
echo   [ OK ] Tauri 桌面模式已启动
goto :end

:: ============================================================
::  [6] 测试模式
:: ============================================================
:do_test
cls
echo.
echo   ====== 测试模式 ======
echo.

call :check_venv
if %errorlevel% neq 0 goto :end

echo   启动后端...
cd /d "%BACKEND%"
start "陈筱雪 - 后端 (8000)" cmd /c ".venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
call :wait_seconds 5

echo   启动前端...
cd /d "%FRONTEND%"
start "陈筱雪 - 前端 (5173)" cmd /c "node node_modules/vite/bin/vite.js"
call :wait_seconds 5

echo   打开浏览器...
start http://localhost:5173

echo.
echo   [ OK ] 测试模式已启动
echo     前端: http://localhost:5173
echo     API:  http://localhost:8000/docs
echo.
echo   提示: 左侧导航 -> [人性化] 标签可测试 Humanizer
goto :end

:: ============================================================
::  [7] 生产模式
:: ============================================================
:do_prod
cls
echo.
echo   ====== 生产模式 ======
echo.

call :check_venv
if %errorlevel% neq 0 goto :end

if not exist "%BACKEND%\.env" (
    echo   [错误] 未找到 .env 文件，请先执行 [1] 环境安装
    goto :end
)

echo   [注意] 生产模式将启动后端 (无热重载)
echo.
echo   启动 FastAPI (端口 8000, 生产配置)...
cd /d "%BACKEND%"
start "陈筱雪 - 后端 (8000)" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"

echo.
echo   [ OK ] 生产模式已启动
echo     API:  http://localhost:8000
echo     健康: http://localhost:8000/health
goto :end

:: ============================================================
::  工具函数
:: ============================================================

:check_venv
if not exist "%VENV%\Scripts\python.exe" (
    echo   [错误] 未找到虚拟环境，请先执行 [1] 环境安装
    exit /b 1
)
exit /b 0

:wait_seconds
:: 兼容不同 Windows 版本的等待函数
:: 用法: call :wait_seconds <秒数>
if exist "%SystemRoot%\System32\timeout.exe" (
    timeout /t %1 /nobreak >nul
) else (
    ping 127.0.0.1 -n %1 >nul
)
exit /b 0

:quit
echo   再见！
exit /b 0

:end
echo.
echo   按任意键返回菜单...
pause >nul
goto :menu
