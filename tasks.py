from crewai import Task
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

# 0. Planning & Roadmapping Task
planning_task = Task(
    description=(
        "Given the project goal ({project_goal}) and high-level requirements ({voice_reqs}), "
        "analyze prior project memory (via tools) and construct a concrete, multi-phase delivery plan. "
        "Identify milestones for vision, architecture, implementation, testing, documentation, "
        "optimization, and sustainability. Persist this plan into long-horizon memory."
    ),
    expected_output="A structured, actionable roadmap with milestones and risk notes.",
    agent=planner,
)

# 1. Vision Analysis Task
vision_task = Task(
    description=(
        "Analyze the provided visual sketch ({image_desc}) and technical requirements ({voice_reqs}). "
        "Generate a detailed structural wireframe description aligned with the current roadmap."
    ),
    expected_output="Visual context and structural wireframe description.",
    agent=vision_architect,
    context=[planning_task],
)

# 2. Architectural Design Task
arch_task = Task(
    description=(
        "Validate and expand the vision context into a 5-layer architectural blueprint "
        "(Functional, UI, Logic, Automation, Green-AI). Include a Mermaid.js diagram and "
        "link decisions back to the roadmap milestones."
    ),
    expected_output="5-layer architectural blueprint with Mermaid.js diagram.",
    agent=vision_architect,
    context=[planning_task, vision_task],
)

# 3. Code Implementation Task
dev_task = Task(
    description=(
        "Generate real project files based on the Architectural Blueprint. "
        "You MUST use the write_file_tool to save EVERY single file required for the complete "
        "project into the generated_project/ directory. When using the write_file_tool, pass the "
        "input EXACTLY in this format: filename.extension|code_content. Do not just output the "
        "code; you must execute the write_file_tool for each file. Ensure production-grade "
        "architecture, modularity, and PEP8 compliance."
    ),
    expected_output="Complete, production-ready codebase in generated_project/ directory.",
    agent=developer,
    context=[arch_task],
)

# 4. Self-Healing Debug Task
debug_task = Task(
    description=(
        "Analyze the generated code, detect bugs, and apply fixes. Focus on syntax errors, "
        "missing imports, failure paths, and integration issues. Document changes in a clear "
        "debug report and persist key findings to memory."
    ),
    expected_output="Refactored code and a detailed debug_report.md.",
    agent=debug_engineer,
    context=[dev_task],
)

# 5. Test & QA Task
test_task = Task(
    description=(
        "Design and implement automated tests (unit, integration or API-level as appropriate) "
        "for the generated project. Use write_file_tool to create test files under generated_project/. "
        "Where possible, infer realistic test scenarios from the roadmap, blueprint and requirements. "
        "Summarize overall coverage and remaining risks."
    ),
    expected_output="A test suite in generated_project/ and a concise test strategy summary.",
    agent=test_engineer,
    context=[dev_task, debug_task],
)

# 6. Performance Optimization Task
opt_task = Task(
    description=(
        "Identify and replace heavy dependencies. Optimize runtime overhead and resource usage "
        "without sacrificing readability. Propose concrete code-level and infrastructure-level "
        "changes and, when safe, apply them directly."
    ),
    expected_output="Optimization report and lightweight code adjustments.",
    agent=optimization_specialist,
    context=[dev_task, debug_task, test_task],
)

# 7. Cognitive & DX Audit Task
dx_task = Task(
    description=(
        "Analyze the developer experience and cognitive burden of the system, considering the "
        "project structure, naming, documentation, and tooling. Recommend changes that make the "
        "system easier to extend and maintain, especially over long horizons."
    ),
    expected_output="Cognitive Load Score and DX adaptation recommendations.",
    agent=dx_specialist,
    context=[dev_task, opt_task],
)

# 8. Sustainability Audit Task
sustainability_task = Task(
    description=(
        "Perform a final Green-AI audit of the entire project lifecycle. Evaluate energy usage, "
        "inclusivity, and operational footprint. Recommend practical changes to reduce carbon "
        "impact and improve accessibility."
    ),
    expected_output="Green-AI Audit score and sustainability report.",
    agent=sustainability_auditor,
    context=[dev_task, opt_task],
)

# 9. Documentation Task
documentation_task = Task(
    description=(
        "Generate and/or refine high-quality documentation for the project. This includes a "
        "top-level README, architecture overview, and any API or usage docs that are critical "
        "for onboarding a new engineer. Use write_file_tool to persist documentation into "
        "generated_project/ and keep a brief changelog in memory."
    ),
    expected_output="Documentation files in generated_project/ and a short documentation changelog.",
    agent=documentation_engineer,
    context=[arch_task, dev_task, debug_task, opt_task],
)

# 10. Code Review & Governance Task
review_task = Task(
    description=(
        "Review the final codebase, tests, and documentation from a governance perspective. "
        "Highlight architectural risks, technical debt, and suggested follow-up iterations. "
        "Summarize findings in a review report suitable for long-horizon steering."
    ),
    expected_output="Code review and governance report, suitable for steering future iterations.",
    agent=review_agent,
    context=[
        planning_task,
        arch_task,
        dev_task,
        debug_task,
        test_task,
        opt_task,
        documentation_task,
    ],
)

