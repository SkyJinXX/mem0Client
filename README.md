# 🧠 Mem0 Client - AI Memory Management Tool

一个功能强大的 Mem0 客户端工具，用于上传和管理您的AI记忆。支持自动智能提取和原样存储两种模式，完美适合处理聊天记录、笔记和各种文本内容。

## ✨ 主要功能

### 📤 智能上传
- **多格式支持**：markdown (.md)、文本 (.txt) 文件
- **智能解析**：自动识别聊天对话格式并解析成结构化数据
- **处理模式选择**：
  - `auto` - AI智能提取和处理（推荐）
  - `raw` - 原样存储，保持原始内容
- **🎯 高级配置**（NEW！）：
  - `custom_instructions` - 自定义AI处理指令
  - `includes` - 指定要特别包含的信息类型
  - `excludes` - 指定要排除的敏感或无关信息
- **批量上传**：支持目录批量上传，递归处理子目录
- **元数据标记**：自动记录文件信息、上传时间等

### 🔍 强大搜索
- **语义搜索**：基于内容相似性的智能搜索
- **时间范围搜索**：按天数或具体日期范围查找记忆
- **关联搜索**：查找与指定内容相关的历史记忆
- **过滤支持**：支持用户ID、来源等多种过滤条件

### 📊 专业应用
- **周报生成**：自动收集指定周期的记忆和相关历史记忆
- **统计分析**：用户记忆统计、来源分布、活跃度分析
- **数据导出**：支持JSON格式导出搜索结果和报告

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件（参考 `env_example.txt`）：

```bash
# 从 https://app.mem0.ai 获取API密钥
MEM0_API_KEY=your_mem0_api_key_here

# 可选：设置默认用户ID
DEFAULT_USER_ID=your_user_id
```

### 3. 验证配置

```bash
python cli.py config-check
```

## 💻 命令行工具使用

### 上传功能

```bash
# 基本上传
python cli.py upload-text "这是一段要记录的内容" --extract-mode auto
python cli.py upload-file chat_log.md --user-id my_user

# 📋 高级配置上传 (NEW!)
# 使用自定义指令控制AI处理方式
python cli.py upload-text "技术API文档" \
  --user-id my_user \
  --custom-instructions "请专注于提取API接口信息和参数，忽略认证凭据" \
  --includes "API endpoints, parameters, return values" \
  --excludes "passwords, credentials, personal information" \
  --infer  # 启用智能推理（默认）

# 原始存储模式（不进行智能推理）
python cli.py upload-text "重要的原始数据记录" \
  --user-id my_user \
  --no-infer  # 关闭智能推理，保存原始内容

# 文件上传也支持高级配置
python cli.py upload-file meeting_notes.md \
  --custom-instructions "提取会议决策和行动项，忽略个人联系信息" \
  --includes "decisions, action items, timelines" \
  --excludes "phone numbers, email addresses, personal names" \
  --infer  # 智能推理提取关键信息

# 批量上传目录
python cli.py upload-directory ./chat_logs --extract-mode auto --recursive

# 上传时添加元数据
python cli.py upload-text "重要会议记录" --metadata '{"source":"meeting", "category":"work"}'
```

### 搜索功能

```bash
# 语义搜索
python cli.py search "Python编程相关的讨论" --limit 10

# 时间范围搜索
python cli.py search-time --days 7 --query "项目进展"
python cli.py search-time --start-date 2024-01-01 --end-date 2024-01-07

# 查找相关记忆
python cli.py search-related "上周的工作总结" --exclude-days 7
```

### 报告生成

```bash
# 生成上周的周报数据
python cli.py weekly-report --weeks-back 1 --output weekly_report.json

# 查看用户统计
python cli.py stats --user-id my_user
```

## 🌐 Web界面使用

启动Web界面：

```bash
streamlit run web_app.py
```

然后在浏览器中访问 `http://localhost:8501`

### Web界面功能
- 📤 **上传**：支持文本输入和文件上传
- 🔍 **搜索**：直观的搜索界面和结果展示
- 📅 **时间搜索**：可视化时间范围选择
- 📊 **周报**：一键生成周报数据和可视化展示
- 📈 **统计**：用户记忆统计图表

## 📁 项目结构

```
mem0-client/
├── cli.py              # 命令行工具入口
├── web_app.py          # Web界面应用
├── config.yaml         # 配置文件
├── requirements.txt    # Python依赖
├── env_example.txt     # 环境变量示例
└── core/
    ├── config.py       # 配置管理
    ├── parser.py       # 文件解析器
    ├── uploader.py     # 上传处理器
    └── searcher.py     # 搜索引擎
```

## ⚙️ 配置选项

编辑 `config.yaml` 来自定义设置：

```yaml
# 默认设置
defaults:
  user_id: "default_user"        # 默认用户ID
  extract_mode: "auto"           # 默认提取模式
  batch_size: 10                 # 批处理大小

# 文件处理
file_processing:
  supported_formats:             # 支持的文件格式
    - ".md"
    - ".txt"
    - ".markdown"
  max_file_size_mb: 10          # 最大文件大小(MB)

# 搜索设置
search:
  default_limit: 10             # 默认搜索结果数量
  max_limit: 100                # 最大搜索结果数量

# 调试设置
debug:
  enable_api_logging: true      # 是否显示API调用详细日志
```

## 📝 使用场景

### 1. 聊天记录管理
```bash
# 上传ChatGPT对话记录
python cli.py upload-file chatgpt_conversation.md --extract-mode auto

# 搜索编程相关的对话
python cli.py search "Python编程" --limit 5
```

### 2. 工作笔记整理
```bash
# 批量上传工作笔记
python cli.py upload-directory ./work_notes --user-id work

# 生成本周工作记忆
python cli.py weekly-report --weeks-back 1 --user-id work
```

### 3. 学习资料归档
```bash
# 上传学习笔记（原样保存）
python cli.py upload-file study_notes.txt --extract-mode raw

# 查找相关学习资料
python cli.py search-related "机器学习基础概念"
```

## 🎯 高级配置功能（NEW！）

### Custom Instructions（自定义指令）
通过自定义指令，您可以精确控制AI如何处理和提取内容：

```bash
# 技术文档处理
--custom-instructions "请专注于提取API接口、参数和返回值，忽略具体的认证凭据"

# 会议记录处理  
--custom-instructions "提取会议的核心决策、行动项和时间安排，保持结构化格式"

# 学习笔记处理
--custom-instructions "提取编程概念、代码示例和技术要点，这是学习材料"
```

### Includes（包含配置）
指定要特别关注和包含的信息类型：

```bash
# 技术相关
--includes "API endpoints, parameters, return values, technical concepts"

# 业务相关
--includes "decisions, action items, timelines, business requirements"

# 学习相关  
--includes "code examples, programming concepts, learning insights"
```

### Excludes（排除配置）
指定要排除的敏感或无关信息：

```bash
# 排除敏感信息
--excludes "passwords, credentials, personal information, contact details"

# 排除个人数据
--excludes "personal names, email addresses, phone numbers, ID numbers"

# 排除临时信息
--excludes "temporary notes, debugging info, draft content"
```

### Infer（智能推理控制）
控制是否启用AI智能推理和提取记忆：

```bash
# 启用智能推理（默认行为）
--infer

# 关闭智能推理，保存原始内容
--no-infer
```

**infer 参数说明：**
- `--infer` (True): AI会智能分析内容，推理并提取关键记忆点
- `--no-infer` (False): 保存原始消息内容，不进行智能处理和推理

**使用场景：**
- **infer=True**: 适合日常对话、学习笔记、会议记录等需要智能提取的内容
- **infer=False**: 适合需要保持原始格式的代码、配置文件、精确数据记录等

### Web界面的预设排除选项
在Web界面中，我们提供了便捷的预设排除选项：
- 个人姓名
- 联系方式  
- 地址信息
- 财务信息
- 密码/秘钥
- 身份证号
- 其他敏感信息

### 组合使用示例

```python
# 在Python代码中使用
from core.uploader import MemoryUploader
from core.config import Config

config = Config()
uploader = MemoryUploader(config)

# 示例1：技术文档上传 - 智能提取
result = uploader.upload_text(
    content=tech_document,
    custom_instructions="专注提取API接口和技术规范，排除认证信息",
    includes="API endpoints, technical specifications, parameters",
    excludes="passwords, credentials, personal data",
    infer=True  # 启用智能推理
)

# 示例2：重要数据记录 - 原样保存  
result = uploader.upload_text(
    content=important_data,
    custom_instructions="这是重要的结构化数据，需要保持完整性",
    infer=False  # 关闭智能推理，保存原始内容
)

# 示例3：会议记录上传 - 提取关键信息
result = uploader.upload_file(
    file_path="meeting_notes.md",
    custom_instructions="提取会议决策、行动项和时间安排",
    includes="decisions, action items, deadlines, assignments",
    excludes="personal contact information, private discussions",
    infer=True  # 智能提取关键业务信息
)
```

## 🔧 高级用法

### 文件格式支持

工具能自动识别以下聊天记录格式：

```markdown
**User:** 你好，我想学习Python
**Assistant:** 你好！我很乐意帮助你学习Python...

## User
请介绍一下Python的基础语法

## Assistant  
Python的基础语法非常简洁...

User: 什么是变量？
Assistant: 变量是用来存储数据的容器...

[User] 如何定义函数？
[Assistant] 在Python中定义函数使用def关键字...
```

### 元数据使用

```bash
# 添加丰富的元数据
python cli.py upload-text "项目会议纪要" \
  --metadata '{"source":"meeting", "project":"AI", "participants":["Alice","Bob"], "date":"2024-01-15"}'

# 搜索时利用元数据
python cli.py search "会议" --limit 20
```

### API集成

您也可以在自己的Python项目中使用这些核心组件：

```python
from core.config import Config
from core.uploader import MemoryUploader
from core.searcher import MemorySearcher

# 初始化
config = Config()
uploader = MemoryUploader(config)
searcher = MemorySearcher(config)

# 上传记忆
result = uploader.upload_text("要记录的内容", user_id="my_user")

# 搜索记忆
results = searcher.search_by_query("搜索关键词", user_id="my_user")
```

## 🔍 调试功能（NEW！）

### API调用日志
工具现在支持详细的API调用日志，帮助你了解发送给Mem0的具体参数：

```bash
# 在配置文件中启用
debug:
  enable_api_logging: true

# 日志输出示例
🔍 [DEBUG] Mem0.add() 调用参数:
  📱 user_id: my_user
  💬 messages[0]: role='user', content='这是测试内容...'
  🎯 custom_instructions: '请专注于提取技术要点'
  ✅ includes: 'technical concepts, API information'
  ❌ excludes: 'personal information, credentials'
  📋 metadata: {'upload_time': '2025-01-15T10:30:00', 'extract_mode': 'auto', ...}
```

### 日志内容说明
- **user_id**: 用户标识
- **messages**: 发送的消息内容（自动截取前20字符）
- **custom_instructions**: 自定义AI处理指令
- **includes**: 要包含的信息类型
- **excludes**: 要排除的信息类型  
- **metadata**: 元数据信息（长字段自动截取）

### 控制选项
```yaml
# 完全关闭调试日志
debug:
  enable_api_logging: false
```

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   ```bash
   # 检查配置
   python cli.py config-check
   
   # 确认API密钥设置正确
   echo $MEM0_API_KEY
   ```

2. **文件上传失败**
   ```bash
   # 检查文件格式和大小
   # 支持格式：.md, .txt, .markdown
   # 最大大小：10MB（可在config.yaml中修改）
   ```

3. **搜索结果为空**
   ```bash
   # 检查用户ID是否正确
   python cli.py stats --user-id your_user_id
   
   # 尝试更广泛的搜索词
   python cli.py search "关键词" --limit 50
   ```

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Mem0 官方文档](https://docs.mem0.ai/)
- [Mem0 平台](https://app.mem0.ai/)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)

---

🧠 **开始构建您的AI记忆库吧！** 