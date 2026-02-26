from crew_flow import run_aura_crew
import os

def test_imports():
    print("Testing CrewAI imports and initialization...")
    try:
        from agents import vision_architect
        from tasks import vision_task
        print("✅ Agents and Tasks imported successfully.")
        
        from resilient_engine import get_resilient_llm
        llm = get_resilient_llm()
        print(f"✅ Resilient LLM initialized: {llm.model_name}")
        
        print("🚀 Aura-Dev CrewAI components are correctly configured.")
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")

if __name__ == "__main__":
    test_imports()
