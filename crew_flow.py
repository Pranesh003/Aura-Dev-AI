import os
import time
from crewai import Crew, Process
from tasks import (
    vision_task, arch_task, dev_task, debug_task,
    opt_task, dx_task, sustainability_task
)
from agents import (
    vision_architect, developer, debug_engineer,
    optimization_specialist, dx_specialist, sustainability_auditor
)

def run_aura_crew(image_path, user_desc, voice_reqs, model_choice=None):
    """
    Executes the 7-agent CrewAI flow and yields status updates.
    """
    # Initialize the Crew
    if model_choice:
        from resilient_engine import get_resilient_llm
        new_llm = get_resilient_llm(model_choice)
        for agent in [vision_architect, developer, debug_engineer, optimization_specialist, dx_specialist, sustainability_auditor]:
            agent.llm = new_llm
            
    aura_crew = Crew(
        agents=[
            vision_architect, developer, debug_engineer,
            optimization_specialist, dx_specialist, sustainability_auditor
        ],
        tasks=[
            vision_task, arch_task, dev_task, debug_task,
            opt_task, dx_task, sustainability_task
        ],
        process=Process.sequential,
        verbose=True
    )

    inputs = {
        "image_desc": f"Technical sketch at {image_path}",
        "voice_reqs": voice_reqs,
        "project_goal": user_desc
    }

    # Since CrewAI's kickoff is blocking, we can't easily yield granular task-by-task 
    # progress WITHOUT a custom callback. We'll use a callback or just yield 
    # checkpoints if we were running them individually, but kickoff is better.
    
    yield {"status": "🚀 CrewAI: Orchestrating 7-Agent Architecture...", "progress": 5}
    
    try:
        # For granular updates, we could use task callbacks, but for now we'll 
        # run the kickoff and then provide the results.
        result = aura_crew.kickoff(inputs=inputs)
        
        # In a real scenario, we'd parse the 'result' object which contains task outputs.
        # CrewAI 1.9.3 result object has tasks_output.
        
        # Mapping results to the UI expectation
        final_update = {
            "status": "Aura-Dev CrewAI Workflow Complete!",
            "progress": 100,
            "final_result": str(aura_crew.tasks_output[2]), # dev_task
            "vision": str(aura_crew.tasks_output[0]),
            "blueprint": str(aura_crew.tasks_output[1]),
            "debug": str(aura_crew.tasks_output[3]),
            "optimization": str(aura_crew.tasks_output[4]),
            "cog_report": str(aura_crew.tasks_output[5]),
            "audit": str(aura_crew.tasks_output[6]) if len(aura_crew.tasks_output) > 6 else "Sustainability Audit Complete."
        }
        
        yield final_update
        
    except Exception as e:
        import traceback
        err_trace = traceback.format_exc()
        yield {"error": f"CrewAI Workflow failed: {str(e)}\n\nTraceback:\n{err_trace}"}
