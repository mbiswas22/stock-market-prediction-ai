"""
Agent Orchestrator
Coordinates the 3-agent intelligence system.
"""
from typing import Dict
from agents.news_ingestion_agent import NewsIngestionAgent
from agents.earnings_event_agent import EarningsEventAgent
from agents.sentiment_indicator_agent import SentimentIndicatorAgent
from schemas.agent_schemas import IntelligenceReport

class AgentOrchestrator:
    def __init__(self):
        self.news_agent = NewsIngestionAgent()
        self.earnings_agent = EarningsEventAgent()
        self.sentiment_agent = SentimentIndicatorAgent()
    
    def run_intelligence(
        self,
        ticker: str,
        prediction: str,
        indicators: Dict,
        confidence: float = 50.0
    ) -> IntelligenceReport:
        """
        Run all 3 agents in sequence and return combined intelligence report.
        
        Args:
            ticker: Stock ticker symbol
            prediction: Model prediction (e.g., "UP 📈")
            indicators: Dict of technical indicators (MA20, MA50, RSI, etc.)
            confidence: Model confidence percentage
        
        Returns:
            IntelligenceReport with news, earnings, and sentiment analysis
        """
        # Agent 1: News Ingestion
        news_output = self.news_agent.run(ticker)
        
        # Agent 2: Earnings & Event Awareness
        earnings_output = self.earnings_agent.run(ticker)
        
        # Agent 3: Sentiment + Indicator Explanation (with confidence overlay)
        sentiment_output = self.sentiment_agent.run(
            news_output,
            earnings_output,
            prediction,
            indicators,
            confidence
        )
        
        return IntelligenceReport(
            news=news_output,
            earnings=earnings_output,
            sentiment=sentiment_output
        )
