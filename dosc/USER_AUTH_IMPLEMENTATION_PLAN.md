# 用户认证和分用户管理系统实施计划

## 📅 创建日期
2026-05-05

## 🎯 目标
为陈筱雪 AI 助手添加完整的用户注册、登录和分用户管理功能，实现多用户数据隔离。

---

## ✅ 已完成的工作

### 1. 数据模型层
- ✅ **User 模型** (`backend/app/models/user.py`)
  - 用户基本信息（用户名、邮箱、密码哈希）
  - 扩展信息（昵称、头像URL）
  - 状态标志（活跃状态、管理员权限）
  - 时间戳（创建时间、更新时间、最后登录）
  - 与 Conversation 的一对多关系

- ✅ **Conversation 模型更新** (`backend/app/models/conversation.py`)
  - 添加 `user_id` 外键字段
  - 建立与 User 的关系
  - 支持级联删除

### 2. 认证服务
- ✅ **Auth Service** (`backend/app/services/auth_service.py`)
  - 密码加密/验证（bcrypt）
  - JWT Token 生成和验证
  - Access Token（7天有效期）
  - Refresh Token（30天有效期）

### 3. 认证依赖
- ✅ **Auth Dependencies** (`backend/app/dependencies/auth.py`)
  - `get_current_user`: 从 Token 获取当前用户
  - `get_current_active_user`: 验证用户活跃状态
  - OAuth2 Bearer Token 认证

### 4. 认证路由
- ✅ **Auth Router** (`backend/app/routers/auth.py`)
  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  - `GET /api/auth/me` - 获取当前用户信息
  - `PUT /api/auth/me` - 更新用户信息
  - `POST /api/auth/logout` - 用户登出

---

## 🔄 待完成的工作

### Phase 1: 后端核心功能（高优先级）

#### 1. 更新数据库服务
**文件**: `backend/app/services/database.py`

**任务**:
- [ ] 修改 `save_conversation` 接受 `user_id` 参数
- [ ] 修改 `get_conversations` 按 `user_id` 过滤
- [ ] 修改 `delete_conversation` 验证用户权限
- [ ] 修改 `clear_conversations` 仅清空当前用户数据
- [ ] 添加用户相关的 CRUD 操作

**示例代码**:
```python
async def save_conversation(conv: ConversationCreate, user_id: int) -> Conversation:
    """保存对话记录（关联用户）"""
    async with await get_session() as session:
        db_conv = Conversation(
            user_id=user_id,  # 新增
            user_input=conv.user_input,
            assistant_response=conv.assistant_response,
            # ... 其他字段
        )
        session.add(db_conv)
        await session.commit()
        await session.refresh(db_conv)
        return db_conv


async def get_conversations(
    user_id: int,  # 新增参数
    limit: int = 50, 
    offset: int = 0
) -> tuple[list[Conversation], int]:
    """获取指定用户的对话历史"""
    async with await get_session() as session:
        # 查询总数（按用户过滤）
        count_query = select(func.count()).select_from(
            Conversation
        ).where(Conversation.user_id == user_id)
        total = (await session.execute(count_query)).scalar() or 0

        # 查询分页数据
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)  # 按用户过滤
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        items = list(result.scalars().all())

        return items, total
```

#### 2. 更新聊天路由
**文件**: `backend/app/routers/chat.py`

**任务**:
- [ ] 在 `/send` 端点添加 `current_user` 依赖
- [ ] 保存对话时传入 `user_id`
- [ ] 在 `/history` 端点添加 `current_user` 依赖
- [ ] 按用户过滤历史记录
- [ ] 删除操作验证用户权限

**示例代码**:
```python
from app.dependencies.auth import get_current_user
from app.models.user import User

@router.post("/send", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    current_user: User = Depends(get_current_user)  # 新增
):
    """发送消息并获取 AI 回复"""
    try:
        # ... 现有逻辑
        
        # 6. 保存到数据库（传入 user_id）
        conv = ConversationCreate(
            user_input=req.message,
            assistant_response=result["response"],
            emotion=emotion_result.emotion,
            model_name=result["model_name"],
            tokens_used=result["usage"].get("total_tokens", 0),
        )
        await save_conversation(conv, user_id=current_user.id)  # 修改
        
        # ... 返回响应
```

#### 3. 更新 Self-Improving 模块
**文件**: `backend/app/self_improving/manager.py`, `storage.py`

**任务**:
- [ ] 记忆文件按用户隔离存储
- [ ] 目录结构: `memory/{user_id}/memory.md`
- [ ] 加载记忆时根据 `user_id` 读取对应文件

**目录结构**:
```
backend/app/self_improving/memory/
├── 1/
│   ├── memory.md
│   ├── projects/
│   └── domains/
├── 2/
│   ├── memory.md
│   └── ...
└── default/
    └── memory.md
```

#### 4. 数据库迁移脚本
**文件**: `backend/migrations/add_user_support.py`

**任务**:
- [ ] 创建 users 表
- [ ] 为 conversations 表添加 user_id 列
- [ ] 设置外键约束
- [ ] 数据迁移（现有数据标记为默认用户）

**SQL 示例**:
```sql
-- 创建 users 表
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
);

-- 为 conversations 添加 user_id
ALTER TABLE conversations ADD COLUMN user_id INTEGER;

-- 设置外键
ALTER TABLE conversations ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 为现有数据设置默认用户 ID（假设默认用户 ID 为 1）
UPDATE conversations SET user_id = 1 WHERE user_id IS NULL;
```

#### 5. 注册主路由
**文件**: `backend/app/main.py`

**任务**:
- [ ] 导入 auth router
- [ ] 注册到 FastAPI 应用

**示例代码**:
```python
from app.routers import auth

app.include_router(auth.router)
```

---

### Phase 2: 前端界面（中优先级）

#### 1. 创建认证 API 客户端
**文件**: `frontend/src/services/auth.ts`

**任务**:
- [ ] 注册 API
- [ ] 登录 API
- [ ] Token 存储（localStorage）
- [ ] 自动附加 Token 到请求头
- [ ] Token 刷新逻辑

**示例代码**:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// 请求拦截器：自动附加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理 401 错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，跳转到登录页
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data: RegisterData) => api.post('/auth/register', data),
  login: (data: LoginData) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (data: UpdateData) => api.put('/auth/me', data),
};
```

#### 2. 创建登录/注册页面
**文件**: 
- `frontend/src/pages/Login.tsx`
- `frontend/src/pages/Register.tsx`

**功能**:
- [ ] 登录表单（用户名、密码）
- [ ] 注册表单（用户名、邮箱、密码、确认密码）
- [ ] 表单验证
- [ ] 错误提示
- [ ] 登录成功后跳转

#### 3. 创建用户菜单
**文件**: `frontend/src/components/User/UserMenu.tsx`

**功能**:
- [ ] 显示当前用户信息（头像、昵称）
- [ ] 下拉菜单（个人资料、设置、退出登录）
- [ ] 未登录时显示"登录/注册"按钮

#### 4. 更新 App 组件
**文件**: `frontend/src/App.tsx`

**任务**:
- [ ] 检查登录状态
- [ ] 未登录时重定向到登录页
- [ ] 传递用户信息给子组件

---

### Phase 3: 数据迁移和测试（低优先级）

#### 1. 数据库迁移
- [ ] 执行迁移脚本
- [ ] 验证表结构
- [ ] 测试数据完整性

#### 2. 单元测试
- [ ] 用户注册测试
- [ ] 用户登录测试
- [ ] Token 验证测试
- [ ] 用户隔离测试

#### 3. 集成测试
- [ ] 完整注册流程
- [ ] 完整登录流程
- [ ] 多用户对话隔离
- [ ] 权限验证

---

## 🔧 技术细节

### 1. 密码安全
- **算法**: bcrypt
- **盐值**: 自动生成
- **强度**: 12 rounds
- **库**: `passlib[bcrypt]`

### 2. JWT Token
- **算法**: HS256
- **Access Token**: 7天有效期
- **Refresh Token**: 30天有效期
- **Payload**: `{sub: username, user_id: id, exp: timestamp}`

### 3. 数据隔离策略
- **对话记录**: 通过 `user_id` 外键隔离
- **记忆系统**: 按用户ID分目录存储
- **情感分析**: 每个用户独立的偏好学习
- **Self-Improving**: 用户专属的记忆文件

### 4. 权限控制
- **公开路由**: `/api/auth/register`, `/api/auth/login`
- **保护路由**: 所有其他 API 需要 Bearer Token
- **管理员路由**: 预留 `is_superuser` 检查

---

## 📋 实施步骤

### Step 1: 安装依赖
```bash
cd backend
pip install passlib[bcrypt] python-jose[cryptography] email-validator
```

### Step 2: 更新 settings.py
```python
# 添加 SECRET_KEY 配置
SECRET_KEY: str = "your-secret-key-change-in-production"
```

### Step 3: 执行数据库迁移
```bash
python backend/migrations/add_user_support.py
```

### Step 4: 注册路由
在 `main.py` 中添加：
```python
from app.routers import auth
app.include_router(auth.router)
```

### Step 5: 更新现有路由
- 修改 `chat.py` 添加用户依赖
- 修改 `database.py` 支持用户隔离
- 修改 self-improving 模块

### Step 6: 前端开发
- 创建登录/注册页面
- 实现 Token 管理
- 更新 API 调用

### Step 7: 测试
- 单元测试
- 集成测试
- 多用户场景测试

---

## ⚠️ 注意事项

### 1. 向后兼容
- 现有对话数据需要迁移到默认用户
- 提供"游客模式"选项（可选）

### 2. 安全性
- SECRET_KEY 必须从环境变量读取
- 生产环境使用强随机密钥
- HTTPS 强制（生产环境）
- CORS 配置限制

### 3. 性能
- 用户查询添加索引
- Token 验证缓存（可选）
- 大量用户时的分页优化

### 4. 用户体验
- 清晰的错误提示
- 密码强度要求
- 忘记密码功能（未来）
- 邮箱验证（未来）

---

## 🎯 预期效果

完成后，陈筱雪将具备：

✅ **多用户支持** - 多个用户独立使用  
✅ **数据隔离** - 每个用户的对话、记忆完全独立  
✅ **安全认证** - JWT Token + bcrypt 密码加密  
✅ **个性化体验** - 每个用户有自己的偏好和学习  
✅ **隐私保护** - 用户只能访问自己的数据  

---

**下一步**: 开始实施 Phase 1 的后端核心功能更新。
