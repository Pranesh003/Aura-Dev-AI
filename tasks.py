from crewai import Task
from agents import (
    vision_architect, developer, debug_engineer,
    optimization_specialist, dx_specialist, sustainability_auditor
)

# 1. Vision Analysis Task
vision_task = Task(
    description="Analyze the provided visual sketch ({image_desc}) and technical requirements ({voice_reqs}). Generate a detailed structural wireframe description.",
    expected_output="Visual context and structural wireframe description.",
    agent=vision_architect
)

# 2. Architectural Design Task
arch_task = Task(
    description="Validate and expand the vision context into a 5-layer architectural blueprint (Functional, UI, Logic, Automation, Green-AI). Include a Mermaid.js diagram.",
    expected_output="5-layer architectural blueprint with Mermaid.js diagram.",
    agent=vision_architect, # Can be reused or delegated
    context=[vision_task]
)

# 3. Code Implementation Task
dev_task = Task(
    description="""Generate real project files based on the Architectural Blueprint. 
    Use the format: ---FILE_START--- filename|content ---FILE_END--- for EVERY file. 
    Ensure PEP8 compliance and modularity.""",
    expected_output="Complete codebase in generated_project/ directory.",
    agent=developer,
    context=[arch_task]
)

# 4. Self-Healing Debug Task
debug_task = Task(
    description="Analyze the generated code, detect bugs, and apply fixes. Document changes in a debug report.",
    expected_output="Refactored code and a detailed debug_report.md.",
    agent=debug_engineer,
    context=[dev_task]
)

# 5. Performance Optimization Task
opt_task = Task(
    description="Identify and replace heavy dependencies. Optimize runtime overhead.",
    expected_output="Optimization report and lightweight code adjustments.",
    agent=optimization_specialist,
    context=[dev_task, debug_task]
)

# 6. Cognitive & DX Audit Task
dx_task = Task(
    description="Analyze the developer experience and cognitive burden of the system.",
    expected_output="Cognitive Load Score and DX adaptation recommendations.",
    agent=dx_specialist,
    context=[dev_task, opt_task]
)

# 7. Sustainability Audit Task
sustainability_task = Task(
    description="Perform a final Green-AI audit of the entire project lifecycle.",
    expected_output="Green-AI Audit score and sustainability report.",
    agent=sustainability_auditor,
    context=[dev_task, opt_task]
)