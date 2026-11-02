# -*- coding: utf-8 -*-
"""
陈筱雪 Reborn — 统一启动器 v3.0 (Python 版)
================================================
用法:
    python launcher.py            # 交互式菜单
    python launcher.py setup      # 环境安装
    python launcher.py dev        # 开发模式 (后端 + 前端)
    python launcher.py backend    # 仅后端 (FastAPI :8000)
    python launcher.py frontend   # 仅前端 (Vite :5173)
    python launcher.py tauri      # Tauri 桌面模式
    python launcher.py test       # 测试模式 (自动打开浏览器)
    python launcher.py prod       # 生产模式
    python launcher.py stop       # 停止 8000/5173 端口上的服务

特性:
    - 纯 Python 实现，无 cmd 转义/编码坑，路径含空格、&、中文均可
    - 后端启动后自动做 /health 健康检查，就绪后再拉起前端/浏览器
    - 端口占用检测，避免重复启动
    - 后端缺失虚拟环境时可自动进入安装流程
"""

import os
import sys
import socket
import subprocess
import time
import urllib.request
import urllib.error
import webbrowser

# ---------------------------------------------------------------- 基础配置
ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")
VENV_PY = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")
BACKEND_REQ = os.path.join(BACKEND, "requirements.txt")

BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://127.0.0.1:{FRONTEND_PORT}"

CREATE_NEW_CONSOLE = 0x00000010  # Windows: 新开控制台窗口

MODES = ("setup", "dev", "backend", "frontend", "tauri", "test", "prod", "stop")


# ---------------------------------------------------------------- 小工具
def ok(msg):
    print(f"  [ OK ] {msg}")


def warn(msg):
    print(f"  [注意] {msg}")


def fail(msg):
    print(f"  [错误] {msg}")


def info_urls(show_docs=True):
    print(f"        前端:   {FRONTEND_URL}")
    print(f"        后端:   {BACKEND_URL}")
    if show_docs:
        print(f"        文档:   {BACKEND_URL}/docs")
    print(f"        健康:   {BACKEND_URL}/health")
    print("        关闭对应的 CMD 窗口即可停止服务")


def find_on_path(name):
    """在 PATH 上查找可执行文件，返回完整路径或 None"""
    exts = os.environ.get("PATHEXT", ".EXE;.CMD;.BAT").split(";")
    for d in os.environ.get("PATH", "").split(os.pathsep):
        d = d.strip().strip('"')
        if not d:
            continue
        for ext in exts:
            p = os.path.join(d, name + ext)
            if os.path.isfile(p):
                return p
    return None


def sys_python():
    """返回系统 Python 解释器（py -3 优先），找不到返回 None"""
    try:
        r = subprocess.run(
            ["py", "-3", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return ["py", "-3"]
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        r = subprocess.run(
            ["python", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.strip():
            return ["python"]
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def port_in_use(port):
    """检测端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_backend(timeout=60):
    """轮询后端 /health，返回是否就绪"""
    print(f"  等待后端就绪 (最多 {timeout} 秒)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_in_use(BACKEND_PORT):
            try:
                with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=2) as r:
                    if r.status == 200:
                        return True
            except (urllib.error.URLError, OSError):
                pass
        time.sleep(1)
    return False


def new_console(title, args, cwd):
    """在新的 CMD 窗口中运行命令，保持窗口不关闭"""
    cmd = ["cmd", "/k", f"title {title}"] + list(args)
    subprocess.Popen(cmd, cwd=cwd, creationflags=CREATE_NEW_CONSOLE)


def run(args, cwd=None, check=True, capture=False):
    r = subprocess.run(
        args, cwd=cwd,
        capture_output=capture, text=True, encoding="utf-8", errors="replace",
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"命令失败 ({r.returncode}): {' '.join(args)}\n{r.stderr or ''}")
    return r


# ---------------------------------------------------------------- 环境检测
def check_venv(auto_fix=True):
    """确认后端虚拟环境可用，必要时引导安装"""
    if os.path.isfile(VENV_PY):
        return True
    fail("未找到后端虚拟环境 (backend\\.venv)")
    if auto_fix:
        ans = input("  是否现在执行环境安装? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            do_setup()
            return os.path.isfile(VENV_PY)
    return False


def check_node_modules(auto_fix=True):
    if os.path.isdir(os.path.join(FRONTEND, "node_modules")):
        return True
    fail("未找到前端依赖 (frontend\\node_modules)")
    if auto_fix:
        ans = input("  是否现在安装前端依赖 (npm install)? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            npm = find_on_path("npm")
            if not npm:
                fail("未找到 npm，请先安装 Node.js 18+: https://nodejs.org/")
                return False
            run([npm, "install"], cwd=FRONTEND, check=False)
            return os.path.isdir(os.path.join(FRONTEND, "node_modules"))
    return False


# ---------------------------------------------------------------- 各模式实现
def do_setup():
    print()
    print("  ====== 环境安装 ======")
    print()

    # [1/6] Python
    print("  [1/6] 检查 Python...")
    py = sys_python()
    if not py:
        fail("未找到 Python，请安装 Python 3.10+")
        fail("        下载: https://www.python.org/downloads/")
        return False
    r = run(py + ["--version"], capture=True)
    ok(f"Python {r.stdout.strip()}")

    # [2/6] Node
    print("  [2/6] 检查 Node.js...")
    npm = find_on_path("npm")
    if not npm:
        fail("未找到 Node.js，请安装 Node.js 18+")
        fail("        下载: https://nodejs.org/")
        return False
    r = run(["node", "--version"], capture=True, check=False)
    ok(f"Node.js {r.stdout.strip()}")

    # [3/6] venv
    print("  [3/6] 创建虚拟环境...")
    if not os.path.isfile(VENV_PY):
        os.makedirs(BACKEND, exist_ok=True)
        run(py + ["-m", "venv", os.path.join(BACKEND, ".venv")])
    if not os.path.isfile(VENV_PY):
        fail("虚拟环境创建失败")
        return False
    ok("backend\\.venv 就绪")

    # [4/6] 后端依赖
    print("  [4/6] 安装后端依赖...")
    req = BACKEND_REQ if os.path.isfile(BACKEND_REQ) else os.path.join(ROOT, "requirements.txt")
    run([VENV_PY, "-m", "pip", "install", "--upgrade", "pip", "-q"], check=False)
    r = run([VENV_PY, "-m", "pip", "install", "-r", req, "-q"], check=False, capture=True)
    if r.returncode != 0:
        fail("后端依赖安装失败:")
        print(r.stderr or r.stdout or "")
        return False
    ok("后端依赖安装完成")

    # [5/6] .env
    print("  [5/6] 配置环境变量...")
    env_path = os.path.join(BACKEND, ".env")
    if not os.path.isfile(env_path):
        example = os.path.join(BACKEND, ".env.example")
        if os.path.isfile(example):
            with open(example, "rb") as f:
                data = f.read()
            with open(env_path, "wb") as f:
                f.write(data)
            warn("已从 .env.example 创建 .env，请编辑填入 API Key")
        else:
            warn("未找到 .env.example，跳过 (后端可能使用默认配置)")
    else:
        print("        .env 已存在，跳过")

    # [6/6] 前端依赖
    print("  [6/6] 安装前端依赖...")
    if os.path.isdir(os.path.join(FRONTEND, "node_modules")):
        print("        node_modules 已存在，跳过")
    else:
        r = run([npm, "install"], cwd=FRONTEND, check=False, capture=True)
        if r.returncode != 0:
            fail("前端依赖安装失败:")
            print(r.stderr or r.stdout or "")
            return False
    ok("前端依赖安装完成")

    print()
    print("  ====== 安装完成！ ======")
    print()
    print("  提示: python launcher.py dev  启动开发模式")
    return True


def start_backend(reload=True, prod=False):
    args = [VENV_PY, "-m", "uvicorn", "app.main:app"]
    if prod:
        args += ["--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--workers", "2"]
    else:
        args += ["--reload", "--port", str(BACKEND_PORT)]
    new_console(f"陈筱雪 - 后端 ({BACKEND_PORT})", args, cwd=BACKEND)
    ok(f"后端已启动 (端口 {BACKEND_PORT})")


def start_frontend():
    vite_js = os.path.join(FRONTEND, "node_modules", "vite", "bin", "vite.js")
    node = find_on_path("node")
    if os.path.isfile(vite_js) and node:
        new_console(f"陈筱雪 - 前端 ({FRONTEND_PORT})", [node, vite_js], cwd=FRONTEND)
    else:
        npm = find_on_path("npm")
        new_console(f"陈筱雪 - 前端 ({FRONTEND_PORT})", [npm, "run", "dev"], cwd=FRONTEND)
    ok(f"前端已启动 (端口 {FRONTEND_PORT})")


def do_dev():
    print()
    print("  ====== 开发模式 ======")
    print()
    if not check_venv():
        return
    if not check_node_modules():
        return
    if port_in_use(BACKEND_PORT):
        warn(f"端口 {BACKEND_PORT} 已被占用，跳过后端启动 (可能已在运行)")
    else:
        print(f"  [1/2] 启动后端 (端口 {BACKEND_PORT})...")
        start_backend(reload=True)
        wait_backend(timeout=30)
    if port_in_use(FRONTEND_PORT):
        warn(f"端口 {FRONTEND_PORT} 已被占用，跳过前端启动 (可能已在运行)")
    else:
        print(f"  [2/2] 启动前端 (端口 {FRONTEND_PORT})...")
        start_frontend()
    print()
    ok("开发模式已启动 (双窗口)")
    info_urls()


def do_backend():
    print()
    print("  ====== 仅后端 ======")
    print()
    if not check_venv():
        return
    if port_in_use(BACKEND_PORT):
        warn(f"端口 {BACKEND_PORT} 已被占用，可能已在运行")
        return
    print(f"  启动 FastAPI (端口 {BACKEND_PORT})...")
    start_backend(reload=True)
    wait_backend(timeout=30)
    print()
    info_urls()


def do_frontend():
    print()
    print("  ====== 仅前端 ======")
    print()
    if not check_node_modules():
        return
    if port_in_use(FRONTEND_PORT):
        warn(f"端口 {FRONTEND_PORT} 已被占用，可能已在运行")
        return
    print(f"  启动 Vite (端口 {FRONTEND_PORT})...")
    start_frontend()
    print()
    ok(f"前端已启动: {FRONTEND_URL}")


def do_tauri():
    print()
    print("  ====== Tauri 桌面模式 ======")
    print()
    try:
        r = run(["rustc", "--version"], capture=True, check=False)
        if r.returncode != 0:
            raise RuntimeError
    except (OSError, RuntimeError):
        fail("未找到 Rust，请先安装: https://rustup.rs/")
        return
    if not check_venv():
        return
    if not check_node_modules():
        return
    if not port_in_use(BACKEND_PORT):
        print("  启动后端 (后台)...")
        start_backend(reload=False)
        wait_backend(timeout=30)
    else:
        warn(f"端口 {BACKEND_PORT} 已有服务，复用现有后端")
    print("  启动 Tauri 桌面应用...")
    npm = find_on_path("npm")
    new_console("陈筱雪 - Tauri", [npm, "run", "tauri", "dev"], cwd=FRONTEND)
    print()
    ok("Tauri 桌面模式已启动")


def do_test():
    print()
    print("  ====== 测试模式 ======")
    print()
    if not check_venv():
        return
    if not check_node_modules():
        return
    backend_ready = port_in_use(BACKEND_PORT)
    if not backend_ready:
        print("  启动后端...")
        start_backend(reload=True)
        backend_ready = wait_backend(timeout=60)
    else:
        warn(f"端口 {BACKEND_PORT} 已有服务，复用现有后端")
    frontend_ready = port_in_use(FRONTEND_PORT)
    if not frontend_ready:
        print("  启动前端...")
        start_frontend()
        deadline = time.time() + 30
        while time.time() < deadline and not port_in_use(FRONTEND_PORT):
            time.sleep(1)
        frontend_ready = port_in_use(FRONTEND_PORT)
    print("  打开浏览器...")
    webbrowser.open(FRONTEND_URL)
    print()
    ok("测试模式已启动")
    info_urls()
    print("  提示: 左侧导航 -> [人性化] 标签可测试 Humanizer")


def do_prod():
    print()
    print("  ====== 生产模式 ======")
    print()
    if not check_venv(auto_fix=False):
        return
    if not os.path.isfile(os.path.join(BACKEND, ".env")):
        fail("未找到 backend\\.env 文件，请先执行 setup")
        return
    if port_in_use(BACKEND_PORT):
        warn(f"端口 {BACKEND_PORT} 已被占用，可能已在运行")
        return
    warn("生产模式将启动后端 (无热重载, 2 workers)")
    print(f"  启动 FastAPI (端口 {BACKEND_PORT}, 生产配置)...")
    start_backend(prod=True)
    wait_backend(timeout=60)
    print()
    info_urls(show_docs=False)


def do_stop():
    print()
    print("  ====== 停止服务 ======")
    print()
    for port, name in ((BACKEND_PORT, "后端"), (FRONTEND_PORT, "前端")):
        if port_in_use(port):
            r = run(
                ["cmd", "/c", f"netstat -ano | findstr :{port}"],
                capture=True, check=False,
            )
            pids = set()
            for line in (r.stdout or "").splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[1].endswith(f":{port}") and parts[3] == "LISTENING":
                    pids.add(parts[4])
            if not pids:
                warn(f"{name} 端口 {port} 被占用但未找到监听进程 PID")
                continue
            for pid in pids:
                kr = run(["taskkill", "/PID", pid, "/F"], capture=True, check=False)
                if kr.returncode == 0:
                    ok(f"已停止 {name} (端口 {port}, PID {pid})")
                else:
                    fail(f"停止 {name} 失败 (PID {pid}): {kr.stderr.strip()}")
        else:
            print(f"  {name} 端口 {port} 未被占用")
    print()
    print("  提示: 也可以直接关闭对应的 CMD 窗口")


# ---------------------------------------------------------------- 菜单
MENU = """
  ========================================
    陈筱雪 Reborn - 统一启动器 v3.0
  ========================================

  [1] 环境安装     (首次使用请先执行)
  [2] 开发模式     (后端 + 前端，双窗口)
  [3] 仅后端       (FastAPI :8000)
  [4] 仅前端       (Vite :5173)
  [5] Tauri 桌面   (Rust 原生窗口)
  [6] 测试模式     (Humanizer + 浏览器)
  [7] 生产模式     (后端生产配置)
  [8] 停止服务     (释放 8000/5173 端口)

  [Q] 退出
"""

MENU_ACTIONS = {
    "1": do_setup, "2": do_dev, "3": do_backend, "4": do_frontend,
    "5": do_tauri, "6": do_test, "7": do_prod, "8": do_stop,
}


def menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(MENU)
        choice = input("  输入选择 [1-8/Q]: ").strip().lower()
        if choice == "q":
            print("  再见！")
            return
        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("  [错误] 无效选择，请重试")
            time.sleep(1.5)
            continue
        action()
        print()
        input("  按回车返回菜单...")
        print()


# ---------------------------------------------------------------- 入口
def run():
    # pythonw 启动 (无控制台) 时，重新在新的控制台窗口中启动自身
    if sys.stdout is None or sys.stderr is None:
        py_exe = sys.executable
        # pythonw.exe 无控制台，改用同目录的 python.exe
        if os.path.basename(py_exe).lower().startswith("pythonw"):
            py_exe = os.path.join(os.path.dirname(py_exe), "python.exe")
            if not os.path.isfile(py_exe):
                py_exe = "python"
        subprocess.Popen(
            ["cmd", "/k", "title 陈筱雪 Reborn - 启动器", py_exe,
             os.path.abspath(__file__)] + sys.argv[1:],
            creationflags=CREATE_NEW_CONSOLE,
        )
        return

    # Windows 控制台切换到 UTF-8，保证中文正常显示
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
        except Exception:
            pass

    mode = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    if mode == "":
        menu()
    elif mode in MODES:
        {"setup": do_setup, "dev": do_dev, "backend": do_backend,
         "frontend": do_frontend, "tauri": do_tauri, "test": do_test,
         "prod": do_prod, "stop": do_stop}[mode]()
        if mode not in ("",):
            print()
            input("  按回车退出...")
    else:
        print(f"[错误] 未知模式: {sys.argv[1]}")
        print(f"可用模式: {', '.join(MODES)}")
        print()
        input("  按回车退出...")


if __name__ == "__main__":
    run()
