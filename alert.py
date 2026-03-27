import yfinance as yf
import requests

BOT_TOKEN = "8721722831:AAFknrRbkNuR8vIJugsCwOJ6PurFT8slWeA"
CHAT_ID = "743218151"

data = yf.download("^NSEI", period="10d", interval="1d")
close = data['Close']

ret_7d = (close.iloc[-1] / close.iloc[-7]) - 1

if ret_7d < -0.02:
    msg = "🚨 NIFTY falling >2% (7d). Invest before 2 PM"
else:
    msg = "ℹ️ No major fall today"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
