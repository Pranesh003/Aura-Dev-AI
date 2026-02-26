import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

with open("available_models.txt", "w", encoding="utf-8") as f:
    try:
        models = genai.list_models()
        for m in models:
            f.write(f"{m.name}\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
