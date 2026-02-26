from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List, Dict, Optional
import sys

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

@app.get("/api/files/tree")
def get_file_tree(path: str = "."):
    """Returns a recursive tree of files in the generated_project directory."""
    def build_tree(current_path):
        full_path = os.path.join(GENERATED_DIR, current_path)
        if not os.path.isdir(full_path):
            return None
        
        nodes = []
        for item in sorted(os.listdir(full_path)):
            item_rel_path = os.path.relpath(os.path.join(full_path, item), GENERATED_DIR)
            is_dir = os.path.isdir(os.path.join(full_path, item))
            node = {
                "name": item,
                "path": item_rel_path.replace("\\", "/"),
                "isDir": is_dir,
            }
            if is_dir:
                node["children"] = build_tree(item_rel_path)
            nodes.append(node)
        return nodes

    return build_tree(path)

@app.get("/api/file")
def read_file(path: str):
    """Reads a file from the generated_project directory."""
    full_path = os.path.join(GENERATED_DIR, path)
    if not os.path.exists(full_path) or os.path.isdir(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"content": f"Error reading file: {str(e)}"}

@app.post("/api/file")
def write_file(file: FileContent):
    """Writes a file to the generated_project directory."""
    full_path = os.path.join(GENERATED_DIR, file.path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(file.content)
    return {"status": "success"}

@app.delete("/api/file")
def delete_file(path: str):
    """Deletes a file or directory."""
    full_path = os.path.join(GENERATED_DIR, path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Path not found")
    if os.path.isdir(full_path):
        shutil.rmtree(full_path)
    else:
        os.remove(full_path)
    return {"status": "success"}

# State for the long-running Aura flow
aura_status = {
    "status": "Idle", 
    "progress": 0, 
    "logs": [], 
    "is_running": False,
    "phases": {
        "Vision": "pending",
        "Architect": "pending",
        "Developer": "pending",
        "Debug": "pending",
        "Optimization": "pending",
        "Sustainability": "pending"
    }
}

@app.post("/api/run")
def start_aura_flow(req: RunRequest, background_tasks: BackgroundTasks):
    global aura_status
    if aura_status["is_running"]:
        raise HTTPException(status_code=400, detail="Flow already running")
    
    aura_status = {
        "status": "Initializing", 
        "progress": 0, 
        "logs": [], 
        "is_running": True,
        "phases": {p: "pending" for p in aura_status["phases"]}
    }
    
    # Save image if provided
    temp_image = os.path.join(PROJECT_ROOT, "temp_sketch.png")
    if req.image_data:
        import base64
        try:
            with open(temp_image, "wb") as f:
                f.write(base64.b64decode(req.image_data.split(",")[-1]))
        except:
            pass # Handle invalid base64 gracefully
    
    background_tasks.add_task(run_agents, temp_image, req.user_desc, req.voice_reqs, req.model_id)
    return {"status": "started"}

def run_agents(image_path, user_desc, voice_reqs, model_id):
    global aura_status
    try:
        for update in run_direct_flow(image_path, user_desc, voice_reqs, model_id):
            aura_status["status"] = update.get("status", aura_status["status"])
            aura_status["progress"] = update.get("progress", aura_status["progress"])
            
            # Map update status to phases
            for phase in aura_status["phases"]:
                if phase in aura_status["status"]:
                    aura_status["phases"][phase] = "running"
                    # Mark previous as complete
                    phases_list = list(aura_status["phases"].keys())
                    current_idx = phases_list.index(phase)
                    for i in range(current_idx):
                        aura_status["phases"][phases_list[i]] = "complete"

            if "status" in update:
                aura_status["logs"].append(update["status"])
        
        # Mark all as complete at end
        for phase in aura_status["phases"]:
            aura_status["phases"][phase] = "complete"
            
    except Exception as e:
        aura_status["status"] = f"Error: {str(e)}"
    finally:
        aura_status["is_running"] = False

@app.get("/api/status")
def get_status():
    return aura_status

@app.get("/api/terminal/run")
def run_command(command: str):
    """Simulates running a command and returning output."""
    import subprocess
    try:
        # Run command inside the generated project
        result = subprocess.run(command, shell=True, cwd=GENERATED_DIR, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout, 
            "stderr": result.stderr, 
            "exit_code": result.returncode,
            "full_output": (result.stdout + "\n" + result.stderr).strip()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/automation/run")
def run_automation_tool(tool_name: str, target_file: Optional[str] = None):
    """Runs specialized productivity tools from the suite."""
    import subprocess
    script_path = ""
    if tool_name == "auto_doc":
        script_path = os.path.join(GENERATED_DIR, "productivity_tools", "auto_doc.py")
        cmd = f"python \"{script_path}\" \"{os.path.join(GENERATED_DIR, target_file) if target_file else '.'}\""
    elif tool_name == "test_oracle":
        script_path = os.path.join(GENERATED_DIR, "productivity_tools", "test_oracle.py")
        cmd = f"python \"{script_path}\""
    elif tool_name == "ci_cd":
        script_path = os.path.join(GENERATED_DIR, "intelligent_automation", "workflow_engine.py")
        cmd = f"python \"{script_path}\""
    else:
        return {"error": "Tool not found"}

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"output": (result.stdout + "\n" + result.stderr).strip()}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
