import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "models/gemini-flash-latest"
]

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        model = genai.GenerativeModel(m)
        res = model.generate_content("Hi")
        print(f"SUCCESS: {m}")
    except Exception as e:
        print(f"FAILED: {m} - {str(e)}")
