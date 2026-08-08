# -*- coding: utf-8 -*-
"""
直接测试 launcher.bat 的各个模式
"""
import subprocess
import os

bat_dir = r"d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"
bat_name = "launcher.bat"

def test_mode(mode, description):
    """测试指定模式"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"命令: cd 到目录 && launcher.bat {mode if mode else '(无参数)'}")
    print('='*60)
    
    try:
        # 先切换到目录，再执行批处理
        result = subprocess.run(
            f'cmd /c "cd /d "{bat_dir}" && {bat_name} {mode}"',
            shell=True,
            capture_output=True,
            text=True,
            encoding='gbk',
            timeout=5
        )
        
        if result.stdout:
            # 只显示前30行
            lines = result.stdout.split('\n')[:30]
            print('\n'.join(lines))
            if len(result.stdout.split('\n')) > 30:
                print("... (输出截断)")
        
        if result.returncode != 0 and result.stderr:
            print(f"\n错误信息:")
            print(result.stderr[:500])
            
    except subprocess.TimeoutExpired:
        print("\n[超时] 这是正常的，某些模式会启动服务并保持运行")
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("launcher.bat 功能测试")
    print("="*60)
    
    # 测试各个模式
    test_mode("", "交互式菜单（应该显示菜单）")
    test_mode("invalid", "无效参数（应显示错误提示）")
    test_mode("setup", "环境安装模式（检查依赖）")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n手动测试建议:")
    print(f'1. 打开 CMD')
    print(f'2. 运行: cd /d "{bat_dir}"')
    print(f'3. 运行: launcher.bat [mode]')
    print(f'\n可用模式:')
    print(f'  - 无参数: 显示交互式菜单')
    print(f'  - setup: 一键安装环境')
    print(f'  - dev: 开发模式（后端+前端）')
    print(f'  - backend: 仅后端')
    print(f'  - frontend: 仅前端')
    print(f'  - tauri: Tauri 桌面模式')
    print(f'  - test: 测试模式')
    print(f'  - prod: 生产模式')
