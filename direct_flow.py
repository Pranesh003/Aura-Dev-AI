import os
import time
import base64
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv
import shutil

load_dotenv()

# High-resilience key and model rotation
VISION_MODELS = [
    "openrouter/qwen/qwen3.5-35b-a3b",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest"
]

TEXT_MODELS = [
    "openrouter/qwen/qwen3.5-35b-a3b",
    "models/gemini-flash-latest",
    "models/gemini-2.0-flash",
    "models/gemini-pro-latest"
]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def safe_generate(client, model_id, prompt, is_openai, image_path=None, api_key=None):
    """
    Helper to generate content with built-in retry logic and fallback signaling.
    Now hardened with Nuclear-Tier error detection (503s, 500s, 429s).
    """
    if not is_openai and api_key:
        genai.configure(api_key=api_key)

    max_retries = 3
    retry_delay = 10 # Initial stable delay

    for attempt in range(max_retries):
        try:
            if is_openai:
                if image_path:
                    base64_image = encode_image(image_path)
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ]
                else:
                    messages = [{"role": "user", "content": prompt}]
                
                response = client.chat.completions.create(model=model_id, messages=messages)
                return response.choices[0].message.content
            else:
                model = genai.GenerativeModel(model_id)
                if image_path:
                    img = Image.open(image_path)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                return response.text
        except Exception as e:
            err_msg = str(e).lower()
            
            # 1. Critical Failures (Model Missing/Unsupported)
            if any(x in err_msg for x in ["404", "not found", "not supported", "not exist"]):
                raise RuntimeError(f"MODEL_NOT_FOUND: {model_id}")
                
            # 2. Quota & Transient Failures (Nuclear-Tier Detection)
            is_quota = any(x in err_msg for x in ["429", "resource_exhausted", "quota", "rate limit reached"])
            is_transient = any(x in err_msg for x in ["500", "503", "service unavailable", "internal error", "deadline exceeded", "heavy load"])
            
            if is_quota or is_transient:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"[RETRY] {model_id} hit transient error: {err_msg[:50]}... Waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"QUOTA_EXHAUSTED: {model_id}")
            
            # Default fallback for unhandled exceptions
            raise e

def run_direct_flow(image_path, user_desc, voice_reqs, model_id="gemini-2.0-flash"):
    """
    Executes a 7-phase agentic flow with robust multi-key fallback.
    """
    google_keys = [
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GOOGLE_API_KEY_2"),
        os.getenv("GOOGLE_API_KEY_3"),
        os.getenv("GOOGLE_API_KEY_4"),
        os.getenv("GOOGLE_API_KEY_5"),
        os.getenv("GOOGLE_API_KEY_6"),
        os.getenv("GOOGLE_API_KEY_7"),
        os.getenv("GOOGLE_API_KEY_8")
    ]
    google_keys = [k for k in google_keys if k] # Filter out missing keys
    
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    current_model = model_id
    current_key_idx = 0
    
    def get_next_model(failed_model, is_vision=False):
        rotation = VISION_MODELS if is_vision else TEXT_MODELS
        try:
            current_idx = rotation.index(failed_model)
            return rotation[(current_idx + 1) % len(rotation)]
        except ValueError:
            return rotation[0]

    def execute_with_fallback(prompt, has_image=False):
        nonlocal current_model, current_key_idx
        
        # Ensure model is valid for the task type
        if has_image and current_model not in VISION_MODELS:
            current_model = VISION_MODELS[0]
        elif not has_image and current_model not in TEXT_MODELS:
            current_model = TEXT_MODELS[0]

        attempts = 0
        while attempts < 12: # Aligned with resilient_engine
            is_openai = "gpt" in current_model.lower()
            is_openrouter = "openrouter" in current_model.lower()
            client = openai_client if (is_openai or is_openrouter) else None
            
            if is_openrouter:
                try:
                    raw_model = current_model.replace("openrouter/", "")
                    print(f"[OPENROUTER] Trying {raw_model}...")
                    # Manual OpenRouter Call via OpenAI Client
                    router_client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=os.getenv("OPENROUTER_API_KEY")
                    )
                    return safe_generate(router_client, raw_model, prompt, True, image_path if has_image else None)
                except Exception as e:
                    if "402" in str(e) or "quota" in str(e).lower():
                        print(f"[QUOTA] OpenRouter limit reached. Rotating...")
                    else: raise e
            elif not is_openai:
                # Try all Google keys for the current model
                keys_to_try = google_keys[current_key_idx:] + google_keys[:current_key_idx]
                for key in keys_to_try:
                    k_idx = google_keys.index(key) + 1
                    try:
                        print(f"[ROTATION] {current_model} | Key {k_idx}/8...")
                        res = safe_generate(client, current_model, prompt, is_openai, image_path if has_image else None, api_key=key)
                        current_key_idx = google_keys.index(key) 
                        return res
                    except Exception as e:
                        if "MODEL_NOT_FOUND" in str(e):
                            print(f"[ERROR] Model {current_model} NOT FOUND. Skipping all keys...")
                            break # Go immediately to next model fallback
                        if "QUOTA_EXHAUSTED" in str(e):
                            print(f"[QUOTA] Key {k_idx} hit limit for {current_model}. Rotating key...")
                            continue 
                        raise e
            else:
                try:
                    print(f"[OPENAI] Trying OpenAI model {current_model}...")
                    return safe_generate(client, current_model, prompt, is_openai, image_path if has_image else None)
                except Exception as e:
                    if "QUOTA_EXHAUSTED" not in str(e):
                        raise e
            
            # If all keys failed for this model, fallback to next model
            next_model = get_next_model(current_model, is_vision=has_image)
            wait_time = 3 
            print(f"[NUCLEAR_FAILOVER] Exhausted {current_model}. Falling back to {next_model} in {wait_time}s...")
            current_model = next_model
            current_key_idx = 0
            attempts += 1
            time.sleep(wait_time)
            
        raise RuntimeError("CRITICAL FAILURE: Complete resource exhaustion after exhaustive Nuclear-Tier rotation.")

    # Setup project
    if os.path.exists("generated_project"):
        shutil.rmtree("generated_project")
    os.makedirs("generated_project")

    # PHASE 1: VISION AGENT
    yield {"status": f"Phase 1: Vision Agent Analyzing Sketch (Resilience Active)...", "progress": 5}
    vision_prompt = f"""
    ROLE: Vision Agent
    TASK: Generate initial blueprint from visual sketches.
    CONTEXT: {user_desc} | Requirements: {voice_reqs}
    OUTPUT: Detailed visual context and structural wireframe description.
    """
    try:
        vision_context = execute_with_fallback(vision_prompt, has_image=True)
        yield {"status": "Vision Analysis Complete!", "vision": vision_context, "progress": 15}
    except Exception as e:
        yield {"error": f"Vision Phase failed: {str(e)}"}
        return

    # PHASE 2: ARCHITECT AGENT
    yield {"status": f"Phase 2: Architect Agent Designing System ({current_model})...", "progress": 25}
    arch_prompt = f"""
    ROLE: Architect Agent
    TASK: Validate and expand the blueprint into a deep-reasoning engineering document.
    CONTEXT: {vision_context}
    OUTPUT: 5-layer architectural blueprint (Functional, UI, Logic, Automation, Green-AI).
    Include a Mermaid.js diagram for the architecture.
    """
    try:
        blueprint = execute_with_fallback(arch_prompt)
        yield {"status": "Architectural Blueprint Created!", "blueprint": blueprint, "progress": 40}
    except Exception as e:
        yield {"error": f"Architectural Phase failed: {str(e)}"}
        return

    # PHASE 3: DEVELOPER AGENT
    yield {"status": f"Phase 3: Developer Agent Generating Code ({current_model})...", "progress": 55}
    dev_prompt = f"""
    ROLE: Developer Agent
    TASK: Generate real project files using the filename|content precision format.
    CONTEXT: {blueprint}
    OUTPUT: Complete codebase. Every file must be bounded by ---FILE_START--- and ---FILE_END---.
    Format: filename|content
    """
    try:
        dev_output = execute_with_fallback(dev_prompt)
        
        # Robust Parsing
        files_created = []
        if "---FILE_START---" in dev_output:
            file_blocks = dev_output.split("---FILE_START---")[1:]
            for block in file_blocks:
                if "---FILE_END---" in block:
                    content_block = block.split("---FILE_END---")[0].strip()
                    if "|" in content_block:
                        filename, code = content_block.split("|", 1)
                        filename = filename.strip("`").strip()
                        if code.startswith("```"):
                            lines = code.splitlines()
                            if len(lines) > 2: code = "\n".join(lines[1:-1])
                        
                        filepath = os.path.join("generated_project", filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(code)
                        files_created.append(filename)
        
        yield {"status": f"Developed {len(files_created)} files!", "files": files_created, "progress": 70}
    except Exception as e:
        yield {"error": f"Development Phase failed: {str(e)}"}
        return

    # PHASE 4: DEBUG AGENT
    yield {"status": f"Phase 4: Debug Agent Self-Healing ({current_model})...", "progress": 75}
    debug_prompt = f"""
    ROLE: Debug Agent
    TASK: Improve reliability through automated self-healing and code fixes.
    CONTEXT: {dev_output}
    OUTPUT: Detailed debug report and refactored snippets.
    """
    try:
        debug_report = execute_with_fallback(debug_prompt)
        with open(os.path.join("generated_project", "debug_report.md"), "w", encoding="utf-8") as f:
            f.write(debug_report)
        yield {"status": "Debug & Healing Complete!", "debug": debug_report, "progress": 82}
    except Exception as e:
        yield {"error": f"Debug Phase failed: {str(e)}"}
        return

    # PHASE 5: OPTIMIZATION AGENT
    yield {"status": f"Phase 5: Optimization Agent Enhancing Efficiency ({current_model})...", "progress": 85}
    opt_prompt = f"""
    ROLE: Optimization Agent
    TASK: Improve efficiency by minimizing dependencies and runtime overhead.
    CONTEXT: {dev_output}
    OUTPUT: Lightweight code structure and optimization report.
    """
    try:
        opt_report = execute_with_fallback(opt_prompt)
        yield {"status": "Optimization Analysis Complete!", "optimization": opt_report, "progress": 88}
    except Exception as e:
        yield {"error": f"Optimization Phase failed: {str(e)}"}
        return

    # PHASE 6: COGNITIVE LOAD & DX AGENT
    yield {"status": f"Phase 6: Cognitive Load & DX Agent Analyzing Complexity ({current_model})...", "progress": 90}
    cog_prompt = f"""
    ROLE: Cognitive Load & Developer Experience Optimization Agent
    TASK: Analyze developer interaction patterns and detect signs of cognitive overload.
    MISSION: Dynamically adapt system complexity to match the developer’s mental capacity.
    CONTEXT: {user_desc} | {blueprint} | {dev_output}
    ANALYZE:
    1. Prompt Complexity (Length, Ambiguity, Repeated clarifications)
    2. Debugging Friction (Frequency of errors, frustration)
    3. Architectural Cognitive Burden (Excessive abstraction, over-modularization, dependencies)
    
    IF OVERLOAD DETECTED: Recommend simplification, beginner-friendly explanations, or step-by-step breakdowns.
    
    OUTPUT FORMAT:
    - Cognitive Load Score (1–10)
    - Detected Friction Sources
    - Architecture Simplification Suggestions
    - Developer Productivity Adaptations
    - Mentorship Style Guidance
    """
    try:
        cog_report = execute_with_fallback(cog_prompt)
        yield {"status": "Cognitive & DX Audit Complete!", "cognitive_load": cog_report, "progress": 92}
    except Exception as e:
        yield {"error": f"Cognitive Phase failed: {str(e)}"}
        return

    # PHASE 7: SUSTAINABILITY AGENT
    yield {"status": f"Phase 7: Sustainability Agent Auditing Green-AI ({current_model})...", "progress": 95}
    audit_prompt = f"""
    ROLE: Sustainability Agent
    TASK: Evaluate global impact and carbon footprint.
    CONTEXT: {blueprint} | {dev_output}
    OUTPUT: Green-AI Audit score and exclusivity/inclusivity report.
    """
    try:
        audit_report = execute_with_fallback(audit_prompt)
        yield {
            "status": "Aura-Dev 7-Agent Workflow Complete!", 
            "audit": audit_report, 
            "progress": 100, 
            "final_result": dev_output, 
            "debug_report": debug_report,
            "opt_report": opt_report,
            "cog_report": cog_report
        }
    except Exception as e:
        yield {"error": f"Sustainability Phase failed: {str(e)}"}
        return
