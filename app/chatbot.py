"""
Enhanced chatbot tools using Finnhub API and yfinance
"""
import yfinance as yf
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from services.finnhub_client import FinnhubClient

# Initialize Finnhub client
finnhub = FinnhubClient()

def get_stock_price(ticker: str) -> str:
    """Get current stock price using yfinance"""
    try:
        print(f"DEBUG: Ticker={ticker}")
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            change = data['Close'].iloc[-1] - data['Open'].iloc[0]
            change_pct = (change / data['Open'].iloc[0]) * 100
            return f"💰 {ticker} Price: ${price:.2f}\n📊 Change: ${change:.2f} ({change_pct:+.2f}%)"
        return f"Could not fetch price for {ticker}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_stock_info(ticker: str) -> str:
    """Get basic stock information using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        name = info.get('longName', 'N/A')
        sector = info.get('sector', 'N/A')
        market_cap = info.get('marketCap', 0)
        return f"🏢 {name} ({ticker})\n🏭 Sector: {sector}\n💼 Market Cap: ${market_cap:,.0f}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_stock_history(ticker: str) -> str:
    """Get 30-day stock price history using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1mo")
        if not data.empty:
            high = data['High'].max()
            low = data['Low'].min()
            avg = data['Close'].mean()
            return f"📈 {ticker} 30-day Stats:\n🔺 High: ${high:.2f}\n🔻 Low: ${low:.2f}\n📊 Average: ${avg:.2f}"
        return f"No history available for {ticker}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_company_news(ticker: str) -> str:
    """Get latest company news using Finnhub"""
    try:
        news = finnhub.get_company_news(ticker, days=7)
        if not news:
            return f"No recent news found for {ticker}"
        
        result = f"📰 Latest News for {ticker}:\n\n"
        for i, article in enumerate(news[:3], 1):
            headline = article.get('headline', 'No headline')
            source = article.get('source', 'Unknown')
            result += f"{i}. [{source}] {headline}\n\n"
        
        return result
    except Exception as e:
        return f"Error fetching news: {str(e)}"

def get_earnings_info(ticker: str) -> str:
    """Get earnings calendar using Finnhub"""
    try:
        earnings = finnhub.get_earnings_calendar(ticker)
        if not earnings:
            return f"No earnings data available for {ticker}"
        
        date = earnings.get('date', 'N/A')
        estimate = earnings.get('epsEstimate', 'N/A')
        actual = earnings.get('epsActual', 'N/A')
        
        result = f"📅 Earnings Info for {ticker}:\n"
        result += f"Date: {date}\n"
        result += f"EPS Estimate: {estimate}\n"
        if actual != 'N/A':
            result += f"EPS Actual: {actual}\n"
        
        return result
    except Exception as e:
        return f"Error fetching earnings: {str(e)}"

def analyze_sentiment(ticker: str) -> str:
    """Analyze sentiment from news headlines"""
    try:
        news = finnhub.get_company_news(ticker, days=3)
        if not news:
            return f"No recent news to analyze for {ticker}"
        
        positive_words = ['surge', 'gain', 'profit', 'growth', 'up', 'rise', 'bullish', 'strong', 'beat', 'high']
        negative_words = ['fall', 'loss', 'decline', 'down', 'drop', 'bearish', 'weak', 'miss', 'low', 'cut']
        
        pos_count = 0
        neg_count = 0
        
        for article in news[:5]:
            headline = article.get('headline', '').lower()
            summary = article.get('summary', '').lower()
            text = headline + ' ' + summary
            
            pos_count += sum(1 for word in positive_words if word in text)
            neg_count += sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            sentiment = "🟢 Positive"
            emoji = "📈"
        elif neg_count > pos_count:
            sentiment = "🔴 Negative"
            emoji = "📉"
        else:
            sentiment = "🟡 Neutral"
            emoji = "➡️"
        
        return f"{emoji} Sentiment Analysis for {ticker}:\n{sentiment}\n\nPositive signals: {pos_count}\nNegative signals: {neg_count}\nBased on {len(news[:5])} recent articles"
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

def send_stock_report(ticker: str, recipient_email: str, api_key: str = None, sender_email: str = None) -> str:
    """Generate and send stock summary report via email using SendGrid API"""
    try:
        print(f"DEBUG: send_stock_report called with ticker={ticker}")
        # Generate comprehensive report
        report_parts = []
        report_parts.append(f"Stock Summary Report for {ticker}")
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append("=" * 50)
        report_parts.append("")
        
        # Gather data from all tools
        report_parts.append("PRICE INFORMATION")
        report_parts.append(get_stock_price(ticker))
        report_parts.append("")
        
        report_parts.append("COMPANY INFORMATION")
        report_parts.append(get_stock_info(ticker))
        report_parts.append("")
        
        report_parts.append("30-DAY HISTORY")
        report_parts.append(get_stock_history(ticker))
        report_parts.append("")
        
        report_parts.append("SENTIMENT ANALYSIS")
        report_parts.append(analyze_sentiment(ticker))
        report_parts.append("")
        
        report_parts.append("LATEST NEWS")
        report_parts.append(get_company_news(ticker))
        report_parts.append("")
        
        report_parts.append("EARNINGS INFORMATION")
        report_parts.append(get_earnings_info(ticker))
        report_parts.append("")
        
        report_parts.append("=" * 50)
        report_parts.append("⚠️ Not financial advice. For educational purposes only.")
        
        report_text = "\n".join(report_parts)
        
        # If no API key provided, return report preview
        if not api_key or not sender_email:
            return f"📧 Email Report Preview:\n\n{report_text}\n\n⚠️ To send emails, configure SENDGRID_API_KEY and EMAIL_USER in .env file"
        
        # Create and send email using SendGrid
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=f"Stock Report: {ticker} - {datetime.now().strftime('%Y-%m-%d')}",
            plain_text_content=report_text
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return f"✅ Stock report for {ticker} sent successfully to {recipient_email}!"
    except Exception as e:
        error_msg = str(e)
        report_text = "\n".join(report_parts) if 'report_parts' in locals() else "Report generation failed"
        
        if "403" in error_msg or "Forbidden" in error_msg:
            return f"❌ SendGrid Error: Sender email '{sender_email}' is not verified.\n\n📧 Report Preview:\n\n{report_text}\n\n⚠️ To send emails:\n1. Verify sender email at https://app.sendgrid.com/settings/sender_auth\n2. Or use Single Sender Verification\n3. Wait for verification email and confirm"
        
        return f"❌ Error: {error_msg}\n\n📧 Report Preview:\n\n{report_text}"

# Agent tools mapping
AGENT_TOOLS = {
    "price": get_stock_price,
    "info": get_stock_info,
    "history": get_stock_history,
    "news": get_company_news,
    "earnings": get_earnings_info,
    "sentiment": analyze_sentiment,
    "email": send_stock_report
}

def process_query(query: str) -> str:
    """Process user query and route to appropriate agent tool"""
    query_lower = query.lower()
    
    # Common stock tickers to look for
    common_tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC', 'GE']
    
    # Extract ticker from query - improved logic
    ticker = None
    
    # Method 1: Check for common tickers first
    for common_ticker in common_tickers:
        if common_ticker.lower() in query_lower:
            ticker = common_ticker
            print(f"1. DEBUG: common_ticker={ticker}")
            break
    
    # Method 2: Look for uppercase words (likely tickers)
    if not ticker:
        words = query.split()
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,?!').upper()
            # Check if it's 1-5 letters and all alpha
            if 1 <= len(clean_word) <= 5 and clean_word.isalpha():
                print(f"DEBUG: Look for uppercase words with ticker={ticker}")
                ticker = clean_word
                break
    
    # Method 3: Look for any short alphabetic word
    if not ticker:
        words = query.upper().split()
        for word in words:
            clean_word = word.strip('.,?!')
            if 2 <= len(clean_word) <= 5 and clean_word.isalpha():
                ticker = clean_word
                print(f"DEBUG: Look for any short alphabetic word with ticker={ticker}")
                break
    
    if not ticker:
        return "❓ Please specify a stock ticker (e.g., AAPL, MSFT, TSLA)"
    
    # Route to appropriate tool based on keywords
    if any(word in query_lower for word in ['email', 'send', 'mail']):
        # Extract email if present
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', query)
        if email_match:
            recipient = email_match.group(0)
            import os
            api_key = os.getenv('SENDGRID_API_KEY')
            sender = os.getenv('EMAIL_USER')
            return AGENT_TOOLS['email'](ticker, recipient, api_key, sender)
        else:
            return "❓ Please provide a recipient email address (e.g., 'Send AAPL report to user@example.com')"
    elif any(word in query_lower for word in ['price', 'cost', 'trading', 'quote', 'worth']):
        return AGENT_TOOLS['price'](ticker)
    elif any(word in query_lower for word in ['news', 'headlines', 'articles', 'latest']):
        return AGENT_TOOLS['news'](ticker)
    elif any(word in query_lower for word in ['earnings', 'eps', 'report']):
        return AGENT_TOOLS['earnings'](ticker)
    elif any(word in query_lower for word in ['sentiment', 'feeling', 'mood', 'opinion']):
        return AGENT_TOOLS['sentiment'](ticker)
    elif any(word in query_lower for word in ['history', 'past', 'trend', 'stats']):
        return AGENT_TOOLS['history'](ticker)
    elif any(word in query_lower for word in ['info', 'about', 'company', 'profile', 'what']):
        return AGENT_TOOLS['info'](ticker)
    else:
        # Default to price
        return AGENT_TOOLS['price'](ticker)
