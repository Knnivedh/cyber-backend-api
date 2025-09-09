#!/usr/bin/env python3
"""
🧠 Smart Cache Manager - Free Resource Optimization
Intelligent caching system to reduce API calls and improve performance
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import threading

class SmartCacheManager:
    """Intelligent cache manager for API responses and query patterns"""

    def __init__(self, max_size: int = 2000, ttl_hours: int = 24):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }

    def _generate_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key from query and context"""
        key_data = {
            "query": query.lower().strip(),
            "model": context.get("model", ""),
            "temperature": context.get("temperature", 0.7)
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - timestamp > self.ttl

    def get(self, query: str, context: Dict[str, Any]) -> Optional[Any]:
        """Get cached response if available"""
        key = self._generate_key(query, context)

        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                # Check if expired
                if self._is_expired(entry["timestamp"]):
                    del self.cache[key]
                    self.stats["evictions"] += 1
                    return None

                # Move to end (LRU)
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                return entry["data"]

        self.stats["misses"] += 1
        return None

    def put(self, query: str, context: Dict[str, Any], data: Any) -> None:
        """Store response in cache"""
        key = self._generate_key(query, context)

        with self.lock:
            # Remove if exists
            if key in self.cache:
                del self.cache[key]

            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
                self.stats["evictions"] += 1

            # Add new entry
            self.cache[key] = {
                "data": data,
                "timestamp": datetime.now(),
                "query": query,
                "context": context
            }
            self.stats["size"] = len(self.cache)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": f"{hit_rate:.1f}%",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "ttl_hours": self.ttl.total_seconds() / 3600
        }

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.stats = {k: 0 for k in self.stats.keys()}
            self.stats["size"] = 0
