import pandas as pd
import os
from dotenv import load_dotenv

from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill
from rich import print

# Import our custom LangSmith runtime
from langsmith_runtime import LangSmithOpenAIChatRuntime

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API for Ollama
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "ollama")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

# Configure OpenAI client for Ollama
import openai
openai.api_base = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
openai.api_key = os.getenv("OPENAI_API_KEY", "ollama")

# Configure LangSmith (optional - will be disabled if not configured)
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_api_key:
    print(f"✅ LangSmith tracing enabled with project: {os.getenv('LANGSMITH_PROJECT', 'adala-agent')}")
else:
    print("⚠️  LangSmith API key not found. Tracing will be disabled.")

# Train dataset
train_df = pd.DataFrame([
    ["It was the negative first impressions, and then it started working.", "Positive"],
    ["Not loud enough and doesn't turn on like it should.", "Negative"],
    ["I don't know what to say.", "Neutral"],
    ["Manager was rude, but the most important that mic shows very flat frequency response.", "Positive"],
    ["The phone doesn't seem to accept anything except CBR mp3s.", "Negative"],
    ["I tried it before, I bought this device for my son.", "Neutral"],
], columns=["text", "sentiment"])

# Test dataset
test_df = pd.DataFrame([
    "All three broke within two months of use.",
    "The device worked for a long time, can't say anything bad.",
    "Just a random line of text."
], columns=["text"])

# Create LangSmith-enabled runtime
langsmith_runtime = LangSmithOpenAIChatRuntime(
    model='llama3:8b',
    api_key=os.getenv("OPENAI_API_KEY")
)

agent = Agent(
    # connect to a dataset
    environment=StaticEnvironment(df=train_df),

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
    },
    default_runtime='openai',
    default_teacher_runtime='default',
)

print(agent)
print(agent.skills)

print('\n🚀 Starting agent learning with LangSmith tracing...')
agent.learn(learning_iterations=3, accuracy_threshold=0.95)

print('\n=> Run tests ...')
predictions = agent.run(test_df)
print('\n => Test results:')
print(predictions)

# If LangSmith is enabled, provide information about viewing traces
if langsmith_api_key:
    print(f"\n🔍 View traces in LangSmith: https://smith.langchain.com/")
    print(f"   Project: {os.getenv('LANGSMITH_PROJECT', 'adala-agent')}")
