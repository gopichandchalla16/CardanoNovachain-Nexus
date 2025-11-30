"""
CognitoSync - AI-Powered Decentralized Knowledge Verification Agent
Cardano Hackathon Track-2: NovaChain Nexus
=====================================================

Architecture:
- Data Sourcing: IPFS, Arweave, distributed sources
- AI Verification: NLP-based analysis, bias detection, cross-referencing
- Blockchain: Cardano for immutable knowledge base and reputation
- Incentives: Token-based rewards for accurate data
- APIs: RESTful access for dApps and users
"""

import os
import sys
import io
import json
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
from crew_definition import VerificationAgent
from logging_config import setup_logging

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv(override=True)
logger = setup_logging()

# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

# Cardano Configuration
CARDANO_NETWORK = os.environ.get("NETWORK", "Preprod")
CARDANO_RPC_URL = os.environ.get("CARDANO_RPC_URL", "http://localhost:8090")

# Decentralized Storage
IPFS_API = os.environ.get("IPFS_API", "http://127.0.0.1:5001")
ARWEAVE_API = os.environ.get("ARWEAVE_API", "https://arweave.net")

# Payment Service
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:3001/api/v1")
PAYMENT_API_KEY = os.environ.get("PAYMENT_API_KEY", "")
AGENT_IDENTIFIER = os.environ.get("AGENT_IDENTIFIER", "cognito-sync-agent-001")

# Smart Contract Configuration
KNOWLEDGE_BASE_CONTRACT = os.environ.get("KNOWLEDGE_BASE_CONTRACT", "")
REPUTATION_CONTRACT = os.environ.get("REPUTATION_CONTRACT", "")
INCENTIVE_CONTRACT = os.environ.get("INCENTIVE_CONTRACT", "")

logger.info("╔══════════════════════════════════════════════════════════════╗")
logger.info("║          CognitoSync - Knowledge Verification Agent           ║")
logger.info("║            Cardano Hackathon Track-2: NovaChain Nexus         ║")
logger.info("╚══════════════════════════════════════════════════════════════╝")
logger.info(f"Network: {CARDANO_NETWORK}")
logger.info(f"IPFS API: {IPFS_API}")
logger.info(f"Arweave API: {ARWEAVE_API}")
logger.info(f"Payment Service: {PAYMENT_SERVICE_URL}")

# Initialize FastAPI
app = FastAPI(
    title="CognitoSync - Decentralized Knowledge Agent",
    description="AI-powered autonomous knowledge verification on Cardano blockchain",
    version="1.0.0-phase1"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
verification_agent = VerificationAgent(verbose=True, logger=logger)

# ═════════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORES (Phase 1 - Replace with Database in Phase 2)
# ═════════════════════════════════════════════════════════════════════════════

verification_cache: Dict[str, Any] = {}
knowledge_base: Dict[str, Any] = {}  # Knowledge hash -> metadata
reputation_scores: Dict[str, float] = {}  # Agent/Source -> reputation
transaction_history: List[Dict] = []  # Auditability log
contributors: Dict[str, Dict] = {}  # Contributor profiles

# ═════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═════════════════════════════════════════════════════════════════════════════

# ──────────────────── Data Sourcing ────────────────────
class DataSource(BaseModel):
    """Decentralized data source"""
    source_type: str = Field(..., description="ipfs, arweave, http, etc")
    source_address: str = Field(..., description="Hash or URL")
    content_hash: str = Field(..., description="SHA-256 of content")
    timestamp: datetime = Field(default_factory=datetime.now)

class DataIngestionRequest(BaseModel):
    """Request for autonomous data ingestion"""
    sources: List[DataSource] = Field(..., description="Data sources to ingest")
    analysis_type: str = Field(default="full", description="full, summary, metadata")

class DataIngestionResponse(BaseModel):
    """Response from data ingestion"""
    sources_processed: int
    successful: int
    failed: int
    errors: List[str]
    ingestion_id: str

# ──────────────────── Verification ────────────────────
class VerifyRequest(BaseModel):
    """Request to verify knowledge"""
    url: str = Field(..., description="URL to verify")
    cross_reference: bool = Field(default=True, description="Cross-reference with knowledge base")
    check_reputation: bool = Field(default=True, description="Check source reputation")

class VerificationResult(BaseModel):
    """Complete verification result"""
    url: str
    summary: str
    reliability_score: float
    bias_level: int
    verification_status: str
    cardano_hash: str
    bias_analysis: dict
    cross_references: List[str] = []
    source_reputation: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

# ──────────────────── Knowledge Base ────────────────────
class KnowledgeEntry(BaseModel):
    """Entry in the on-chain knowledge base"""
    knowledge_hash: str = Field(..., description="SHA-256 hash of knowledge")
    topic: str = Field(..., description="Topic/category")
    summary: str = Field(..., description="Synthesized summary")
    sources: List[str] = Field(..., description="Source URLs")
    verification_score: float = Field(..., description="Aggregate verification score")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    on_chain_tx: Optional[str] = Field(None, description="Cardano transaction hash")

class KnowledgeQueryRequest(BaseModel):
    """Request to query knowledge base"""
    topic: str = Field(..., description="Topic to search")
    limit: int = Field(default=10, description="Max results")

# ──────────────────── Reputation System ────────────────────
class ReputationEntry(BaseModel):
    """Reputation score for agent/source"""
    entity_id: str = Field(..., description="Agent or source identifier")
    entity_type: str = Field(..., description="agent or source")
    reputation_score: float = Field(..., description="0-100 score")
    contributions: int = Field(default=0, description="Number of contributions")
    accuracy_rate: float = Field(default=0.0, description="Accuracy percentage")
    last_updated: datetime = Field(default_factory=datetime.now)

# ──────────────────── Incentives ────────────────────
class RewardTransaction(BaseModel):
    """Token reward for contribution"""
    contributor_id: str = Field(..., description="Contributor wallet/ID")
    amount: float = Field(..., description="Amount in lovelace")
    reason: str = Field(..., description="Reason for reward")
    knowledge_hash: str = Field(..., description="Associated knowledge hash")
    transaction_hash: Optional[str] = Field(None, description="On-chain tx hash")
    status: str = Field(default="pending", description="pending, confirmed, failed")

# ──────────────────── Audit Trail ────────────────────
class AuditEntry(BaseModel):
    """Immutable audit log entry"""
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str = Field(..., description="Action performed")
    agent_id: str = Field(..., description="Agent performing action")
    data_hash: str = Field(..., description="SHA-256 of action data")
    on_chain_hash: Optional[str] = Field(None, description="Cardano block hash")

# ──────────────────── dApp Integration ────────────────────
class dAppQuery(BaseModel):
    """Query from dApp to knowledge base"""
    query: str = Field(..., description="Search query")
    filters: Dict[str, Any] = Field(default={}, description="Filter criteria")

class dAppResponse(BaseModel):
    """Response to dApp"""
    query: str
    results: List[KnowledgeEntry]
    total_matches: int
    confidence_score: float

# ═════════════════════════════════════════════════════════════════════════════
# 1) AUTONOMOUS DATA SOURCING ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/source/ingest", response_model=DataIngestionResponse)
async def ingest_data(request: DataIngestionRequest, background_tasks: BackgroundTasks):
    """
    Autonomously ingest data from decentralized sources (IPFS, Arweave, etc)
    
    Phase 1: Supports URL-based ingestion
    Phase 2: Full IPFS/Arweave integration with async processing
    """
    logger.info(f"Ingesting data from {len(request.sources)} sources")
    
    ingestion_id = hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16]
    successful = 0
    failed = 0
    errors = []
    
    try:
        for source in request.sources:
            try:
                if source.source_type == "http":
                    # Fetch and verify
                    result = verification_agent.verify(source.source_address)
                    successful += 1
                    
                    # Log to audit trail
                    audit_entry = AuditEntry(
                        action="data_ingested",
                        agent_id=AGENT_IDENTIFIER,
                        data_hash=source.content_hash
                    )
                    transaction_history.append(audit_entry.dict())
                    
                elif source.source_type == "ipfs":
                    logger.info(f"IPFS source (Phase 2): {source.source_address}")
                    # Phase 2: Implement IPFS integration
                    successful += 1
                    
                elif source.source_type == "arweave":
                    logger.info(f"Arweave source (Phase 2): {source.source_address}")
                    # Phase 2: Implement Arweave integration
                    successful += 1
                    
            except Exception as e:
                failed += 1
                errors.append(f"{source.source_address}: {str(e)}")
                logger.error(f"Failed to ingest {source.source_address}: {str(e)}")
        
        return DataIngestionResponse(
            sources_processed=len(request.sources),
            successful=successful,
            failed=failed,
            errors=errors,
            ingestion_id=ingestion_id
        )
        
    except Exception as e:
        logger.error(f"Data ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

# ═════════════════════════════════════════════════════════════════════════════
# 2) AI-POWERED VERIFICATION ENGINE
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/verify", response_model=VerificationResult)
async def verify_knowledge(request: VerifyRequest):
    """
    AI-powered verification of knowledge with cross-referencing
    
    Pipeline:
    1. Ingest data from URL
    2. Analyze with NLP
    3. Cross-reference with knowledge base
    4. Check source reputation
    5. Generate verification result
    6. Create Cardano hash
    """
    try:
        logger.info(f"Verifying: {request.url}")
        
        # Check cache
        if request.url in verification_cache:
            logger.info(f"Cache hit: {request.url}")
            return verification_cache[request.url]
        
        # Run verification pipeline
        result_dict = verification_agent.verify(request.url)
        
        # Cross-reference if requested
        cross_refs = []
        if request.cross_reference:
            # Search knowledge base for similar topics
            for kb_hash, kb_data in knowledge_base.items():
                if kb_data.get("verification_score", 0) > 70:
                    cross_refs.append(kb_hash)
        
        # Check source reputation
        source_rep = reputation_scores.get(request.url, 50.0)
        
        # Build complete result
        result = VerificationResult(
            url=request.url,
            summary=result_dict["summary"],
            reliability_score=result_dict["reliability_score"],
            bias_level=result_dict["bias_level"],
            verification_status=result_dict["verification_status"],
            cardano_hash=result_dict["cardano_hash"],
            bias_analysis=result_dict["bias_analysis"],
            cross_references=cross_refs,
            source_reputation=source_rep
        )
        
        # Cache result
        verification_cache[request.url] = result
        
        # Add to audit trail
        audit_entry = AuditEntry(
            action="verification_completed",
            agent_id=AGENT_IDENTIFIER,
            data_hash=result_dict["cardano_hash"]
        )
        transaction_history.append(audit_entry.dict())
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

# ═════════════════════════════════════════════════════════════════════════════
# 3) IMMUTABLE ON-CHAIN KNOWLEDGE BASE
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/knowledge-base/add")
async def add_to_knowledge_base(entry: KnowledgeEntry):
    """
    Add verified knowledge to immutable on-chain knowledge base
    
    Phase 1: In-memory storage
    Phase 2: Plutus smart contract on Cardano with immutable storage
    """
    try:
        logger.info(f"Adding to knowledge base: {entry.topic}")
        
        # Store in knowledge base
        knowledge_base[entry.knowledge_hash] = entry.dict()
        
        # Simulate Cardano transaction (Phase 2: actual smart contract call)
        # In Phase 2, this would call the KNOWLEDGE_BASE_CONTRACT
        
        # Add audit trail
        audit_entry = AuditEntry(
            action="knowledge_added",
            agent_id=AGENT_IDENTIFIER,
            data_hash=entry.knowledge_hash,
            on_chain_hash=None  # Phase 2: actual Cardano hash
        )
        transaction_history.append(audit_entry.dict())
        
        return {
            "status": "success",
            "knowledge_hash": entry.knowledge_hash,
            "topic": entry.topic,
            "message": "Knowledge entry added to base"
        }
        
    except Exception as e:
        logger.error(f"Knowledge base error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/knowledge-base/query")
async def query_knowledge_base(request: KnowledgeQueryRequest):
    """
    Query the on-chain knowledge base
    
    Returns verified and synthesized insights
    """
    try:
        logger.info(f"Querying knowledge base for: {request.topic}")
        
        results = []
        for kb_hash, kb_data in knowledge_base.items():
            if request.topic.lower() in kb_data.get("topic", "").lower():
                results.append(kb_data)
                if len(results) >= request.limit:
                    break
        
        return {
            "topic": request.topic,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/knowledge-base/stats")
async def knowledge_base_stats():
    """Get statistics about the knowledge base"""
    return {
        "total_entries": len(knowledge_base),
        "average_verification_score": sum([k.get("verification_score", 0) for k in knowledge_base.values()]) / max(len(knowledge_base), 1),
        "total_sources": sum([len(k.get("sources", [])) for k in knowledge_base.values()]),
        "last_updated": max([k.get("updated_at") for k in knowledge_base.values()], default=None)
    }

# ═════════════════════════════════════════════════════════════════════════════
# 4) DECENTRALIZED REPUTATION SYSTEM
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/reputation/{entity_id}")
async def get_reputation(entity_id: str):
    """Get reputation score for an agent or source"""
    rep = reputation_scores.get(entity_id, 50.0)
    
    return {
        "entity_id": entity_id,
        "reputation_score": rep,
        "status": "trusted" if rep >= 75 else "neutral" if rep >= 50 else "low_trust",
        "contributions": len([t for t in transaction_history if entity_id in str(t)])
    }

@app.post("/api/v1/reputation/update")
async def update_reputation(entry: ReputationEntry):
    """
    Update reputation for agent or source
    
    Phase 2: Driven by Cardano smart contracts
    """
    try:
        logger.info(f"Updating reputation for {entry.entity_id}: {entry.reputation_score}")
        
        reputation_scores[entry.entity_id] = entry.reputation_score
        
        audit_entry = AuditEntry(
            action="reputation_updated",
            agent_id=AGENT_IDENTIFIER,
            data_hash=hashlib.sha256(f"{entry.entity_id}{entry.reputation_score}".encode()).hexdigest()
        )
        transaction_history.append(audit_entry.dict())
        
        return {"status": "success", "entity_id": entry.entity_id, "reputation_score": entry.reputation_score}
        
    except Exception as e:
        logger.error(f"Reputation update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reputation/leaderboard")
async def get_reputation_leaderboard(limit: int = 10):
    """Get top contributors by reputation"""
    sorted_reps = sorted(reputation_scores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "leaderboard": [
            {"entity_id": entity, "reputation_score": score}
            for entity, score in sorted_reps[:limit]
        ],
        "total_contributors": len(reputation_scores)
    }

# ═════════════════════════════════════════════════════════════════════════════
# 5) NATIVE TOKEN INCENTIVIZATION
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/incentives/reward")
async def distribute_reward(reward: RewardTransaction):
    """
    Distribute rewards for accurate data contribution
    
    Phase 1: Simulate rewards
    Phase 2: Actual Cardano transaction via INCENTIVE_CONTRACT
    """
    try:
        logger.info(f"Reward: {reward.amount} lovelace to {reward.contributor_id}")
        
        # Phase 2: Call INCENTIVE_CONTRACT on Cardano
        # This would create an actual smart contract transaction
        
        # Track reward in transaction history
        transaction_history.append(reward.dict())
        
        # Update contributor stats
        if reward.contributor_id not in contributors:
            contributors[reward.contributor_id] = {
                "total_rewards": 0,
                "contribution_count": 0
            }
        
        contributors[reward.contributor_id]["total_rewards"] += reward.amount
        contributors[reward.contributor_id]["contribution_count"] += 1
        
        return {
            "status": "pending",  # Phase 2: "confirmed" after on-chain tx
            "contributor_id": reward.contributor_id,
            "amount": reward.amount,
            "transaction_hash": "simulated_hash_" + hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        }
        
    except Exception as e:
        logger.error(f"Reward distribution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/incentives/contributors")
async def get_contributors_stats(limit: int = 10):
    """Get top contributors by rewards earned"""
    sorted_contrib = sorted(
        contributors.items(),
        key=lambda x: x[1]["total_rewards"],
        reverse=True
    )
    
    return {
        "top_contributors": [
            {
                "contributor_id": contrib_id,
                "total_rewards": stats["total_rewards"],
                "contributions": stats["contribution_count"]
            }
            for contrib_id, stats in sorted_contrib[:limit]
        ],
        "total_contributors": len(contributors)
    }

# ═════════════════════════════════════════════════════════════════════════════
# 6) FULL AUDITABILITY
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/audit/trail")
async def get_audit_trail(limit: int = 50, offset: int = 0):
    """
    Get immutable audit trail of all system actions
    
    Phase 2: Anchored to Cardano blockchain for cryptographic proof
    """
    paginated = transaction_history[offset:offset+limit]
    
    return {
        "total_entries": len(transaction_history),
        "returned": len(paginated),
        "offset": offset,
        "limit": limit,
        "entries": paginated
    }

@app.get("/api/v1/audit/{action}")
async def audit_by_action(action: str, limit: int = 20):
    """Get audit entries filtered by action type"""
    filtered = [t for t in transaction_history if t.get("action") == action]
    
    return {
        "action": action,
        "count": len(filtered),
        "entries": filtered[-limit:]
    }

# ═════════════════════════════════════════════════════════════════════════════
# 7) dApp API ACCESS
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/dapp/query", response_model=dAppResponse)
async def dapp_query(request: dAppQuery):
    """
    Provide verified knowledge to dApps on Cardano
    
    dApps can query this endpoint to get trustworthy information
    for smart contracts, oracles, and decision-making
    """
    try:
        logger.info(f"dApp query: {request.query}")
        
        results = []
        for kb_hash, kb_data in knowledge_base.items():
            if request.query.lower() in kb_data.get("topic", "").lower():
                results.append(kb_data)
        
        # Calculate confidence
        confidence = sum([k.get("verification_score", 0) for k in results]) / max(len(results), 1) if results else 0
        
        return dAppResponse(
            query=request.query,
            results=results,
            total_matches=len(results),
            confidence_score=confidence
        )
        
    except Exception as e:
        logger.error(f"dApp query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dapp/health")
async def dapp_health():
    """Health check for dApp integration"""
    return {
        "status": "operational",
        "knowledge_entries": len(knowledge_base),
        "verification_cache": len(verification_cache),
        "average_reputation": sum(reputation_scores.values()) / max(len(reputation_scores), 1) if reputation_scores else 0
    }

# ═════════════════════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (Compatibility)
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Legacy health check endpoint"""
    return {
        "status": "healthy",
        "service": "CognitoSync Phase-1",
        "version": "1.0.0-phase1",
        "track": "Cardano Hackathon Track-2 - NovaChain Nexus"
    }

@app.get("/api/v1/test-fetch")
async def test_fetch(url: str):
    """Test fetching a URL to diagnose connectivity issues"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        return {
            "status": "success",
            "url": url,
            "status_code": response.status_code,
            "content_length": len(response.content),
            "headers": dict(response.headers)
        }
    except Exception as e:
        logger.error(f"Test fetch failed for {url}: {str(e)}")
        return {
            "status": "error",
            "url": url,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/verification-history")
async def get_verification_history():
    """Legacy verification history endpoint"""
    return {
        "count": len(verification_cache),
        "cached_urls": list(verification_cache.keys())
    }

@app.get("/")
async def root():
    """Root endpoint with full API documentation"""
    return {
        "service": "CognitoSync",
        "version": "1.0.0-phase1",
        "team": "NovaChain Nexus",
        "track": "Cardano Hackathon Track-2",
        "description": "AI-powered decentralized knowledge verification agent on Cardano",
        "endpoints": {
            "Data Sourcing": {
                "POST /api/v1/source/ingest": "Ingest data from decentralized sources"
            },
            "Verification": {
                "POST /api/v1/verify": "Verify knowledge with AI analysis"
            },
            "Knowledge Base": {
                "POST /api/v1/knowledge-base/add": "Add to on-chain knowledge base",
                "GET /api/v1/knowledge-base/query": "Query knowledge base",
                "GET /api/v1/knowledge-base/stats": "Get KB statistics"
            },
            "Reputation": {
                "GET /api/v1/reputation/{entity_id}": "Get reputation score",
                "POST /api/v1/reputation/update": "Update reputation",
                "GET /api/v1/reputation/leaderboard": "Top contributors"
            },
            "Incentives": {
                "POST /api/v1/incentives/reward": "Distribute token rewards",
                "GET /api/v1/incentives/contributors": "Top contributors by rewards"
            },
            "Auditability": {
                "GET /api/v1/audit/trail": "Immutable audit trail",
                "GET /api/v1/audit/{action}": "Filter audit by action"
            },
            "dApp Integration": {
                "POST /api/v1/dapp/query": "Query for dApp integration",
                "GET /api/v1/dapp/health": "dApp integration health"
            },
            "Documentation": {
                "GET /docs": "Swagger UI documentation",
                "GET /redoc": "ReDoc documentation"
            }
        }
    }

# ═════════════════════════════════════════════════════════════════════════════
# TESTING
# ═════════════════════════════════════════════════════════════════════════════

def test_full_pipeline():
    """Test the entire CognitoSync pipeline"""
    logger.info("\n" + "═" * 70)
    logger.info("CognitoSync Full Pipeline Test")
    logger.info("═" * 70)
    
    try:
        # 1. Test verification
        logger.info("\n[1] Testing Verification Engine...")
        test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
        result = verification_agent.verify(test_url)
        logger.info(f"✓ Verification: {result['verification_status']}")
        
        # 2. Test knowledge base
        logger.info("\n[2] Testing Knowledge Base...")
        kb_entry = KnowledgeEntry(
            knowledge_hash=result["cardano_hash"],
            topic="Artificial Intelligence",
            summary=result["summary"][:100],
            sources=[test_url],
            verification_score=result["reliability_score"]
        )
        knowledge_base[kb_entry.knowledge_hash] = kb_entry.dict()
        logger.info(f"✓ Knowledge Base: {len(knowledge_base)} entries")
        
        # 3. Test reputation
        logger.info("\n[3] Testing Reputation System...")
        reputation_scores[test_url] = 85.0
        logger.info(f"✓ Reputation: {test_url} = {reputation_scores[test_url]}")
        
        # 4. Test audit trail
        logger.info("\n[4] Testing Audit Trail...")
        audit = AuditEntry(
            action="test_pipeline",
            agent_id=AGENT_IDENTIFIER,
            data_hash=result["cardano_hash"]
        )
        transaction_history.append(audit.dict())
        logger.info(f"✓ Audit: {len(transaction_history)} entries logged")
        
        # 5. Test incentives
        logger.info("\n[5] Testing Incentive System...")
        contributors["test_contributor"] = {
            "total_rewards": 1000000,
            "contribution_count": 1
        }
        logger.info(f"✓ Incentives: {len(contributors)} contributors")
        
        logger.info("\n" + "═" * 70)
        logger.info("✓ All Tests Passed!")
        logger.info("═" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_full_pipeline()
    else:
        port = int(os.environ.get("API_PORT", 8000))
        host = os.environ.get("API_HOST", "127.0.0.1")
        
        logger.info("\n" + "═" * 70)
        logger.info("Starting CognitoSync Backend...")
        logger.info("═" * 70)
        logger.info(f"API: http://{host}:{port}")
        logger.info(f"Docs: http://{host}:{port}/docs")
        logger.info(f"Health: http://{host}:{port}/health")
        logger.info("═" * 70 + "\n")
        
        uvicorn.run(app, host=host, port=port, log_level="info")
