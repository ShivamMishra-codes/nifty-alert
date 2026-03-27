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

        if n >= 252:
            d365 = ((latest / float(close.iloc[-252])) - 1) * 100
        else:
            d365 = ((latest / float(close.iloc[0])) - 1) * 100

        # ===== DRAWDOWN =====
        peak_6m = float(close.tail(126).max())
        drawdown_6m = ((latest - peak_6m) / peak_6m) * 100

        peak_ath = float(close.max())
        drawdown_ath = ((latest - peak_ath) / peak_ath) * 100

        # ===== BASIC SIGNAL =====
        if drawdown_ath <= -20 or drawdown_6m <= -15:
            signal = "🔴 CRASH"
            base_pct = 0.60
        elif drawdown_6m <= -12:
            signal = "🟠 DEEP CORRECTION (High)"
            base_pct = 0.30
        elif drawdown_6m <= -8:
            signal = "🟡 CORRECTION"
            base_pct = 0.25
        elif drawdown_6m <= -5:
            signal = "🟢 SMALL DIP"
            base_pct = 0.15
        else:
            signal = "⚪ NORMAL"
            base_pct = 0.0

        # ===== BASIC ₹ =====
        basic_amount = int(TOTAL_CAPITAL * base_pct)
        basic_1L = int(100000 * base_pct)

        # ===== ADVANCED FILTERS =====
        ma50 = float(close.tail(50).mean())

        if latest < ma50:
            trend = "⚠️ Downtrend"
            trend_factor = 0.7
        else:
            trend = "✅ Uptrend"
            trend_factor = 1.0

        if d1 <= -2:
            vol = "🔥 Panic"
            vol_factor = 1.2
        elif d1 <= -1:
            vol = "⚠️ Weak"
            vol_factor = 1.0
        else:
            vol = "😐 Stable"
            vol_factor = 0.9

        # ===== ADVANCED ₹ =====
        adv_pct = base_pct * trend_factor * vol_factor
        adv_pct = min(adv_pct, 0.65)

        adv_amount = int(TOTAL_CAPITAL * adv_pct)
        adv_1L = int(100000 * adv_pct)

        # ===== MESSAGE =====
        msg = f"""📊 NIFTY: {round(latest,2)}

--- BASIC VIEW ---
1D: {round(d1,2)}%
7D: {round(d7,2)}%
1M: {round(d30,2)}%
1Y: {round(d365,2)}%

Drawdown (6M): {round(drawdown_6m,2)}%
Drawdown (ATH): {round(drawdown_ath,2)}%

Signal: {signal}
💰 Invest Today: ₹{basic_amount} (₹{basic_1L} for ₹1L)

--- ADVANCED VIEW ---
Trend: {trend}
Volatility: {vol}

💰 Adjusted Invest: ₹{adv_amount} (₹{adv_1L} for ₹1L)
"""

        send(msg)

except Exception as e:
    send(f"❌ Error: {str(e)}")
