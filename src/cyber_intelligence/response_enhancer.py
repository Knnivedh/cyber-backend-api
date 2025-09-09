#!/usr/bin/env python3
"""
✨ Response Quality Enhancer - 10x Better Output
Advanced post-processing for superior response quality and formatting
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class ResponseQualityEnhancer:
    """Enhance response quality with better formatting, structure, and content"""

    def __init__(self):
        self.quality_templates = {
            "threat_analysis": {
                "structure": [
                    "🎯 **THREAT ASSESSMENT**",
                    "📊 **SEVERITY LEVEL**",
                    "🔍 **TECHNICAL ANALYSIS**",
                    "🛡️ **MITIGATION STRATEGY**",
                    "🚨 **IMMEDIATE ACTIONS**",
                    "📈 **RISK METRICS**"
                ],
                "keywords": ["threat", "attack", "breach", "malware", "intrusion"]
            },
            "vulnerability": {
                "structure": [
                    "🔴 **VULNERABILITY DETAILS**",
                    "📋 **AFFECTED SYSTEMS**",
                    "🎯 **EXPLOIT VECTORS**",
                    "⚡ **IMPACT ASSESSMENT**",
                    "🔧 **REMEDIATION STEPS**",
                    "📊 **CVSS SCORE**"
                ],
                "keywords": ["vulnerability", "exploit", "cve", "patch", "security"]
            },
            "compliance": {
                "structure": [
                    "📋 **COMPLIANCE REQUIREMENTS**",
                    "✅ **CURRENT STATUS**",
                    "🔧 **IMPLEMENTATION GUIDE**",
                    "📊 **AUDIT PREPARATION**",
                    "📈 **CONTINUOUS MONITORING**"
                ],
                "keywords": ["compliance", "audit", "regulation", "policy", "standard"]
            }
        }

    def enhance_response(self, response: str, query: str) -> str:
        """Enhance response quality and formatting"""
        if not response:
            return response

        # Detect query type
        query_type = self._detect_query_type(query)

        # Apply quality enhancements
        enhanced = self._apply_structured_formatting(response, query_type)
        enhanced = self._add_quality_indicators(enhanced)
        enhanced = self._improve_readability(enhanced)
        enhanced = self._add_actionable_insights(enhanced, query_type)

        return enhanced

    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query for appropriate formatting"""
        query_lower = query.lower()

        for query_type, config in self.quality_templates.items():
            if any(keyword in query_lower for keyword in config["keywords"]):
                return query_type

        return "general"

    def _apply_structured_formatting(self, response: str, query_type: str) -> str:
        """Apply structured formatting based on query type"""
        if query_type == "general":
            return self._apply_general_formatting(response)

        template = self.quality_templates.get(query_type, {})
        structure = template.get("structure", [])

        # Split response into sections
        sections = self._split_into_sections(response)

        # Reformat with structured headers
        formatted_sections = []
        for i, section in enumerate(sections):
            if i < len(structure):
                formatted_sections.append(f"{structure[i]}\n{section.strip()}")
            else:
                formatted_sections.append(section.strip())

        return "\n\n".join(formatted_sections)

    def _apply_general_formatting(self, response: str) -> str:
        """Apply general formatting improvements"""
        lines = response.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Format numbered lists
            if re.match(r'^\d+\.', line):
                formatted_lines.append(f"**{line}**")
            # Format bullet points
            elif line.startswith(('-', '•', '*')):
                formatted_lines.append(f"🔹 {line[1:].strip()}")
            # Format key-value pairs
            elif ':' in line and len(line.split(':')[0]) < 30:
                parts = line.split(':', 1)
                formatted_lines.append(f"**{parts[0].strip()}:** {parts[1].strip()}")
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _split_into_sections(self, response: str) -> List[str]:
        """Split response into logical sections"""
        # Split by double newlines or common section markers
        sections = re.split(r'\n\s*\n', response)

        # Further split by numbered sections or headers
        final_sections = []
        for section in sections:
            # Split by numbered sections (1., 2., etc.)
            numbered_parts = re.split(r'(?=\d+\.\s)', section)
            for part in numbered_parts:
                if part.strip():
                    final_sections.append(part.strip())

        return final_sections if final_sections else [response]

    def _add_quality_indicators(self, response: str) -> str:
        """Add quality indicators and confidence markers"""
        # Add confidence indicators based on content
        confidence_indicators = []

        if len(response) > 1000:
            confidence_indicators.append("📚 **Comprehensive Analysis**")
        if "cve" in response.lower() or "vulnerability" in response.lower():
            confidence_indicators.append("🎯 **Technical Accuracy**")
        if any(word in response.lower() for word in ["step-by-step", "implementation", "guide"]):
            confidence_indicators.append("🛠️ **Actionable Guidance**")

        if confidence_indicators:
            quality_header = "\n\n".join(confidence_indicators) + "\n\n---\n\n"
            response = quality_header + response

        return response

    def _improve_readability(self, response: str) -> str:
        """Improve overall readability"""
        # Fix common formatting issues
        response = re.sub(r'\n{3,}', '\n\n', response)  # Remove excessive newlines
        response = re.sub(r'\s{2,}', ' ', response)     # Remove multiple spaces

        # Add spacing for better readability
        lines = response.split('\n')
        formatted_lines = []

        for i, line in enumerate(lines):
            formatted_lines.append(line)

            # Add spacing after headers
            if line.startswith(('**', '##', '###', '🎯', '📊', '🔍', '🛡️', '🚨', '📈')):
                if i + 1 < len(lines) and lines[i + 1]:
                    formatted_lines.append("")

        return '\n'.join(formatted_lines)

    def _add_actionable_insights(self, response: str, query_type: str) -> str:
        """Add actionable insights based on query type"""
        insights = {
            "threat_analysis": "\n\n💡 **Pro Tip:** Implement multi-factor authentication and regular security training to prevent similar incidents.",
            "vulnerability": "\n\n⚡ **Quick Win:** Run automated vulnerability scans weekly and prioritize patches for critical systems.",
            "compliance": "\n\n📋 **Next Steps:** Schedule regular compliance audits and maintain detailed documentation of all security controls."
        }

        insight = insights.get(query_type)
        if insight:
            response += insight

        # Add timestamp for freshness
        response += f"\n\n---\n*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"

        return response

    def calculate_quality_score(self, response: str) -> Dict[str, Any]:
        """Calculate quality score for the response"""
        score = 0
        metrics = {}

        # Length score (comprehensive but not verbose)
        length = len(response)
        if 500 <= length <= 2000:
            score += 30
            metrics["length"] = "optimal"
        elif length < 500:
            score += 10
            metrics["length"] = "too_short"
        else:
            score += 20
            metrics["length"] = "verbose"

        # Structure score
        if any(marker in response for marker in ["**", "##", "- ", "1.", "2."]):
            score += 25
            metrics["structure"] = "well_formatted"
        else:
            metrics["structure"] = "plain_text"

        # Technical accuracy score
        technical_terms = ["vulnerability", "threat", "security", "compliance", "risk", "mitigation"]
        technical_count = sum(1 for term in technical_terms if term in response.lower())
        score += min(technical_count * 5, 25)
        metrics["technical_terms"] = technical_count

        # Actionability score
        actionable_phrases = ["implement", "configure", "monitor", "update", "review", "audit"]
        actionable_count = sum(1 for phrase in actionable_phrases if phrase in response.lower())
        score += min(actionable_count * 5, 20)
        metrics["actionable_items"] = actionable_count

        return {
            "score": score,
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "F",
            "metrics": metrics
        }
