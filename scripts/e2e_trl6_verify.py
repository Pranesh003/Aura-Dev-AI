import os
import sys
import shutil

# Ensure we can import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from direct_flow import run_direct_flow

def run_e2e_test():
    print("🚀 Starting TRL 6 E2E Verification...")
    
    # Clean previous runs
    gen_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_project")
    if os.path.exists(gen_dir):
        shutil.rmtree(gen_dir)
        
    print("✅ Cleaned previous generated_project directory.")
    
    # Mock parameters
    user_desc = "A simple python script that prints Hello World, with a setup.py."
    voice_reqs = "Uses standard libraries only. Must be PEP8 compliant."
    model_id = "models/gemini-2.0-flash" 
    
    print("🤖 Triggering 7-Agent Core Workflow (direct_flow.py)...")
    
    final_state = None
    try:
        # direct_flow yields updates, we just want to run to completion and get the final result
        for update in run_direct_flow(image_path=None, user_desc=user_desc, voice_reqs=voice_reqs, model_id=model_id):
            if "status" in update:
                print(f"   -> Agent Status: {update['status']}")
            final_state = update
            
        print("✅ Workflow execution completed successfully.")
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE during execution: {e}")
        sys.exit(1)
        
    # Verification Steps
    print("\n🔍 Verifying Output Integrity...")
    
    # 1. Check generated directory exists
    if not os.path.exists(gen_dir):
        print("❌ generated_project directory was not created.")
        sys.exit(1)
        
    # 2. Check files created
    files_created = []
    for root, _, files in os.walk(gen_dir):
        for f in files:
            files_created.append(os.path.relpath(os.path.join(root, f), gen_dir))
            
    if not files_created:
        print("❌ No files were generated.")
        sys.exit(1)
        
    print(f"✅ Verified {len(files_created)} files generated: {files_created}")
    
    # 3. Check for specific reports
    has_md = any(f.endswith(".md") for f in files_created)
    if not has_md:
        print("⚠️ No markdown reports generated (Debug/Audit).")
    else:
        print("✅ Verified Audit/Debug reports exist.")

    print("\n🎉 TRL 6 E2E Verification Passed Successfully! The system is ready for relevant environment demonstration.")

if __name__ == "__main__":
    run_e2e_test()
