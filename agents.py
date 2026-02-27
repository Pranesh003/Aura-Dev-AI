from crewai import Agent
from resilient_engine import get_resilient_llm
from tools import DevelopmentTools

tools = DevelopmentTools()

# Shared Resilient LLM
resilient_llm = get_resilient_llm(model_name="gemini-1.5-flash")

# 1. Lead Multimodal Vision Architect
vision_architect = Agent(
    role='Lead Multimodal Vision Architect',
    goal='Convert abstract visual sketches into deep-reasoning engineering blueprints.',
    backstory='Expert in visual analysis and translating UI/UX sketches into technical requirements.',
    llm=get_resilient_llm(model_name="gemini-1.5-flash"), 
    tools=[tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 3. Senior Autonomous Full-Stack Engineer
developer = Agent(
    role='Senior Autonomous Full-Stack Engineer',
    goal='Convert blueprints into production-ready, modular software architectures.',
    backstory='Expert coder proficient in multiple languages, following best practices and PEP8.',
    llm=resilient_llm,
    tools=[tools.write_file_tool],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 4. Autonomous Debugging Engineer
debug_engineer = Agent(
    role='Autonomous Debugging Engineer',
    goal='Detect and fix syntax errors, missing imports, and logic bottlenecks.',
    backstory='Expert troubleshooter who heals code and ensures it runs perfectly.',
    llm=resilient_llm,
    tools=[tools.write_file_tool, tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 5. Performance Optimization Specialist
optimization_specialist = Agent(
    role='Performance Optimization Specialist',
    goal='Reduce runtime overhead by identifying heavy dependencies and suggesting alternatives.',
    backstory='Optimizer who trims the fat from software to make it lean and fast.',
    llm=resilient_llm,
    tools=[tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 7. Green AI & Sustainable Software Auditor
sustainability_auditor = Agent(
    role='Green AI & Sustainable Software Auditor',
    goal='Evaluate compute efficiency, carbon risk, and inclusivity.',
    backstory='Sustainability engineer focused on minimizing the environmental impact of AI.',
    llm=resilient_llm,
    tools=[tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 6. Cognitive Load & DX Optimization Specialist
dx_specialist = Agent(
    role='Cognitive Load & DX Optimization Specialist',
    goal='Analyze interaction patterns and simplify systems to reduce developer burden.',
    backstory='Human-Computer Interaction expert focused on Developer Experience.',
    llm=resilient_llm,
    tools=[tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)

# 15. Workflow Controller (Orchestrator)
workflow_controller = Agent(
    role='Workflow Controller',
    goal='Orchestrate the sequential autonomous development flow across all agents.',
    backstory='Management agent that ensures the mission goal is achieved efficiently.',
    llm=resilient_llm,
    tools=[tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200
)
