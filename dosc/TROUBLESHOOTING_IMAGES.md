# 陈筱雪 Reborn - 图片加载问题快速修复指南

## 🔍 问题诊断步骤

### 步骤 1: 运行诊断脚本

在项目根目录执行：

```bash
python test_resources.py
```

这将检查：
- ✅ RESOURCE_PATH 配置是否正确
- ✅ 角色图片目录是否存在
- ✅ 背景图片目录是否存在
- ✅ 资源文件数量统计

### 步骤 2: 确保后端服务运行

#### A. 安装依赖（首次运行或更新后）

```bash
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
```

#### B. 启动后端

```bash
# 在 backend 目录下
uvicorn app.main:app --reload --port 8000
```

**验证后端启动成功：**
- 打开浏览器访问：http://localhost:8000/docs
- 应该能看到 FastAPI 的 API 文档页面

### 步骤 3: 测试资源 API

在浏览器中访问以下 URL：

1. **背景图片列表**：
   ```
   http://localhost:8000/api/resources/backgrounds
   ```
   应该返回 JSON 格式的背景图片列表

2. **角色图片列表**：
   ```
   http://localhost:8000/api/resources/characters
   ```
   应该返回 JSON 格式的角色图片列表

3. **直接访问图片**（替换为实际文件名）：
   ```
   http://localhost:8000/api/resources/file/characters/20200922232838_082dc.gif
   ```
   应该能直接看到图片

### 步骤 4: 检查前端

1. **启动前端**（新终端）：
   ```bash
   cd frontend
   npm run dev
   ```

2. **打开浏览器开发者工具** (F12)：
   - 切换到 **Network** 标签
   - 刷新页面
   - 查找红色（失败）的请求
   - 点击失败的请求查看详细信息

3. **常见错误及解决**：

   | 错误类型 | 原因 | 解决方案 |
   |---------|------|---------|
   | 404 Not Found | 后端路由错误或文件不存在 | 检查 RESOURCE_PATH 配置 |
   | 500 Internal Server Error | 后端代码错误 | 查看后端控制台日志 |
   | Failed to fetch | 后端未启动 | 启动后端服务 |
   | CORS Error | 跨域问题 | 检查后端 CORS 配置 |

## 🛠️ 已修复的问题

### 1. RESOURCE_PATH 配置错误 ✅

**问题**：settings.py 中的 RESOURCE_PATH 计算逻辑可能指向错误的目录

**修复**：已调整查找顺序，优先使用当前项目的 resource 目录

```python
# 修复前：先查找父目录
new_resource = self.BASE_DIR.parent / "resource"

# 修复后：先查找当前项目
new_resource = self.BASE_DIR / "resource"
```

### 2. 角色图片路径 ✅

已在 CharacterPanel.tsx 中使用正确的 API 路径：
```typescript
'/api/resources/file/characters/20200922232838_082dc.gif'
```

## 📋 完整启动流程

### 方法 1: 使用一键启动脚本（推荐）

```bash
# Windows
scripts\dev.bat
```

### 方法 2: 手动启动

**终端 1 - 后端**：
```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**终端 2 - 前端**：
```bash
cd frontend
npm run dev
```

**访问应用**：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs

## ❓ 常见问题

### Q1: 后端启动报错 "No module named 'pydantic_settings'"

**解决**：
```bash
cd backend
.\.venv\Scripts\activate
pip install pydantic-settings
# 或者重新安装所有依赖
pip install -r requirements.txt
```

### Q2: 图片显示 404 错误

**排查**：
1. 运行 `python test_resources.py` 检查路径配置
2. 确认后端正在运行
3. 直接在浏览器访问图片 URL 测试
4. 检查后端控制台的错误日志

### Q3: 前端显示空白背景

**可能原因**：
- 后端未启动
- Background Image 目录为空
- API 请求失败

**解决**：
1. 确保后端运行在 8000 端口
2. 检查 `resource/Background Image/` 目录是否有图片文件
3. 查看浏览器控制台的错误信息

### Q4: 角色图片不显示但背景正常

**可能原因**：
- Character Image 目录路径错误
- 图片文件格式不支持
- 前端组件渲染问题

**解决**：
1. 运行诊断脚本检查目录
2. 确认图片格式为 .gif, .png, .jpg, .jpeg
3. 检查浏览器控制台是否有 JavaScript 错误

## 🔧 高级调试

### 查看后端日志

后端控制台会显示所有请求的日志：
```
INFO:     127.0.0.1:xxxxx - "GET /api/resources/backgrounds HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "GET /api/resources/file/characters/xxx.gif HTTP/1.1" 200 OK
```

如果看到 404 或 500 错误，说明有问题。

### 启用详细日志

修改 `backend/.env`：
```env
LOG_LEVEL=DEBUG
```

重启后端以查看详细日志。

### 测试单个图片加载

在浏览器控制台执行：
```javascript
fetch('/api/resources/file/characters/20200922232838_082dc.gif')
  .then(r => console.log('Status:', r.status))
  .catch(e => console.error('Error:', e));
```

## 📞 需要帮助？

如果以上步骤都无法解决问题，请提供：

1. `python test_resources.py` 的输出
2. 后端控制台的错误日志
3. 浏览器控制台的错误信息（F12 -> Console）
4. Network 标签中失败请求的详细信息

---

**最后更新**: 2026-05-05  
**版本**: 1.0