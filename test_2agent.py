from crewai import Agent, Task, Crew
from resilient_engine import get_resilient_llm
import os

def test_2agent_crew():
    llm = get_resilient_llm(model_name="gemini-1.5-flash")
    
    agent1 = Agent(
        role='Researcher',
        goal='Research the topic.',
        backstory='Expert researcher.',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    agent2 = Agent(
        role='Writer',
        goal='Write a summary.',
        backstory='Expert writer.',
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    task1 = Task(
        description='Research about AI.',
        expected_output='Key AI facts.',
        agent=agent1
    )
    
    task2 = Task(
        description='Summarize the research.',
        expected_output='A nice summary.',
        agent=agent2,
        context=[task1]
    )
    
    crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])
    try:
        result = crew.kickoff()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_2agent_crew()
