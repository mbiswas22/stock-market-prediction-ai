"""
News Ingestion Agent
Fetches company news, tags by reason type, and returns top 3 most relevant headlines.
"""
from typing import List, Dict
from datetime import datetime
from services.finnhub_client import FinnhubClient
from schemas.agent_schemas import NewsAgentOutput, NewsHeadline

class NewsIngestionAgent:
    # Keyword-based tagging rules
    REASON_KEYWORDS = {
        "earnings": ["earnings", "revenue", "profit", "eps", "quarterly", "q1", "q2", "q3", "q4"],
        "product": ["launch", "product", "release", "unveil", "announce"],
        "analyst": ["upgrade", "downgrade", "rating", "analyst", "price target"],
        "macro": ["fed", "inflation", "interest rate", "economy", "recession"],
        "regulatory": ["sec", "lawsuit", "regulation", "investigation", "fine"]
    }
    
    def __init__(self):
        self.client = FinnhubClient()
    
    def _tag_headline(self, headline: str) -> str:
        """Tag headline based on keyword matching."""
        headline_lower = headline.lower()
        
        for reason, keywords in self.REASON_KEYWORDS.items():
            if any(kw in headline_lower for kw in keywords):
                return reason
        
        return "other"
    
    def _deduplicate_headlines(self, news_list: List[Dict]) -> List[Dict]:
        """Remove similar headlines based on first 50 characters."""
        seen = set()
        unique_news = []
        
        for news in news_list:
            headline_key = news["headline"][:50].lower()
            if headline_key not in seen:
                seen.add(headline_key)
                unique_news.append(news)
        
        return unique_news
    
    def run(self, ticker: str, days: int = 7) -> NewsAgentOutput:
        """
        Fetch and process news for a ticker.
        Returns top 3 most recent + relevant headlines.
        """
        # Fetch news from Finnhub
        news_list = self.client.get_company_news(ticker, days)
        
        if not news_list:
            return NewsAgentOutput(
                ticker=ticker,
                top_headlines=[],
                headline_count=0
            )
        
        # Deduplicate
        news_list = self._deduplicate_headlines(news_list)
        
        # Tag each headline
        for news in news_list:
            news["reason_tag"] = self._tag_headline(news["headline"])
        
        # Sort by datetime (most recent first)
        news_list.sort(key=lambda x: x["datetime"], reverse=True)
        
        # Prioritize earnings/analyst news, then take top 3
        priority_news = [n for n in news_list if n["reason_tag"] in ["earnings", "analyst"]]
        other_news = [n for n in news_list if n["reason_tag"] not in ["earnings", "analyst"]]
        
        top_3 = (priority_news + other_news)[:3]
        
        # Convert to schema
        headlines = [
            NewsHeadline(
                headline=n["headline"],
                source=n["source"],
                datetime=n["datetime"].strftime("%Y-%m-%d %H:%M"),
                url=n["url"],
                reason_tag=n["reason_tag"]
            )
            for n in top_3
        ]
        
        return NewsAgentOutput(
            ticker=ticker,
            top_headlines=headlines,
            headline_count=len(news_list)
        )
