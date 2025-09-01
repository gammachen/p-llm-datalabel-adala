# Adala Agent with LangSmith Tracing

这个项目展示了如何使用 LangSmith 来跟踪和监控 Adala 框架中的 Agent 调用步骤。

## 功能特性

- ✅ 详细的 LLM 调用跟踪
- ✅ 输入/输出记录
- ✅ 执行时间监控
- ✅ 元数据记录
- ✅ 错误处理和回退机制
- ✅ 可配置的项目和标签

## 安装依赖

```bash
# 安装 LangSmith
pip install langsmith

# 安装其他依赖
pip install python-dotenv
```

## 配置 LangSmith

1. 获取 LangSmith API Key：
   - 访问 [LangSmith](https://smith.langchain.com/settings)
   - 创建账户并获取 API Key

2. 配置环境变量：
   ```bash
   # 在 .env 文件中添加以下配置
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT=adala-agent
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   ```

## 使用方法

### 基本使用

```python
from langsmith_runtime import LangSmithOpenAIChatRuntime
from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill

# 创建 LangSmith 集成的运行时
langsmith_runtime = LangSmithOpenAIChatRuntime(
    model='llama3:8b',
    api_key='ollama'
)

# 创建 Agent
agent = Agent(
    environment=StaticEnvironment(df=train_df),
    skills=ClassificationSkill(
        name='sentiment',
        instructions="Label text as positive, negative or neutral.",
        labels={"sentiment": ["Positive", "Negative", "Neutral"]},
        input_template="Text: {text}",
        output_template="Sentiment: {sentiment}"
    ),
    runtimes={'openai': langsmith_runtime},
    teacher_runtimes={'default': langsmith_runtime},
    default_runtime='openai',
    default_teacher_runtime='default',
)

# 运行 Agent（所有调用都会被跟踪）
agent.learn(learning_iterations=3, accuracy_threshold=0.95)
predictions = agent.run(test_df)
```

### 查看跟踪状态

```python
# 检查跟踪状态
status = langsmith_runtime.get_tracing_status()
print(status)
```

## 跟踪内容

LangSmith 会跟踪以下内容：

### 执行跟踪 (execute)
- 模型名称和配置
- 输入消息内容
- 输出响应
- 执行时间
- 消息数量
- 时间戳

### 记录到记录跟踪 (record_to_record)
- 输入模板
- 指令模板
- 输出模板
- 记录数据
- 字段模式
- 执行时间

## 查看跟踪结果

1. 访问 [LangSmith Dashboard](https://smith.langchain.com/)
2. 选择你的项目（默认：`adala-agent`）
3. 查看运行记录和详细跟踪信息

## 标签和元数据

每个跟踪都会包含以下标签：
- `adala` - 框架标识
- `sentiment-analysis` - 任务类型
- `ollama` - 模型提供商
- `llama3` - 模型名称
- `execute` / `record-to-record` - 操作类型

## 错误处理

- 如果 LangSmith 不可用，系统会自动回退到标准执行
- 所有错误都会被记录但不会中断程序执行
- 详细的错误日志会输出到控制台

## 配置选项

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `LANGSMITH_API_KEY` | - | LangSmith API Key（必需） |
| `LANGSMITH_PROJECT` | `adala-agent` | 项目名称 |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` | LangSmith API 端点 |

## 示例输出

```
✅ LangSmith tracing enabled for project: adala-agent
🚀 Starting agent learning with LangSmith tracing...
✅ LangSmith traced execution completed: adala-llama3:8b-1703123456 (took 2.34s)
✅ LangSmith traced record-to-record completed: adala-record-1234-1703123457 (took 1.87s)

🔍 View traces in LangSmith: https://smith.langchain.com/
   Project: adala-agent
```

## 故障排除

### 常见问题

1. **LangSmith 未启用**
   - 检查 `LANGSMITH_API_KEY` 是否正确设置
   - 确认 LangSmith 包已安装

2. **跟踪不显示**
   - 检查网络连接
   - 确认 API Key 有效
   - 查看控制台错误日志

3. **性能问题**
   - 跟踪会增加少量延迟
   - 可以通过禁用跟踪来优化性能

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.INFO)
```

