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

    if data is None or data.empty or len(data) < 30:
        send("⚠️ NIFTY data not available")
    else:
        close = data['Close']

        latest = float(close.iloc[-1])
        d1 = float((close.iloc[-1] / close.iloc[-2]) - 1)
        d7 = float((close.iloc[-1] / close.iloc[-7]) - 1)
        d30 = float((close.iloc[-1] / close.iloc[-30]) - 1)
        d365 = float((close.iloc[-1] / close.iloc[-252]) - 1)

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
