import os
from direct_flow import run_direct_flow
import google.generativeai as genai

def run_demo():
    print("🚀 Triggering 7-Agent Super-Ultimate Demo...")
    # Mocking inputs for speed
    image_path = "temp_sketch.png"
    user_desc = "Building a complex microservices architecture"
    voice_reqs = "I want multiple databases and high abstraction."
    
    # Run the flow (Phase 6 is our target)
    for update in run_direct_flow(image_path, user_desc, voice_reqs, model_id="openrouter/qwen/qwen3.5-35b-a3b"):
        if "status" in update:
            print(f"[{update['progress']}%] {update['status']}")
        if "cognitive_load" in update:
            print("\n" + "="*40)
            print("🧠 COGNITIVE LOAD AUDIT SUCCESS!")
            print("="*40)
            print(update["cognitive_load"])
            print("="*40)
            break
        if "error" in update:
            print(f"❌ ERROR: {update['error']}")
            break

if __name__ == "__main__":
    # Ensure a temp image exists
    from PIL import Image
    Image.new('RGB', (100, 100), color = (73, 109, 137)).save("temp_sketch.png")
    run_demo()
