import yfinance as yf
import requests

BOT_TOKEN = "8721722831:AAFknrRbkNuR8vIJugsCwOJ6PurFT8slWeA"
CHAT_ID = "743218151"

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

try:
    data = yf.download("^NSEI", period="10d", interval="1d")

    if data.empty or len(data) < 7:
        send("⚠️ Data not available")
    else:
        close = data['Close']

        ret_7d = float((close.iloc[-1] / close.iloc[-7]) - 1)

        if ret_7d < -0.02:
            send("🚨 NIFTY falling >2% (7d). Invest before 2 PM")
        else:
            send("ℹ️ No major fall today")

except Exception as e:
    send(f"❌ Error: {str(e)}")
