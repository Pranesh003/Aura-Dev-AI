import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

models = [
    "qwen/qwen-3.5-35b-instruct", 
    "qwen/qwen-3.5-35b-a3b", 
    "qwen/qwen-3.5-35b",
    "qwen/qwen-2.5-coder-32b-instruct"
]

print("Testing OpenRouter models...")
for m in models:
    try:
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1", 
            api_key=api_key, 
            model=m, 
            max_tokens=10
        )
        res = llm.invoke("Say ok")
        print(f"Success: {m} -> {res.content}")
        sys.exit(0)
    except Exception as e:
        print(f"Failed {m}: {e}")

