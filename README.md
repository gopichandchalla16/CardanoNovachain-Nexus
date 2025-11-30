CognitoSync – AI-Powered Decentralized Knowledge Agent on Cardano (Track 2: AI Agents on Masumi)

Built at Cardano Hackathon Asia — IBW Edition 2025
Team: NovaChain Nexus

CognitoSync is an AI-powered decentralized knowledge verification agent designed to fight misinformation and fragmented data in the Web3 world.
Powered by Masumi’s Agent Framework, CrewAI, Cardano, and IPFS, CognitoSync autonomously ingests information, analyzes it, verifies credibility, detects bias, and produces structured, trustworthy knowledge objects suitable for on-chain storage and dApp integration.

This repository contains our Phase-1 working prototype built during the 30-hour hackathon.  

Project Vision

CognitoSync aims to become the “Truth Layer” for Cardano and decentralized systems.

The world today is flooded with:

misinformation

biased narratives

fragmented data stored across IPFS / Arweave

centralized information gatekeeping

CognitoSync solves this through a trustless, AI-native, decentralized verification pipeline.

What CognitoSync Does
✔️ 1. Autonomous Data Ingestion

Accepts text from dApps, users, APIs, IPFS/Arweave sources.

✔️ 2. AI-Powered Verification Pipeline

The agent generates:

Summary of the text

Extracted key claims

Reliability score (0–100)

Bias level (low | medium | high)

Human-readable bias explanation

✔️ 3. Structured Knowledge Object Output

Compatible with:

IPFS storage

Cardano metadata

Masumi-compliant agent interfaces

✔️ 4. Masumi Agent Compliance

Implements:

/availability

/input_schema

/start_job

/status

✔️ 5. Integration-Ready Stable API

dApps and other agents can query CognitoSync for:

verified summaries

trust scores

provenance metadata

🛠️ Tech Stack
AI + Agent Layer

CrewAI

FastAPI

Python 3.10+

Blockhain & Decentralization

Cardano (metadata, future reputation system)

Masumi Network (MIP-003 agent format)

IPFS (knowledge object storage)

Optional AI Models

Gemini
