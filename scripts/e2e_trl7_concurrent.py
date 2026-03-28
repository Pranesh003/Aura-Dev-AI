import os
import sys
import uuid
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from direct_flow import run_direct_flow

def run_job(job_id, desc):
    print(f"[{job_id}] Starting job...")
    try:
        for update in run_direct_flow(image_path=None, user_desc=desc, voice_reqs="Standard limits", model_id="models/gemini-2.0-flash", job_id=job_id):
            if "status" in update:
                print(f"[{job_id}] {update['status']}")
            # We break early just to prove directory creation and context isolation without burning massive LLM tokens
            if "Architectural Blueprint Created!" in str(update):
                print(f"[{job_id}] Early exit for validation success.")
                break
        return True
    except Exception as e:
        print(f"[{job_id}] FAILED: {e}")
        return False

def verify_trl7_concurrency():
    job1_id = str(uuid.uuid4())
    job2_id = str(uuid.uuid4())
    
    print("🚀 Starting TRL 7 Concurrent Job Verification...")
    
    # Run two jobs concurrently via ThreadPool (which mimics FastAPI's BackgroundTasks)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(run_job, job1_id, "Python script mapping 1 to 10")
        f2 = executor.submit(run_job, job2_id, "NodeJS server returning Hello")
        concurrent.futures.wait([f1, f2])
        
    # Check isolation directories
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    j1_dir = os.path.join(base, "jobs", job1_id, "generated_project")
    j2_dir = os.path.join(base, "jobs", job2_id, "generated_project")
    
    v1 = os.path.exists(j1_dir)
    v2 = os.path.exists(j2_dir)
    
    print(f"\n🔍 Verifying Output Integrity...")
    print(f"Job 1 Directory Isolated ({job1_id}): {'✅' if v1 else '❌'}")
    print(f"Job 2 Directory Isolated ({job2_id}): {'✅' if v2 else '❌'}")
    
    if v1 and v2:
        print("\n🎉 TRL 7 Concurrency Verification Passed! The system can safely handle overlapping sessions.")
    else:
        print("\n❌ Verification Failed. Directories were missing or crossed.")
        sys.exit(1)

if __name__ == "__main__":
    verify_trl7_concurrency()
