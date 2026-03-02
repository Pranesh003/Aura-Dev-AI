import os
from PIL import Image

def test():
    if not os.path.exists("temp_sketch.png"):
        Image.new('RGB', (100, 100), color = (73, 109, 137)).save("temp_sketch.png")
    
    from crew_flow import run_aura_crew
    # Avoid non-ASCII characters that can break some terminals
    print("Triggering crew_flow test...")
    
    # Run the generator
    for update in run_aura_crew(
        image_path=os.path.abspath("temp_sketch.png"),
        user_desc="Building a real-time chat app",
        voice_reqs="Should use websockets",
        model_choice="gemini-2.0-flash-latest"
    ):
        # Strip non-ASCII chars (like emojis) to avoid Windows cp1252 encoding errors
        def _clean(text: str) -> str:
            return text.encode("ascii", errors="ignore").decode("ascii")

        if "status" in update:
            status = _clean(update["status"])
            print(f"[{update.get('progress', 0)}%] {status}")
        if "error" in update:
            err = _clean(update["error"])
            print(f"\nERROR: {err}")
            return
        if "final_result" in update:
            print("\nCREW AI COMPLETED SUCCESSFULLY!")
            return

if __name__ == "__main__":
    test()
