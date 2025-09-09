#!/usr/bin/env python3
"""
Bolt AI Backend - Cyber Intelligence API
FastAPI backend for cyber intelligence queries using Supabase data
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cyber Intelligence API",
    description="AI-powered cyber intelligence backend for Bolt AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://odczfcygmifymbfqpmra.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9kY3pmY3lnbWlmeW1iZnFwbXJhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzA2OTE4NSwiZXhwIjoyMDcyNjQ1MTg1fQ.cY7wGRfVTxRyFPpf3Of27Q_xHFXqjQAzce2-b5pwlMs")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cyber Intelligence API for Bolt AI",
        "status": "active",
        "endpoints": [
            "/search - Search cyber intelligence",
            "/vulnerabilities - Get vulnerability data",
            "/threats - Get threat indicators",
            "/expert-knowledge - Get expert articles"
        ]
    }

@app.get("/search")
async def search_cyber_intelligence(
    query: str = Query(..., description="Search query for cyber intelligence"),
    limit: int = Query(10, description="Number of results to return")
):
    """Search across all cyber intelligence data"""
    try:
        results = []

        # Search expert knowledge
        expert_results = supabase.table('expert_knowledge').select('*').or_(
            f'title.ilike.%{query}%,content.ilike.%{query}%,keywords.ilike.%{query}%'
        ).limit(limit).execute()

        for record in expert_results.data:
            results.append({
                "type": "expert_knowledge",
                "title": record.get('title', ''),
                "content": record.get('content', '')[:500] + "..." if len(record.get('content', '')) > 500 else record.get('content', ''),
                "category": record.get('category', ''),
                "quality_score": record.get('quality_score', 0),
                "source": "web_scraped"
            })

        # Search vulnerabilities
        vuln_results = supabase.table('vulnerabilities').select('*').or_(
            f'cve_id.ilike.%{query}%,description.ilike.%{query}%'
        ).limit(limit//2).execute()

        for record in vuln_results.data:
            results.append({
                "type": "vulnerability",
                "cve_id": record.get('cve_id', ''),
                "description": record.get('description', ''),
                "severity": record.get('severity', ''),
                "cvss_score": record.get('cvss_score', 0),
                "source": record.get('source', '')
            })

        # Search threat indicators
        threat_results = supabase.table('threat_indicators').select('*').ilike('indicator', f'%{query}%').limit(limit//2).execute()

        for record in threat_results.data:
            results.append({
                "type": "threat_indicator",
                "indicator": record.get('indicator', ''),
                "indicator_type": record.get('type', ''),
                "confidence": record.get('confidence', 0),
                "source": record.get('source', '')
            })

        return {
            "query": query,
            "total_results": len(results),
            "results": results[:limit]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/vulnerabilities")
async def get_vulnerabilities(
    severity: Optional[str] = None,
    limit: int = Query(20, description="Number of vulnerabilities to return")
):
    """Get vulnerability data"""
    try:
        query = supabase.table('vulnerabilities').select('*')

        if severity:
            query = query.eq('severity', severity)

        results = query.limit(limit).execute()

        return {
            "count": len(results.data),
            "vulnerabilities": results.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch vulnerabilities: {str(e)}")

@app.get("/threats")
async def get_threat_indicators(
    indicator_type: Optional[str] = None,
    limit: int = Query(20, description="Number of threat indicators to return")
):
    """Get threat indicators"""
    try:
        query = supabase.table('threat_indicators').select('*')

        if indicator_type:
            query = query.eq('type', indicator_type)

        results = query.limit(limit).execute()

        return {
            "count": len(results.data),
            "threat_indicators": results.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threat indicators: {str(e)}")

@app.get("/expert-knowledge")
async def get_expert_knowledge(
    category: Optional[str] = None,
    limit: int = Query(10, description="Number of articles to return")
):
    """Get expert knowledge articles"""
    try:
        query = supabase.table('expert_knowledge').select('*')

        if category:
            query = query.eq('category', category)

        results = query.limit(limit).execute()

        return {
            "count": len(results.data),
            "articles": results.data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch expert knowledge: {str(e)}")

@app.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = {}

        # Get counts for each table
        tables = ['expert_knowledge', 'vulnerabilities', 'threat_indicators', 'malware_signatures', 'network_security_data', 'cyber_intelligence_reports']

        for table in tables:
            try:
                result = supabase.table(table).select('*', count='exact').execute()
                stats[table] = result.count
            except:
                stats[table] = 0

        return {
            "database_stats": stats,
            "total_records": sum(stats.values())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
