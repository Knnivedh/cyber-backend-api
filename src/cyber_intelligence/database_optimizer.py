#!/usr/bin/env python3
"""
🗄️ Database Optimization Engine - Free Performance Boost
Intelligent database queries and caching for maximum efficiency
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json

from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseOptimizationEngine:
    """Optimized database engine with intelligent caching and query optimization"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Query result cache
        self.query_cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(hours=1)

        # Query patterns for optimization
        self.query_patterns = {
            "threat_search": "threat_type,severity,description",
            "vulnerability_lookup": "cve_id,severity,affected_systems",
            "security_events": "event_type,timestamp,severity",
            "compliance_check": "standard,requirement,status"
        }

        # Statistics
        self.stats = {
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0
        }

    async def optimized_query(self, table: str, query_params: Dict[str, Any]) -> List[Dict]:
        """Execute optimized database query with caching"""
        import time
        start_time = time.time()

        # Generate cache key
        cache_key = self._generate_cache_key(table, query_params)

        # Check cache first
        if cache_key in self.query_cache:
            cached_result = self.query_cache[cache_key]
            if datetime.now() - cached_result["timestamp"] < self.cache_ttl:
                self.stats["cache_hits"] += 1
                logger.info(f"✅ Database cache hit for {table}")
                return cached_result["data"]

        self.stats["cache_misses"] += 1

        try:
            # Optimize query based on table and parameters
            optimized_query = self._optimize_query(table, query_params)

            # Execute query
            result = await self._execute_query(optimized_query)

            # Cache result
            self.query_cache[cache_key] = {
                "data": result,
                "timestamp": datetime.now()
            }

            # Update statistics
            execution_time = time.time() - start_time
            self.stats["queries_executed"] += 1
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["queries_executed"] - 1)) +
                execution_time
            ) / self.stats["queries_executed"]

            return result

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    def _generate_cache_key(self, table: str, params: Dict[str, Any]) -> str:
        """Generate unique cache key for query"""
        key_data = {
            "table": table,
            "params": sorted(params.items())
        }
        return hash(json.dumps(key_data, sort_keys=True))

    def _optimize_query(self, table: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize query based on table structure and parameters"""
        optimized = {
            "table": table,
            "select": self.query_patterns.get(table, "*"),
            "filters": {},
            "order_by": None,
            "limit": params.get("limit", 100)
        }

        # Apply intelligent filtering
        if "search" in params:
            search_term = params["search"].lower()
            if table == "threat_search":
                optimized["filters"]["description"] = f"ilike.*{search_term}*"
            elif table == "vulnerability_lookup":
                optimized["filters"]["cve_id"] = f"ilike.*{search_term}*"

        # Add severity filtering for better results
        if "severity" in params:
            severity = params["severity"]
            if severity in ["critical", "high"]:
                optimized["filters"]["severity"] = f"eq.{severity}"

        # Optimize ordering for relevance
        if table in ["threat_search", "vulnerability_lookup"]:
            optimized["order_by"] = "severity.desc,timestamp.desc"

        return optimized

    async def _execute_query(self, query_config: Dict[str, Any]) -> List[Dict]:
        """Execute the optimized query against Supabase"""
        try:
            # Build Supabase query
            query = self.supabase.table(query_config["table"]).select(query_config["select"])

            # Apply filters
            for field, condition in query_config["filters"].items():
                if "ilike" in condition:
                    query = query.ilike(field, condition.split("ilike.")[1])
                elif "eq" in condition:
                    query = query.eq(field, condition.split("eq.")[1])

            # Apply ordering
            if query_config["order_by"]:
                order_field, order_dir = query_config["order_by"].split(".")
                query = query.order(order_field, desc=(order_dir == "desc"))

            # Apply limit
            if query_config["limit"]:
                query = query.limit(query_config["limit"])

            # Execute query
            result = query.execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Supabase query execution failed: {e}")
            return []

    async def semantic_search(self, query: str, table: str = "cyber_intelligence") -> List[Dict]:
        """Perform semantic search with intelligent ranking"""
        # Extract keywords from query
        keywords = self._extract_keywords(query)

        # Search across multiple fields with weights
        results = []

        for keyword in keywords:
            # Search in description field (highest weight)
            desc_results = await self.optimized_query(table, {
                "search": keyword,
                "field": "description",
                "limit": 20
            })

            # Search in title/summary field (medium weight)
            title_results = await self.optimized_query(table, {
                "search": keyword,
                "field": "title",
                "limit": 20
            })

            # Combine and score results
            all_results = desc_results + title_results
            scored_results = self._score_results(all_results, keyword, query)

            results.extend(scored_results)

        # Remove duplicates and sort by score
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x.get("relevance_score", 0), reverse=True)[:50]

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query"""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}

        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Add bigrams for better matching
        bigrams = []
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i+1] not in stop_words:
                bigrams.append(f"{words[i]} {words[i+1]}")

        return keywords + bigrams

    def _score_results(self, results: List[Dict], keyword: str, original_query: str) -> List[Dict]:
        """Score search results based on relevance"""
        scored_results = []

        for result in results:
            score = 0

            # Title matches (highest weight)
            title = result.get("title", "").lower()
            if keyword in title:
                score += 10
                if title.startswith(keyword):
                    score += 5

            # Description matches (medium weight)
            description = result.get("description", "").lower()
            if keyword in description:
                score += 5
                keyword_count = description.count(keyword)
                score += min(keyword_count, 5)  # Bonus for multiple occurrences

            # Severity boost for critical/high severity items
            severity = result.get("severity", "").lower()
            if severity in ["critical", "high"]:
                score += 3

            # Recency boost (newer items get slight preference)
            if "timestamp" in result:
                try:
                    item_date = datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
                    days_old = (datetime.now() - item_date).days
                    if days_old < 30:
                        score += 2
                    elif days_old < 90:
                        score += 1
                except:
                    pass

            result["relevance_score"] = score
            scored_results.append(result)

        return scored_results

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on ID or content"""
        seen = set()
        unique_results = []

        for result in results:
            # Use ID if available, otherwise use title+description hash
            if "id" in result:
                identifier = result["id"]
            else:
                content = f"{result.get('title', '')}{result.get('description', '')}"
                identifier = hash(content)

            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)

        return unique_results

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        return {
            "queries_executed": self.stats["queries_executed"],
            "cache_hit_rate": f"{(self.stats['cache_hits'] / max(self.stats['queries_executed'], 1) * 100):.1f}%",
            "average_response_time": f"{self.stats['avg_response_time']:.3f}s",
            "cache_size": len(self.query_cache),
            "timestamp": datetime.now().isoformat()
        }

    async def clear_cache(self) -> Dict[str, Any]:
        """Clear query cache"""
        cache_size = len(self.query_cache)
        self.query_cache.clear()

        return {
            "message": f"Cleared {cache_size} cached queries",
            "timestamp": datetime.now().isoformat()
        }
