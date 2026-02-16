"""
Earnings & Event Awareness Agent
Detects upcoming/recent earnings and assigns risk level.
"""
from datetime import datetime, timedelta
from typing import Optional
from services.finnhub_client import FinnhubClient
from schemas.agent_schemas import EarningsAgentOutput

class EarningsEventAgent:
    def __init__(self):
        self.client = FinnhubClient()
    
    def _calculate_risk_level(self, earnings_date_str: Optional[str]) -> tuple:
        """
        Calculate event risk level based on earnings date proximity.
        Returns (risk_level, reason).
        """
        if not earnings_date_str:
            return "LOW", "No upcoming earnings detected"
        
        try:
            earnings_date = datetime.strptime(earnings_date_str, "%Y-%m-%d")
        except:
            return "LOW", "Unable to parse earnings date"
        
        today = datetime.now()
        days_diff = (earnings_date - today).days
        
        # HIGH RISK: Earnings in next 3 days or released 1-2 days ago
        if -2 <= days_diff <= 3:
            if days_diff < 0:
                return "HIGH", f"Earnings released {abs(days_diff)} day(s) ago - high volatility period"
            else:
                return "HIGH", f"Earnings in {days_diff} day(s) - expect high volatility"
        
        # MEDIUM RISK: Earnings within 4-14 days or last week
        if -7 <= days_diff <= 14:
            if days_diff < 0:
                return "MEDIUM", f"Earnings released last week - volatility settling"
            else:
                return "MEDIUM", f"Earnings in {days_diff} day(s) - moderate risk"
        
        # LOW RISK: Otherwise
        if days_diff > 14:
            return "LOW", f"Earnings in {days_diff} day(s) - low immediate risk"
        else:
            return "LOW", "Earnings date outside risk window"
    
    def run(self, ticker: str) -> EarningsAgentOutput:
        """
        Check earnings calendar and determine event risk.
        """
        earnings_data = self.client.get_earnings_calendar(ticker)
        
        earnings_date = None
        if earnings_data:
            earnings_date = earnings_data.get("date")
        
        risk_level, risk_reason = self._calculate_risk_level(earnings_date)
        
        return EarningsAgentOutput(
            earnings_date=earnings_date,
            event_risk_level=risk_level,
            event_risk_reason=risk_reason
        )
