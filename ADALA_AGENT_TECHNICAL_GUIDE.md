# ADALA Agent 技术文档 - 文本情感分类实战指南

## 概述

本文档基于 `quickstart_zh.py` 示例，详细介绍如何使用 ADALA (Autonomous Data Labeling Agent) 框架构建一个智能文本情感分类系统。该系统能够自动学习和改进文本情感分类能力，支持中英文混合文本处理。

## 技术架构

ADALA Agent 采用模块化设计，主要包含以下核心组件：

- **Agent**: 智能代理，负责协调整个学习过程
- **Environment**: 环境配置，提供训练和测试数据
- **Skills**: 技能定义，指定具体任务类型和要求
- **Runtimes**: 运行时配置，定义使用的AI模型和API

## 环境准备

### 1. 依赖安装

确保已安装以下Python包：

```bash
pip install adala pandas python-dotenv openai rich
```

### 2. 环境变量配置

创建 `.env` 文件配置API访问：

```bash
# OpenAI API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=http://localhost:11434/v1  # 使用Ollama本地服务
```

### 3. Ollama本地部署（可选）

如果使用本地Ollama服务，请确保已安装并运行：

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动llama3:8b模型
ollama run llama3:8b
```

## 核心组件详解

### 1. 数据准备

#### 训练数据集格式
训练数据使用Pandas DataFrame格式，包含两列：
- `text`: 文本内容（中英文混合支持）
- `sentiment`: 情感标签（正面/负面/中性）

```python
train_df = pd.DataFrame([
    ["It was the negative first impressions, and then it started working.", "Positive"],
    ["音量不够大，而且无法正常开机。", "负面"],
    ["I don't know what to say.", "Neutral"],
    # ... 更多训练样本
], columns=["text", "sentiment"])
```

#### 测试数据集格式
测试数据只需提供文本内容：

```python
test_df = pd.DataFrame([
    "All three broke within two months of use.",
    "这个设备用了很长时间，说不出什么缺点。",
    # ... 更多测试文本
], columns=["text"])
```

### 2. 环境配置 (StaticEnvironment)

`StaticEnvironment` 提供静态数据环境，将训练数据连接到Agent：

```python
from adala.environments import StaticEnvironment

environment = StaticEnvironment(df=train_df)
```

### 3. 技能定义 (ClassificationSkill)

`ClassificationSkill` 定义文本分类任务的具体要求：

```python
from adala.skills import ClassificationSkill

skill = ClassificationSkill(
    name='sentiment',                    # 技能名称
    instructions="Label text as positive, negative or neutral.",  # 任务说明
    labels={"sentiment": ["Positive", "Negative", "Neutral"]},   # 标签定义
    input_template="Text: {text}",       # 输入模板
    output_template="Sentiment: {sentiment}"  # 输出模板
)
```

#### 参数说明
- **name**: 技能唯一标识符
- **instructions**: 给AI模型的任务说明，应清晰明确
- **labels**: 分类标签字典，key为字段名，value为标签列表
- **input_template**: 输入格式化模板，使用 `{field}` 占位符
- **output_template**: 输出格式化模板

### 4. 运行时配置 (OpenAIChatRuntime)

配置AI模型运行时环境：

```python
from adala.runtimes import OpenAIChatRuntime

runtime = OpenAIChatRuntime(
    model='llama3:8b',                   # 使用的模型名称
    api_key=os.getenv("OPENAI_API_KEY")  # API密钥
)
```

#### 支持的配置
- **model**: 模型名称（如 gpt-3.5-turbo, llama3:8b, claude-3-sonnet 等）
- **api_key**: API访问密钥
- **base_url**: 自定义API端点（通过环境变量配置）

### 5. Agent配置与初始化

整合所有组件创建Agent实例：

```python
from adala.agents import Agent

agent = Agent(
    environment=StaticEnvironment(df=train_df),
    skills=ClassificationSkill(...),
    runtimes={
        'openai': OpenAIChatRuntime(...)
    },
    teacher_runtimes={
        'default': OpenAIChatRuntime(...)
    },
    default_runtime='openai',
    default_teacher_runtime='default'
)
```

#### 关键配置项
- **environment**: 数据环境配置
- **skills**: 定义的任务技能列表
- **runtimes**: 运行时配置字典，可配置多个模型
- **teacher_runtimes**: 教师模型配置，用于指导学习
- **default_runtime**: 默认使用的运行时
- **default_teacher_runtime**: 默认使用的教师运行时

## 学习过程

### 启动学习

Agent通过 `learn()` 方法自动学习和改进：

```python
agent.learn(
    learning_iterations=3,      # 学习迭代次数
    accuracy_threshold=0.95     # 准确率阈值
)
```

#### 学习参数
- **learning_iterations**: 学习迭代次数，建议3-5次
- **accuracy_threshold**: 准确率阈值，达到后停止学习

### 学习过程说明

1. **初始评估**: Agent评估初始性能
2. **策略改进**: 基于训练数据调整分类策略
3. **迭代优化**: 多次迭代直至达到准确率要求
4. **模型固化**: 保存最优模型配置

## 预测与推理

### 执行预测

使用训练好的Agent进行文本情感分类：

```python
predictions = agent.run(test_df)
print(predictions)
```

### 输出格式

预测结果包含以下信息：
- 输入文本
- 预测的情感标签
- 置信度分数（如适用）

## 高级配置

### 多模型支持

可配置多个运行时以支持不同模型：

```python
runtimes = {
    'openai': OpenAIChatRuntime(model='gpt-3.5-turbo', api_key='...'),
    'local': OpenAIChatRuntime(model='llama3:8b', api_key='ollama'),
    'claude': OpenAIChatRuntime(model='claude-3-sonnet', api_key='...')
}
```

### 自定义技能

可扩展支持其他分类任务：

```python
# 主题分类
ClassificationSkill(
    name='topic_classification',
    instructions="Classify text into technology, sports, politics, or entertainment topics",
    labels={"topic": ["technology", "sports", "politics", "entertainment"]},
    input_template="Text: {text}",
    output_template="Topic: {topic}"
)
```

## 最佳实践

### 1. 数据质量
- 确保训练数据标签准确
- 保持类别平衡，避免数据倾斜
- 提供足够数量的训练样本（每类至少20-50个）

### 2. 提示优化
- 使用清晰、具体的任务说明
- 提供示例输出格式
- 考虑中英文语境差异

### 3. 模型选择
- 英文文本：gpt-3.5-turbo, llama3:8b
- 中文文本：gpt-3.5-turbo, 中文优化模型
- 本地部署：llama3:8b, mistral

### 4. 性能调优
- 调整 `learning_iterations` 平衡准确率和训练时间
- 设置合理的 `accuracy_threshold` 避免过拟合
- 监控训练过程中的性能指标

## 故障排除

### 常见问题

#### API连接失败
```python
# 检查环境变量
print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("OPENAI_BASE_URL"))

# 测试连接
curl http://localhost:11434/v1/models
```

#### 准确率过低
- 增加训练数据量
- 调整模型参数
- 检查标签质量
- 优化任务说明

#### 内存不足
- 减少批处理大小
- 使用较小模型
- 优化数据预处理

## 完整示例代码

```python
import pandas as pd
import os
from dotenv import load_dotenv
from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill
from adala.runtimes import OpenAIChatRuntime
from rich import print

# 加载环境变量
load_dotenv()

# 配置API
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "ollama")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

# 准备数据
train_df = pd.DataFrame([
    ["产品质量很好，我很满意", "正面"],
    ["服务态度差，不会再购买", "负面"],
    ["一般般，没什么特别的", "中性"],
], columns=["text", "sentiment"])

test_df = pd.DataFrame([
    "这个商品质量超出预期",
    "客服回复太慢了",
], columns=["text"])

# 创建Agent
agent = Agent(
    environment=StaticEnvironment(df=train_df),
    skills=ClassificationSkill(
        name='sentiment',
        instructions="分析文本情感倾向，分类为正面、负面或中性",
        labels={"sentiment": ["正面", "负面", "中性"]},
        input_template="文本: {text}",
        output_template="情感: {sentiment}"
    ),
    runtimes={
        'openai': OpenAIChatRuntime(
            model='llama3:8b',
            api_key=os.getenv("OPENAI_API_KEY")
        ),
    },
    teacher_runtimes={
        'default': OpenAIChatRuntime(
            model='llama3:8b',
            api_key=os.getenv("OPENAI_API_KEY")
        ),
    },
    default_runtime='openai',
    default_teacher_runtime='default',
)

# 训练
agent.learn(learning_iterations=3, accuracy_threshold=0.9)

# 预测
predictions = agent.run(test_df)
print("预测结果:", predictions)
```

## 总结

ADALA Agent 提供了一个强大而灵活的框架，能够自动学习和改进文本分类任务。通过合理配置环境、技能和运行时，可以构建适应多种场景的智能分类系统。本文档提供的配置和最佳实践将帮助您快速上手并优化系统性能。