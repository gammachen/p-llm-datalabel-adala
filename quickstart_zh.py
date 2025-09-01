import pandas as pd
import os
from dotenv import load_dotenv

from adala.agents import Agent
from adala.environments import StaticEnvironment
from adala.skills import ClassificationSkill
from adala.runtimes import OpenAIChatRuntime
from rich import print

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API for Ollama
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "ollama")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

# Configure OpenAI client for Ollama
import openai
openai.api_base = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
openai.api_key = os.getenv("OPENAI_API_KEY", "ollama")

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
        'openai': OpenAIChatRuntime(
            model='llama3:8b',
            api_key=os.getenv("OPENAI_API_KEY")
        ),
    },
    teacher_runtimes = {
        'default': OpenAIChatRuntime(
            model='llama3:8b',
            api_key=os.getenv("OPENAI_API_KEY")
        ),
    },
    default_runtime='openai',
    default_teacher_runtime='default',
)

print(agent)
print(agent.skills)

agent.learn(learning_iterations=3, accuracy_threshold=0.95)

print('\n=> Run tests ...')
predictions = agent.run(test_df)
print('\n => Test results:')
print(predictions)
