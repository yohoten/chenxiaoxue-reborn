# 用户认证系统 - 快速开始指南

## 📦 第一步：安装依赖

### 后端依赖
```bash
cd backend
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 email-validator==2.2.0
```

或者使用 requirements.txt：
```bash
cd backend
pip install -r requirements.txt
```

### 前端依赖（如果需要）
前端部分使用现有的 axios，无需额外安装。

---

## 🗄️ 第二步：执行数据库迁移

```bash
cd backend
python migrations/add_user_support.py
```

**预期输出**：
```
🔄 开始数据库迁移...
✅ 数据库初始化完成
📝 创建 users 表...
✅ users 表创建成功
📝 为 conversations 表添加 user_id 列...
✅ user_id 列添加成功
📝 创建默认用户...
✅ 默认用户创建成功
   用户名: admin
   密码: admin123
   ⚠️  请在生产环境中修改密码！
📝 将现有对话关联到用户 ID 1...
✅ 更新了 X 条对话记录
📝 添加外键约束...
ℹ️  SQLite 不支持动态添加外键约束，已在应用层实现完整性检查

🎉 数据库迁移完成！
```

---

## 🚀 第三步：启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

访问 API 文档：http://localhost:8000/docs

---

## 🧪 第四步：测试认证 API

### 1. 注册新用户

**请求**：
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123456",
    "nickname": "测试用户"
  }'
```

**响应**：
```json
{
  "id": 2,
  "username": "testuser",
  "email": "test@example.com",
  "nickname": "测试用户",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2026-05-05T20:40:00",
  "last_login": null
}
```

### 2. 用户登录

**请求**：
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@chenxiaoxue.com",
    "nickname": "管理员",
    "avatar_url": null,
    "is_active": true,
    "created_at": "2026-05-05T20:40:00",
    "last_login": "2026-05-05T20:45:00"
  }
}
```

### 3. 获取当前用户信息

**请求**：
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 发送聊天消息（需要认证）

**请求**：
```bash
curl -X POST "http://localhost:8000/api/chat/send" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "你好，陈筱雪！"
  }'
```

### 5. 获取聊天历史（仅当前用户）

**请求**：
```bash
curl -X GET "http://localhost:8000/api/chat/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔐 安全注意事项

### 1. 修改 SECRET_KEY
在 `.env` 文件或 `settings.py` 中修改：
```python
SECRET_KEY = "your-super-secret-random-key-here-change-this"
```

生成强密钥的方法：
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. 修改默认密码
登录后立即修改 admin 账户密码：
```bash
curl -X PUT "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewSecurePassword123!"
  }'
```

### 3. 生产环境配置
- ✅ 使用 HTTPS
- ✅ 设置强 SECRET_KEY
- ✅ 限制 CORS 来源
- ✅ 启用速率限制
- ✅ 定期备份数据库

---

## 📊 数据隔离验证

### 测试多用户隔离

1. **创建两个用户**：
   - User A: `alice` / `Alice@123`
   - User B: `bob` / `Bob@123`

2. **分别登录获取 Token**

3. **用 Alice 的 Token 发送消息**：
   ```bash
   curl -X POST "http://localhost:8000/api/chat/send" \
     -H "Authorization: Bearer ALICE_TOKEN" \
     -d '{"message": "Alice的消息"}'
   ```

4. **用 Bob 的 Token 发送消息**：
   ```bash
   curl -X POST "http://localhost:8000/api/chat/send" \
     -H "Authorization: Bearer BOB_TOKEN" \
     -d '{"message": "Bob的消息"}'
   ```

5. **验证隔离**：
   - Alice 查看历史：只看到 "Alice的消息"
   - Bob 查看历史：只看到 "Bob的消息"

---

## 🐛 常见问题

### Q1: 迁移失败，提示表已存在
**A**: 如果之前已经手动创建了表，可以跳过迁移步骤，直接启动服务。

### Q2: 登录后收到 401 错误
**A**: 检查 Token 是否正确传递：
- Header 格式：`Authorization: Bearer <token>`
- 注意 `Bearer` 后面有空格

### Q3: 无法注册，提示用户名已存在
**A**: 用户名必须唯一，尝试其他用户名或删除已有用户。

### Q4: 聊天接口返回 401
**A**: 确保在请求头中包含了有效的 Token。

### Q5: 如何删除用户？
**A**: 当前版本不提供删除功能（保护数据安全）。如需删除，可直接操作数据库：
```sql
DELETE FROM users WHERE username = 'testuser';
-- 级联删除该用户的所有对话
```

---

## 📝 下一步：前端集成

后端 API 已完成，接下来需要：
1. 创建登录/注册页面
2. 实现 Token 管理
3. 更新 API 调用自动附加 Token
4. 添加用户菜单和登出功能

详见前端开发文档（待创建）。

---

## 📞 技术支持

如有问题，请检查：
1. 后端日志输出
2. 浏览器控制台网络请求
3. 数据库文件是否存在
4. 依赖是否正确安装

祝使用愉快！🎉
