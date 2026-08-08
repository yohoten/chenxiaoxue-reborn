# 🌸 陈筱雪 AI 助手 - 用户认证系统

## 📖 简介

陈筱雪现已支持完整的用户注册、登录和多用户数据隔离功能！每个用户都有独立的对话历史、记忆和个性化体验。

---

## 🚀 快速开始

### 方法一：一键初始化（推荐）

**Windows 用户**：
```bash
scripts\init_auth.bat
```

脚本会自动完成：
1. ✅ 安装后端依赖
2. ✅ 执行数据库迁移
3. ✅ 安装前端依赖
4. ✅ 启动后端服务
5. ✅ 启动前端服务

### 方法二：手动安装

#### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 email-validator==2.2.0

# 执行数据库迁移
python migrations/add_user_support.py

# 启动后端服务
python -m uvicorn app.main:app --reload --port 8000
```

#### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动前端服务
npm run dev
```

---

## 🔐 默认账户

系统会自动创建一个默认管理员账户：

- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: `admin@chenxiaoxue.com`
- **昵称**: `管理员`

⚠️ **重要**: 首次登录后请立即修改密码！

---

## 📋 功能特性

### ✅ 已实现

#### 后端功能
- [x] 用户注册（用户名、邮箱、密码）
- [x] 用户登录（JWT Token 认证）
- [x] 获取/更新用户信息
- [x] 用户登出
- [x] 密码加密存储（bcrypt）
- [x] JWT Token 管理（7天有效期）
- [x] 多用户数据隔离
- [x] 对话记录关联用户
- [x] Self-Improving 记忆按用户隔离

#### 前端功能
- [x] 登录页面
- [x] 注册页面
- [x] 表单验证
- [x] 路由保护
- [x] Token 自动管理
- [x] 用户菜单（右上角）
- [x] 401 错误自动处理
- [x] 响应式设计

### 🔄 规划中

- [ ] 个人资料编辑页面
- [ ] 头像上传
- [ ] 忘记密码功能
- [ ] 邮箱验证
- [ ] Token 自动刷新
- [ ] OAuth2 第三方登录
- [ ] 双因素认证（2FA）

---

## 🎯 使用流程

### 1. 首次访问

1. 打开浏览器访问 http://localhost:5173
2. 自动跳转到登录页面
3. 点击"立即注册"创建新账户
4. 或直接使用默认账户登录

### 2. 注册用户

1. 填写注册表单：
   - 用户名（必填，3-20字符）
   - 邮箱（可选）
   - 昵称（可选）
   - 密码（必填，至少6字符）
   - 确认密码（必填）
2. 点击"✨ 注册"
3. 注册成功后跳转到登录页

### 3. 登录系统

1. 输入用户名和密码
2. 点击"🔐 登录"
3. 登录成功后进入主界面

### 4. 使用聊天功能

- 发送消息会自动保存到当前用户的历史
- 查看历史只显示当前用户的对话
- 不同用户的数据完全隔离

### 5. 退出登录

1. 点击右上角用户菜单
2. 选择"🚪 退出登录"
3. 清除 Token，返回登录页

---

## 📊 API 端点

### 认证相关

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取当前用户 | ✅ |
| PUT | `/api/auth/me` | 更新用户信息 | ✅ |
| POST | `/api/auth/logout` | 用户登出 | ✅ |

### 示例请求

**注册新用户**：
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test@123",
    "nickname": "测试用户"
  }'
```

**用户登录**：
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**获取用户信息**：
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 配置说明

### 后端配置

**文件**: `backend/app/config/settings.py`

```python
# JWT 密钥（生产环境必须修改）
SECRET_KEY = "your-super-secret-key-here"

# Token 有效期（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
```

**生成强密钥**：
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 前端配置

**文件**: `frontend/package.json`

确保包含以下依赖：
```json
{
  "dependencies": {
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0"
  }
}
```

---

## 🗄️ 数据库结构

### users 表

| 字段 | 类型 | 描述 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| email | VARCHAR(100) | 邮箱，唯一（可选） |
| hashed_password | VARCHAR(255) | bcrypt 加密的密码 |
| nickname | VARCHAR(50) | 昵称（可选） |
| avatar_url | VARCHAR(255) | 头像 URL（可选） |
| is_active | BOOLEAN | 是否激活，默认 true |
| is_superuser | BOOLEAN | 是否管理员，默认 false |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| last_login | DATETIME | 最后登录时间 |

### conversations 表（新增字段）

| 字段 | 类型 | 描述 |
|------|------|------|
| user_id | INTEGER | 外键，关联 users.id |

---

## 🛡️ 安全建议

### 生产环境部署

1. **修改 SECRET_KEY**
   ```python
   SECRET_KEY = "随机生成的强密钥"
   ```

2. **启用 HTTPS**
   - 使用 Let's Encrypt 免费证书
   - 配置 Nginx 反向代理

3. **限制 CORS**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

4. **启用速率限制**
   ```python
   pip install slowapi
   ```

5. **定期备份数据库**
   ```bash
   cp data/chenxiaoxue.db backups/chenxiaoxue_$(date +%Y%m%d).db
   ```

6. **监控异常登录**
   - 记录登录 IP
   - 检测异常频率
   - 发送告警通知

---

## 🐛 常见问题

### Q1: 登录后仍然跳转到登录页？
**A**: 
- 检查浏览器控制台是否有错误
- 确认 localStorage 中有 `access_token`
- 清除浏览器缓存后重试

### Q2: API 请求返回 401？
**A**:
- 确认后端服务正常运行
- 检查 SECRET_KEY 配置是否正确
- 查看 Token 格式：`Bearer <token>`

### Q3: 注册时提示用户名已存在？
**A**: 尝试其他用户名，或删除已有用户。

### Q4: 如何删除用户？
**A**: 
```sql
DELETE FROM users WHERE username = 'testuser';
-- 会级联删除该用户的所有对话
```

### Q5: 忘记管理员密码怎么办？
**A**: 
```python
# 在 Python 中重新生成密码哈希
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
print(pwd_context.hash("new_password"))

# 然后更新数据库
UPDATE users SET hashed_password = '新生成的哈希值' WHERE username = 'admin';
```

### Q6: 如何禁用某个用户？
**A**:
```sql
UPDATE users SET is_active = FALSE WHERE username = 'testuser';
```

### Q7: Token 有效期可以调整吗？
**A**: 可以，修改 `backend/app/services/auth_service.py` 中的 `ACCESS_TOKEN_EXPIRE_MINUTES`。

---

## 📚 相关文档

- [用户认证实施计划](USER_AUTH_IMPLEMENTATION_PLAN.md)
- [快速开始指南](USER_AUTH_QUICKSTART.md)
- [前端集成指南](FRONTEND_AUTH_INTEGRATION.md)
- [完整实施总结](USER_AUTH_COMPLETE_SUMMARY.md)

---

## 🎉 结语

恭喜！陈筱雪 AI 助手现在已经是一个真正的多用户平台了！

**主要成就**：
- 🔐 安全的用户认证系统
- 📊 完整的数据隔离
- 🎨 美观的用户界面
- ⚡ 流畅的使用体验
- 🛡️ 多层次的安全保障

每个用户都可以拥有：
- ✨ 独立的对话历史
- 🧠 专属的记忆和学习
- 🎯 个性化的 AI 体验
- 🔒 私密的数据空间

祝使用愉快！🌸

---

**版本**: v1.0.0  
**更新日期**: 2026-05-05  
**开发者**: Lingma (灵码)
