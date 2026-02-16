"""
Pydantic schemas for agent outputs.
Ensures type safety and validation.
"""
from typing import List, Optional
from pydantic import BaseModel

class NewsHeadline(BaseModel):
    headline: str
    source: str
    datetime: str
    url: str
    reason_tag: str

class NewsAgentOutput(BaseModel):
    ticker: str
    top_headlines: List[NewsHeadline]
    headline_count: int

class EarningsAgentOutput(BaseModel):
    earnings_date: Optional[str]
    event_risk_level: str  # LOW, MEDIUM, HIGH
    event_risk_reason: str

class SentimentAgentOutput(BaseModel):
    overall_sentiment: str  # Positive, Neutral, Negative
    sentiment_score: float  # -1.0 to 1.0
    supportive_context: List[str]  # Factors that may strengthen confidence
    risk_factors: List[str]  # Factors that may reduce confidence
    confidence_summary: str  # Concise analyst-style explanation
    explanation_markdown: str  # Legacy field for backward compatibility

class IntelligenceReport(BaseModel):
    """Combined output from all agents."""
    news: NewsAgentOutput
    earnings: EarningsAgentOutput
    sentiment: SentimentAgentOutput
