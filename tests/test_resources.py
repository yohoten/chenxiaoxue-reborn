"""
资源路径诊断脚本
用于检查 RESOURCE_PATH 配置和资源文件是否可访问
"""

from pathlib import Path
import sys

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.config.settings import settings
    
    print("=" * 60)
    print("陈筱雪 Reborn - 资源配置诊断工具")
    print("=" * 60)
    
    print(f"\n📁 BASE_DIR: {settings.BASE_DIR}")
    print(f"📁 RESOURCE_PATH: {settings.RESOURCE_PATH}")
    print(f"✅ RESOURCE_PATH exists: {settings.RESOURCE_PATH.exists()}")
    
    # 检查角色图片目录
    char_dir = settings.RESOURCE_PATH / "Character Image"
    print(f"\n🎭 Character Image 目录:")
    print(f"   路径: {char_dir}")
    print(f"   存在: {char_dir.exists()}")
    
    if char_dir.exists():
        files = list(char_dir.iterdir())
        image_files = [f for f in files if f.suffix.lower() in ['.gif', '.png', '.jpg', '.jpeg']]
        print(f"   图片数量: {len(image_files)}")
        if image_files:
            print(f"   示例文件:")
            for f in image_files[:5]:
                print(f"     - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"   ⚠️  目录不存在！")
    
    # 检查背景图片目录
    bg_dir = settings.RESOURCE_PATH / "Background Image"
    print(f"\n🖼️  Background Image 目录:")
    print(f"   路径: {bg_dir}")
    print(f"   存在: {bg_dir.exists()}")
    
    if bg_dir.exists():
        files = list(bg_dir.iterdir())
        image_files = [f for f in files if f.suffix.lower() in ['.gif', '.png', '.jpg', '.jpeg']]
        print(f"   图片数量: {len(image_files)}")
        if image_files:
            print(f"   示例文件:")
            for f in image_files[:5]:
                print(f"     - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    else:
        print(f"   ⚠️  目录不存在！")
    
    # 其他资源目录
    other_dirs = ["ECG Image", "Player Image", "Star Map"]
    print(f"\n📂 其他资源目录:")
    for dir_name in other_dirs:
        dir_path = settings.RESOURCE_PATH / dir_name
        exists = dir_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {dir_name}: {exists}")
    
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("   1. 确保后端服务正在运行 (uvicorn app.main:app --reload)")
    print("   2. 访问 http://localhost:8000/api/resources/backgrounds 测试")
    print("   3. 访问 http://localhost:8000/api/resources/characters 测试")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保已安装依赖:")
    print("  cd backend")
    print("  .venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 诊断失败: {e}")
    import traceback
    traceback.print_exc()