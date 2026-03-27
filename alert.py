import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
r = requests.post(url, data={"chat_id": CHAT_ID, "text": "🔥 FINAL TEST MESSAGE"})
print(r.text)
