import os
from dotenv import load_dotenv

load_dotenv()

def check_keys():
    print("--- Environment Key Check ---")
    vars = ["GOOGLE_API_KEY", "OPENAI_API_KEY"]
    for v in vars:
        val = os.getenv(v)
        if val:
            print(f"{v}: Length={len(val)}")
            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                print(f"⚠️  {v} has literal quotes in its value!")
            if val != val.strip():
                print(f"⚠️  {v} has leading/trailing whitespaces!")
        else:
            print(f"{v}: NOT FOUND")

if __name__ == "__main__":
    check_keys()
