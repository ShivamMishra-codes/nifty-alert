# -*- coding: utf-8 -*-

import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TOTAL_CAPITAL = 500000

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def clamp(x, low, high):
    return max(low, min(x, high))

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ===== NSE PE FETCH =====
def get_nifty_pe():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        headers = {"User-Agent": "Mozilla/5.0"}

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)

        response = session.get(url, headers=headers)
        data = response.json()

        return float(data["data"][0]["pe"])
    except:
        return None

# ===== PE → PERCENTILE =====
def pe_to_percentile(pe):
    if pe is None:
        return None
    if pe < 18:
        return 20
    elif pe < 21:
        return 40
    elif pe < 24:
        return 60
    elif pe < 27:
        return 80
    else:
        return 95

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
        d365 = ((latest / float(close.iloc[-252])) - 1) * 100 if n >= 252 else 0

        # ===== DRAWDOWN =====
        peak_6m = float(close.tail(126).max())
        drawdown_6m = ((latest - peak_6m) / peak_6m) * 100

        peak_ath = float(close.max())
        drawdown_ath = ((latest - peak_ath) / peak_ath) * 100

        # ===== SIGNAL =====
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

        basic_amount = int(TOTAL_CAPITAL * base_pct)
        basic_1L = int(100000 * base_pct)

        # ===== TREND =====
        ma50 = float(close.tail(50).mean())
        if latest < ma50:
            trend = "⚠️ Downtrend"
            trend_factor = 0.75
        else:
            trend = "✅ Uptrend"
            trend_factor = 1.0

        # ===== VOLATILITY =====
        if d1 <= -2:
            vol = "🔥 Panic"
            vol_factor = 1.05
        elif d1 <= -1:
            vol = "⚠️ Weak"
            vol_factor = 1.0
        else:
            vol = "😐 Stable"
            vol_factor = 0.95

        # ===== RSI =====
        rsi14 = float(compute_rsi(close).iloc[-1])

        if rsi14 < 30:
            rsi_state = "Oversold 🟢"
        elif rsi14 < 40:
            rsi_state = "Weak ⚠️"
        elif rsi14 <= 60:
            rsi_state = "Neutral 😐"
        elif rsi14 <= 70:
            rsi_state = "Strong 📈"
        else:
            rsi_state = "Overbought 🔴"

        # ===== REGIME =====
        regime = "🐻 Bear" if d365 < 0 else "🐂 Bull"

        # ===== VALUATION (DYNAMIC) =====
        pe = get_nifty_pe()
        pe_percentile = pe_to_percentile(pe)

        valuation = "😐 Fair (Fallback)"
        valuation_cap = None

        if pe_percentile is not None:
            if pe_percentile <= 25:
                valuation = "🟢 Cheap"
                valuation_cap = 0.45
            elif pe_percentile <= 60:
                valuation = "😐 Fair"
                valuation_cap = 0.35
            elif pe_percentile <= 85:
                valuation = "⚠️ Slightly Expensive"
                valuation_cap = 0.30
            else:
                valuation = "🔴 Expensive"
                valuation_cap = 0.25

        # ===== ADVANCED =====
        adv_pct = base_pct * trend_factor * vol_factor

        if rsi14 <= 30:
            adv_pct *= 1.05
        elif rsi14 >= 70:
            adv_pct *= 0.95

        if regime.startswith("🐻") and drawdown_6m < -10:
            adv_pct *= 0.8

        if valuation_cap is not None:
            adv_pct = min(adv_pct, valuation_cap)

        adv_pct = clamp(adv_pct, 0.0, 0.65)

        adv_amount = int(TOTAL_CAPITAL * adv_pct)
        adv_1L = int(100000 * adv_pct)

        # ===== TRANCHE =====
        stage1 = int(adv_amount * 0.40)
        stage2 = int(adv_amount * 0.35)
        stage3 = int(adv_amount * 0.25)

        # ===== MESSAGE =====
        msg = f"""📊 NIFTY: {round(latest, 2)}

--- BASIC VIEW ---
1D: {round(d1, 2)}%
7D: {round(d7, 2)}%
1M: {round(d30, 2)}%
1Y: {round(d365, 2)}%

Drawdown (6M): {round(drawdown_6m, 2)}%
Drawdown (ATH): {round(drawdown_ath, 2)}%

Signal: {signal}
💰 Invest Today: ₹{basic_amount} (₹{basic_1L} for ₹1L)

--- ADVANCED VIEW ---
Trend: {trend}
Volatility: {vol}
Regime: {regime}
RSI(14): {round(rsi14, 1)} ({rsi_state})
Valuation: {valuation} (PE: {round(pe,1) if pe else 'N/A'})

💰 Adjusted Invest: ₹{adv_amount} (₹{adv_1L} for ₹1L)

--- PRO DEPLOYMENT PLAN ---
Stage 1: ₹{stage1}
Stage 2: ₹{stage2}
Stage 3: ₹{stage3}
"""

        send(msg)

except Exception as e:
    send(f"❌ Error: {str(e)}")
