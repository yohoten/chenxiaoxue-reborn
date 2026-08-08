"""
数据库迁移脚本 - 添加用户支持

执行方式:
    python backend/migrations/add_user_support.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.services.database import init_db, get_session


async def migrate_database():
    """执行数据库迁移"""
    print("🔄 开始数据库迁移...")
    
    # 初始化数据库（创建基础表）
    await init_db()
    print("✅ 数据库初始化完成")
    
    async with await get_session() as session:
        try:
            # 1. 检查 users 表是否已存在
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            )
            users_table_exists = result.scalar_one_or_none() is not None
            
            if users_table_exists:
                print("⚠️  users 表已存在，跳过创建")
            else:
                # 2. 创建 users 表
                print("📝 创建 users 表...")
                await session.execute(text("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE,
                        hashed_password VARCHAR(255) NOT NULL,
                        nickname VARCHAR(50),
                        avatar_url VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        is_superuser BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME
                    )
                """))
                await session.commit()
                print("✅ users 表创建成功")
            
            # 3. 检查 conversations 表是否有 user_id 列
            result = await session.execute(
                text("PRAGMA table_info(conversations)")
            )
            columns = [row[1] for row in result.fetchall()]
            
            if 'user_id' in columns:
                print("⚠️  conversations.user_id 列已存在，跳过添加")
            else:
                # 4. 为 conversations 表添加 user_id 列
                print("📝 为 conversations 表添加 user_id 列...")
                await session.execute(text("""
                    ALTER TABLE conversations ADD COLUMN user_id INTEGER
                """))
                await session.commit()
                print("✅ user_id 列添加成功")
            
            # 5. 创建默认用户（用于迁移现有数据）
            from app.services.auth_service import get_password_hash
            from app.models.user import User
            
            result = await session.execute(
                text("SELECT COUNT(*) FROM users")
            )
            user_count = result.scalar_one()
            
            if user_count == 0:
                print("📝 创建默认用户...")
                default_user = User(
                    username="admin",
                    email="admin@chenxiaoxue.com",
                    hashed_password=get_password_hash("admin123"),
                    nickname="管理员",
                    is_active=True,
                    is_superuser=True,
                )
                session.add(default_user)
                await session.commit()
                print("✅ 默认用户创建成功")
                print("   用户名: admin")
                print("   密码: admin123")
                print("   ⚠️  请在生产环境中修改密码！")
                
                default_user_id = default_user.id
            else:
                # 获取第一个用户 ID
                result = await session.execute(
                    text("SELECT id FROM users LIMIT 1")
                )
                default_user_id = result.scalar_one()
            
            # 6. 将现有对话关联到默认用户
            print(f"📝 将现有对话关联到用户 ID {default_user_id}...")
            result = await session.execute(text("""
                UPDATE conversations 
                SET user_id = :user_id 
                WHERE user_id IS NULL
            """), {"user_id": default_user_id})
            await session.commit()
            updated_count = result.rowcount
            print(f"✅ 更新了 {updated_count} 条对话记录")
            
            # 7. 添加外键约束（SQLite 需要特殊处理）
            print("📝 添加外键约束...")
            # SQLite 不支持直接添加外键，需要在应用层保证完整性
            print("ℹ️  SQLite 不支持动态添加外键约束，已在应用层实现完整性检查")
            
            print("\n🎉 数据库迁移完成！")
            print("\n📋 迁移总结:")
            print(f"  - users 表: {'已存在' if users_table_exists else '新建'}")
            print(f"  - conversations.user_id: {'已存在' if 'user_id' in columns else '新增'}")
            print(f"  - 默认用户: admin / admin123")
            print(f"  - 迁移对话数: {updated_count}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 迁移失败: {e}")
            raise


if __name__ == "__main__":
    try:
        asyncio.run(migrate_database())
    except KeyboardInterrupt:
        print("\n⚠️  迁移被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
