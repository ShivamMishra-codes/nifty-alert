import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TOTAL_CAPITAL = 500000  # change

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

try:
    data = yf.download("^NSEI", period="max", interval="1d")

    if data is None or data.empty:
        send("⚠️ NIFTY data not available")
    else:
        close = data['Close']
        n = len(close)

        latest = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if n >= 2 else latest

        # ===== RETURNS =====
        d1 = ((latest / prev) - 1) * 100
        d7 = ((latest / float(close.iloc[-5])) - 1) * 100 if n >= 5 else 0
        d30 = ((latest / float(close.iloc[-21])) - 1) * 100 if n >= 21 else 0

        # ===== DRAWDOWN =====
        peak_6m = float(close.tail(126).max())
        drawdown_6m = ((latest - peak_6m) / peak_6m) * 100

        peak_ath = float(close.max())
        drawdown_ath = ((latest - peak_ath) / peak_ath) * 100

        # ===== SIGNAL =====
        if drawdown_ath <= -20 or drawdown_6m <= -15:
            signal = "🔴 CRASH"
            invest_pct = 0.60
        elif drawdown_6m <= -10:
            signal = "🟠 DEEP CORRECTION"
            invest_pct = 0.40
        elif drawdown_6m <= -5:
            signal = "🟡 CORRECTION"
            invest_pct = 0.25
        else:
            signal = "⚪ NORMAL"
            invest_pct = 0.0

        # ===== ₹ CALC =====
        invest_amount = int(TOTAL_CAPITAL * invest_pct)
        invest_1L = int(100000 * invest_pct)

        # Momentum tweak
        if d1 < -2 and invest_pct > 0:
            invest_amount = int(invest_amount * 1.2)
            invest_1L = int(invest_1L * 1.2)

        # ===== MESSAGE =====
        msg = f"""📊 NIFTY: {round(latest,2)}

1D: {round(d1,2)}%
7D: {round(d7,2)}%
1M: {round(d30,2)}%

Drawdown (6M): {round(drawdown_6m,2)}%
Drawdown (ATH): {round(drawdown_ath,2)}%

Signal: {signal}

💰 Invest Today: ₹{invest_amount} (₹{invest_1L} for ₹1L capital)
"""

        send(msg)

except Exception as e:
    send(f"❌ Error: {str(e)}")
