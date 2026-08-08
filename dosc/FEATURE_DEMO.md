# Chen筱雪 Reborn - 功能演示指南

## 📸 界面预览

### 1. 主聊天界面
**访问**: http://localhost:5175  
**标签**: 💬 对话

**主要特性**:
- ✅ 左侧角色动画面板（350px 宽度）
- ✅ ECG 心电图状态栏
- ✅ 导航按钮（4个标签页）
- ✅ 快速操作栏（导出/主题/清空）
- ✅ 右侧消息列表（自动滚动）
- ✅ 底部输入框（Enter 发送）
- ✅ GIF 背景轮播（30秒切换）

**交互说明**:
1. 在输入框输入消息
2. 按 Enter 或点击"发送"按钮
3. 观察 AI 回复的打字机效果
4. 查看左侧角色情感变化
5. ECG 波形随系统状态变化

---

### 2. 组件展示页面
**访问**: http://localhost:5175  
**标签**: 🎨 组件

**展示内容**:
- 🎯 所有按钮变体（default/primary/danger/secondary/nav）
- 🎭 角色面板（带动画和情感标签）
- 💚 ECG 状态栏（动态波形）
- 💬 聊天气泡（用户/AI 样式）
- ⚡ 快速操作栏
- 🎨 颜色系统（4种主题色）

**用途**:
- UI 开发参考
- 样式调试
- 组件测试
- 设计文档

---

### 3. 设置页面
**访问**: http://localhost:5175  
**标签**: ⚙️ 设置

**显示信息**:
- 模型配置状态
- API 连接模式（MCP/直接）
- 当前主题
- 版本信息
- 技术架构

---

### 4. 梦境空间
**访问**: http://localhost:5175  
**标签**: 🌙 梦境

**状态**: 开发中  
**占位符**: 空状态图标 + 提示文本

---

## 🎬 功能演示步骤

### 演示 1: 智能对话
1. 打开浏览器访问 http://localhost:5175
2. 在输入框输入："你好，陈筱雪！"
3. 按 Enter 发送
4. 观察：
   - ✅ AI 回复的打字机效果
   - ✅ 左侧角色情感变化（平静 → 开心）
   - ✅ ECG 波形活跃
   - ✅ 消息气泡的时间戳和模型标注

### 演示 2: 背景轮播
1. 等待 30 秒
2. 观察背景 GIF 自动切换
3. 或者刷新页面查看不同背景

### 演示 3: 角色动画
1. 观察左侧角色面板
2. 等待眨眼效果触发（约3秒间隔）
3. 发送不同情感的消息观察角色反应

### 演示 4: 快速操作
1. 点击"🗑️ 清空"按钮
2. 确认消息列表被清空
3. 尝试其他按钮（导出、主题）

### 演示 5: 组件展示
1. 点击"🎨 组件"标签
2. 滚动查看所有组件
3. 悬停按钮查看 hover 效果
4. 观察颜色系统展示

---

## 🎨 视觉特色

### 像素风格元素
- **边框**: 3px 实线，深蓝色 (#2a3b5a)
- **字体**: Zpix / Press Start 2P
- **阴影**: 4px 偏移
- **圆角**: 0px（保持像素风格）
- **动画**: step-end 关键帧

### 颜色方案
```
背景色:     #1a1a2e (深蓝)
文字色:     #e0e0e0 (浅灰)
高亮色:     #ff9d00 (橙色)
强调色:     #4a77c5 (蓝色)
成功色:     #3aff5e (绿色)
边框色:     #2a3b5a (深蓝)
```

### 动画效果
- **打字机光标**: █ 闪烁
- **加载指示器**: ... 动画
- **淡入效果**: pixel-fade-in
- **眨眼效果**: brightness 滤镜
- **ECG 波形**: Canvas 实时绘制

---

## 🔍 调试技巧

### 检查背景加载
```javascript
// 在浏览器控制台运行
document.querySelectorAll('.background-layer img')
```

### 检查角色图片
```javascript
// 查看角色面板
document.querySelector('.character-panel img')
```

### 检查 ECG 动画
```javascript
// 查看 Canvas
document.querySelector('.ecg-status-bar canvas')
```

### 查看网络请求
```
浏览器开发者工具 → Network 标签
筛选: /api/chat
```

---

## 📱 响应式测试

### 桌面端 (>768px)
- 左右分栏布局
- 左侧固定 350px
- 右侧自适应

### 移动端 (<768px)
- 上下堆叠布局
- 左侧面板最大 300px
- 触摸友好按钮

**测试方法**:
1. F12 打开开发者工具
2. 点击设备工具栏图标
3. 选择不同设备尺寸
4. 观察布局变化

---

## 🐛 常见问题排查

### Q1: 背景不显示
**检查**:
1. 文件是否存在于 `public/assets/backgrounds/`
2. 后端 `/api/resources/backgrounds` 是否返回数据
3. 浏览器控制台是否有 404 错误

**解决**:
```bash
# 重新复制资源
xcopy "旧项目路径\resource\Background Image\*.gif" "frontend\public\assets\backgrounds\" /Y
```

### Q2: 角色图片不显示
**检查**:
1. `CharacterPanel.tsx` 中的路径是否正确
2. 文件是否存在于 `public/assets/characters/`

**解决**:
```typescript
// 检查 CHARACTER_IMAGES 数组
console.log(CHARACTER_IMAGES)
```

### Q3: ECG 不动画
**检查**:
1. Canvas 是否渲染
2. `isActive` prop 是否为 true
3. 浏览器是否支持 requestAnimationFrame

**解决**:
```typescript
// 添加调试日志
console.log('ECG isActive:', isActive)
```

### Q4: TypeScript 报错
**解决**:
```bash
cd frontend
npx tsc --noEmit
# 查看详细错误
```

---

## 🎯 性能优化建议

### 图片优化
- 使用 TinyPNG 压缩 GIF
- 考虑转换为 WebP 格式
- 实现懒加载（IntersectionObserver）

### 代码优化
- React.memo() 包裹纯组件
- useMemo() 缓存计算结果
- useCallback() 缓存回调函数

### 网络优化
- API 响应缓存（SWR/React Query）
- 图片预加载
- 代码分割（React.lazy）

---

## 📊 浏览器兼容性

| 浏览器 | 版本 | 状态 |
|--------|------|------|
| Chrome | 90+ | ✅ 完全支持 |
| Firefox | 88+ | ✅ 完全支持 |
| Safari | 14+ | ✅ 完全支持 |
| Edge | 90+ | ✅ 完全支持 |

**必需特性**:
- CSS Custom Properties
- Canvas API
- requestAnimationFrame
- Flexbox/Grid
- ES6+ JavaScript

---

**最后更新**: 2026-05-04  
**维护者**: Chen筱雪团队
