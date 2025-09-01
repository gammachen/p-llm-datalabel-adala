#!/usr/bin/env python3
"""
Adala Agent with LangSmith Tracing Example

This example demonstrates how to use LangSmith to trace and monitor
Adala framework Agent calls with detailed step-by-step tracking.

Prerequisites:
1. Install LangSmith: pip install langsmith
2. Get LangSmith API key from: https://smith.langchain.com/settings
3. Configure environment variables (see .env.example)

Usage:
    python quickstart_with_langsmith.py
"""

import pandas as pd
import os
import logging
from dotenv import load_dotenv

from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill
from rich import print

# Import our custom LangSmith runtime
from langsmith_runtime import LangSmithOpenAIChatRuntime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def setup_environment():
    """Setup environment variables and configuration."""
    # Configure OpenAI API for Ollama
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "ollama")
    os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

    # Configure OpenAI client for Ollama
    import openai
    openai.api_base = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    openai.api_key = os.getenv("OPENAI_API_KEY", "ollama")

    # Check LangSmith configuration
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_api_key:
        print(f"✅ LangSmith tracing enabled with project: {os.getenv('LANGSMITH_PROJECT', 'adala-agent')}")
        print(f"   API Key: {langsmith_api_key[:8]}...{langsmith_api_key[-4:] if len(langsmith_api_key) > 8 else '***'}")
    else:
        print("⚠️  LangSmith API key not found. Tracing will be disabled.")
        print("   To enable tracing, add LANGSMITH_API_KEY to your .env file")

def create_datasets():
    """Create training and test datasets."""

    # Train dataset
    train_df = pd.DataFrame([
        ["It was the negative first impressions, and then it started working.", "Positive"],
        ["Not loud enough and doesn't turn on like it should.", "Negative"],
        ["I don't know what to say.", "Neutral"],
        ["Manager was rude, but the most important that mic shows very flat frequency response.", "Positive"],
        ["The phone doesn't seem to accept anything except CBR mp3s.", "Negative"],
        ["I tried it before, I bought this device for my son.", "Neutral"],
        ["一开始的印象很糟糕，但后来它开始正常工作了。", "正面"],
        ["音量不够大，而且无法正常开机。", "负面"],
        ["我不知道该说什么。", "中性"],
        ["经理态度粗鲁，但最重要的是麦克风的频率响应非常平坦。", "正面"],
        ["这款手机似乎只支持CBR格式的MP3文件。", "负面"],
        ["我之前试用过，买这个设备是给我儿子的。", "中性"],
    ], columns=["text", "sentiment"])

    # Test dataset
    test_df = pd.DataFrame([
        "All three broke within two months of use.",
        "The device worked for a long time, can't say anything bad.",
        "Just a random line of text."
        "三个都在使用两个月内坏了。",
        "这个设备用了很长时间，说不出什么缺点。",
        "只是一句随机的文本。"
    ], columns=["text"])

    return train_df, test_df

def create_agent_with_langsmith():
    """Create Agent with LangSmith tracing enabled."""
    # Create LangSmith-enabled runtime
    langsmith_runtime = LangSmithOpenAIChatRuntime(
        model='llama3:8b',
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    langsmith_runtime_of_qwen2 = LangSmithOpenAIChatRuntime(
        model='qwen2:latest',
        api_key=os.getenv("OPENAI_API_KEY")
    )    

    # Check tracing status
    tracing_status = langsmith_runtime.get_tracing_status()
    print(f"\n🔍 Tracing Status:")
    for key, value in tracing_status.items():
        print(f"   {key}: {value}")

    # Create agent
    agent = Agent(
        # connect to a dataset
        environment=StaticEnvironment(df=create_datasets()[0]),

        # define a skill
        skills=ClassificationSkill(
            name='sentiment',
            instructions="Label text as positive, negative or neutral.",
            labels={"sentiment": ["Positive", "Negative", "Neutral"]},
            input_template="Text: {text}",
            output_template="Sentiment: {sentiment}"
        ),

        # define all the different runtimes your skills may use
        runtimes = {
            'openai': langsmith_runtime,
        },
        teacher_runtimes = {
            'default': langsmith_runtime,
            'qwen2': langsmith_runtime_of_qwen2,
        },
        default_runtime='openai',
        default_teacher_runtime='default',
    )

    return agent

def main():
    """Main function to run the example."""
    print("🚀 Adala Agent with LangSmith Tracing Example")
    print("=" * 50)

    # Setup environment
    setup_environment()

    # Create datasets
    train_df, test_df = create_datasets()
    print(f"\n📊 Dataset loaded:")
    print(f"   Training samples: {len(train_df)}")
    print(f"   Test samples: {len(test_df)}")

    # Create agent with LangSmith tracing
    print(f"\n🤖 Creating Agent with LangSmith tracing...")
    agent = create_agent_with_langsmith()

    print(f"\n{agent}")
    print(f"{agent.skills}")

    # Start learning with tracing
    print(f"\n🚀 Starting agent learning with LangSmith tracing...")
    print(f"   This will generate detailed traces for each LLM call")
    print(f"   View traces at: https://smith.langchain.com/")
    
    agent.learn(learning_iterations=3, accuracy_threshold=0.95)

    # Run tests
    print(f"\n=> Run tests with tracing...")
    predictions = agent.run(test_df)
    print(f"\n => Test results:")
    print(predictions)

    # Final summary
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if langsmith_api_key:
        print(f"\n🔍 LangSmith Integration Summary:")
        print(f"   ✅ All LLM calls have been traced")
        print(f"   📊 View detailed traces: https://smith.langchain.com/")
        print(f"   🏷️  Project: {os.getenv('LANGSMITH_PROJECT', 'adala-agent')}")
        print(f"   🏷️  Tags: adala, sentiment-analysis, ollama, llama3")
        print(f"\n💡 Tips:")
        print(f"   - Each trace includes input/output, execution time, and metadata")
        print(f"   - Use tags to filter and search traces")
        print(f"   - Compare different runs to analyze performance")
    else:
        print(f"\n⚠️  LangSmith not configured")
        print(f"   To enable tracing, add LANGSMITH_API_KEY to your .env file")

if __name__ == "__main__":
    main() 