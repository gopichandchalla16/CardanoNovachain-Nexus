import os
import uvicorn
import uuid
import importlib
import asyncio # Add asyncio for background tasks if needed, though not strictly required for this logic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

# --------------------------------------------------------------------------
# Load Environment Variables
# --------------------------------------------------------------------------
load_dotenv()


# --------------------------------------------------------------------------
# Masumi SDK (dynamic import with fallback stubs)
# --------------------------------------------------------------------------
try:
    # Attempt to import Masumi SDK components
    masumi_config = importlib.import_module("masumi.config")
    masumi_payment = importlib.import_module("masumi.payment")

    Config = getattr(masumi_config, "Config")
    Payment = getattr(masumi_payment, "Payment")
    Amount = getattr(masumi_payment, "Amount")

except Exception:
    # Fallback for local development
    class Config:
        def __init__(self, payment_service_url=None, payment_api_key=None):
            self.payment_service_url = payment_service_url
            self.payment_api_key = payment_api_key

    class Amount:
        def __init__(self, amount, unit):
            self.amount = amount
            self.unit = unit

        def __repr__(self):
            return f"Amount(amount={self.amount}, unit={self.unit})"

    class Payment:
        def __init__(
            self,
            agent_identifier=None,
            config=None,
            identifier_from_purchaser=None,
            input_data=None,
            network=None,
            amounts=None,
        ):
            self.agent_identifier = agent_identifier
            self.identifier_from_purchaser = identifier_from_purchaser
            self.input_data = input_data
            self.network = network
            self.config = config
            self.amounts = amounts or []
            self.payment_ids = set()
            self.input_hash = "dev-hash"

        async def create_payment_request(self):
            return {
                "data": {
                    "blockchainIdentifier": "stub-blockchain-id",
                    "submitResultTime": None,
                    "unlockTime": None,
                    "externalDisputeUnlockTime": None,
                    "payByTime": None,
                }
            }

        async def start_status_monitoring(self, callback):
            return

        async def check_payment_status(self):
            # In a real app, this would check if payment is confirmed
            return {"data": {"status": "completed"}} 

        async def complete_payment(self, payment_id, result_string):
            return {"status": "completed"}

        def stop_status_monitoring(self):
            return


# --------------------------------------------------------------------------
# Local Modules (Correct RELATIVE imports)
# --------------------------------------------------------------------------
# These imports require crew_definition.py, logging_config.py, and verification_agent.py 
# to be present in the same directory.
from .crew_definition import ResearchCrew
from .logging_config import setup_logging, get_logger
from .verification_agent import VerificationAgent 


# --------------------------------------------------------------------------
# Setup Logger
# --------------------------------------------------------------------------
logger = setup_logging()


# --------------------------------------------------------------------------
# Load Keys and Settings
# --------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
NETWORK = os.getenv("NETWORK")
AGENT_IDENTIFIER = os.getenv("AGENT_IDENTIFIER")


# --------------------------------------------------------------------------
# Gemini -> CrewAI Compatible Setup
# --------------------------------------------------------------------------
if GEMINI_API_KEY:
    # CrewAI uses the OpenAI client interface, which Gemini supports
    os.environ["OPENAI_API_KEY"] = GEMINI_API_KEY
    os.environ["OPENAI_API_BASE"] = (
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    # Default model to use for CrewAI agents
    os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME", "gemini-2.5-flash")
    logger.info("CrewAI configured for Gemini API compatibility")
else:
    logger.warning("⚠ No GEMINI_API_KEY found! CrewAI tasks will likely fail.")


# --------------------------------------------------------------------------
# FastAPI App Init + CORS
# --------------------------------------------------------------------------
app = FastAPI(
    title="CognitoSync Masumi Agent",
    description="AI-powered decentralized knowledge verification engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Global Stores
# --------------------------------------------------------------------------
jobs: Dict[str, Dict[str, Any]] = {}
payment_instances: Dict[str, Payment] = {}


# --------------------------------------------------------------------------
# Pydantic Models
# --------------------------------------------------------------------------
class StartJobRequest(BaseModel):
    identifier_from_purchaser: str
    input_data: Dict[str, str]


# --------------------------------------------------------------------------
# CrewAI Task Runner (Synchronous execution)
# --------------------------------------------------------------------------
def execute_crew_task(job_id: str, input_data: Dict[str, str]):
    """Synchronously executes the CrewAI task and updates the job status."""
    logger.info(f"Running CrewAI task for job {job_id}")
    try:
        crew = ResearchCrew(verbose=False, logger=logger)
        result = crew.crew.kickoff(inputs=input_data)
        
        # Update job status with result
        jobs[job_id]["result"] = result
        jobs[job_id]["status"] = "completed"
        logger.info(f"Job {job_id} completed successfully.")
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = f"Task failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {str(e)}")


# --------------------------------------------------------------------------
# POST /start_job
# --------------------------------------------------------------------------
@app.post("/start_job")
async def start_job(request: StartJobRequest):
    job_id = str(uuid.uuid4())

    logger.info(f"📝 New job {job_id} created, awaiting payment")

    # Masumi payment configuration
    amounts = [Amount(amount="10000000", unit="lovelace")]  # Example: 10 ADA default

    payment = Payment(
        agent_identifier=AGENT_IDENTIFIER,
        identifier_from_purchaser=request.identifier_from_purchaser,
        input_data=request.input_data,
        network=NETWORK,
        amounts=amounts,
        config=Config(
            payment_service_url=PAYMENT_SERVICE_URL,
            payment_api_key=PAYMENT_API_KEY,
        ),
    )

    payment_req = await payment.create_payment_request()
    blockchain_id = payment_req["data"]["blockchainIdentifier"]

    payment.payment_ids.add(blockchain_id)
    payment_instances[job_id] = payment

    jobs[job_id] = {
        "status": "awaiting_payment",
        "payment_status": "pending",
        "input_data": request.input_data,
        "result": None,
        "blockchain_identifier": blockchain_id,
        "payment_instance": payment # Store the instance for monitoring
    }

    # In a real Masumi implementation, you would start monitoring here.
    # For this stub, we will assume completion and start the task immediately.

    # Start the task (using a simple placeholder logic for demonstration)
    def start_processing():
        # In a production agent, you would wait for payment confirmation here.
        # For the stub: assume payment is confirmed and start the task in a thread/process.
        execute_crew_task(job_id, request.input_data)

    # Use asyncio.to_thread to run the synchronous CrewAI task without blocking FastAPI
    asyncio.to_thread(start_processing)
    
    return {
        "status": "success",
        "job_id": job_id,
        "blockchainIdentifier": blockchain_id,
        "agentIdentifier": AGENT_IDENTIFIER,
        "amounts": amounts,
        "message": "Job initiated. Check status endpoint for completion."
    }


# --------------------------------------------------------------------------
# GET /status
# --------------------------------------------------------------------------
@app.get("/status")
async def job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job_info = jobs[job_id].copy()
    # Remove the internal Payment instance before returning
    job_info.pop("payment_instance", None) 
    
    return job_info


# --------------------------------------------------------------------------
# GET /health
# --------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "healthy"}


# --------------------------------------------------------------------------
# GET /input_schema (Masumi Standard)
# --------------------------------------------------------------------------
@app.get("/input_schema")
async def input_schema():
    return {
        "input_data": [
            {
                "id": "text",
                "type": "string",
                "name": "Task Description",
                "data": {
                    "description": "Enter text for CognitoSync AI to analyze",
                    "placeholder": "Enter your topic...",
                },
            }
        ]
    }


# --------------------------------------------------------------------------
# Run App
# --------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )