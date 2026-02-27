import os
import shutil
from crewai import Crew, Process
from tasks import (
    planning_task,
    vision_task,
    arch_task,
    dev_task,
    debug_task,
    test_task,
    opt_task,
    dx_task,
    sustainability_task,
    documentation_task,
    review_task,
)
from agents import (
    planner,
    vision_architect,
    developer,
    debug_engineer,
    test_engineer,
    optimization_specialist,
    dx_specialist,
    sustainability_auditor,
    documentation_engineer,
    review_agent,
)
from memory_store import append_memory


def run_aura_crew(image_path, user_desc, voice_reqs, model_choice=None):
    """
    Executes the multi-agent Aura-Dev flow and yields status updates.
    This is the high-level, collaborative society of agents pipeline.
    """
    # Setup project
    if os.path.exists("generated_project"):
        shutil.rmtree("generated_project")
    os.makedirs("generated_project")

    # Initialize the Crew and optionally retarget LLMs
    if model_choice:
        from resilient_engine import get_resilient_llm

        new_llm = get_resilient_llm(model_choice)
        for agent in [
            planner,
            vision_architect,
            developer,
            debug_engineer,
            test_engineer,
            optimization_specialist,
            dx_specialist,
            sustainability_auditor,
            documentation_engineer,
            review_agent,
        ]:
            agent.llm = new_llm

    aura_crew = Crew(
        agents=[
            planner,
            vision_architect,
            developer,
            debug_engineer,
            test_engineer,
            optimization_specialist,
            dx_specialist,
            sustainability_auditor,
            documentation_engineer,
            review_agent,
        ],
        tasks=[
            planning_task,
            vision_task,
            arch_task,
            dev_task,
            debug_task,
            test_task,
            opt_task,
            dx_task,
            sustainability_task,
            documentation_task,
            review_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    inputs = {
        "image_desc": f"Technical sketch at {image_path}",
        "voice_reqs": voice_reqs,
        "project_goal": user_desc,
    }

    append_memory(
        "runs",
        {
            "kind": "run_start",
            "summary": f"New Aura-Dev run started for goal='{user_desc}'",
            "image_path": image_path,
        },
    )

    yield {"status": "🚀 CrewAI: Orchestrating multi-agent Aura-Dev workflow...", "progress": 5}

    try:
        result = aura_crew.kickoff(inputs=inputs)

        # Gather files from generated_project
        files_created = []
        if os.path.exists("generated_project"):
            for root, _, filenames in os.walk("generated_project"):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), "generated_project"
                    )
                    files_created.append(rel_path)

        # Map task outputs by index for clarity
        outputs = result.tasks_output

        planning_out = str(outputs[0]) if len(outputs) > 0 else ""
        vision_out = str(outputs[1]) if len(outputs) > 1 else ""
        arch_out = str(outputs[2]) if len(outputs) > 2 else ""
        dev_out = str(outputs[3]) if len(outputs) > 3 else ""
        debug_out = str(outputs[4]) if len(outputs) > 4 else ""
        test_out = str(outputs[5]) if len(outputs) > 5 else ""
        opt_out = str(outputs[6]) if len(outputs) > 6 else ""
        dx_out = str(outputs[7]) if len(outputs) > 7 else ""
        sustain_out = str(outputs[8]) if len(outputs) > 8 else ""
        docs_out = str(outputs[9]) if len(outputs) > 9 else ""
        review_out = str(outputs[10]) if len(outputs) > 10 else ""

        append_memory(
            "runs",
            {
                "kind": "run_complete",
                "summary": f"Aura-Dev run completed for goal='{user_desc}'",
            },
        )

        final_update = {
            "status": "Aura-Dev CrewAI Workflow Complete!",
            "progress": 100,
            "final_result": dev_out,
            "files": files_created,
            "roadmap": planning_out,
            "vision": vision_out,
            "blueprint": arch_out,
            "debug": debug_out,
            "tests": test_out,
            "optimization": opt_out,
            "cog_report": dx_out,
            "audit": sustain_out or "Sustainability Audit Complete.",
            "docs": docs_out,
            "review": review_out,
        }

        yield final_update

    except Exception as e:
        import traceback

        err_trace = traceback.format_exc()
        append_memory(
            "runs",
            {
                "kind": "run_error",
                "summary": f"CrewAI workflow failed: {str(e)}",
            },
        )
        yield {"error": f"CrewAI Workflow failed: {str(e)}\n\nTraceback:\n{err_trace}"}
