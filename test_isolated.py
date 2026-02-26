from crewai import Agent, Task, Crew
from resilient_engine import get_resilient_llm
from tools import DevelopmentTools
import os
import traceback

def test_isolated_crew():
    print("🚀 Starting Isolated Crew Test...")
    try:
        llm = get_resilient_llm()
        tools = DevelopmentTools()
        
        # Simple agent with the resilient LLM
        agent = Agent(
            role='Test Agent',
            goal='Write a simple summary to a file.',
            backstory='A helpful assistant.',
            llm=llm,
            tools=[tools.write_file_tool],
            verbose=True
        )
        
        task = Task(
            description='Write "Test passed" to a file named "isolated_test.txt" using write_file_tool.',
            expected_output='Confirmation message from tool.',
            agent=agent
        )
        
        crew = Crew(agents=[agent], tasks=[task])
        print("Kickoff starting...")
        result = crew.kickoff()
        print(f"✅ Success! Result: {result}")
        
    except Exception as e:
        print(f"❌ Failure: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_isolated_crew()
