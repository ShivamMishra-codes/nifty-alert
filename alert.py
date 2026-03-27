import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

try:
    data = yf.download("^NSEI", period="1y", interval="1d")

    if data is None or data.empty:
        send("⚠️ NIFTY data not available")
    else:
        close = data['Close']
        n = len(close)

        latest = float(close.iloc[-1])

        # SAFE calculations
        d1 = float((close.iloc[-1] / close.iloc[-2]) - 1) if n >= 2 else 0
        d7 = float((close.iloc[-1] / close.iloc[-7]) - 1) if n >= 7 else 0
        d30 = float((close.iloc[-1] / close.iloc[-30]) - 1) if n >= 30 else 0
        d365 = float((close.iloc[-1] / close.iloc[-252]) - 1) if n >= 252 else 0

        # SIGNAL LOGIC
        if d30 < -0.10:
            signal = "🔴 CRASH"
            action = "Invest 50-60%"
        elif d30 < -0.05:
            signal = "🟡 MEDIUM DIP"
            action = "Invest 20-30%"
        elif d7 < -0.02:
            signal = "🟢 SMALL DIP"
            action = "Invest 10-15%"
        else:
            signal = "⚪ STABLE"
            action = "No extra investment"

        msg = f"""📊 NIFTY: {round(latest,2)}

1D: {round(d1*100,2)}%
7D: {round(d7*100,2)}%
1M: {round(d30*100,2)}%
1Y: {round(d365*100,2)}%

Signal: {signal}
Action: {action}
"""

        send(msg)

except Exception as e:
    send(f"❌ Error: {str(e)}")
