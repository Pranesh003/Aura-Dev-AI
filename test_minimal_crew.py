from crewai import Agent, Task, Crew
from resilient_engine import get_resilient_llm
import os

def test_minimal_crew():
    llm = get_resilient_llm()
    agent = Agent(
        role='Tester',
        goal='Test if prompt slices work.',
        backstory='A simple tester.',
        llm=llm,
        verbose=True
    )
    task = Task(
        description='Write "Hello World"',
        expected_output='The string "Hello World"',
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[task])
    try:
        result = crew.kickoff()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_minimal_crew()
