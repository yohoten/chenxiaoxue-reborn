# 用户认证系统 - 前端集成指南

## 📦 第一步：安装前端依赖

```bash
cd frontend
npm install react-router-dom@^6.20.0 axios@^1.6.0
```

或者使用 yarn：
```bash
cd frontend
yarn add react-router-dom@^6.20.0 axios@^1.6.0
```

---

## 🚀 第二步：启动前端开发服务器

```bash
cd frontend
npm run dev
```

访问：http://localhost:5173

---

## 🎯 功能说明

### 1. 路由结构

- `/login` - 登录页面（公开）
- `/register` - 注册页面（公开）
- `/*` - 主应用（需要认证）
  - `/chat` - 对话页面（默认）
  - `/history` - 历史记录
  - `/settings` - 设置
  - `/dream` - 梦境空间
  - `/starmap` - 星图
  - `/showcase` - 组件展示

### 2. 认证流程

#### 首次访问
1. 用户访问 http://localhost:5173
2. 检测到未登录，自动跳转到 `/login`
3. 用户输入用户名和密码
4. 登录成功后保存 Token，跳转到主页

#### 已登录状态
1. 用户访问任何受保护的路由
2. 检查 localStorage 中的 Token
3. 如果 Token 有效，正常显示页面
4. 如果 Token 无效或过期，跳转到登录页

#### 登出
1. 点击右上角用户菜单
2. 选择"退出登录"
3. 清除 Token，跳转到登录页

### 3. API 请求自动认证

所有 API 请求会自动附加 Token：

```typescript
// 无需手动添加 Authorization header
const response = await api.get('/api/chat/history');

// axios 拦截器会自动添加：
// Authorization: Bearer <token>
```

### 4. 401 错误自动处理

如果收到 401 错误（Token 过期或无效）：
- 自动清除本地 Token
- 自动跳转到登录页
- 用户需要重新登录

---

## 🎨 UI 组件

### 1. 登录页面 (`/login`)

**功能**：
- 用户名输入
- 密码输入
- 登录按钮
- 注册链接
- 错误提示

**样式**：
- 居中布局
- 渐变背景
- 像素风格边框
- 响应式设计

### 2. 注册页面 (`/register`)

**功能**：
- 用户名输入（必填，3-20字符）
- 邮箱输入（可选）
- 昵称输入（可选）
- 密码输入（必填，至少6字符）
- 确认密码（必填）
- 表单验证
- 注册按钮
- 登录链接

**验证规则**：
- 用户名：3-20个字符
- 邮箱：有效的邮箱格式（如果填写）
- 密码：至少6个字符
- 确认密码：必须与密码一致

### 3. 用户菜单（右上角）

**未登录状态**：
- 显示"🔐 登录"按钮
- 点击跳转到登录页

**已登录状态**：
- 显示用户头像（首字母）
- 显示用户昵称或用户名
- 下拉菜单包含：
  - 👤 个人资料（待实现）
  - ⚙️ 设置（待实现）
  - 🚪 退出登录

**交互**：
- 点击触发下拉菜单
- 点击外部区域关闭菜单
- 平滑动画效果

---

## 🔧 技术实现

### 1. Token 管理

**存储位置**：localStorage

**存储内容**：
- `access_token`: JWT Token
- `user_info`: 用户信息 JSON

**示例**：
```javascript
// 登录后
localStorage.setItem('access_token', 'eyJhbGci...');
localStorage.setItem('user_info', JSON.stringify({
  id: 1,
  username: 'admin',
  nickname: '管理员',
  ...
}));

// 获取 Token
const token = localStorage.getItem('access_token');

// 获取用户信息
const user = JSON.parse(localStorage.getItem('user_info'));
```

### 2. Axios 拦截器

**请求拦截器**：
```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**响应拦截器**：
```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，清除并跳转
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 3. 路由保护

**ProtectedRoute 组件**：
```typescript
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authAPI.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};
```

**PublicRoute 组件**（防止已登录用户访问登录页）：
```typescript
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authAPI.isAuthenticated();
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};
```

---

## 🧪 测试流程

### 1. 测试注册

1. 访问 http://localhost:5173/register
2. 填写注册表单：
   - 用户名：testuser
   - 邮箱：test@example.com（可选）
   - 昵称：测试用户（可选）
   - 密码：Test@123
   - 确认密码：Test@123
3. 点击"✨ 注册"
4. 注册成功后跳转到登录页

### 2. 测试登录

1. 访问 http://localhost:5173/login
2. 输入用户名和密码
3. 点击"🔐 登录"
4. 登录成功后跳转到主页

### 3. 测试数据隔离

1. 用用户 A 登录，发送几条消息
2. 退出登录
3. 用用户 B 登录
4. 查看历史，应该看不到用户 A 的消息

### 4. 测试 Token 过期

1. 登录后正常使用
2. 手动修改 localStorage 中的 Token 为无效值
3. 刷新页面或发送请求
4. 应该自动跳转到登录页

---

## 🐛 常见问题

### Q1: 登录后仍然跳转到登录页
**A**: 检查浏览器控制台是否有错误，确认 Token 是否正确保存。

### Q2: API 请求返回 401
**A**: 
- 检查后端是否正常运行
- 确认 SECRET_KEY 配置正确
- 检查 Token 格式是否正确

### Q3: 注册时提示用户名已存在
**A**: 尝试其他用户名，或删除已有用户。

### Q4: 无法看到用户菜单
**A**: 确认已登录，检查 localStorage 中是否有 `user_info`。

### Q5: 样式显示不正常
**A**: 
- 确认 CSS 文件正确加载
- 检查浏览器控制台是否有 CSS 错误
- 清除浏览器缓存后重试

---

## 📝 下一步优化建议

### 短期（已完成）
- ✅ 用户注册/登录
- ✅ JWT Token 认证
- ✅ 路由保护
- ✅ 数据隔离
- ✅ 用户菜单

### 中期（待实现）
- [ ] 个人资料编辑页面
- [ ] 头像上传功能
- [ ] 忘记密码功能
- [ ] 邮箱验证
- [ ] Token 自动刷新

### 长期（规划中）
- [ ] OAuth2 第三方登录（GitHub、Google等）
- [ ] 双因素认证（2FA）
- [ ] 用户权限管理
- [ ] 管理员后台
- [ ] 用户数据统计

---

## 🎉 完成！

现在陈筱雪 AI 助手已经具备完整的用户认证和多用户支持功能！

**主要特性**：
- 🔐 安全的用户注册和登录
- 🛡️ JWT Token 认证
- 📊 多用户数据完全隔离
- 🎨 美观的像素风格界面
- 📱 响应式设计
- ⚡ 流畅的用户体验

祝使用愉快！🌸
