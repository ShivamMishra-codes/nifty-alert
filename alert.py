"""
LEGACY ORIGINAL (preserved exactly for reference)

import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TOTAL_CAPITAL = 100000  # change

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
"""

import math
import os

import pandas as pd
import requests
import yfinance as yf

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TOTAL_CAPITAL = 100000  # change
SYMBOL = "^NSEI"


def send(msg: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=20)


def safe_float(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def compute_rsi(close: pd.Series, period: int = 14) -> float:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, math.nan)
    rsi = 100 - (100 / (1 + rs))
    return safe_float(rsi.iloc[-1], 50.0)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


try:
    data = yf.download(SYMBOL, period="max", interval="1d", progress=False)

    if data is None or data.empty:
        send("⚠️ NIFTY data not available")
    else:
        close = data["Close"].dropna()
        high = data["High"].dropna() if "High" in data.columns else close
        low = data["Low"].dropna() if "Low" in data.columns else close

        n = len(close)
        latest = safe_float(close.iloc[-1])
        prev = safe_float(close.iloc[-2]) if n >= 2 else latest

        # ===== RETURNS =====
        d1 = ((latest / prev) - 1) * 100 if n >= 2 else 0.0
        d7 = ((latest / safe_float(close.iloc[-5])) - 1) * 100 if n >= 5 else 0.0
        d30 = ((latest / safe_float(close.iloc[-21])) - 1) * 100 if n >= 21 else 0.0
        d365 = ((latest / safe_float(close.iloc[-252])) - 1) * 100 if n >= 252 else ((latest / safe_float(close.iloc[0])) - 1) * 100

        # ===== DRAWDOWN =====
        peak_6m = safe_float(close.tail(126).max())
        drawdown_6m = ((latest - peak_6m) / peak_6m) * 100 if peak_6m else 0.0

        peak_ath = safe_float(close.max())
        drawdown_ath = ((latest - peak_ath) / peak_ath) * 100 if peak_ath else 0.0

        # ===== BASIC SIGNAL (preserved) =====
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

        # ===== SIMPLE FILTERS (kept controlled) =====
        ma50 = safe_float(close.tail(50).mean())
        ma200 = safe_float(close.tail(200).mean())
        rsi14 = compute_rsi(close, 14)

        if latest < ma50:
            trend = "⚠️ Downtrend"
            trend_factor = 0.70
        else:
            trend = "✅ Uptrend"
            trend_factor = 1.00

        if d1 <= -2:
            vol = "🔥 Panic"
            vol_factor = 1.10
        elif d1 <= -1:
            vol = "⚠️ Weak"
            vol_factor = 1.00
        else:
            vol = "😐 Stable"
            vol_factor = 0.92

        if rsi14 <= 30:
            rsi_state = "Oversold"
        elif rsi14 >= 70:
            rsi_state = "Overbought"
        else:
            rsi_state = "Neutral"

        if latest >= ma50 and ma50 >= ma200:
            regime = "Bull"
        elif latest < ma50 and ma50 < ma200:
            regime = "Bear"
        elif drawdown_6m <= -12:
            regime = "Correction"
        else:
            regime = "Mixed"

        # ===== VALUATION HOOK (optional via env var) =====
        # Set PE_PERCENTILE in environment to use valuation adjustment.
        valuation = "Unknown"
        valuation_cap = None
        try:
            pe_percentile = float(os.environ.get("PE_PERCENTILE", "nan"))
            if pe_percentile <= 25:
                valuation = "Cheap"
                valuation_cap = 0.45
            elif pe_percentile <= 75:
                valuation = "Fair"
                valuation_cap = 0.35
            else:
                valuation = "Expensive"
                valuation_cap = 0.25
        except Exception:
            pass

        # ===== ADVANCED ₹ =====
        # Keep the base ladder, then apply only a few controlled adjustments.
        adv_pct = base_pct
        adv_pct *= trend_factor
        adv_pct *= vol_factor

        # RSI is used as a small nudge, not a full multiplier stack.
        if rsi14 <= 30:
            adv_pct *= 1.05
        elif rsi14 >= 70:
            adv_pct *= 0.95

        # Valuation is a cap, not a compounding multiplier.
        if valuation_cap is not None:
            adv_pct = min(adv_pct, valuation_cap)

        # Final cap for sanity.
        adv_pct = clamp(adv_pct, 0.0, 0.65)

        adv_amount = int(TOTAL_CAPITAL * adv_pct)
        adv_1L = int(100000 * adv_pct)

        # ===== PRO DEPLOYMENT PLAN =====
        if adv_amount <= 0:
            stage1 = stage2 = stage3 = 0
        else:
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
Valuation: {valuation}

💰 Adjusted Invest: ₹{adv_amount} (₹{adv_1L} for ₹1L)

--- PRO DEPLOYMENT PLAN ---
Stage 1: ₹{stage1}
Stage 2: ₹{stage2}
Stage 3: ₹{stage3}
"""

        send(msg)

except Exception as e:
    try:
        send(f"❌ Error: {str(e)}")
    except Exception:
        pass
