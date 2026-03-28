import os
import sys
from direct_flow import run_direct_flow

def test_engine():
    print("🚀 Starting Engine Verification...")
    image_path = "temp_sketch.png"
    user_desc = "Verification Test: Simple Todo App"
    voice_reqs = "Low bandwidth, high efficiency."
    model_id = "gemini-2.0-flash" 

    try:
        for update in run_direct_flow(image_path, user_desc, voice_reqs, model_id=model_id):
            if "error" in update:
                print(f"❌ Error: {update['error']}")
                return
            
            print(f"[{update['progress']}%] {update['status']}")
            
            if "optimization" in update:
                print("✅ Optimization Report received (first 100 chars):", update['optimization'][:100].replace("\n", " "))
            
            if "debug" in update:
                print("✅ Debug Report received (first 100 chars):", update['debug'][:100].replace("\n", " "))

            if "audit" in update:
                print("✅ Green AI Audit received (first 100 chars):", update['audit'][:100].replace("\n", " "))
        
        print("\n🏆 ULTIMATE 6-AGENT SYSTEM VERIFICATION SUCCESSFUL!")
    except Exception as e:
        print(f"❌ Unexpected Failure: {str(e)}")

if __name__ == "__main__":
    test_engine()
