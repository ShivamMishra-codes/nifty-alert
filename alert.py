import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

try:
    data = yf.download("^NSEI", period="10d", interval="1d")

    # Always send message (important)
    if data is None or data.empty or len(data) < 7:
        send("⚠️ NIFTY data not available today (API issue)")
    else:
        close = data['Close']
        ret_7d = float((close.iloc[-1] / close.iloc[-7]) - 1)

        msg = f"📊 NIFTY 7-day return: {round(ret_7d*100,2)}%"

        if ret_7d < -0.02:
            msg += "\n🚨 Market falling → Invest before 2 PM"
        else:
            msg += "\nℹ️ No major fall"

        send(msg)

except Exception as e:
    send(f"❌ Error: {str(e)}")
