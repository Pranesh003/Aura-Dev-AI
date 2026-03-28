from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import asyncio
import uuid
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from direct_flow import run_direct_flow
from logger_config import log_queue

app = FastAPI(title="Aura-IDE Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = os.path.join(PROJECT_ROOT, "jobs")

if not os.path.exists(JOBS_DIR):
    os.makedirs(JOBS_DIR)

class RunRequest(BaseModel):
    user_desc: str
    voice_reqs: str
    model_id: str
    image_data: Optional[str] = None

# Multi-tenant state
jobs: Dict[str, dict] = {}
# WebSocket connections per job
connected_clients: Dict[str, List[WebSocket]] = {}

@app.websocket("/api/ws/logs/{job_id}")
async def websocket_logs(websocket: WebSocket, job_id: str):
    await websocket.accept()
    if job_id not in connected_clients:
        connected_clients[job_id] = []
    connected_clients[job_id].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients[job_id].remove(websocket)
        if not connected_clients[job_id]:
            del connected_clients[job_id]

async def log_pump():
    while True:
        while not log_queue.empty():
            try:
                msg_tuple = log_queue.get_nowait()
                # Ensure compatibility if some old logs don't use tuple
                if isinstance(msg_tuple, tuple) and len(msg_tuple) == 2:
                    job_id, msg = msg_tuple
                else:
                    job_id, msg = "global", str(msg_tuple)
                
                # Broadcast to the specific job, and also anyone listening to "global"
                targets = []
                if job_id in connected_clients:
                    targets.extend(connected_clients[job_id])
                if "global" in connected_clients and job_id != "global":
                    targets.extend(connected_clients["global"])
                    
                for client in targets:
                    try:
                        await client.send_text(msg)
                    except Exception:
                        pass
            except Exception:
                pass
        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(log_pump())

def run_aura_background(job_id, image_path, user_desc, voice_reqs, model_id):
    jobs[job_id]["is_running"] = True
    try:
        for update in run_direct_flow(image_path, user_desc, voice_reqs, model_id, job_id=job_id):
            for k, v in update.items():
                jobs[job_id][k] = v
    except Exception as e:
        jobs[job_id]["error"] = str(e)
    finally:
        jobs[job_id]["is_running"] = False

@app.post("/api/run")
def run_aura(req: RunRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "Initializing Engine...",
        "progress": 0,
        "is_running": False
    }
    
    image_path = None
    if req.image_data:
        image_path = os.path.join(PROJECT_ROOT, f"temp_sketch_{job_id}.png")
        import base64
        with open(image_path, "wb") as f:
            header, encoded = req.image_data.split(",", 1) if "," in req.image_data else ("", req.image_data)
            f.write(base64.b64decode(encoded))
            
    background_tasks.add_task(run_aura_background, job_id, image_path, req.user_desc, req.voice_reqs, req.model_id)
    return {"message": "Started execution", "job_id": job_id}

@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
