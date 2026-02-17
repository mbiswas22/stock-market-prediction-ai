"""
Finnhub API client with retry logic and error handling.
Provides company news and earnings calendar data.
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            print("⚠️ FINNHUB_API_KEY not found in .env")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with retry logic."""
        if not self.api_key:
            return None
        
        params["token"] = self.api_key
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("⚠️ Rate limit hit, retrying...")
                raise
            print(f"❌ HTTP error: {e}")
            return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_company_news(self, ticker: str, days: int = 7) -> List[Dict]:
        """
        Fetch company news for the last N days.
        Returns list of news articles with headline, source, datetime, url.
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        params = {
            "symbol": ticker,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d")
        }
        
        data = self._make_request("company-news", params)
        if not data:
            return []
        
        # Normalize response
        news_list = []
        for item in data:
            news_list.append({
                "headline": item.get("headline", ""),
                "source": item.get("source", "Unknown"),
                "datetime": datetime.fromtimestamp(item.get("datetime", 0)),
                "url": item.get("url", ""),
                "summary": item.get("summary", "")
            })
        
        return news_list
    
    def get_earnings_calendar(self, ticker: str) -> Optional[Dict]:
        """
        Fetch earnings calendar for a ticker.
        Returns earnings date and estimate info.
        """
        # Get earnings calendar for next 30 days
        to_date = datetime.now() + timedelta(days=30)
        from_date = datetime.now() - timedelta(days=30)
        
        params = {
            "symbol": ticker,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d")
        }
        
        data = self._make_request("calendar/earnings", params)
        if not data or "earningsCalendar" not in data:
            return None
        
        # Find the most relevant earnings date
        earnings = data["earningsCalendar"]
        if not earnings:
            return None
        
        # Get the closest earnings date
        for item in earnings:
            if item.get("symbol") == ticker:
                return {
                    "date": item.get("date"),
                    "epsEstimate": item.get("epsEstimate"),
                    "epsActual": item.get("epsActual")
                }
        
        return None
