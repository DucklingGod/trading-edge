#!/usr/bin/env python3
"""
Ichimoku Kinko Hyo (Ichimoku Cloud) analysis.

Fetches daily OHLCV for a ticker from Yahoo Finance (via Python urllib with a
browser User-Agent — curl fails on this host for foreign hosts), computes the
five Ichimoku components, evaluates cloud status / TK cross / kumo twist /
chikou confirmation, prints a compact analysis table + verdict, and saves a
matplotlib chart (candles + shaded kumo + spans) to
C:/Users/iHC/AppData/Local/hermes/cache/images/{TICKER}_ichimoku.png

Usage:
    python ichimoku.py MU
    python ichimoku.py MU --range 6mo
    python ichimoku.py MU --no-chart
"""

import argparse
import gzip
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TENKAN_N = 9              # conversion line window
KIJUN_N = 26              # base line window
SPANB_N = 52              # leading span B window
DISPLACEMENT = 26         # periods Senkou spans are plotted ahead / Chikou back
CROSS_LOOKBACK = 5        # periods to look back for a "fresh" TK cross
TWIST_LOOKBACK = 5        # periods to look back for an impending kumo twist
CHART_DIR = r"C:/Users/iHC/AppData/Local/hermes/cache/images"

YAHOO_URLS = [
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval=1d",
    "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval=1d",
]
UA = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "identity"}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def fetch_ohlcv(ticker, rng="1y"):
    """Fetch daily OHLCV from the Yahoo Finance chart API.

    Returns a DataFrame indexed by tz-aware date with open/high/low/close/volume.
    Rows with a null close are dropped; stray nulls are forward-filled.
    """
    last_err = None
    for url_tpl in YAHOO_URLS:
        url = url_tpl.format(ticker=ticker, rng=rng)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
            if raw[:2] == b"\x1f\x8b":  # server sent gzip despite identity
                raw = gzip.decompress(raw)
            payload = json.loads(raw.decode("utf-8", errors="replace"))
            result = payload["chart"]["result"][0]
            ts = result["timestamp"]
            q = result["indicators"]["quote"][0]
            dates = [datetime.fromtimestamp(t, tz=timezone.utc) for t in ts]
            df = pd.DataFrame(
                {
                    "open": q["open"],
                    "high": q["high"],
                    "low": q["low"],
                    "close": q["close"],
                    "volume": q["volume"],
                },
                index=pd.DatetimeIndex(dates, name="date"),
            )
            df = df.dropna(subset=["close"])             # skip null closes
            df = df[~df.index.duplicated(keep="last")]   # de-dup dates
            df = df.ffill()                              # patch stray nulls
            df["volume"] = df["volume"].fillna(0.0)
            if len(df) < SPANB_N + DISPLACEMENT:
                raise ValueError(
                    f"only {len(df)} rows — need >= {SPANB_N + DISPLACEMENT} "
                    "for a complete Ichimoku (52-period Span B + 26 displacement)"
                )
            return df
        except Exception as exc:  # noqa: BLE001 — try next host, keep last error
            last_err = exc
    raise RuntimeError(f"failed to fetch {ticker}: {last_err}")


# ---------------------------------------------------------------------------
# Ichimoku math
# ---------------------------------------------------------------------------
def midpoint(df, n):
    """Midpoint of the highest high and lowest low over the last n periods."""
    return (df["high"].rolling(n, min_periods=n).max()
            + df["low"].rolling(n, min_periods=n).min()) / 2.0


def compute_ichimoku(df):
    """Compute all five Ichimoku components (aligned to the source index)."""
    tenkan = midpoint(df, TENKAN_N)                                  # Midpoint(9)
    kijun = midpoint(df, KIJUN_N)                                    # Midpoint(26)
    span_a_raw = (tenkan + kijun) / 2.0                              # (T+K)/2
    span_b_raw = midpoint(df, SPANB_N)                               # Midpoint(52)
    span_a = span_a_raw.shift(DISPLACEMENT)   # plotted 26 periods AHEAD
    span_b = span_b_raw.shift(DISPLACEMENT)   # plotted 26 periods AHEAD
    chikou = df["close"].shift(DISPLACEMENT)  # close plotted 26 periods BACK
    return pd.DataFrame(
        {
            "tenkan": tenkan,
            "kijun": kijun,
            "span_a_raw": span_a_raw,
            "span_b_raw": span_b_raw,
            "span_a": span_a,
            "span_b": span_b,
            "chikou": chikou,
        },
        index=df.index,
    )


def last_cross(series):
    """Most recent sign change of `series`, scanning backward from the end.

    Returns (direction, index) where direction is 'BULLISH' (series turned
    positive) or 'BEARISH' (series turned negative), or None if no change.
    """
    n = len(series)
    prev = None
    for i in range(n - 1, -1, -1):
        v = series.iloc[i]
        if pd.isna(v) or v == 0.0:
            continue
        if prev is not None and (prev > 0) != (v > 0):
            direction = "BULLISH" if v > 0 else "BEARISH"
            return direction, series.index[i]
        prev = v
    return None


def kumo_twist_status(ind):
    """Detect a kumo twist from the RAW (unshifted) spans.

    A twist (Span A / Span B exchange) happens in the raw series and shows up
    in the projected cloud ~26 sessions later. Returns:
      ('IMPENDING', dir)  -> cross within the last TWIST_LOOKBACK bars; the
                             twist is forming in the cloud ~26 sessions ahead
      ('IN_CLOUD', dir)   -> cross that sits at the current cloud (26 bars ago)
      None                -> no recent twist
    """
    raw_diff = ind["span_a_raw"] - ind["span_b_raw"]
    cross = last_cross(raw_diff)
    if cross is None:
        return None
    direction, idx = cross
    pos = raw_diff.index.get_loc(idx)
    days_ago = len(raw_diff) - 1 - pos
    if days_ago <= TWIST_LOOKBACK:
        return ("IMPENDING", direction)
    if abs(days_ago - DISPLACEMENT) <= 2:
        return ("IN_CLOUD", direction)
    return None


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def analyze(df, ind):
    """Evaluate cloud status, signals and composite verdict. Returns a dict."""
    close = df["close"]
    i = len(df) - 1
    last_close = float(close.iloc[-1])
    last_date = df.index[-1].strftime("%Y-%m-%d")

    tenkan = float(ind["tenkan"].iloc[-1])
    kijun = float(ind["kijun"].iloc[-1])
    sa = float(ind["span_a"].iloc[-1])
    sb = float(ind["span_b"].iloc[-1])
    chikou_last = float(ind["chikou"].iloc[-1])  # == close 26 sessions ago

    # --- cloud position -----------------------------------------------------
    if math.isnan(sa) or math.isnan(sb):
        cloud_pos, pct_off = "N/A", float("nan")
    else:
        if last_close > max(sa, sb):
            cloud_pos, pct_off = "ABOVE", (last_close - max(sa, sb)) / max(sa, sb) * 100.0
        elif last_close < min(sa, sb):
            cloud_pos, pct_off = "BELOW", (last_close - min(sa, sb)) / min(sa, sb) * 100.0
        else:
            cloud_pos, pct_off = "INSIDE", 0.0

    cloud_bull = (not math.isnan(sa) and not math.isnan(sb)) and sa >= sb
    thickness = abs(sa - sb) if not (math.isnan(sa) or math.isnan(sb)) else float("nan")
    hist_thick = (ind["span_a"] - ind["span_b"]).abs().dropna().tail(20)
    avg_thick = float(hist_thick.mean()) if len(hist_thick) else float("nan")

    # --- slopes over last 5 sessions ----------------------------------------
    def slope(s, k=5):
        s = s.dropna()
        if len(s) < k + 1:
            return float("nan")
        return float(s.iloc[-1] - s.iloc[-1 - k])

    tenkan_slope = slope(ind["tenkan"])
    kijun_slope = slope(ind["kijun"])
    span_a_slope = slope(ind["span_a"])
    span_b_slope = slope(ind["span_b"])

    # --- TK cross -----------------------------------------------------------
    diff = ind["tenkan"] - ind["kijun"]
    tk = None
    cross = last_cross(diff)
    if cross is not None:
        direction, cidx = cross
        days_ago = i - diff.index.get_loc(cidx)
        tk = {
            "direction": direction,
            "days_ago": int(days_ago),
            "fresh": int(days_ago) <= CROSS_LOOKBACK,
        }

    # --- chikou confirmation (last plotted point vs price 26 bars ago) ------
    chikou_above = last_close > chikou_last

    # --- kumo twist ---------------------------------------------------------
    twist = kumo_twist_status(ind)

    # --- key levels ---------------------------------------------------------
    cloud_top = max(sa, sb) if not (math.isnan(sa) or math.isnan(sb)) else float("nan")
    cloud_bottom = min(sa, sb) if not (math.isnan(sa) or math.isnan(sb)) else float("nan")
    # projected cloud for the next ~26 sessions starts at the raw spans
    future_a = float(ind["span_a_raw"].iloc[-1])
    future_b = float(ind["span_b_raw"].iloc[-1])

    # --- composite verdict --------------------------------------------------
    score = 0
    if cloud_pos == "ABOVE":
        score += 2
    elif cloud_pos == "BELOW":
        score -= 2
    score += 1 if tenkan > kijun else -1
    score += 1 if cloud_bull else -1
    score += 1 if chikou_above else -1
    if tk is not None and tk["fresh"]:
        score += 2 if tk["direction"] == "BULLISH" else -2

    if score >= 6:
        verdict = "STRONG BULLISH"
    elif score >= 3:
        verdict = "BULLISH"
    elif score >= 1:
        verdict = "MILD BULLISH"
    elif score <= -6:
        verdict = "STRONG BEARISH"
    elif score <= -3:
        verdict = "BEARISH"
    elif score <= -1:
        verdict = "MILD BEARISH"
    else:
        verdict = "NEUTRAL / CHOP"

    return {
        "ticker": None, "last_close": last_close, "last_date": last_date,
        "tenkan": tenkan, "kijun": kijun, "span_a": sa, "span_b": sb,
        "chikou": chikou_last,
        "tenkan_slope": tenkan_slope, "kijun_slope": kijun_slope,
        "span_a_slope": span_a_slope, "span_b_slope": span_b_slope,
        "cloud_pos": cloud_pos, "pct_off": pct_off, "cloud_bull": cloud_bull,
        "thickness": thickness, "avg_thick": avg_thick,
        "tk": tk, "chikou_above": chikou_above, "twist": twist,
        "cloud_top": cloud_top, "cloud_bottom": cloud_bottom,
        "future_cloud_lo": min(future_a, future_b),
        "future_cloud_hi": max(future_a, future_b),
        "score": score, "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def fmt_price(v, nd=2):
    return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"${v:,.{nd}f}"


def print_table(df, ind, r, ticker):
    bar = "=" * 62
    thin = "-" * 62
    print(bar)
    print(f" ICHIMOKU KINKO HYO — {ticker}   (daily · {len(df)} bars)")
    print(bar)
    print(f" Last close : {fmt_price(r['last_close'])}   ({r['last_date']})")
    print(thin)
    print(f" {'Component':<22}{'Value':>12}{'Slope(5d)':>12}   Role")
    print(f" {'Tenkan-sen (9)':<22}{fmt_price(r['tenkan']):>12}"
          f"{r['tenkan_slope']:>+12.2f}   signal line")
    print(f" {'Kijun-sen (26)':<22}{fmt_price(r['kijun']):>12}"
          f"{r['kijun_slope']:>+12.2f}   base / confirmation")
    print(f" {'Senkou Span A':<22}{fmt_price(r['span_a']):>12}"
          f"{r['span_a_slope']:>+12.2f}   cloud edge (fast, +26)")
    print(f" {'Senkou Span B':<22}{fmt_price(r['span_b']):>12}"
          f"{r['span_b_slope']:>+12.2f}   cloud edge (slow, +26)")
    print(f" {'Chikou Span':<22}{fmt_price(r['chikou']):>12}{'':>12}   close 26 bars ago")
    print(thin)
    print(" Cloud analysis")
    pos_note = {
        "ABOVE": f"price is {r['pct_off']:+.2f}% above cloud top — bullish regime",
        "BELOW": f"price is {r['pct_off']:+.2f}% below cloud bottom — bearish regime",
        "INSIDE": "price inside cloud — chop / transition",
        "N/A": "insufficient data",
    }[r["cloud_pos"]]
    print(f"   Position vs cloud : {r['cloud_pos']:<7} {pos_note}")
    print(f"   Cloud color / bias: {'BULLISH (Span A >= Span B)' if r['cloud_bull'] else 'BEARISH (Span A < Span B)'}")
    thick_tag = "thick" if (not math.isnan(r["thickness"]) and r["thickness"] >= r["avg_thick"]) else "thin"
    print(f"   Cloud thickness   : {fmt_price(r['thickness'])}   (20d avg {fmt_price(r['avg_thick'])}) → {thick_tag}")
    print(thin)
    print(" Signals")
    if r["tk"]:
        age = "FRESH" if r["tk"]["fresh"] else f"{r['tk']['days_ago']}d old"
        loc = "" if r["cloud_pos"] == "INSIDE" else f" — {'above' if r['cloud_pos'] == 'ABOVE' else 'below'} cloud"
        print(f"   TK cross          : {r['tk']['direction']} ({age}){loc}")
    else:
        print("   TK cross          : none")
    if r["twist"]:
        state, direction = r["twist"]
        print(f"   Kumo twist        : {state} — {direction} (Span A/B exchange)")
    else:
        print("   Kumo twist        : none in the near window")
    print(f"   Chikou vs price   : {'ABOVE price → bullish confirmation' if r['chikou_above'] else 'BELOW price → bearish confirmation'}")
    print(thin)
    print(" Key levels")
    print(f"   Cloud top/bottom  : {fmt_price(r['cloud_top'])} / {fmt_price(r['cloud_bottom'])}")
    print(f"   Kijun-sen (dyn S/R): {fmt_price(r['kijun'])}")
    print(f"   Projected cloud   : {fmt_price(r['future_cloud_lo'])} – {fmt_price(r['future_cloud_hi'])} (next ~26 sessions)")
    print(thin)
    print(f" VERDICT: {r['verdict']}   (composite score {r['score']:+d}/7)")
    print(bar)


# ---------------------------------------------------------------------------
# Chart
# ---------------------------------------------------------------------------
def plot_chart(df, ind, ticker, out_path, verdict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    n = len(df)
    x = np.arange(n)
    dates = df.index

    fig, (ax, axv) = plt.subplots(
        2, 1, figsize=(15, 9), sharex=True,
        gridspec_kw={"height_ratios": [3.2, 1.0]},
    )
    fig.patch.set_facecolor("#111111")
    for a in (ax, axv):
        a.set_facecolor("#111111")
        a.grid(alpha=0.15)

    up = (df["close"] >= df["open"]).to_numpy()
    colors = np.where(up, "#26a69a", "#ef5350")
    for i in range(n):
        o, h, l, c = df["open"].iloc[i], df["high"].iloc[i], df["low"].iloc[i], df["close"].iloc[i]
        ax.vlines(i, l, h, color=colors[i], linewidth=0.8)
        body_lo, body_hi = min(o, c), max(o, c)
        if body_hi - body_lo < 1e-9:
            ax.plot([i], [o], marker="_", color=colors[i])
        else:
            ax.add_patch(Rectangle((i - 0.35, body_lo), 0.7, body_hi - body_lo,
                                   facecolor=colors[i], edgecolor=colors[i], linewidth=0.5))

    sa = ind["span_a"].to_numpy()
    sb = ind["span_b"].to_numpy()
    ax.fill_between(x, sa, sb, where=sa >= sb, color="#26a69a", alpha=0.25,
                    interpolate=True, label="Kumo (bullish)")
    ax.fill_between(x, sa, sb, where=sa < sb, color="#ef5350", alpha=0.25,
                    interpolate=True, label="Kumo (bearish)")

    ax.plot(x, ind["tenkan"].to_numpy(), color="#42a5f5", lw=1.3, label="Tenkan-sen (9)")
    ax.plot(x, ind["kijun"].to_numpy(), color="#ef5350", lw=1.3, label="Kijun-sen (26)")
    ax.plot(x, ind["span_a"].to_numpy(), color="#66bb6a", lw=1.0, label="Senkou Span A")
    ax.plot(x, ind["span_b"].to_numpy(), color="#ab47bc", lw=1.0, label="Senkou Span B")
    ax.plot(x, ind["chikou"].to_numpy(), color="#ffca28", lw=1.0, ls=":",
            label="Chikou Span (lag 26)")

    ax.axhline(float(df["close"].iloc[-1]), color="#ffffff", lw=0.8, ls="--", alpha=0.6)
    ax.set_title(f"{ticker} — Ichimoku Kinko Hyo (daily)  ·  Verdict: {verdict}",
                 color="#eeeeee", fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9, facecolor="#222222", edgecolor="#444444",
              labelcolor="#eeeeee")
    ax.set_ylabel("Price", color="#bbbbbb")

    axv.bar(x, df["volume"].to_numpy(), color=colors, alpha=0.6, width=0.7)
    axv.set_ylabel("Volume", color="#bbbbbb")

    step = max(1, n // 8)
    ticks = list(range(0, n, step))
    ax.set_xticks(ticks)
    ax.set_xticklabels([dates[i].strftime("%Y-%m-%d") for i in ticks], color="#bbbbbb")
    for lab in ax.get_yticklabels() + axv.get_yticklabels():
        lab.set_color("#bbbbbb")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Ichimoku Kinko Hyo analysis (Yahoo Finance daily data)")
    ap.add_argument("ticker", help="ticker symbol, e.g. MU, AAPL, BTC-USD")
    ap.add_argument("--range", default="1y", choices=["3mo", "6mo", "1y", "2y"],
                    help="history range (default: 1y)")
    ap.add_argument("--no-chart", action="store_true", help="skip saving the chart")
    args = ap.parse_args()

    ticker = args.ticker.upper()
    df = fetch_ohlcv(ticker, args.range)
    ind = compute_ichimoku(df)
    r = analyze(df, ind)
    r["ticker"] = ticker
    print_table(df, ind, r, ticker)

    if not args.no_chart:
        os.makedirs(CHART_DIR, exist_ok=True)
        out = os.path.join(CHART_DIR, f"{ticker}_ichimoku.png")
        plot_chart(df, ind, ticker, out, r["verdict"])
        print(f"Chart saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
