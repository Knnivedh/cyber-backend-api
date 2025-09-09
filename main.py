#!/usr/bin/env python3
"""
Main entry point for the Enhanced Cyber Intelligence API
Used for Bolt.new deployment and local development
"""

import uvicorn
from src.cyber_intelligence.groq_cyber_api import app

if __name__ == "__main__":
    uvicorn.run(
        "src.cyber_intelligence.groq_cyber_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
