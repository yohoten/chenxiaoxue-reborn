"""
用户认证系统测试脚本

使用方法:
    python backend/tests/test_auth.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import httpx
from app.services.auth_service import get_password_hash, verify_password

BASE_URL = "http://localhost:8000"


async def test_password_hashing():
    """测试密码加密和验证"""
    print("\n🔐 测试1: 密码加密和验证")
    
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    print(f"  原始密码: {password}")
    print(f"  哈希值: {hashed[:50]}...")
    print(f"  长度: {len(hashed)} 字符")
    
    # 验证正确密码
    is_valid = verify_password(password, hashed)
    print(f"  ✓ 正确密码验证: {'通过' if is_valid else '失败'}")
    
    # 验证错误密码
    is_invalid = verify_password("WrongPassword", hashed)
    print(f"  ✓ 错误密码验证: {'正确拒绝' if not is_invalid else '失败'}")
    
    return is_valid and not is_invalid


async def test_user_registration():
    """测试用户注册"""
    print("\n📝 测试2: 用户注册")
    
    async with httpx.AsyncClient() as client:
        # 注册新用户
        response = await client.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": f"testuser_{int(asyncio.get_event_loop().time())}",
                "email": f"test{int(asyncio.get_event_loop().time())}@example.com",
                "password": "Test@123456",
                "nickname": "测试用户"
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"  ✓ 注册成功")
            print(f"    用户名: {data['username']}")
            print(f"    用户ID: {data['id']}")
            print(f"    昵称: {data['nickname']}")
            return True, data
        else:
            print(f"  ✗ 注册失败: {response.status_code}")
            print(f"    错误: {response.text}")
            return False, None


async def test_user_login(username: str, password: str):
    """测试用户登录"""
    print(f"\n🔑 测试3: 用户登录 ({username})")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 登录成功")
            print(f"    Token: {data['access_token'][:50]}...")
            print(f"    Token 类型: {data['token_type']}")
            print(f"    用户: {data['user']['username']}")
            return True, data['access_token']
        else:
            print(f"  ✗ 登录失败: {response.status_code}")
            print(f"    错误: {response.text}")
            return False, None


async def test_get_current_user(token: str):
    """测试获取当前用户信息"""
    print("\n👤 测试4: 获取当前用户信息")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 获取成功")
            print(f"    用户名: {data['username']}")
            print(f"    昵称: {data.get('nickname', 'N/A')}")
            return True
        else:
            print(f"  ✗ 获取失败: {response.status_code}")
            return False


async def test_unauthorized_access():
    """测试未授权访问"""
    print("\n🚫 测试5: 未授权访问保护")
    
    async with httpx.AsyncClient() as client:
        # 尝试不带 Token 访问受保护的路由
        response = await client.get(f"{BASE_URL}/api/auth/me")
        
        if response.status_code == 401:
            print(f"  ✓ 正确拒绝未授权访问 (401)")
            return True
        else:
            print(f"  ✗ 安全漏洞: 返回 {response.status_code}")
            return False


async def test_chat_with_auth(token: str):
    """测试带认证的聊天功能"""
    print("\n💬 测试6: 带认证的聊天功能")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/chat/send",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "你好，这是一条测试消息"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 发送消息成功")
            print(f"    回复长度: {len(data['response'])} 字符")
            print(f"    模型: {data['model_name']}")
            return True
        else:
            print(f"  ✗ 发送失败: {response.status_code}")
            print(f"    错误: {response.text}")
            return False


async def test_chat_history_isolation(token: str):
    """测试聊天历史隔离"""
    print("\n📜 测试7: 聊天历史数据隔离")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/chat/history?limit=5&offset=0",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 获取历史成功")
            print(f"    总记录数: {data['total']}")
            print(f"    返回记录: {len(data['items'])}")
            
            # 验证所有记录都属于当前用户
            if data['items']:
                user_ids = set(item['user_id'] for item in data['items'])
                print(f"    用户ID集合: {user_ids}")
                if len(user_ids) == 1:
                    print(f"  ✓ 数据隔离正确")
                    return True
                else:
                    print(f"  ✗ 数据隔离失败")
                    return False
            else:
                print(f"  ℹ️ 暂无历史记录")
                return True
        else:
            print(f"  ✗ 获取失败: {response.status_code}")
            return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("  陈筱雪 AI 助手 - 用户认证系统测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 密码加密
    try:
        result = await test_password_hashing()
        results.append(("密码加密", result))
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("密码加密", False))
    
    # 测试2: 用户注册
    try:
        success, user_data = await test_user_registration()
        results.append(("用户注册", success))
        
        if not success:
            print("\n⚠️  注册失败，跳过后续测试")
            return
        
        username = user_data['username']
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("用户注册", False))
        return
    
    # 测试3: 用户登录
    try:
        success, token = await test_user_login(username, "Test@123456")
        results.append(("用户登录", success))
        
        if not success or not token:
            print("\n⚠️  登录失败，跳过后续测试")
            return
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("用户登录", False))
        return
    
    # 测试4: 获取用户信息
    try:
        result = await test_get_current_user(token)
        results.append(("获取用户信息", result))
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("获取用户信息", False))
    
    # 测试5: 未授权访问
    try:
        result = await test_unauthorized_access()
        results.append(("未授权访问保护", result))
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("未授权访问保护", False))
    
    # 测试6: 聊天功能
    try:
        result = await test_chat_with_auth(token)
        results.append(("聊天功能", result))
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("聊天功能", False))
    
    # 测试7: 数据隔离
    try:
        result = await test_chat_history_isolation(token)
        results.append(("数据隔离", result))
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        results.append(("数据隔离", False))
    
    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status:<8} - {test_name}")
    
    print("-" * 60)
    print(f"  总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查问题。")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
