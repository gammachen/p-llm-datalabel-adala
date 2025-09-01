# Adala Agent with LangSmith Tracing - 集成总结

## 🎯 项目目标

为 Adala 框架中的 Agent 调用提供详细的步骤跟踪和监控功能，使用 LangSmith 作为跟踪平台。

## ✅ 已实现功能

### 1. 核心集成组件

- **`LangSmithOpenAIChatRuntime`** - 自定义运行时类，继承自 `OpenAIChatRuntime`
- **自动环境变量配置** - 支持 `.env` 文件配置
- **错误处理和回退机制** - 当 LangSmith 不可用时自动回退到标准执行
- **详细的元数据记录** - 包含模型信息、执行时间、输入输出等

### 2. 跟踪功能

#### 执行跟踪 (execute)
- ✅ 模型名称和配置
- ✅ 输入消息内容
- ✅ 输出响应
- ✅ 执行时间监控
- ✅ 消息数量统计
- ✅ 时间戳记录

#### 记录到记录跟踪 (record_to_record)
- ✅ 输入模板
- ✅ 指令模板
- ✅ 输出模板
- ✅ 记录数据
- ✅ 字段模式
- ✅ 执行时间

### 3. 配置选项

| 环境变量 | 默认值 | 描述 |
|---------|--------|------|
| `LANGSMITH_API_KEY` | - | LangSmith API Key（必需） |
| `LANGSMITH_PROJECT` | `adala-agent` | 项目名称 |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` | LangSmith API 端点 |

### 4. 标签和元数据

每个跟踪都包含以下标签：
- `adala` - 框架标识
- `sentiment-analysis` - 任务类型
- `ollama` - 模型提供商
- `llama3` - 模型名称
- `execute` / `record-to-record` - 操作类型

## 🚀 使用方法

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

## 📊 跟踪内容示例

### 执行跟踪示例

```json
{
  "name": "adala-llama3:8b-1703123456",
  "project_name": "adala-agent",
  "tags": ["adala", "sentiment-analysis", "ollama", "llama3", "execute"],
  "metadata": {
    "model": "llama3:8b",
    "runtime_type": "OpenAIChatRuntime",
    "framework": "adala",
    "input_length": 156,
    "message_count": 2,
    "timestamp": 1703123456
  }
}
```

### 记录到记录跟踪示例

```json
{
  "name": "adala-record-1234-1703123457",
  "project_name": "adala-agent",
  "tags": ["adala", "record-to-record", "sentiment-analysis"],
  "metadata": {
    "model": "llama3:8b",
    "runtime_type": "OpenAIChatRuntime",
    "framework": "adala",
    "input_template": "Text: {text}",
    "instructions_template": "Label text as positive, negative or neutral.",
    "output_template": "Sentiment: {sentiment}",
    "record_keys": ["text"],
    "timestamp": 1703123457
  }
}
```

## 🔍 查看跟踪结果

1. 访问 [LangSmith Dashboard](https://smith.langchain.com/)
2. 选择你的项目（默认：`adala-agent`）
3. 查看运行记录和详细跟踪信息

## 🛠️ 技术实现细节

### 1. 类结构

```python
class LangSmithOpenAIChatRuntime(OpenAIChatRuntime):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_langsmith()
    
    def _setup_langsmith(self):
        # 初始化 LangSmith 客户端和配置
    
    def execute(self, messages: List[Dict[str, Any]]) -> str:
        # 带跟踪的执行方法
    
    def record_to_record(self, ...) -> Dict[str, str]:
        # 带跟踪的记录到记录方法
```

### 2. 错误处理

- 自动检测 LangSmith 可用性
- 优雅降级到标准执行
- 详细的错误日志记录

### 3. 性能优化

- 异步跟踪支持
- 最小化跟踪开销
- 可配置的跟踪级别

## 📈 监控和分析

### 1. 性能指标

- 执行时间统计
- 成功率监控
- 错误率分析

### 2. 质量指标

- 输入输出质量
- 模型响应一致性
- 用户反馈分析

### 3. 成本分析

- API 调用次数
- 令牌使用量
- 成本趋势

## 🎯 使用场景

### 1. 开发调试

- 详细的调用步骤跟踪
- 输入输出验证
- 性能瓶颈识别

### 2. 生产监控

- 实时性能监控
- 错误检测和报警
- 用户行为分析

### 3. 模型优化

- 提示工程优化
- 模型性能对比
- A/B 测试支持

## 🔧 故障排除

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

## 🚀 未来改进

### 1. 功能增强

- [ ] 支持更多运行时类型
- [ ] 自定义跟踪过滤器
- [ ] 实时监控仪表板
- [ ] 自动报告生成

### 2. 性能优化

- [ ] 批量跟踪支持
- [ ] 缓存机制
- [ ] 异步跟踪优化

### 3. 集成扩展

- [ ] 支持其他跟踪平台
- [ ] 多环境配置
- [ ] 团队协作功能

## 📝 总结

通过 LangSmith 集成，我们成功实现了：

1. **详细的步骤跟踪** - 每个 LLM 调用都有完整的输入输出记录
2. **性能监控** - 实时跟踪执行时间和成功率
3. **错误处理** - 优雅的错误处理和回退机制
4. **可配置性** - 灵活的环境变量配置
5. **易用性** - 简单的 API 和清晰的文档

这个集成为 Adala 框架提供了强大的可观测性能力，使得开发者可以更好地理解、调试和优化他们的 Agent 应用。 