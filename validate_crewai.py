from crewai import Agent
from crewai.tools import tool
import os

@tool("test_tool")
def test_tool(data: str):
    """Test tool"""
    return data

try:
    agent = Agent(
        role='Tester',
        goal='Test',
        backstory='Test',
        tools=[test_tool],
        verbose=True,
        # llm=... (optional for simple validation)
    )
    print("Agent creation validation passed!")
except Exception as e:
    import traceback
    traceback.print_exc()
