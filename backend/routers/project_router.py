import os
import uuid
import base64
import shutil
import tempfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

# Internal Modules
import database, models, auth, crud
from state import jobs
from direct_flow import run_direct_flow

router = APIRouter(
    prefix="/api",
    tags=["Projects"],
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RunRequest(BaseModel):
    user_desc: str
    voice_reqs: str
    model_id: str
    image_data: Optional[str] = None

def run_aura_background(job_id, user_id, image_path, user_desc, voice_reqs, model_id):
    jobs[job_id]["is_running"] = True
    db = database.SessionLocal()
    try:
        for update in run_direct_flow(image_path, user_desc, voice_reqs, model_id, job_id=job_id):
            for k, v in update.items():
                jobs[job_id][k] = v
                
        # Compress and Upload to Supabase Storage
        job_dir = os.path.join(PROJECT_ROOT, "jobs", job_id, "generated_project")
        if os.path.exists(job_dir):
            temp_zip = os.path.join(tempfile.gettempdir(), f"aura_{job_id}")
            shutil.make_archive(temp_zip, 'zip', job_dir)
            
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            if url and key:
                from supabase import create_client
                supabase_client = create_client(url, key)
                # Ensure bucket exists
                try: supabase_client.storage.create_bucket("artifacts")
                except Exception: pass
                
                with open(f"{temp_zip}.zip", "rb") as f:
                    supabase_client.storage.from_("artifacts").upload(
                        path=f"{job_id}.zip",
                        file=f.read(),
                        file_options={"content-type": "application/zip", "upsert": "true"}
                    )
                # Clean up local un-tracked HDD state
                shutil.rmtree(os.path.join(PROJECT_ROOT, "jobs", job_id), ignore_errors=True)

        crud.update_project_status(db, job_id, "Completed")
    except Exception as e:
        jobs[job_id]["error"] = str(e)
        crud.update_project_status(db, job_id, "Failed")
    finally:
        jobs[job_id]["is_running"] = False
        db.close()

@router.post("/run")
def run_aura(
    req: RunRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    CREDIT_COST = 10
    if current_user.credit_balance < CREDIT_COST:
        raise HTTPException(status_code=402, detail="Insufficient Aura Credits. Please recharge.")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "Initializing Engine...",
        "progress": 0,
        "is_running": False
    }
    
    image_path = None
    if req.image_data:
        image_path = os.path.join(PROJECT_ROOT, "backend", f"temp_sketch_{job_id}.png")
        with open(image_path, "wb") as f:
            header, encoded = req.image_data.split(",", 1) if "," in req.image_data else ("", req.image_data)
            f.write(base64.b64decode(encoded))
            
    # Deduct credits and save project
    crud.update_user_credits(db, current_user.id, -CREDIT_COST)
    
    proj_create = schemas.ProjectCreate(prompt_desc=req.user_desc) if 'schemas' in globals() else type("MockCreate", (object,), {"prompt_desc": req.user_desc})()
    if not isinstance(proj_create, dict):
        # Hotfix for imports inside modularity
        import schemas
        proj_create = schemas.ProjectCreate(prompt_desc=req.user_desc)

    crud.create_user_project(db, proj_create, current_user.id, job_id)

    background_tasks.add_task(run_aura_background, job_id, current_user.id, image_path, req.user_desc, req.voice_reqs, req.model_id)
    return {"message": "Started execution", "job_id": job_id, "remaining_credits": current_user.credit_balance - CREDIT_COST}

@router.get("/projects")
def list_projects(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_user_projects(db, current_user.id)

@router.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found in active running engine context")
    return jobs[job_id]

@router.get("/projects/{job_id}/download")
def download_project(
    job_id: str, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verify ownership
    project = crud.get_user_projects(db, current_user.id)
    if not any(p.id == job_id for p in project):
        raise HTTPException(status_code=403, detail="You do not own this project.")
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not (url and key):
        raise HTTPException(status_code=500, detail="Supabase Storage not configured.")
        
    try:
        from supabase import create_client
        supabase_client = create_client(url, key)
        file_data = supabase_client.storage.from_("artifacts").download(f"{job_id}.zip")
        
        temp_zip = os.path.join(tempfile.gettempdir(), f"download_{job_id}.zip")
        with open(temp_zip, "wb") as f:
            f.write(file_data)
            
        return FileResponse(
            temp_zip, 
            media_type='application/zip', 
            filename=f"AuraProject_{job_id[:8]}.zip"
        )
    except Exception as e:
        print("Storage Download Error:", e)
        # Fallback to local disk if running old version
        job_dir = os.path.join(PROJECT_ROOT, "jobs", job_id, "generated_project")
        if not os.path.exists(job_dir):
            raise HTTPException(status_code=404, detail="Project archive could not be generated and is missing from Cloud Storage.")
            
        temp_zip = os.path.join(tempfile.gettempdir(), f"aura_{job_id}")
        shutil.make_archive(temp_zip, 'zip', job_dir)
        return FileResponse(f"{temp_zip}.zip", media_type='application/zip', filename=f"AuraProject_{job_id[:8]}.zip")
