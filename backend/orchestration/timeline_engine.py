import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ValidationError

from llm.grok_client import GroqClient
from prompts import TIMELINE_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

# Data Structures
class NormalizedDate(BaseModel):
    raw: str
    normalized: str  # YYYY-MM-DD
    type: Literal["explicit", "relative", "period"]
    certainty: Literal["low", "medium", "high"]

class TimelineEvent(BaseModel):
    event_id: str
    description: str
    date: NormalizedDate
    is_deadline: bool = False
    urgency_score: int = Field(default=1, ge=1, le=10)

class TimelineConflict(BaseModel):
    conflict_id: str
    description: str
    severity: Literal["low", "medium", "high"]

class TimelineAnalysisResult(BaseModel):
    events: List[TimelineEvent] = []
    conflicts: List[TimelineConflict] = []
    recommendations: List[str] = []

class TimelineEngine:
    """
    Stateless Mini Timeline Engine for temporal reasoning.
    """
    
    def __init__(self, client: Optional[GroqClient] = None):
        from llm.grok_client import llm_client
        self.client = client or llm_client

    async def analyze(self, content: str) -> TimelineAnalysisResult:
        """
        Main entry point: Analyze content for timeline validation.
        """
        logger.info("TimelineEngine: Analyzing content...")
        
        # 1. Extraction via LLM
        events = await self._extract_timeline_events(content)
        
        # 2. Conflict Detection (Local logic)
        conflicts = self._detect_conflicts(events, content)
        
        # 3. Generate Recommendations
        recommendations = self._generate_recommendations(events, conflicts)
        
        result = TimelineAnalysisResult(
            events=events,
            conflicts=conflicts,
            recommendations=recommendations
        )
        
        # Log result summary
        logger.info(f"TimelineEngine: Found {len(events)} events, {len(conflicts)} conflicts")
        return result

    async def _extract_timeline_events(self, content: str) -> List[TimelineEvent]:
        """
        Extract timeline events using Groq LLM.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = TIMELINE_EXTRACTION_PROMPT.format(
            current_date=current_date,
            content=content
        )
        
        try:
            # We use a direct complete call, assuming the prompt expects JSON
            response_text = await self.client.complete(
                system_prompt="You are a Timeline Extraction Agent. Respond with valid JSON only.",
                user_prompt=prompt,
                temperature=0.1
            )
            
            data = GroqClient.extract_json(response_text)
            
            events = []
            for item in data.get("events", []):
                try:
                    event = TimelineEvent.model_validate(item)
                    events.append(event)
                except ValidationError as e:
                    logger.warning(f"Invalid timeline event: {e}")
                    continue
            return events
            
        except Exception as e:
            logger.error(f"Timeline Extraction Failed: {e}")
            return []

    def _detect_conflicts(self, events: List[TimelineEvent], content: str) -> List[TimelineConflict]:
        """
        Detect logical conflicts within the extracted events and content content.
        """
        conflicts = []
        today = datetime.now().date()
        
        # Check 1: Past Deadlines
        for event in events:
            if event.is_deadline:
                try:
                    event_date = datetime.strptime(event.date.normalized, "%Y-%m-%d").date()
                    if event_date < today:
                        conflicts.append(TimelineConflict(
                            conflict_id="TL-C-PAST",
                            description=f"Deadline '{event.description}' ({event.date.normalized}) is in the past.",
                            severity="high"
                        ))
                    elif event_date == today:
                        conflicts.append(TimelineConflict(
                            conflict_id="TL-C-TODAY",
                            description=f"Deadline '{event.description}' is today. High pressure.",
                            severity="medium"
                        ))
                except ValueError:
                    continue # Skip invalid date formats
        
        # Check 2: Immediate Urgency with no date
        if "asap" in content.lower() or "urgent" in content.lower():
            has_deadline = any(e.is_deadline for e in events)
            if not has_deadline:
                conflicts.append(TimelineConflict(
                    conflict_id="TL-C-AMBIGUOUS-URGENCY",
                    description="Message is marked URGENT/ASAP but has no explicit deadline.",
                    severity="medium"
                ))

        # Check 3: Conflicting Deadlines (Simple Heuristic: Multiple high-certainty deadlines)
        deadlines = [e for e in events if e.is_deadline and e.date.certainty == "high"]
        if len(deadlines) > 1:
            # If dates differ significantly
            dates = set(e.date.normalized for e in deadlines)
            if len(dates) > 1:
                conflicts.append(TimelineConflict(
                    conflict_id="TL-C-MULTIPLE-DEADLINES",
                    description=f"Multiple conflicting deadlines found: {dates}",
                    severity="high"
                ))
                
        return conflicts

    def _generate_recommendations(self, events: List[TimelineEvent], conflicts: List[TimelineConflict]) -> List[str]:
        recommendations = []
        
        if not events and not conflicts:
            return []
            
        if any(c.severity == "high" for c in conflicts):
            recommendations.append("URGENT: Clarify timeline conflicts immediately.")
            
        uncertain_events = [e for e in events if e.date.certainty == "low"]
        if uncertain_events:
            recommendations.append("Clarify ambiguous dates: " + ", ".join([e.date.raw for e in uncertain_events]))
            
        if any(e.urgency_score >= 8 for e in events):
            recommendations.append("High urgency detected. Prioritize risk assessment.")
            
        return recommendations
