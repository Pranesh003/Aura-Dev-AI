import os
from PIL import Image

def test():
    if not os.path.exists("temp_sketch.png"):
        Image.new('RGB', (100, 100), color = (73, 109, 137)).save("temp_sketch.png")
    
    from crew_flow import run_aura_crew
    print("🚀 Triggering crew_flow test...")
    
    # Run the generator
    for update in run_aura_crew(
        image_path=os.path.abspath("temp_sketch.png"),
        user_desc="Building a real-time chat app",
        voice_reqs="Should use websockets",
        model_choice="gemini-2.0-flash-latest"
    ):
        if "status" in update:
            print(f"[{update.get('progress', 0)}%] {update['status']}")
        if "error" in update:
            print(f"\n❌ ERROR: {update['error']}")
            return
        if "final_result" in update:
            print("\n✅ CREW AI COMPLETED SUCCESSFULLY!")
            return

if __name__ == "__main__":
    test()
