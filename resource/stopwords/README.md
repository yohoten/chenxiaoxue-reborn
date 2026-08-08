# 停用词模块说明

## 目录结构

stopwords/
├── stopword.txt                  # 综合性停用词表
├── 中文停用词库.txt              # 常用中文停用词库
├── 哈工大停用词表.txt            # 哈尔滨工业大学提供的停用词表
├── 四川大学机器智能实验室停用词库.txt # 四川大学机器智能实验室整理
└── 百度停用词列表.txt            # 百度搜索引擎相关停用词

## 使用方法

### 在代码中使用停用词管理器

```python
from stopwords_manager import stopwords_manager

# 检查单词是否为停用词
if stopwords_manager.is_stopword("的"):
    print("这是停用词")

# 获取所有停用词
all_stopwords = stopwords_manager.get_stopwords()

# 获取停用词来源列表
sources = stopwords_manager.get_sources()
```

### 直接使用工具函数

```python
from stopwords_manager import is_stopword, get_stopwords

# 检查单词是否为停用词
if is_stopword("的"):
    print("这是停用词")

# 获取所有停用词
all_stopwords = get_stopwords()
```

## 文件来源

停用词文件来源于公开的中文自然语言处理资源：

1. **stopword.txt** - 综合性停用词表
2. **中文停用词库.txt** - 常用中文停用词库
3. **哈工大停用词表.txt** - 哈尔滨工业大学提供的停用词表
4. **四川大学机器智能实验室停用词库.txt** - 四川大学机器智能实验室整理
5. **百度停用词列表.txt** - 百度搜索引擎相关停用词

## 维护说明

- 所有停用词文件会在程序启动时自动加载
- 可以通过 `stopwords_manager.add_stopword()` 和 `stopwords_manager.remove_stopword()` 动态管理停用词
- 停用词管理器会自动去重，确保不会有重复的停用词
