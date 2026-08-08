# -*- coding: utf-8 -*-
"""
测试 launcher.bat 脚本的各个功能
"""
import subprocess
import os
import time

bat_path = r"d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn\launcher.bat"

def test_help_mode():
    """测试帮助模式（带无效参数）"""
    print("=" * 60)
    print("测试 1: 无效参数（应显示帮助信息）")
    print("=" * 60)
    result = subprocess.run(
        ["cmd", "/c", bat_path, "invalid"],
        capture_output=True,
        text=True,
        encoding='gbk'
    )
    print("输出:")
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    print()

def test_setup_check():
    """检查 setup 模式的依赖"""
    print("=" * 60)
    print("测试 2: 检查 Python 和 Node.js 是否安装")
    print("=" * 60)
    
    # 检查 Python
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Python: {result.stdout.strip()}")
    except:
        print("✗ Python 未安装")
    
    # 检查 Node.js
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        print(f"✓ Node.js: {result.stdout.strip()}")
    except:
        print("✗ Node.js 未安装")
    
    print()

def test_backend_check():
    """检查后端环境"""
    print("=" * 60)
    print("测试 3: 检查后端虚拟环境")
    print("=" * 60)
    
    venv_path = r"d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn\backend\.venv\Scripts\activate.bat"
    if os.path.exists(venv_path):
        print(f"✓ 虚拟环境存在: {venv_path}")
    else:
        print(f"✗ 虚拟环境不存在，需要运行 setup")
    print()

def test_frontend_check():
    """检查前端环境"""
    print("=" * 60)
    print("测试 4: 检查前端 node_modules")
    print("=" * 60)
    
    node_modules = r"d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn\frontend\node_modules"
    if os.path.exists(node_modules):
        print(f"✓ node_modules 存在")
    else:
        print(f"✗ node_modules 不存在，需要运行 setup")
    print()

def test_batch_syntax():
    """测试批处理语法"""
    print("=" * 60)
    print("测试 5: 验证批处理文件语法")
    print("=" * 60)
    
    with open(bat_path, 'r', encoding='gbk') as f:
        content = f.read()
    
    checks = [
        ("@echo off", "文件头"),
        ("setlocal enabledelayedexpansion", "延迟扩展"),
        (":menu", "菜单标签"),
        (":do_setup", "setup 标签"),
        (":do_dev", "dev 标签"),
        (":do_backend", "backend 标签"),
        (":do_frontend", "frontend 标签"),
        (":do_tauri", "tauri 标签"),
        (":do_test", "test 标签"),
        (":do_prod", "prod 标签"),
        (":wait_seconds", "等待函数"),
        (":check_venv", "环境检查函数"),
        ('start "" cmd', "start 命令格式"),
        ("call :wait_seconds", "等待函数调用"),
    ]
    
    for pattern, desc in checks:
        if pattern in content:
            print(f"✓ {desc}: 找到")
        else:
            print(f"✗ {desc}: 未找到")
    print()

def test_chinese_display():
    """测试中文显示"""
    print("=" * 60)
    print("测试 6: 验证中文字符编码")
    print("=" * 60)
    
    with open(bat_path, 'rb') as f:
        data = f.read()
    
    # 检查关键中文字符的 GBK 编码
    test_strings = {
        b'\xb3\xc2\xf3\xe3\xd1\xa9': '陈筱雪',
        b'\xcd\xb3\xd2\xbb': '统一',
        b'\xc6\xf4\xb6\xaf\xc6\xf7': '启动器',
        b'\xbb\xb7\xbe\xb3\xb0\xb2\xd7\xb0': '环境安装',
        b'\xbf\xaa\xb7\xa2\xc4\xa3\xca\xbd': '开发模式',
    }
    
    for gbk_bytes, chinese in test_strings.items():
        if gbk_bytes in data:
            print(f"✓ '{chinese}' 编码正确")
        else:
            print(f"✗ '{chinese}' 编码错误或不存在")
    print()

if __name__ == "__main__":
    print("\n开始测试 launcher.bat 脚本...\n")
    
    test_help_mode()
    test_setup_check()
    test_backend_check()
    test_frontend_check()
    test_batch_syntax()
    test_chinese_display()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n建议下一步操作:")
    print("1. 如果虚拟环境不存在，运行: launcher.bat setup")
    print("2. 如果环境已就绪，运行: launcher.bat dev")
    print("3. 查看帮助: launcher.bat (无参数)")
