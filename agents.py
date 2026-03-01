from crewai import Agent
from resilient_engine import get_resilient_llm
from tools import DevelopmentTools

tools = DevelopmentTools()

# Shared Resilient LLM
resilient_llm = get_resilient_llm(model_name="gemini-1.5-flash")

# 0. Project Planner & Orchestrator
planner = Agent(
    role="Project Planner & Orchestrator",
    goal=(
        "Transform high-level goals into a multi-phase delivery plan, "
        "coordinate agents, and update long-horizon project memory."
    ),
    backstory=(
        "Principal engineer responsible for decomposing work, sequencing agents, "
        "and maintaining a living roadmap for the project."
    ),
    llm=resilient_llm,
    tools=[tools.write_memory, tools.read_memory, tools.list_generated_files],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 1. Lead Multimodal Vision Architect
vision_architect = Agent(
    role="Lead Multimodal Vision Architect",
    goal="Convert abstract visual sketches into deep-reasoning engineering blueprints.",
    backstory="Expert in visual analysis and translating UI/UX sketches into technical requirements.",
    llm=get_resilient_llm(model_name="gemini-1.5-flash"),
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200,
)

# 3. Senior Autonomous Full-Stack Engineer
developer = Agent(
    role="Senior Autonomous Full-Stack Engineer",
    goal="Convert blueprints into production-ready, modular software architectures.",
    backstory="Expert coder proficient in multiple languages, following best practices and PEP8.",
    llm=resilient_llm,
    tools=[tools.write_file_tool, tools.list_generated_files, tools.write_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 4. Autonomous Debugging Engineer
debug_engineer = Agent(
    role="Autonomous Debugging Engineer",
    goal="Detect and fix syntax errors, missing imports, and logic bottlenecks.",
    backstory="Expert troubleshooter who heals code and ensures it runs correctly end-to-end.",
    llm=resilient_llm,
    tools=[tools.write_file_tool, tools.list_generated_files, tools.write_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 4b. Autonomous Test & QA Engineer
test_engineer = Agent(
    role="Autonomous Test & QA Engineer",
    goal=(
        "Design, generate, and iteratively improve automated tests that validate "
        "functional and non-functional requirements."
    ),
    backstory="Quality-focused engineer responsible for robust test suites and continuous validation.",
    llm=resilient_llm,
    tools=[tools.write_file_tool, tools.list_generated_files, tools.write_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 5. Performance Optimization Specialist
optimization_specialist = Agent(
    role="Performance Optimization Specialist",
    goal="Reduce runtime overhead by identifying heavy dependencies and suggesting alternatives.",
    backstory="Optimizer who trims the fat from software to make it lean and fast.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200,
)

# 6. Cognitive Load & DX Optimization Specialist
dx_specialist = Agent(
    role="Cognitive Load & DX Optimization Specialist",
    goal="Analyze interaction patterns and simplify systems to reduce developer burden.",
    backstory="Human-Computer Interaction expert focused on Developer Experience.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200,
)

# 7. Green AI & Sustainable Software Auditor
sustainability_auditor = Agent(
    role="Green AI & Sustainable Software Auditor",
    goal="Evaluate compute efficiency, carbon risk, and inclusivity.",
    backstory="Sustainability engineer focused on minimizing the environmental impact of AI.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=3,
    max_execution_time=1200,
)

# 8. Documentation & Knowledge Engineer
documentation_engineer = Agent(
    role="Documentation & Knowledge Engineer",
    goal=(
        "Produce and continuously refine high-quality documentation, READMEs, "
        "API references, and onboarding guides from the evolving codebase."
    ),
    backstory="Technical writer-engineer hybrid who turns implementation details into clear knowledge assets.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_file_tool, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 9. Code Review & Governance Agent
review_agent = Agent(
    role="Code Review & Governance Agent",
    goal=(
        "Critically review generated code, enforce architecture and style guidelines, "
        "and propose incremental improvements over time."
    ),
    backstory="Principal reviewer responsible for keeping quality high as the system evolves.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)

# 15. Workflow Controller (Orchestrator)
workflow_controller = Agent(
    role="Workflow Controller",
    goal="Orchestrate the sequential autonomous development flow across all agents.",
    backstory="Management agent that ensures the mission goal is achieved efficiently.",
    llm=resilient_llm,
    tools=[tools.list_generated_files, tools.write_memory, tools.read_memory],
    verbose=True,
    allow_delegation=False,
    max_iter=4,
    max_execution_time=1800,
)
