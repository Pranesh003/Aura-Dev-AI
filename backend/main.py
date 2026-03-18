from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List, Dict, Optional
import sys
import time

# Add parent dir to path so we can import direct_flow
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from direct_flow import run_direct_flow

app = FastAPI(title="Aura-IDE Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_DIR = os.path.join(PROJECT_ROOT, "generated_project")

if not os.path.exists(GENERATED_DIR):
    os.makedirs(GENERATED_DIR)

class FileNode(BaseModel):
    name: str
    path: str
    isDir: bool
    children: Optional[List['FileNode']] = None

class FileContent(BaseModel):
    path: str
    content: str

class RunRequest(BaseModel):
    user_desc: str
    voice_reqs: str
    model_id: str
    image_data: Optional[str] = None # Base64 encoded image

@app.get("/api/status")
def get_status():
    return aura_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
