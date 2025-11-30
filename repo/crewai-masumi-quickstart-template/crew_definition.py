import os
import hashlib
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from logging_config import get_logger

# Load environment variables
load_dotenv(override=True)

# Set Gemini API Key
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

os.environ["GOOGLE_API_KEY"] = gemini_api_key

class VerificationAgent:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.search_tool = DuckDuckGoSearchRun()
        self.logger.info("VerificationAgent initialized")

    def verify(self, url: str):
        self.logger.info(f"Verifying URL: {url}")
        
        # Define agents
        researcher = Agent(
            role='Fact-Checking Analyst',
            goal=f'Analyze the content of the URL ({url}) and verify its claims',
            backstory='An expert in fact-checking and content verification',
            verbose=self.verbose,
            tools=[
                Tool(
                    name="DuckDuckGo Search",
                    func=self.search_tool.run,
                    description="Useful for searching the web for information"
                )
            ]
        )

        summarizer = Agent(
            role='Verification Summarizer',
            goal='Summarize the verification findings in a clear and concise report',
            backstory='A skilled writer who can synthesize complex information',
            verbose=self.verbose
        )

        # Define tasks
        research_task = Task(
            description=f'Verify the claims and information presented in the URL: {url}',
            expected_output='A detailed report of the verification findings',
            agent=researcher
        )

        summary_task = Task(
            description='Create a summary of the verification report',
            expected_output='A concise summary of the key findings',
            agent=summarizer
        )

        # Create and run the crew
        crew = Crew(
            agents=[researcher, summarizer],
            tasks=[research_task, summary_task],
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        
        # Simulate results for demonstration
        cardano_hash = hashlib.sha256(url.encode()).hexdigest()
        
        return {
            "url": url,
            "summary": result,
            "reliability_score": 85.0,
            "bias_level": 3,
            "verification_status": "Verified",
            "cardano_hash": cardano_hash,
            "bias_analysis": {"political": "neutral", "commercial": "low"}
        }
