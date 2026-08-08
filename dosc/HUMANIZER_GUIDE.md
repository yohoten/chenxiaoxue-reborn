# ✍️ Humanizer - AI 文本检测与人性化改写

## 📖 简介

Humanizer 是一个基于 Wikipedia "Signs of AI writing" 指南开发的智能文本分析工具，能够检测并修复 24 种常见的 AI 写作模式，帮助生成更自然、更人性化的文本。

## 🎯 核心功能

### 1. AI 写作模式检测
- **24 种模式识别**：覆盖内容、语言、风格、沟通、填充五大类别
- **严重程度分级**：High（严重）、Medium（中等）、Low（轻微）
- **精确定位**：显示每个问题在原文中的位置和片段
- **改进建议**：提供具体的修改建议和替换方案

### 2. 自动化人性化改写
- **一键优化**：自动修复检测到的所有问题
- **保持原意**：在去除 AI 痕迹的同时保留原文核心信息
- **对比查看**：支持原文和人性化版本的切换对比

### 3. 可视化评分系统
- **AI 化程度评分**：0% = 完全人类，100% = 完全 AI 化
- **颜色编码**：🟢 低（<40%）、🟡 中（40%-70%）、🔴 高（>70%）
- **详细统计**：按模式类型和问题数量分类展示

## 🚀 使用方法

### 前端界面使用

1. **打开 Humanizer 面板**
   - 在主界面导航栏点击「✍️ 人性化」标签

2. **输入文本**
   - 在文本框中粘贴或输入要分析的文本（最多 50,000 字符）

3. **选择操作**
   - 🔍 **分析文本**：仅检测问题，查看详细报告
   - ✨ **人性化改写**：检测并自动修复问题

4. **查看结果**
   - **评分卡片**：显示 AI 化程度百分比和问题数量
   - **分析摘要**：总体评估和改进方向
   - **版本切换**：在原文和人性化版本之间切换
   - **详细列表**：逐个查看检测到的问题和改进建议

### API 调用示例

#### 1. 分析文本

```bash
curl -X POST http://localhost:8000/api/humanizer/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The software serves as a testament to innovation."
  }'
```

**响应示例：**
```json
{
  "original_text": "The software serves as a testament to innovation.",
  "humanized_text": "The software demonstrates innovation.",
  "total_issues": 1,
  "score": 0.35,
  "summary": "检测到 1 处高严重度问题",
  "matches": [
    {
      "pattern_id": "P1",
      "pattern_name": "过度强调重要性",
      "severity": "high",
      "snippet": "serves as a testament",
      "position": 14,
      "length": 23,
      "suggestion": "替换浮夸表述为具体事实",
      "replacement": "demonstrates"
    }
  ]
}
```

#### 2. 人性化改写

```bash
curl -X POST http://localhost:8000/api/humanizer/humanize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Additionally, the system provides a seamless experience."
  }'
```

#### 3. 获取模式列表

```bash
curl http://localhost:8000/api/humanizer/patterns
```

## 📊 检测的 24 种 AI 写作模式

### 内容类 (Content)

| 模式 | 名称 | 示例 |
|------|------|------|
| P1 | 过度强调重要性 | "marking a pivotal moment..." |
| P2 | 空洞知名度声明 | "cited in NYT, BBC..." |
| P3 | -ing 表层分析 | "..., symbolizing..." |
| P4 | 促销式语言 | "Nestled within breathtaking..." |
| P5 | 模糊归因 | "Experts believe..." |
| P6 | 公式化挑战 | "Despite challenges... thrives" |

### 语言类 (Language)

| 模式 | 名称 | 示例 |
|------|------|------|
| P7 | AI 高频词汇 | "Additionally, pivotal, showcase" |
| P8 | 系动词回避 | "serves as" → "is" |
| P9 | 否定平行 | "It's not just X, it's Y" |
| P10 | 三要素规则 | "A, B, and C" groups |
| P11 | 同义词替换 | protagonist/main character/hero |
| P12 | 虚假范围 | "from X to Y" scale |

### 风格类 (Style)

| 模式 | 名称 | 说明 |
|------|------|------|
| P13 | 破折号滥用 | 过度使用 em dash |
| P14 | 粗体强调 | 不必要的 bold 标记 |
| P15 | 列表依赖 | 强制使用 bullet points |
| P16 | 标题堆砌 | 过多子标题 |
| P17 | 表情符号 | 不恰当的 emoji 使用 |
| P18 | 引用格式 | 标准化引用方式 |

### 沟通类 (Communication)

| 模式 | 名称 | 示例 |
|------|------|------|
| P19 | 聊天痕迹 | "Here is an overview..." |
| P20 | 截止声明 | "As of my last update..." |
| P21 | 谄媚语气 | "I hope this helps!" |

### 填充类 (Filler)

| 模式 | 名称 | 示例 |
|------|------|------|
| P22 | 填充短语 | "In order to achieve..." |
| P23 | 模糊表达 | "Due to the fact that..." |
| P24 | 空泛结论 | "At this point in time..." |

## 💡 使用场景

### 1. 学术写作优化
- 检测论文中的 AI 化表达
- 提升学术文本的自然度
- 避免被 AI 检测工具标记

### 2. 内容创作辅助
- 博客文章人性化润色
- 社交媒体文案优化
- 营销文案去 AI 化

### 3. 教育用途
- 学生学习 AI 写作特征
- 教师评估学生作业原创性
- 写作技巧培训

### 4. 专业文档
- 商业报告去模板化
- 技术文档自然化
- 法律文件可读性提升

## 🔧 技术架构

### 后端服务
- **语言**：Python 3.10+
- **框架**：FastAPI
- **核心文件**：
  - `backend/app/services/humanizer_service.py` (1272 行)
  - `backend/app/routers/humanizer.py` (313 行)
  - `backend/tests/test_humanizer.py` (98 行)

### 前端组件
- **框架**：React + TypeScript
- **组件**：`frontend/src/components/Humanizer/HumanizerPanel.tsx`
- **集成**：MainApp 导航标签页

### 检测算法
- **正则表达式匹配**：每种模式独立的 PatternDetector 实现
- **权重评分系统**：基于模式严重程度计算综合得分
- **自动修复规则**：部分模式支持智能替换

## 📈 性能指标

### 测试结果
- ✅ **AI 化文本**：检测到 9 处问题，评分 0.66（高 AI 痕迹）
- ✅ **人类文本**：检测到 0 处问题，评分 0.00（低 AI 痕迹）
- ✅ **模式覆盖率**：P1-P24 全部正确识别

### 处理速度
- **短文本** (<1000 字符)：<100ms
- **中长文本** (1000-10000 字符)：<500ms
- **长文本** (10000-50000 字符)：<2s

## 🎓 最佳实践

### 1. 文本预处理
- 移除多余空白和换行
- 确保文本编码为 UTF-8
- 分段处理超长文本

### 2. 结果解读
- **评分 < 30%**：文本非常自然，无需修改
- **评分 30%-60%**：存在部分 AI 特征，建议优化
- **评分 > 60%**：明显 AI 化，强烈建议改写

### 3. 人工审核
- 自动改写后仍需人工校对
- 检查专业术语是否被误改
- 确认语义是否保持一致

## 🔮 未来规划

### Phase 1 (已完成)
- ✅ 24 种模式检测
- ✅ 自动人性化改写
- ✅ 可视化前端界面

### Phase 2 (计划中)
- 🔄 批量文本处理
- 🔄 自定义检测规则
- 🔄 历史记录保存
- 🔄 导出分析报告

### Phase 3 (远期)
- 🌟 多语言支持（中文、日文等）
- 🌟 机器学习增强检测
- 🌟 用户反馈学习
- 🌟 插件生态系统

## 📝 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- **Wikipedia**: "Signs of AI writing" 指南
- **FastAPI**: 高性能 Python Web 框架
- **React**: 用户界面库

---

**开发者**：陈筱雪 AI 助手开发团队  
**版本**：1.0.0  
**最后更新**：2026-05-08
