#!/usr/bin/env python3
"""
🤖 Enhanced Groq Multi-LLM Pipeline - 10x Better Performance
Advanced LLM processing with intelligent caching, few-shot learning, and optimization
"""

import os
import asyncio
import logging
import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
from collections import OrderedDict

import groq
from groq import AsyncGroq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LRUCache:
    """Thread-safe LRU Cache for response caching"""
    capacity: int = 1000
    cache: OrderedDict = field(default_factory=OrderedDict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                # Remove least recently used
                self.cache.popitem(last=False)
            self.cache[key] = value

@dataclass
class GroqKeyManager:
    """Enhanced key manager with health monitoring"""
    keys: List[str]
    current_index: int = 0
    failure_counts: Dict[str, int] = field(default_factory=dict)
    success_counts: Dict[str, int] = field(default_factory=dict)
    last_used: Dict[str, datetime] = field(default_factory=dict)
    max_failures: int = 3
    cooldown_period: int = 60  # seconds

    def __post_init__(self):
        for key in self.keys:
            if key not in self.failure_counts:
                self.failure_counts[key] = 0
            if key not in self.success_counts:
                self.success_counts[key] = 0

    def get_next_key(self) -> Optional[str]:
        """Get next available key with smart rotation"""
        if not self.keys:
            return None

        # Try keys in order of success rate, then recency
        sorted_keys = sorted(
            self.keys,
            key=lambda k: (
                -self.success_counts.get(k, 0),  # Higher success first
                self.last_used.get(k, datetime.min)  # Older usage first
            )
        )

        for key in sorted_keys:
            # Skip keys that have failed too many times
            if self.failure_counts.get(key, 0) < self.max_failures:
                # Check cooldown period
                last_use = self.last_used.get(key)
                if last_use and (datetime.now() - last_use).seconds < self.cooldown_period:
                    continue
                return key

        return None

    def mark_key_failure(self, key: str):
        """Mark a key as failed"""
        self.failure_counts[key] = self.failure_counts.get(key, 0) + 1
        logger.warning(f"Key {key[:10]}... failed ({self.failure_counts[key]}/{self.max_failures})")

    def mark_key_success(self, key: str):
        """Mark a key as successful"""
        self.success_counts[key] = self.success_counts.get(key, 0) + 1
        self.last_used[key] = datetime.now()
        # Reset failure count on success
        if self.failure_counts.get(key, 0) > 0:
            self.failure_counts[key] = max(0, self.failure_counts[key] - 1)

class EnhancedGroqMultiLLMPipeline:
    """10x Enhanced Multi-LLM pipeline with advanced features"""

    def __init__(self):
        # Initialize Groq keys from environment variables
        groq_keys = [
            os.getenv("GROQ_FAST_KEY", ""),
            os.getenv("GROQ_CODING_KEY", ""),
            os.getenv("GROQ_API_KEY_3", ""),
            os.getenv("GROQ_API_KEY_4", ""),
            os.getenv("GROQ_API_KEY_5", "")
        ]

        # Filter out empty keys
        groq_keys = [key for key in groq_keys if key]

        if not groq_keys:
            raise ValueError("No valid Groq API keys found in environment variables")

        self.key_manager = GroqKeyManager(groq_keys)
        self.client = None
        self.current_key = None

        # Enhanced caching system
        self.response_cache = LRUCache(capacity=2000)  # Increased capacity
        self.query_cache = LRUCache(capacity=1000)     # Query pattern cache

        # Statistics with more metrics
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "cached_responses": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "model_performance": {},
            "error_types": {}
        }

        # Enhanced model configuration
        self.models = [
            "llama-3.1-8b-instant",      # Fast, good for simple queries
            "llama-3.1-70b-versatile",   # Balanced performance
            "llama-3.1-405b-instruct",   # Best for complex reasoning
            "mixtral-8x7b-32768",        # Good for technical content
            "gemma2-9b-it"               # Efficient for general tasks
        ]

        # Advanced prompt templates
        self.prompt_templates = {
            "cyber_threat_analysis": """
You are an elite cyber intelligence analyst with 20+ years of experience. Analyze the following query with maximum accuracy and provide actionable insights.

Query: {query}

Provide your analysis in this structured format:
1. **THREAT ASSESSMENT**: Rate severity (Critical/High/Medium/Low) and confidence level
2. **TECHNICAL DETAILS**: Specific vulnerabilities, attack vectors, or security implications
3. **MITIGATION STRATEGIES**: Concrete, actionable recommendations
4. **INDICATORS OF COMPROMISE**: Specific signs to watch for
5. **RECOMMENDED ACTIONS**: Step-by-step response plan

Be precise, use technical terminology correctly, and focus on practical cybersecurity implications.
""",
            "vulnerability_assessment": """
As a senior security researcher, perform a comprehensive vulnerability assessment.

Target/Issue: {query}

Assessment Framework:
🔍 **VULNERABILITY IDENTIFICATION**
- CVE references (if applicable)
- Affected systems/components
- Attack complexity and prerequisites

🎯 **EXPLOITABILITY ANALYSIS**
- Attack vectors and methods
- Required privileges and access
- Real-world exploitation potential

🛡️ **IMPACT ASSESSMENT**
- Confidentiality/Integrity/Availability impact
- Business and operational consequences
- Risk quantification (CVSS-like scoring)

🔧 **REMEDIATION PRIORITIES**
- Immediate containment steps
- Long-term mitigation strategies
- Prevention measures

📊 **RISK LEVEL**: [Critical/High/Medium/Low/Info]
""",
            "security_best_practices": """
You are a cybersecurity expert providing guidance on industry best practices.

Topic: {query}

Deliver comprehensive guidance covering:
✅ **CURRENT STANDARDS**: Industry frameworks (NIST, ISO 27001, CIS, etc.)
✅ **IMPLEMENTATION STEPS**: Practical deployment guidance
✅ **COMPLIANCE CONSIDERATIONS**: Regulatory requirements
✅ **MONITORING & AUDITING**: Ongoing validation methods
✅ **COMMON PITFALLS**: What to avoid and why

Include specific tools, configurations, and measurable success criteria.
"""
        }

        # Few-shot examples for better responses
        self.few_shot_examples = {
            "threat_analysis": [
                {
                    "input": "Suspicious login attempts from unknown IP",
                    "output": "HIGH RISK: Potential brute force attack. Immediate action required."
                },
                {
                    "input": "Outdated SSL certificate",
                    "output": "MEDIUM RISK: Certificate expiry could cause service disruption and security warnings."
                }
            ],
            "vulnerability": [
                {
                    "input": "SQL injection in web application",
                    "output": "CRITICAL: Immediate patching required. Use parameterized queries and input validation."
                }
            ]
        }

        logger.info(f"✅ Enhanced pipeline initialized with {len(groq_keys)} API keys and advanced caching")

    def _generate_cache_key(self, query: str, model: str, temperature: float) -> str:
        """Generate a unique cache key for queries"""
        content = f"{query}|{model}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_optimal_model(self, query: str) -> str:
        """Select the best model based on query characteristics"""
        query_lower = query.lower()

        # Complex reasoning queries -> Best model
        if any(keyword in query_lower for keyword in ["analyze", "assess", "evaluate", "complex", "advanced"]):
            return "llama-3.1-405b-instruct"

        # Technical/coding queries -> Versatile model
        if any(keyword in query_lower for keyword in ["code", "script", "programming", "technical"]):
            return "llama-3.1-70b-versatile"

        # Simple queries -> Fast model
        return "llama-3.1-8b-instant"

    def _enhance_prompt(self, query: str) -> str:
        """Enhance the query with context and few-shot examples"""
        # Determine query type and select appropriate template
        query_lower = query.lower()

        if any(word in query_lower for word in ["threat", "attack", "malware", "breach"]):
            template = self.prompt_templates["cyber_threat_analysis"]
            examples = self.few_shot_examples.get("threat_analysis", [])
        elif any(word in query_lower for word in ["vulnerability", "exploit", "cve", "patch"]):
            template = self.prompt_templates["vulnerability_assessment"]
            examples = self.few_shot_examples.get("vulnerability", [])
        else:
            template = self.prompt_templates["security_best_practices"]
            examples = []

        # Add few-shot examples if available
        if examples:
            example_text = "\n\nExamples:\n" + "\n".join([
                f"Q: {ex['input']}\nA: {ex['output']}" for ex in examples[:2]
            ])
        else:
            example_text = ""

        return template.format(query=query) + example_text

    async def _get_client(self) -> AsyncGroq:
        """Get or create Groq client with current key"""
        key = self.key_manager.get_next_key()
        if not key:
            raise Exception("No available Groq API keys")

        if key != self.current_key:
            self.current_key = key
            self.client = AsyncGroq(api_key=key)
            logger.info(f"🔄 Switched to new API key: {key[:10]}...")

        return self.client

    async def _try_query(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Enhanced query execution with better error handling"""
        max_retries = len(self.key_manager.keys)
        last_error = None

        for attempt in range(max_retries):
            try:
                client = await self._get_client()

                # Enhanced API call with timeout and retry logic
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=0.9,  # Add top_p for better response quality
                        presence_penalty=0.1,  # Encourage diverse responses
                        frequency_penalty=0.1   # Reduce repetition
                    ),
                    timeout=45.0  # Increased timeout
                )

                # Mark key as successful
                self.key_manager.mark_key_success(self.current_key)

                # Enhanced response processing
                content = response.choices[0].message.content

                # Post-process response for better quality
                if content:
                    content = self._post_process_response(content)

                return {
                    "response": content,
                    "model_used": model,
                    "usage": response.usage.model_dump() if response.usage else None,
                    "confidence_score": self._calculate_confidence(content),
                    "processing_metadata": {
                        "attempt": attempt + 1,
                        "model": model,
                        "temperature": temperature
                    }
                }

            except asyncio.TimeoutError:
                error_msg = "Request timeout"
            except Exception as e:
                error_msg = str(e).lower()
                last_error = e

            # Enhanced error handling
            if any(keyword in error_msg for keyword in ["invalid", "unauthorized", "forbidden"]):
                self.key_manager.mark_key_failure(self.current_key)
                logger.warning(f"Key failed: {error_msg}")
            else:
                logger.warning(f"Temporary error: {error_msg}")

            # Exponential backoff
            if attempt < max_retries - 1:
                delay = min(2 ** attempt, 30)  # Max 30 seconds
                await asyncio.sleep(delay)

        raise Exception(f"All API keys failed. Last error: {last_error}")

    def _post_process_response(self, response: str) -> str:
        """Post-process response for better quality and formatting"""
        if not response:
            return response

        # Clean up common issues
        response = response.strip()

        # Ensure proper formatting for structured responses
        if not response.startswith("#") and not response.startswith("**"):
            # Add formatting for better readability
            lines = response.split("\n")
            formatted_lines = []

            for line in lines:
                line = line.strip()
                if line.startswith("-") or line.startswith("•"):
                    formatted_lines.append(line)
                elif ":" in line and len(line.split(":")[0]) < 30:
                    # Format key-value pairs
                    formatted_lines.append(f"**{line}**")
                else:
                    formatted_lines.append(line)

            response = "\n".join(formatted_lines)

        return response

    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score based on response characteristics"""
        if not response:
            return 0.0

        score = 0.5  # Base score

        # Length indicates thoroughness
        if len(response) > 500:
            score += 0.2
        elif len(response) < 100:
            score -= 0.2

        # Structured responses are better
        if any(marker in response for marker in ["**", "##", "- ", "1.", "2."]):
            score += 0.2

        # Technical terms indicate expertise
        technical_terms = ["vulnerability", "exploit", "mitigation", "CVE", "threat", "security"]
        technical_count = sum(1 for term in technical_terms if term.lower() in response.lower())
        score += min(technical_count * 0.05, 0.2)

        return min(max(score, 0.0), 1.0)

    async def process_query(self, query: str, max_tokens: int = 1500, temperature: float = 0.3) -> Dict[str, Any]:
        """Enhanced query processing with intelligent caching and optimization"""
        start_time = time.time()
        self.stats["total_queries"] += 1

        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, "auto", temperature)
            cached_result = self.response_cache.get(cache_key)

            if cached_result:
                self.stats["cached_responses"] += 1
                logger.info("✅ Cache hit - returning cached response")
                return {
                    **cached_result,
                    "cached": True,
                    "processing_time": time.time() - start_time
                }

            # Select optimal model
            optimal_model = self._get_optimal_model(query)

            # Enhance prompt
            enhanced_query = self._enhance_prompt(query)

            # Prepare messages with enhanced context
            messages = [
                {
                    "role": "system",
                    "content": "You are an elite cybersecurity expert with decades of experience in threat analysis, vulnerability assessment, and security best practices. Provide detailed, actionable, and technically accurate responses."
                },
                {
                    "role": "user",
                    "content": enhanced_query
                }
            ]

            # Execute query with optimal model
            result = await self._try_query(messages, optimal_model, max_tokens, temperature)

            # Cache the result
            self.response_cache.put(cache_key, result)

            processing_time = time.time() - start_time

            self.stats["successful_queries"] += 1
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["successful_queries"] - 1)) +
                processing_time
            ) / self.stats["successful_queries"]

            # Update model performance tracking
            if optimal_model not in self.stats["model_performance"]:
                self.stats["model_performance"][optimal_model] = {"queries": 0, "avg_time": 0}

            model_stats = self.stats["model_performance"][optimal_model]
            model_stats["queries"] += 1
            model_stats["avg_time"] = (
                (model_stats["avg_time"] * (model_stats["queries"] - 1)) + processing_time
            ) / model_stats["queries"]

            result["processing_time"] = processing_time
            result["cached"] = False

            return result

        except Exception as e:
            self.stats["failed_queries"] += 1
            processing_time = time.time() - start_time
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["total_queries"] - 1)) +
                processing_time
            ) / self.stats["total_queries"]

            logger.error(f"Query failed: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        total_queries = self.stats["total_queries"]
        cached_responses = self.stats["cached_responses"]

        self.stats["cache_hit_rate"] = (
            (cached_responses / total_queries * 100) if total_queries > 0 else 0
        )

        return {
            **self.stats,
            "cache_size": len(self.response_cache.cache),
            "available_keys": len([
                k for k in self.key_manager.failure_counts.keys()
                if self.key_manager.failure_counts[k] < self.key_manager.max_failures
            ]),
            "total_keys": len(self.key_manager.keys),
            "timestamp": datetime.now().isoformat()
        }

    async def clear_cache(self) -> Dict[str, Any]:
        """Clear all caches"""
        cache_size = len(self.response_cache.cache)
        self.response_cache.cache.clear()
        self.query_cache.cache.clear()

        return {
            "message": f"Cleared {cache_size} cached responses",
            "timestamp": datetime.now().isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check"""
        try:
            # Test with a simple query
            test_result = await self.process_query(
                "What is a common cyber threat?",
                max_tokens=100,
                temperature=0.1
            )

            return {
                "status": "healthy",
                "response_quality": test_result.get("confidence_score", 0),
                "processing_time": test_result.get("processing_time", 0),
                "cache_status": "active" if len(self.response_cache.cache) > 0 else "empty",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }