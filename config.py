import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 核心：加载当前目录下的 .env 文件
load_dotenv()

def get_llm():
    # os.getenv 会自动从 .env 文件中读取对应的值
    api_key = os.getenv("MODEL_API_KEY")
    base_url = os.getenv("MODEL_BASE_URL")
    model_name = os.getenv("MODEL_NAME", "qwen-max")
    
    if not api_key:
        raise ValueError("❌ 未在 .env 文件中找到 MODEL_API_KEY")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0
    )