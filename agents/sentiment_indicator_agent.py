"""
Sentiment + Indicator Explanation Agent
Analyzes sentiment from headlines and generates explanation with citations.
"""
from typing import List, Dict
from schemas.agent_schemas import SentimentAgentOutput, NewsAgentOutput, EarningsAgentOutput

class SentimentIndicatorAgent:
    # Simple keyword-based sentiment scoring
    POSITIVE_KEYWORDS = [
        "beat", "growth", "upgrade", "record", "surge", "rally", "gain",
        "strong", "bullish", "outperform", "buy", "positive", "rise"
    ]
    
    NEGATIVE_KEYWORDS = [
        "miss", "lawsuit", "downgrade", "risk", "decline", "fall", "drop",
        "weak", "bearish", "underperform", "sell", "negative", "loss"
    ]
    
    def _calculate_sentiment_score(self, headlines: List[str]) -> float:
        """
        Calculate sentiment score from -1.0 (negative) to 1.0 (positive).
        """
        if not headlines:
            return 0.0
        
        total_score = 0
        for headline in headlines:
            headline_lower = headline.lower()
            
            pos_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in headline_lower)
            neg_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in headline_lower)
            
            # Simple scoring: +1 for positive, -1 for negative
            total_score += pos_count - neg_count
        
        # Normalize to -1.0 to 1.0 range
        max_possible = len(headlines) * 3  # Assume max 3 keywords per headline
        normalized = total_score / max_possible if max_possible > 0 else 0.0
        
        return max(-1.0, min(1.0, normalized))
    
    def _generate_supportive_context(
        self,
        sentiment_score: float,
        news_output: NewsAgentOutput,
        earnings_output: EarningsAgentOutput,
        prediction: str,
        indicators: Dict,
        confidence: float
    ) -> List[str]:
        """
        Generate factors that may strengthen confidence in the model prediction.
        """
        supportive = []
        
        # High model confidence
        if confidence > 70:
            supportive.append(f"Model shows strong confidence at {confidence:.1f}%")
        
        # Sentiment alignment
        prediction_direction = "UP" if "UP" in prediction else "DOWN"
        if prediction_direction == "UP" and sentiment_score > 0.2:
            supportive.append("Positive news sentiment aligns with upward model signal")
        elif prediction_direction == "DOWN" and sentiment_score < -0.2:
            supportive.append("Negative news sentiment aligns with downward model signal")
        
        # MA trend alignment
        ma20 = indicators.get("MA20")
        ma50 = indicators.get("MA50")
        if ma20 and ma50:
            if prediction_direction == "UP" and ma20 > ma50:
                supportive.append(f"MA20 above MA50 supports upward trend")
            elif prediction_direction == "DOWN" and ma20 < ma50:
                supportive.append(f"MA20 below MA50 supports downward trend")
        
        # RSI continuation potential
        rsi = indicators.get("RSI")
        if rsi:
            if prediction_direction == "UP" and 40 < rsi < 70:
                supportive.append(f"RSI at {rsi:.1f} suggests room for upward continuation")
            elif prediction_direction == "DOWN" and 30 < rsi < 60:
                supportive.append(f"RSI at {rsi:.1f} suggests room for downward continuation")
        
        # Positive earnings coverage
        if earnings_output.event_risk_level == "LOW":
            supportive.append("Low event risk provides stable environment for current trend")
        
        # Analyst upgrades in headlines
        for headline in news_output.top_headlines:
            if "upgrade" in headline.headline.lower():
                supportive.append(f"Analyst upgrade may support confidence [{headline.source}]")
                break
        
        return supportive if supportive else ["Limited supportive factors identified"]
    
    def _generate_risk_factors(
        self,
        sentiment_score: float,
        news_output: NewsAgentOutput,
        earnings_output: EarningsAgentOutput,
        prediction: str,
        indicators: Dict,
        confidence: float
    ) -> List[str]:
        """
        Generate factors that may reduce confidence or introduce uncertainty.
        """
        risks = []
        
        # Low model confidence
        if confidence < 60:
            risks.append(f"Model confidence at {confidence:.1f}% suggests higher uncertainty")
        
        # Imminent earnings
        if earnings_output.event_risk_level == "HIGH":
            risks.append(f"High event risk: {earnings_output.event_risk_reason}")
        elif earnings_output.event_risk_level == "MEDIUM":
            risks.append(f"Moderate event risk: {earnings_output.event_risk_reason}")
        
        # Sentiment-prediction mismatch
        prediction_direction = "UP" if "UP" in prediction else "DOWN"
        if prediction_direction == "UP" and sentiment_score < -0.2:
            risks.append("Negative news sentiment conflicts with upward model signal")
        elif prediction_direction == "DOWN" and sentiment_score > 0.2:
            risks.append("Positive news sentiment conflicts with downward model signal")
        
        # RSI extremes
        rsi = indicators.get("RSI")
        if rsi:
            if rsi > 70:
                risks.append(f"RSI at {rsi:.1f} indicates overbought conditions, potential reversal risk")
            elif rsi < 30:
                risks.append(f"RSI at {rsi:.1f} indicates oversold conditions, potential reversal risk")
        
        # Negative regulatory/legal news
        for headline in news_output.top_headlines:
            headline_lower = headline.headline.lower()
            if any(word in headline_lower for word in ["lawsuit", "investigation", "regulatory"]):
                risks.append(f"Legal/regulatory concerns may introduce volatility [{headline.source}]")
                break
        
        # Mixed sentiment environment
        if -0.2 <= sentiment_score <= 0.2 and len(news_output.top_headlines) > 0:
            risks.append("Mixed news sentiment creates uncertain environment")
        
        return risks if risks else ["No significant risk factors identified"]
    
    def _generate_confidence_summary(
        self,
        sentiment_score: float,
        news_output: NewsAgentOutput,
        earnings_output: EarningsAgentOutput,
        prediction: str,
        indicators: Dict,
        confidence: float
    ) -> str:
        """
        Generate concise analyst-style confidence impact summary.
        """
        parts = []
        
        # Start with model prediction
        parts.append(f"The model predicts {prediction} with {confidence:.1f}% confidence.")
        
        # Sentiment context with citation
        if sentiment_score > 0.2:
            sentiment_desc = "positive"
        elif sentiment_score < -0.2:
            sentiment_desc = "negative"
        else:
            sentiment_desc = "neutral"
        
        if news_output.top_headlines:
            top_headline = news_output.top_headlines[0]
            parts.append(f"Recent {sentiment_desc} news coverage [{top_headline.source}, {top_headline.datetime[:10]}]")
            
            prediction_direction = "UP" if "UP" in prediction else "DOWN"
            if (prediction_direction == "UP" and sentiment_score > 0.2) or \
               (prediction_direction == "DOWN" and sentiment_score < -0.2):
                parts.append("may support the current signal.")
            elif (prediction_direction == "UP" and sentiment_score < -0.2) or \
                 (prediction_direction == "DOWN" and sentiment_score > 0.2):
                parts.append("introduces conflicting signals that could weaken confidence.")
            else:
                parts.append("provides limited directional insight.")
        
        # Event risk impact
        if earnings_output.event_risk_level == "HIGH":
            parts.append(f"However, {earnings_output.event_risk_reason.lower()}, which may introduce significant volatility and reduce confidence in short-term signals.")
        elif earnings_output.event_risk_level == "MEDIUM":
            parts.append(f"{earnings_output.event_risk_reason}, which could introduce moderate uncertainty.")
        
        return " ".join(parts)
    
    def _generate_explanation(
        self,
        sentiment_score: float,
        news_output: NewsAgentOutput,
        earnings_output: EarningsAgentOutput,
        prediction: str,
        indicators: Dict
    ) -> str:
        """
        Generate markdown explanation with inline citations (legacy format).
        """
        explanation_parts = []
        
        # Sentiment summary
        if sentiment_score > 0.2:
            explanation_parts.append("**Sentiment Analysis:** Positive news sentiment detected.")
        elif sentiment_score < -0.2:
            explanation_parts.append("**Sentiment Analysis:** Negative news sentiment detected.")
        else:
            explanation_parts.append("**Sentiment Analysis:** Neutral news sentiment.")
        
        # Add citations from top 3 headlines
        if news_output.top_headlines:
            explanation_parts.append("\n**Recent Headlines:**")
            for headline in news_output.top_headlines[:3]:
                citation = f"- {headline.headline[:80]}... [{headline.source}, {headline.datetime}]"
                explanation_parts.append(citation)
        
        # Event risk context
        explanation_parts.append(f"\n**Event Risk:** {earnings_output.event_risk_level} - {earnings_output.event_risk_reason}")
        
        # Technical indicators
        explanation_parts.append("\n**Technical Indicators:**")
        
        rsi = indicators.get("RSI")
        if rsi:
            if rsi > 70:
                explanation_parts.append(f"- RSI at {rsi:.1f} suggests overbought conditions 🐂")
            elif rsi < 30:
                explanation_parts.append(f"- RSI at {rsi:.1f} suggests oversold conditions 🐻")
            else:
                explanation_parts.append(f"- RSI at {rsi:.1f} is in neutral range")
        
        ma20 = indicators.get("MA20")
        ma50 = indicators.get("MA50")
        if ma20 and ma50:
            if ma20 > ma50:
                explanation_parts.append(f"- MA20 ({ma20:.2f}) above MA50 ({ma50:.2f}) - bullish signal")
            else:
                explanation_parts.append(f"- MA20 ({ma20:.2f}) below MA50 ({ma50:.2f}) - bearish signal")
        
        # Prediction summary
        explanation_parts.append(f"\n**Model Prediction:** {prediction}")
        
        return "\n".join(explanation_parts)
    
    def run(
        self,
        news_output: NewsAgentOutput,
        earnings_output: EarningsAgentOutput,
        prediction: str,
        indicators: Dict,
        confidence: float = 50.0
    ) -> SentimentAgentOutput:
        """
        Analyze sentiment and generate confidence overlay.
        """
        # Extract headlines
        headlines = [h.headline for h in news_output.top_headlines]
        
        # Calculate sentiment
        sentiment_score = self._calculate_sentiment_score(headlines)
        
        # Determine overall sentiment
        if sentiment_score > 0.2:
            overall_sentiment = "Positive"
        elif sentiment_score < -0.2:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"
        
        # Generate confidence overlay components
        supportive_context = self._generate_supportive_context(
            sentiment_score, news_output, earnings_output, prediction, indicators, confidence
        )
        
        risk_factors = self._generate_risk_factors(
            sentiment_score, news_output, earnings_output, prediction, indicators, confidence
        )
        
        confidence_summary = self._generate_confidence_summary(
            sentiment_score, news_output, earnings_output, prediction, indicators, confidence
        )
        
        # Generate legacy explanation for backward compatibility
        explanation = self._generate_explanation(
            sentiment_score, news_output, earnings_output, prediction, indicators
        )
        
        return SentimentAgentOutput(
            overall_sentiment=overall_sentiment,
            sentiment_score=sentiment_score,
            supportive_context=supportive_context,
            risk_factors=risk_factors,
            confidence_summary=confidence_summary,
            explanation_markdown=explanation
        )
