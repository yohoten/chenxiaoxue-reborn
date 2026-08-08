# Launcher 使用指南

## ⚠️ 重要提示

由于项目路径包含特殊字符 `&`（`chenxiaoxue-orgin&reborn_250825`），在某些环境下执行 `launcher.bat` 时可能会遇到路径解析问题。

## ✅ 推荐的执行方式

### 方法 1：在 CMD 中执行（推荐）

```batch
:: 打开 CMD，然后执行：
cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"
launcher.bat
```

### 方法 2：使用引号包裹路径

```batch
cmd /c "cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn" && launcher.bat dev"
```

### 方法 3：双击运行

直接双击 `launcher.bat` 文件即可打开交互式菜单。

## 📋 可用命令

```bash
launcher.bat          # 交互式菜单
launcher.bat setup    # 一键安装环境
launcher.bat dev      # 开发模式（后端 + 前端）
launcher.bat backend  # 仅启动后端
launcher.bat frontend # 仅启动前端
launcher.bat tauri    # Tauri 桌面模式
launcher.bat test     # 测试模式
launcher.bat prod     # 生产模式
```

## 🔧 常见问题

### Q1: 显示 "系统找不到指定的路径"

**原因**: 路径中的 `&` 符号被解释为命令分隔符

**解决方案**:
1. 使用上述"方法 1"在 CMD 中先切换目录再执行
2. 或者将项目移动到不含特殊字符的路径，例如：
   ```
   d:\projects\chenxiaoxue-reborn
   ```

### Q2: 中文显示乱码

**原因**: 文件编码问题

**解决方案**: 
- 确保在 CMD 窗口中运行（不是 PowerShell）
- 文件已使用 GBK 编码，应该能正常显示中文

### Q3: timeout 命令不存在

**解决方案**: 
- launcher.bat 已内置兼容的 `wait_seconds` 函数
- 会自动检测并使用 `ping` 作为替代方案

## 🎯 快速开始

### 首次使用

```batch
:: 1. 打开 CMD
:: 2. 切换到项目目录
cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"

:: 3. 安装环境
launcher.bat setup

:: 4. 启动开发模式
launcher.bat dev
```

### 日常开发

```batch
:: 启动开发环境（后端 + 前端）
cd /d "d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn"
launcher.bat dev

:: 访问应用
:: 前端: http://localhost:5173
:: 后端: http://localhost:8000
:: API 文档: http://localhost:8000/docs
```

## 💡 最佳实践建议

**强烈建议**将项目移动到不含特殊字符的路径，例如：

```
原路径: d:\chenxiaoxue-orgin&reborn_250825\chenxiaoxue-reborn
新路径: d:\projects\chenxiaoxue-reborn
```

这样可以避免所有与特殊字符相关的问题。

## 📝 技术细节

- **文件编码**: GBK（Windows 批处理标准）
- **路径处理**: 使用 `for %%i in ("%~dp0.") do set "ROOT=%%~fi"` 获取完整路径
- **等待函数**: 兼容 `timeout` 和 `ping` 两种方式
- **start 命令**: 使用 `start "" cmd /c "..."` 格式避免路径解析问题
