import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- START MODEL LIST ---")
try:
    for m in genai.list_models():
        print(f"NAME: {m.name} | DISPLAY: {m.display_name}")
except Exception as e:
    print(f"ERROR: {e}")
print("--- END MODEL LIST ---")
