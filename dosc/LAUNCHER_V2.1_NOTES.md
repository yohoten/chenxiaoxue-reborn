# launcher.bat v2.1 更新说明

## 🎯 主要改进

### 1. **修复虚拟环境路径问题** ✅
- **问题**: `uvicorn` 命令找不到正确的 Python 解释器
- **解决**: 使用 `.venv\Scripts\python.exe -m uvicorn` 替代直接调用 `uvicorn`
- **优势**: 避免虚拟环境激活时的路径解析问题

### 2. **修复 .env 编码问题** ✅
- **问题**: slowapi 读取 .env 时出现 `UnicodeDecodeError: 'gbk' codec can't decode byte`
- **临时方案**: 在 `backend/app/main.py` 中注释掉 limiter 初始化
- **建议**: 确保 .env 文件使用 UTF-8 编码（无 BOM）

### 3. **完善依赖安装流程** ✅
- 自动检查并创建虚拟环境
- 自动升级 pip
- 静默安装依赖（减少输出干扰）
- 错误检测和提示

### 4. **改进前端启动方式** ✅
- **问题**: `npm run dev` 在包含 `&` 的路径下失败
- **解决**: 直接使用 `node node_modules/vite/bin/vite.js`
- **优势**: 绕过 npm 脚本的路径解析问题

### 5. **增强错误处理** ✅
- 所有关键操作都有错误检测
- 清晰的错误提示信息
- 提供解决方案（如"请先执行 [1] 环境安装"）

### 6. **优化用户体验** ✅
- 更清晰的进度显示（[1/6], [2/6]...）
- 友好的成功/失败提示
- 服务地址一目了然
- 添加等待时间提示

## 📋 功能列表

| 模式 | 命令 | 功能 | 说明 |
|------|------|------|------|
| 环境安装 | `launcher.bat setup` | 一键安装所有依赖 | 首次使用必选 |
| 开发模式 | `launcher.bat dev` | 后端 + 前端双窗口 | 日常开发推荐 |
| 仅后端 | `launcher.bat backend` | 只启动 FastAPI | API 调试用 |
| 仅前端 | `launcher.bat frontend` | 只启动 Vite | 前端开发用 |
| Tauri 桌面 | `launcher.bat tauri` | Rust 原生应用 | 需要 Rust |
| 测试模式 | `launcher.bat test` | 自动打开浏览器 | 快速测试 |
| 生产模式 | `launcher.bat prod` | 多 worker 部署 | 生产环境 |

## 🔧 技术细节

### 路径处理
```batch
for %%i in ("%~dp0.") do set "ROOT=%%~fi"
```
- 使用 `for` 循环获取完整路径
- 正确处理包含特殊字符（如 `&`）的路径

### 启动命令格式
```batch
start "" cmd /k "cd /d "%BACKEND%" && .venv\Scripts\python.exe -m uvicorn ..."
```
- `start ""`: 空标题，避免路径解析问题
- `cmd /k`: 保持窗口打开
- `cd /d`: 切换驱动器和目录
- `%BACKEND%`: 使用引号包裹的变量

### 等待函数
```batch
:wait_seconds
if exist "%SystemRoot%\System32\timeout.exe" (
    timeout /t %1 /nobreak >nul
) else (
    ping 127.0.0.1 -n %1 >nul
)
```
- 优先使用 `timeout`（更精确）
- 降级到 `ping`（兼容性更好）

## ⚠️ 已知限制

### 1. 路径中的 `&` 符号
**影响**: PowerShell 中直接调用会失败  
**解决**: 
- 在 CMD 中使用：`cd /d "路径" && launcher.bat`
- 或双击运行

### 2. slowapi Limiter 禁用
**原因**: .env 编码问题导致启动失败  
**状态**: 已临时禁用  
**恢复方法**: 
1. 确保 .env 是 UTF-8 编码
2. 取消 `backend/app/main.py` 第 27-33 行的注释
3. 重启后端

### 3. AI 模型配置
**现状**: "AI Router 初始化完成: 0 个模型可用"  
**原因**: .env 中未配置 API Key  
**解决**: 编辑 `.env` 文件，填入至少一个模型的 API Key

## 🚀 快速开始

### 首次使用
```batch
:: 1. 打开 CMD（不是 PowerShell）
:: 2. 切换到项目目录
cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"

:: 3. 安装环境
launcher.bat setup

:: 4. 编辑 .env 文件，填入 API Key
notepad backend\.env

:: 5. 启动开发模式
launcher.bat dev
```

### 日常开发
```batch
:: 直接双击 launcher.bat
:: 选择 [2] 开发模式

:: 或在 CMD 中
cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"
launcher.bat dev
```

## 📊 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | Vite 开发服务器 |
| 后端 | http://localhost:8000 | FastAPI |
| API 文档 | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc 文档 |
| 健康检查 | http://localhost:8000/health | 健康状态 |
| MCP Server | http://localhost:8000/mcp | MCP 协议端点 |

## 💡 最佳实践

1. **移动项目到简单路径**
   ```
   原路径: d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn
   新路径: d:\projects\chenxiaoxue-reborn
   ```

2. **定期更新依赖**
   ```batch
   cd backend
   .venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
   ```

3. **清理缓存**
   ```batch
   :: 前端缓存
   cd frontend
   rm -rf node_modules/.vite
   
   :: 后端缓存
   cd backend
   rm -rf __pycache__
   ```

4. **查看日志**
   - 后端日志直接在启动窗口显示
   - 前端日志在浏览器控制台（F12）

## 🐛 故障排除

### Q1: "系统找不到指定的路径"
**A**: 在 CMD 中使用 `cd /d` 切换目录后再运行

### Q2: "ModuleNotFoundError: No module named 'xxx'"
**A**: 运行 `launcher.bat setup` 重新安装依赖

### Q3: 中文显示乱码
**A**: 确保在 CMD 窗口中运行（不是 PowerShell）

### Q4: 端口被占用
**A**: 修改 `backend/app/main.py` 或 `frontend/vite.config.ts` 中的端口

### Q5: AI 模型不可用
**A**: 编辑 `backend/.env`，填入有效的 API Key

---

**版本**: v2.1  
**更新日期**: 2026-07-21  
**作者**: 陈筱雪 AI 助手开发团队
