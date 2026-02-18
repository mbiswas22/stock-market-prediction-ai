"""
Realized Volatility Analyzer
Calculates and visualizes 30/60/90 day rolling realized volatility trends.
"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, Tuple

class RealizedVolatilityAnalyzer:
    """Analyzes historical realized volatility patterns for equity analysis."""
    
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.data = None
        self.rv_data = None
        
    def fetch_data(self, months: int = 12) -> pd.DataFrame:
        """Fetch historical price data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30 + 100)
        
        stock = yf.Ticker(self.ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {self.ticker}")
        
        self.data = df
        return df
    
    def calculate_realized_volatility(self) -> pd.DataFrame:
        """Calculate 30/60/90 day rolling realized volatility."""
        if self.data is None:
            raise ValueError("Must fetch data first")
        
        prices = self.data['Close']
        log_returns = np.log(prices / prices.shift(1))
        
        rv30 = log_returns.rolling(window=30).std() * np.sqrt(252) * 100
        rv60 = log_returns.rolling(window=60).std() * np.sqrt(252) * 100
        rv90 = log_returns.rolling(window=90).std() * np.sqrt(252) * 100
        
        self.rv_data = pd.DataFrame({'RV30': rv30, 'RV60': rv60, 'RV90': rv90})
        
        cutoff_date = pd.Timestamp(datetime.now() - timedelta(days=365)).tz_localize(self.rv_data.index.tz)
        self.rv_data = self.rv_data[self.rv_data.index >= cutoff_date]
        
        return self.rv_data
    
    def plot_volatility(self) -> plt.Figure:
        """Create time-series chart of realized volatility."""
        if self.rv_data is None:
            raise ValueError("Must calculate volatility first")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(self.rv_data.index, self.rv_data['RV30'], label='RV30', linewidth=2, color='#FF6B6B')
        ax.plot(self.rv_data.index, self.rv_data['RV60'], label='RV60', linewidth=2, color='#4ECDC4')
        ax.plot(self.rv_data.index, self.rv_data['RV90'], label='RV90', linewidth=2, color='#45B7D1')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Annualized Volatility (%)', fontsize=12)
        ax.set_title(f'{self.ticker} 30/60/90 Day Realized Volatility Trends (Past 12 Months)', 
                     fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def analyze_volatility_trends(self) -> Dict[str, any]:
        """Analyze volatility patterns and generate insights."""
        if self.rv_data is None:
            raise ValueError("Must calculate volatility first")
        
        rv_clean = self.rv_data.dropna()
        
        if len(rv_clean) < 40:
            return {"error": "Insufficient data for analysis"}
        
        recent_rv30 = rv_clean['RV30'].iloc[-10:].mean()
        prior_rv30 = rv_clean['RV30'].iloc[-40:-10].mean()
        
        current_rv30 = rv_clean['RV30'].iloc[-1]
        current_rv60 = rv_clean['RV60'].iloc[-1]
        current_rv90 = rv_clean['RV90'].iloc[-1]
        
        rv30_percentile = (rv_clean['RV30'] < current_rv30).sum() / len(rv_clean) * 100
        
        if current_rv30 > current_rv60 > current_rv90:
            regime = "expansion"
        elif current_rv30 < current_rv60 < current_rv90:
            regime = "compression"
        else:
            regime = "mixed"
        
        trend = "increasing" if recent_rv30 > prior_rv30 else "decreasing"
        
        return {
            "current_rv30": current_rv30,
            "current_rv60": current_rv60,
            "current_rv90": current_rv90,
            "recent_rv30_avg": recent_rv30,
            "prior_rv30_avg": prior_rv30,
            "trend": trend,
            "regime": regime,
            "rv30_percentile": rv30_percentile,
            "rv30_vs_rv90_spread": current_rv30 - current_rv90
        }
    
    def generate_analysis_report(self) -> str:
        """Generate structured analytical output."""
        analysis = self.analyze_volatility_trends()
        
        if "error" in analysis:
            return f"⚠️ {analysis['error']}"
        
        report = f"""
## 📊 Realized Volatility Analysis: {self.ticker}

### A) Volatility Trend Interpretation

**Short-term Trend:** {analysis['trend'].upper()}
- Recent 10-day RV30 average: {analysis['recent_rv30_avg']:.2f}%
- Prior 30-day RV30 average: {analysis['prior_rv30_avg']:.2f}%
- Current RV30: {analysis['current_rv30']:.2f}%

**Relative Positioning:**
- RV30 vs RV90 spread: {analysis['rv30_vs_rv90_spread']:+.2f}%
- RV30 is {'ABOVE' if analysis['current_rv30'] > analysis['current_rv90'] else 'BELOW'} RV90
- Current RV30 at {analysis['rv30_percentile']:.1f}th percentile (past 12 months)

### B) Market Regime Assessment

**Volatility Environment:** {analysis['regime'].upper()}
- RV30: {analysis['current_rv30']:.2f}%
- RV60: {analysis['current_rv60']:.2f}%
- RV90: {analysis['current_rv90']:.2f}%

**Interpretation:**
"""
        
        if analysis['regime'] == "expansion":
            report += "- Short-term volatility expanding relative to longer-term measures\n"
            report += "- Market appears to be entering a higher volatility phase\n"
        elif analysis['regime'] == "compression":
            report += "- Short-term volatility compressing relative to longer-term measures\n"
            report += "- Market appears to be stabilizing or entering lower volatility phase\n"
        else:
            report += "- Mixed volatility signals across timeframes\n"
            report += "- Market in transitional volatility state\n"
        
        report += f"\n### C) Quantitative Reasoning\n\n"
        report += f"- RV30 vs RV90 spread of {analysis['rv30_vs_rv90_spread']:+.2f}% "
        report += f"{'suggests elevated near-term uncertainty' if analysis['rv30_vs_rv90_spread'] > 5 else 'indicates relatively stable conditions'}\n"
        report += f"- Current RV30 at {analysis['rv30_percentile']:.1f}th percentile "
        report += f"{'appears elevated' if analysis['rv30_percentile'] > 70 else 'appears subdued' if analysis['rv30_percentile'] < 30 else 'is near historical median'}\n"
        report += f"- Short-term volatility trend is {analysis['trend']}, "
        report += f"{'potentially signaling mean reversion opportunity' if analysis['trend'] == 'increasing' and analysis['rv30_percentile'] > 70 else 'consistent with current regime'}\n"
        
        report += f"\n### 💡 Options Environment Insight\n\n"
        
        if analysis['regime'] == "expansion" and analysis['trend'] == "increasing":
            insight = "Recent volatility patterns suggest a higher movement environment, which is often associated with defined-risk debit spreads or directional positioning with limited risk under elevated premium conditions."
        elif analysis['regime'] == "compression" and analysis['trend'] == "decreasing":
            insight = "Recent volatility patterns suggest a lower movement environment, which is often associated with neutral income structures or credit strategies under compressed premium conditions."
        elif analysis['rv30_percentile'] > 70:
            insight = "Recent volatility patterns suggest an elevated movement environment relative to historical norms, which is often associated with premium selling strategies or defined-risk structures under high implied volatility conditions."
        else:
            insight = "Recent volatility patterns suggest a stable movement environment, which is often associated with balanced risk-defined strategies under moderate premium conditions."
        
        report += f"_{insight}_\n"
        report += f"\n⚠️ **Disclaimer:** This analysis is observational and educational only. Not financial advice.\n"
        
        return report
    
    def run_full_analysis(self) -> Tuple[plt.Figure, str]:
        """Execute complete volatility analysis workflow."""
        self.fetch_data()
        self.calculate_realized_volatility()
        fig = self.plot_volatility()
        report = self.generate_analysis_report()
        return fig, report


def analyze_stock_volatility(ticker: str) -> Tuple[plt.Figure, str]:
    """Convenience function to run complete volatility analysis."""
    analyzer = RealizedVolatilityAnalyzer(ticker)
    return analyzer.run_full_analysis()
