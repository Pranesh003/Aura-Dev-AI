from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import asyncio

# SaaS Modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import auth_router, billing_router, project_router
import database, models
from state import connected_clients
from logger_config import log_queue

# Initialize DB
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Aura-IDE Backend (SaaS Edition)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modular Routers
app.include_router(auth_router.router)
app.include_router(billing_router.router)
app.include_router(project_router.router)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
