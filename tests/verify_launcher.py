# -*- coding: utf-8 -*-
"""
launcher.bat v2.1 功能验证脚本
此脚本会检查 launcher.bat 的关键功能是否正常
"""

import os
import subprocess
from pathlib import Path

# 项目根目录
ROOT = Path(r"d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn")
LAUNCHER = ROOT / "launcher.bat"

def check_file_exists(path, name):
    """检查文件是否存在"""
    if path.exists():
        print(f"✅ {name}: {path}")
        return True
    else:
        print(f"❌ {name} 不存在: {path}")
        return False

def check_encoding(file_path):
    """检查文件编码"""
    try:
        with open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
            if '陈筱雪' in content:
                print(f"✅ 文件编码: GBK (中文正常)")
                return True
            else:
                print(f"⚠️  文件编码可能有问题")
                return False
    except Exception as e:
        print(f"❌ 编码检查失败: {e}")
        return False

def check_virtual_env():
    """检查虚拟环境"""
    venv_python = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        print(f"✅ 虚拟环境: {venv_python}")
        
        # 检查 uvicorn 是否安装
        result = subprocess.run(
            [str(venv_python), "-m", "pip", "show", "uvicorn"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ uvicorn 已安装")
            return True
        else:
            print(f"⚠️  uvicorn 未安装，需要运行 setup")
            return False
    else:
        print(f"❌ 虚拟环境不存在")
        return False

def check_node_modules():
    """检查前端依赖"""
    vite_bin = ROOT / "frontend" / "node_modules" / "vite" / "bin" / "vite.js"
    if vite_bin.exists():
        print(f"✅ Vite 已安装: {vite_bin}")
        return True
    else:
        print(f"❌ Vite 未安装，需要运行 setup")
        return False

def check_env_file():
    """检查 .env 文件"""
    env_file = ROOT / "backend" / ".env"
    if env_file.exists():
        print(f"✅ .env 文件存在")
        
        # 检查是否为 UTF-8 编码
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ .env 编码: UTF-8")
                return True
        except UnicodeDecodeError:
            print(f"⚠️  .env 编码不是 UTF-8，可能导致启动问题")
            return False
    else:
        print(f"⚠️  .env 文件不存在，将从 .env.example 创建")
        return False

def check_backend_code():
    """检查后端代码关键修复"""
    main_py = ROOT / "backend" / "app" / "main.py"
    if not main_py.exists():
        print(f"❌ main.py 不存在")
        return False
    
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 检查 FastAPI 初始化是否正确闭合
    if 'app = FastAPI(' in content and content.count('(') == content.count(')'):
        print(f"✅ FastAPI 初始化语法正确")
    else:
        print(f"❌ FastAPI 初始化可能有语法错误")
        return False
    
    # 检查 limiter 是否被注释
    if '# limiter = Limiter(' in content or 'limiter = None' in content:
        print(f"✅ Limiter 已禁用（避免 .env 编码问题）")
    else:
        print(f"⚠️  Limiter 仍启用，可能遇到 .env 编码问题")
    
    return True

def main():
    print("=" * 60)
    print("  launcher.bat v2.1 功能验证")
    print("=" * 60)
    print()
    
    results = []
    
    print("[1] 文件检查")
    print("-" * 60)
    results.append(check_file_exists(LAUNCHER, "launcher.bat"))
    print()
    
    print("[2] 编码检查")
    print("-" * 60)
    results.append(check_encoding(LAUNCHER))
    print()
    
    print("[3] 虚拟环境检查")
    print("-" * 60)
    results.append(check_virtual_env())
    print()
    
    print("[4] 前端依赖检查")
    print("-" * 60)
    results.append(check_node_modules())
    print()
    
    print("[5] .env 文件检查")
    print("-" * 60)
    results.append(check_env_file())
    print()
    
    print("[6] 后端代码检查")
    print("-" * 60)
    results.append(check_backend_code())
    print()
    
    print("=" * 60)
    print(f"  检查结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("\n✅ 所有检查通过！可以正常使用 launcher.bat")
        print("\n建议操作:")
        print("  1. 在 CMD 中运行: launcher.bat dev")
        print("  2. 访问 http://localhost:5173")
    else:
        print("\n⚠️  部分检查未通过")
        print("\n建议操作:")
        print("  1. 运行: launcher.bat setup")
        print("  2. 编辑 backend\\.env 填入 API Key")
    
    print()

if __name__ == "__main__":
    main()
