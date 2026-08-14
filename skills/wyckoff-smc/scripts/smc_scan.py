#!/usr/bin/env python3
"""
smc_scan.py — Smart Money Concepts / Wyckoff structure scanner.

Fetches OHLCV data from Yahoo Finance, then:
  1. Detects swing highs/lows (fractal pivots)
  2. Labels market structure (HH / HL / LH / LL)
  3. Detects recent Break of Structure (BOS) and Change of Character (CHoCH)
  4. Detects bullish / bearish Order Blocks (last opposing candle before a
     strong displacement move that breaks structure)
  5. Detects Fair Value Gaps (3-candle imbalance)
  6. Prints a structure analysis + directional verdict
  7. Saves an annotated candlestick chart to
     C:/Users/iHC/AppData/Local/hermes/cache/images/{TICKER}_smc.png

Usage:
  python smc_scan.py MU
  python smc_scan.py AAPL --range 6mo --fractal 2 --disp 1.0 --json out.json
  python smc_scan.py BTC-USD --interval 1d

Dependencies: pandas, numpy, matplotlib (all present in the Hermes venv).
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle

IMAGE_DIR = r"C:/Users/iHC/AppData/Local/hermes/cache/images"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval={interval}"


# --------------------------------------------------------------------------
# Data fetching
# --------------------------------------------------------------------------

def fetch_ohlcv(ticker: str, rng: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Download daily OHLCV from the Yahoo Finance chart API.

    Skips rows with a None close (task requirement); forward-fills any other
    missing OHLC fields.
    """
    url = YAHOO_URL.format(ticker=ticker, rng=rng, interval=interval)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    result = payload["chart"]["result"]
    if not result:
        raise RuntimeError(f"No chart data returned for {ticker} (check ticker/range).")
    result = result[0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    rows = []
    for i, ts in enumerate(timestamps):
        close = quote["close"][i]
        if close is None:  # skip rows with missing close
            continue
        o = quote["open"][i]
        h = quote["high"][i]
        l = quote["low"][i]
        v = quote["volume"][i]
        rows.append({
            "date": datetime.fromtimestamp(ts, tz=timezone.utc).date(),
            "open": o if o is not None else close,
            "high": h if h is not None else close,
            "low": l if l is not None else close,
            "close": float(close),
            "volume": float(v) if v is not None else 0.0,
        })

    if len(rows) < 30:
        raise RuntimeError(f"Only {len(rows)} usable bars for {ticker} — need >= 30.")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    return df


def atr_series(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (Wilder-style rolling mean of true range)."""
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


# --------------------------------------------------------------------------
# Swing detection & structure labeling
# --------------------------------------------------------------------------

def find_swings(df: pd.DataFrame, k: int = 2):
    """Fractal-based swing detection.

    A swing high at bar i requires high[i] to be the maximum of the
    (2k+1)-bar window centered on i and strictly above its immediate
    neighbors. Mirror for swing lows. k=2 -> 5-bar fractal.
    """
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)
    sh, sl = [], []
    for i in range(k, n - k):
        if (
            highs[i] == max(highs[i - k:i + k + 1])
            and highs[i] > highs[i - 1]
            and highs[i] > highs[i + 1]
        ):
            sh.append(i)
        if (
            lows[i] == min(lows[i - k:i + k + 1])
            and lows[i] < lows[i - 1]
            and lows[i] < lows[i + 1]
        ):
            sl.append(i)
    return sh, sl


def build_pivots(df: pd.DataFrame, sh, sl):
    """Merge swing-high and swing-low indices into one alternating sequence.

    Consecutive pivots of the same type are collapsed to the more extreme one
    (higher high / lower low), preserving high-low alternation.
    """
    events = [(i, "H", float(df["high"].iloc[i])) for i in sh] + [
        (i, "L", float(df["low"].iloc[i])) for i in sl
    ]
    events.sort(key=lambda x: x[0])
    pivots = []
    for idx, typ, price in events:
        if pivots and pivots[-1][1] == typ:
            if typ == "H" and price > pivots[-1][2]:
                pivots[-1] = (idx, typ, price)
            elif typ == "L" and price < pivots[-1][2]:
                pivots[-1] = (idx, typ, price)
        else:
            pivots.append((idx, typ, price))
    return pivots


def label_structure(pivots):
    """Label each pivot HH / LH / HL / LL relative to the prior pivot of the
    same type. HH = higher high, LH = lower high, HL = higher low, LL = lower low.
    """
    labels = {}
    last_h = None
    last_l = None
    for idx, typ, price in pivots:
        if typ == "H":
            labels[idx] = "HH" if (last_h is None or price > last_h) else "LH"
            last_h = price
        else:
            labels[idx] = "HL" if (last_l is None or price > last_l) else "LL"
            last_l = price
    return labels


def determine_trend(labels: dict, pivots, last_n: int = 8) -> str:
    """Overall regime from the most recent structure labels.

    >= 2/3 of the last labels bullish (HH/HL) -> 'bull'
    >= 2/3 bearish (LH/LL)                      -> 'bear'
    otherwise                                   -> 'range'
    """
    recent = pivots[-last_n:]
    if len(recent) < 4:
        return "range"
    labs = [labels[i] for i, _, _ in recent]
    bull = sum(l in ("HH", "HL") for l in labs)
    bear = sum(l in ("LH", "LL") for l in labs)
    if bull >= max(2, len(labs) * 2 // 3):
        return "bull"
    if bear >= max(2, len(labs) * 2 // 3):
        return "bear"
    return "range"


# --------------------------------------------------------------------------
# BOS / CHoCH detection
# --------------------------------------------------------------------------

def detect_structure_events(df: pd.DataFrame, pivots):
    """Walk the series and record close-based breaks of structure.

    A close above the most recent confirmed swing high is a bullish break;
    a close below the most recent confirmed swing low is a bearish break.
    Each break is classified:
      - BOS   when it continues the current regime
      - CHoCH when it is the first break against the current regime
    Returns a list of dicts: {idx, type, dir, level, price}.
    """
    closes = df["close"].values
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)
    events = []
    trend = "range"
    piv_idx = 0
    last_sh = None  # (idx, price) most recent confirmed swing high
    last_sl = None  # (idx, price) most recent confirmed swing low

    for i in range(n):
        # Confirm pivots strictly before bar i
        while piv_idx < len(pivots) and pivots[piv_idx][0] < i:
            idx, typ, price = pivots[piv_idx]
            if typ == "H":
                last_sh = (idx, price)
            else:
                last_sl = (idx, price)
            piv_idx += 1
        if last_sh is None or last_sl is None:
            continue

        c = closes[i]
        if c > last_sh[1]:
            etype = "BOS" if trend == "bull" else "CHoCH"
            events.append({
                "idx": i, "type": etype, "dir": "bull",
                "level": last_sh[1], "price": c,
            })
            trend = "bull"
            last_sh = (i, highs[i])  # new reference level
        elif c < last_sl[1]:
            etype = "BOS" if trend == "bear" else "CHoCH"
            events.append({
                "idx": i, "type": etype, "dir": "bear",
                "level": last_sl[1], "price": c,
            })
            trend = "bear"
            last_sl = (i, lows[i])  # new reference level
    return events


# --------------------------------------------------------------------------
# Order Blocks
# --------------------------------------------------------------------------

def detect_order_blocks(df: pd.DataFrame, pivots, atr: pd.Series,
                        disp_mult: float = 1.0, lookahead: int = 3,
                        confirm: int = 5):
    """Detect order blocks.

    Bullish OB: the last bearish candle before a strong bullish displacement
    move that subsequently breaks a prior swing high (structure break).
    Zone = [low, open] of the OB candle (ICT open-to-low standard).

    Bearish OB: mirror image — last bullish candle before a strong bearish
    displacement move that breaks a prior swing low. Zone = [open, high].
    """
    opens = df["open"].values
    closes = df["close"].values
    highs = df["high"].values
    lows = df["low"].values
    atrs = atr.values
    n = len(df)
    bull_obs, bear_obs = [], []

    # Precompute the most recent confirmed swing high/low BEFORE each bar i
    # (structure breaks reference the last swing level, not the all-time extreme).
    last_sh = np.full(n, np.nan)
    last_sl = np.full(n, np.nan)
    sh_val = sl_val = np.nan
    pi = 0
    for i in range(n):
        while pi < len(pivots) and pivots[pi][0] < i:
            if pivots[pi][1] == "H":
                sh_val = pivots[pi][2]
            else:
                sl_val = pivots[pi][2]
            pi += 1
        last_sh[i] = sh_val
        last_sl[i] = sl_val

    for i in range(1, n - lookahead - confirm):
        atr_i = atrs[i]
        if atr_i is None or np.isnan(atr_i) or atr_i <= 0:
            continue
        body = closes[i] - opens[i]
        if body < 0:  # bearish candle -> candidate bullish OB
            # strong bullish displacement within lookahead bars
            if not any(
                closes[j] - opens[j] >= disp_mult * atr_i
                for j in range(i + 1, min(i + lookahead + 1, n))
            ):
                continue
            # break of the most recent swing high (structure break) shortly after
            level = last_sh[i]
            if np.isnan(level):
                continue
            if max(highs[i + 1:i + confirm + 1]) > level:
                bull_obs.append({
                    "idx": i, "zone": (float(lows[i]), float(opens[i])),
                    "disp": None, "level": float(level),
                })
        elif body > 0:  # bullish candle -> candidate bearish OB
            if not any(
                closes[j] - opens[j] <= -disp_mult * atr_i
                for j in range(i + 1, min(i + lookahead + 1, n))
            ):
                continue
            level = last_sl[i]
            if np.isnan(level):
                continue
            if min(lows[i + 1:i + confirm + 1]) < level:
                bear_obs.append({
                    "idx": i, "zone": (float(opens[i]), float(highs[i])),
                    "disp": None, "level": float(level),
                })

    # attach measured displacement (max move in the impulse window)
    for ob in bull_obs:
        i = ob["idx"]
        ob["disp"] = float(max(closes[i + 1:i + lookahead + 2]) - opens[i])
    for ob in bear_obs:
        i = ob["idx"]
        ob["disp"] = float(opens[i] - min(closes[i + 1:i + lookahead + 2]))

    # collapse near-duplicate consecutive OBs (keep the most recent)
    def dedupe(obs):
        out = []
        for ob in obs:
            if out and ob["idx"] - out[-1]["idx"] <= 2:
                out[-1] = ob
            else:
                out.append(ob)
        return out

    return dedupe(bull_obs), dedupe(bear_obs)


# --------------------------------------------------------------------------
# Fair Value Gaps
# --------------------------------------------------------------------------

def detect_fvg(df: pd.DataFrame):
    """3-candle imbalance detection.

    Bullish FVG: low[i+1] > high[i-1]  -> zone (high[i-1], low[i+1])
    Bearish FVG: high[i+1] < low[i-1]  -> zone (high[i+1], low[i-1])
    """
    highs = df["high"].values
    lows = df["low"].values
    n = len(df)
    bull, bear = [], []
    for i in range(1, n - 1):
        if lows[i + 1] > highs[i - 1]:
            bull.append({"idx": i, "zone": (float(highs[i - 1]), float(lows[i + 1]))})
        if highs[i + 1] < lows[i - 1]:
            bear.append({"idx": i, "zone": (float(highs[i + 1]), float(lows[i - 1]))})
    return bull, bear


def mark_mitigated(df: pd.DataFrame, fvgs, lookback: int = 60):
    """Mark an FVG 'mitigated' once any later bar trades back inside its zone."""
    lows = df["low"].values
    highs = df["high"].values
    n = len(df)
    for f in fvgs:
        lo, hi = f["zone"]
        f["mitigated"] = any(
            lows[j] <= hi and highs[j] >= lo for j in range(f["idx"] + 1, min(n, f["idx"] + lookback + 1))
        )
    return fvgs


# --------------------------------------------------------------------------
# Verdict
# --------------------------------------------------------------------------

def compose_verdict(trend: str, events, bull_obs, bear_obs, bull_fvg, bear_fvg,
                    last_close: float, lookback: int):
    """Combine signals into a directional bias with a confirmation count."""
    last_event = events[-1] if events else None

    reasons = []
    score = 0

    if trend == "bull":
        score += 1
        reasons.append("structure HH/HL (bullish regime)")
    elif trend == "bear":
        score -= 1
        reasons.append("structure LH/LL (bearish regime)")
    else:
        reasons.append("structure ranging (no clear regime)")

    if last_event is not None:
        ev = last_event
        if ev["dir"] == "bull":
            score += 1
            reasons.append(f"last break is bullish {ev['type']}")
        else:
            score -= 1
            reasons.append(f"last break is bearish {ev['type']}")

    # nearest unmitigated FVGs relative to last close
    near_bull_fvg = [f for f in bull_fvg if not f["mitigated"] and f["zone"][0] < last_close]
    near_bear_fvg = [f for f in bear_fvg if not f["mitigated"] and f["zone"][1] > last_close]
    if near_bull_fvg:
        score += 1
        reasons.append("unmitigated bullish FVG below price (demand)")
    if near_bear_fvg:
        score -= 1
        reasons.append("unmitigated bearish FVG above price (supply)")

    # order blocks near price (within ~8% for daily)
    near_bull_ob = [ob for ob in bull_obs if ob["zone"][0] < last_close <= ob["zone"][1] * 1.08]
    near_bear_ob = [ob for ob in bear_obs if ob["zone"][0] * 0.92 <= last_close < ob["zone"][1]]
    if near_bull_ob:
        score += 1
        reasons.append("bullish order block nearby below")
    if near_bear_ob:
        score -= 1
        reasons.append("bearish order block nearby above")

    if score >= 2:
        verdict = "BULLISH"
    elif score <= -2:
        verdict = "BEARISH"
    elif score == 1:
        verdict = "MILD BULLISH"
    elif score == -1:
        verdict = "MILD BEARISH"
    else:
        verdict = "NEUTRAL / RANGING"

    return verdict, score, reasons, last_event


# --------------------------------------------------------------------------
# Chart
# --------------------------------------------------------------------------

def plot_chart(df: pd.DataFrame, pivots, labels, events, bull_obs, bear_obs,
               bull_fvg, bear_fvg, ticker: str, out_path: str):
    n = len(df)
    x = np.arange(n)
    opens = df["open"].values
    closes = df["close"].values
    highs = df["high"].values
    lows = df["low"].values

    fig, ax = plt.subplots(figsize=(16, 9), dpi=110)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # candlesticks
    for i in range(n):
        color = "#26a69a" if closes[i] >= opens[i] else "#ef5350"
        ax.vlines(i, lows[i], highs[i], color=color, linewidth=0.8, zorder=2)
        lo, hi = min(opens[i], closes[i]), abs(closes[i] - opens[i]) or 1e-6
        ax.add_patch(Rectangle((i - 0.32, lo), 0.64, hi,
                               facecolor=color, edgecolor=color, linewidth=0.5, zorder=3))

    # order block zones
    for ob in bull_obs[-6:]:
        lo, hi = ob["zone"]
        ax.add_patch(Rectangle((ob["idx"] - 0.6, lo), 1.2, hi - lo,
                               facecolor="#26a69a", alpha=0.22, edgecolor="#26a69a",
                               linewidth=0.7, zorder=1))
    for ob in bear_obs[-6:]:
        lo, hi = ob["zone"]
        ax.add_patch(Rectangle((ob["idx"] - 0.6, lo), 1.2, hi - lo,
                               facecolor="#ef5350", alpha=0.22, edgecolor="#ef5350",
                               linewidth=0.7, zorder=1))

    # FVG zones (recent only to limit clutter)
    for f in bull_fvg[-4:]:
        lo, hi = f["zone"]
        ax.axhspan(lo, hi, xmin=max(0, (f["idx"] - 1.5)) / n, xmax=min(1, (f["idx"] + 1.5)) / n,
                   facecolor="#42a5f5", alpha=0.14, zorder=1)
    for f in bear_fvg[-4:]:
        lo, hi = f["zone"]
        ax.axhspan(lo, hi, xmin=max(0, (f["idx"] - 1.5)) / n, xmax=min(1, (f["idx"] + 1.5)) / n,
                   facecolor="#ffa726", alpha=0.14, zorder=1)

    # swing pivots + structure labels
    for idx, typ, price in pivots:
        if typ == "H":
            ax.plot(idx, price, marker="v", color="#ffd54f", markersize=7, zorder=5)
            lab = labels.get(idx, "")
            ax.annotate(lab, (idx, price), textcoords="offset points",
                        xytext=(0, 8), fontsize=7, color="#ffd54f",
                        ha="center", zorder=6)
        else:
            ax.plot(idx, price, marker="^", color="#4fc3f7", markersize=7, zorder=5)
            lab = labels.get(idx, "")
            ax.annotate(lab, (idx, price), textcoords="offset points",
                        xytext=(0, -14), fontsize=7, color="#4fc3f7",
                        ha="center", zorder=6)

    # BOS / CHoCH markers (recent)
    for ev in events[-6:]:
        style = "solid" if ev["type"] == "BOS" else "dashed"
        color = "#26a69a" if ev["dir"] == "bull" else "#ef5350"
        ax.axvline(ev["idx"], color=color, linestyle=style, linewidth=1.0, alpha=0.7, zorder=4)
        ax.annotate(ev["type"], (ev["idx"], ev["price"]), textcoords="offset points",
                    xytext=(4, 6), fontsize=8, color=color, fontweight="bold", zorder=6)

    # last close line
    ax.axhline(closes[-1], color="#e0e0e0", linewidth=0.8, linestyle=":", alpha=0.6)
    ax.annotate(f"last {closes[-1]:.2f}", (n - 1, closes[-1]), textcoords="offset points",
                xytext=(-80, 4), fontsize=8, color="#e0e0e0")

    # axes cosmetics
    ax.set_xlim(-2, n + 2)
    tick_step = max(1, n // 10)
    ax.set_xticks(x[::tick_step])
    ax.set_xticklabels([df.index[i].strftime("%Y-%m-%d") for i in range(0, n, tick_step)],
                       rotation=45, ha="right", fontsize=8, color="#c9d1d9")
    ax.tick_params(colors="#c9d1d9")
    for spine in ax.spines.values():
        spine.set_color("#30363d")
    ax.set_title(f"{ticker} — SMC/Wyckoff Structure Scan  ({df.index[0].date()} → {df.index[-1].date()})",
                 color="#e6edf3", fontsize=13, fontweight="bold")
    ax.set_ylabel("Price", color="#c9d1d9")

    handles = [
        mpatches.Patch(facecolor="#26a69a", alpha=0.3, label="Bullish OB"),
        mpatches.Patch(facecolor="#ef5350", alpha=0.3, label="Bearish OB"),
        mpatches.Patch(facecolor="#42a5f5", alpha=0.3, label="Bullish FVG"),
        mpatches.Patch(facecolor="#ffa726", alpha=0.3, label="Bearish FVG"),
        plt.Line2D([0], [0], marker="v", color="w", markerfacecolor="#ffd54f", label="Swing high (HH/LH)"),
        plt.Line2D([0], [0], marker="^", color="w", markerfacecolor="#4fc3f7", label="Swing low (HL/LL)"),
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8, facecolor="#0d1117",
              edgecolor="#30363d", labelcolor="#c9d1d9")

    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def fmt_zone(zone):
    return f"[{zone[0]:.2f} – {zone[1]:.2f}]"


def print_report(df, pivots, labels, trend, events, bull_obs, bear_obs,
                 bull_fvg, bear_fvg, verdict, score, reasons, ticker, lookback):
    last_close = float(df["close"].iloc[-1])
    print("=" * 72)
    print(f"=== SMC / WYCKOFF STRUCTURE SCAN: {ticker}")
    print(f"=== {df.index[0].date()} → {df.index[-1].date()}  |  bars: {len(df)}  |  last close: {last_close:.2f}")
    print("=" * 72)

    print(f"\n[1] MARKET STRUCTURE  regime: {trend.upper()}")
    seq = ", ".join(f"{labels[i]}@{df.index[i].strftime('%Y-%m-%d')}" for i, _, _ in pivots[-10:])
    print(f"    recent pivot labels: {seq}")
    print(f"    swings: {sum(1 for _, t, _ in pivots if t == 'H')} highs / "
          f"{sum(1 for _, t, _ in pivots if t == 'L')} lows")

    print(f"\n[2] STRUCTURAL BREAKS (BOS / CHoCH) — last {lookback} bars")
    recent = [e for e in events if e["idx"] >= len(df) - lookback]
    if recent:
        for e in recent[-5:]:
            d = df.index[e["idx"]].strftime("%Y-%m-%d")
            arrow = "▲" if e["dir"] == "bull" else "▼"
            print(f"    {d}  {e['type']:5s} {arrow}  close {e['price']:.2f} vs level {e['level']:.2f}")
    else:
        print("    none within lookback window")
    if events:
        e = events[-1]
        d = df.index[e["idx"]].strftime("%Y-%m-%d")
        print(f"    most recent overall: {e['type']} ({e['dir']}) on {d}")

    print(f"\n[3] ORDER BLOCKS")
    print("    bullish OBs (last opposing bearish candle + displacement + BOS):")
    for ob in bull_obs[-4:]:
        print(f"      {df.index[ob['idx']].strftime('%Y-%m-%d')}  zone {fmt_zone(ob['zone'])}  "
              f"disp {ob['disp']:.2f}  broke level {ob['level']:.2f}")
    if not bull_obs:
        print("      none detected")
    print("    bearish OBs (last opposing bullish candle + displacement + BOS):")
    for ob in bear_obs[-4:]:
        print(f"      {df.index[ob['idx']].strftime('%Y-%m-%d')}  zone {fmt_zone(ob['zone'])}  "
              f"disp {ob['disp']:.2f}  broke level {ob['level']:.2f}")
    if not bear_obs:
        print("      none detected")

    print(f"\n[4] FAIR VALUE GAPS (3-candle imbalance)")
    print("    bullish FVGs (recent, 'unmitigated' = price has NOT returned into the gap):")
    ubf = [f for f in bull_fvg if not f["mitigated"]]
    for f in bull_fvg[-4:]:
        m = "unmitigated" if not f["mitigated"] else "mitigated"
        print(f"      {df.index[f['idx']].strftime('%Y-%m-%d')}  zone {fmt_zone(f['zone'])}  [{m}]")
    if not bull_fvg:
        print("      none")
    print(f"    total: {len(bull_fvg)} | unmitigated: {len(ubf)}")
    print("    bearish FVGs (recent):")
    ubf2 = [f for f in bear_fvg if not f["mitigated"]]
    for f in bear_fvg[-4:]:
        m = "unmitigated" if not f["mitigated"] else "mitigated"
        print(f"      {df.index[f['idx']].strftime('%Y-%m-%d')}  zone {fmt_zone(f['zone'])}  [{m}]")
    if not bear_fvg:
        print("      none")
    print(f"    total: {len(bear_fvg)} | unmitigated: {len(ubf2)}")

    print(f"\n[5] VERDICT: {verdict}  (score {score:+d})")
    for r in reasons:
        print(f"    • {r}")

    # key levels
    supports = sorted(
        [f["zone"][0] for f in bull_fvg if not f["mitigated"] and f["zone"][0] < last_close] +
        [ob["zone"][0] for ob in bull_obs if ob["zone"][0] < last_close],
        reverse=True,
    )
    resistances = sorted(
        [f["zone"][1] for f in bear_fvg if not f["mitigated"] and f["zone"][1] > last_close] +
        [ob["zone"][1] for ob in bear_obs if ob["zone"][1] > last_close],
    )
    print("\n[6] KEY LEVELS")
    print(f"    nearest support:    {supports[0]:.2f}" if supports else "    nearest support:    n/a")
    print(f"    nearest resistance: {resistances[0]:.2f}" if resistances else "    nearest resistance: n/a")
    print("=" * 72)


def build_json(ticker, df, pivots, labels, trend, events, bull_obs, bear_obs,
               bull_fvg, bear_fvg, verdict, score):
    return {
        "ticker": ticker,
        "range_start": str(df.index[0].date()),
        "range_end": str(df.index[-1].date()),
        "bars": len(df),
        "last_close": float(df["close"].iloc[-1]),
        "regime": trend,
        "structure": [
            {"date": str(df.index[i].date()), "type": t, "price": round(p, 4), "label": labels.get(i)}
            for i, t, p in pivots
        ],
        "breaks": [
            {"date": str(df.index[e["idx"]].date()), "type": e["type"], "dir": e["dir"],
             "level": round(e["level"], 4), "close": round(e["price"], 4)}
            for e in events
        ],
        "order_blocks": {
            "bullish": [
                {"date": str(df.index[o["idx"]].date()), "zone_low": round(o["zone"][0], 4),
                 "zone_high": round(o["zone"][1], 4), "displacement": round(o["disp"], 4)}
                for o in bull_obs
            ],
            "bearish": [
                {"date": str(df.index[o["idx"]].date()), "zone_low": round(o["zone"][0], 4),
                 "zone_high": round(o["zone"][1], 4), "displacement": round(o["disp"], 4)}
                for o in bear_obs
            ],
        },
        "fvg": {
            "bullish": [
                {"date": str(df.index[f["idx"]].date()), "zone_low": round(f["zone"][0], 4),
                 "zone_high": round(f["zone"][1], 4), "mitigated": bool(f["mitigated"])}
                for f in bull_fvg
            ],
            "bearish": [
                {"date": str(df.index[f["idx"]].date()), "zone_low": round(f["zone"][0], 4),
                 "zone_high": round(f["zone"][1], 4), "mitigated": bool(f["mitigated"])}
                for f in bear_fvg
            ],
        },
        "verdict": verdict,
        "score": score,
    }


def main():
    ap = argparse.ArgumentParser(description="Smart Money Concepts / Wyckoff structure scanner")
    ap.add_argument("ticker", help="Yahoo Finance ticker, e.g. MU, AAPL, BTC-USD")
    ap.add_argument("--range", default="1y", help="data range (default 1y)")
    ap.add_argument("--interval", default="1d", help="bar interval (default 1d)")
    ap.add_argument("--fractal", type=int, default=2, help="fractal window k (default 2)")
    ap.add_argument("--atr", type=int, default=14, help="ATR period (default 14)")
    ap.add_argument("--disp", type=float, default=1.0, help="displacement multiple of ATR (default 1.0)")
    ap.add_argument("--lookback", type=int, default=30, help="recent bars for break reporting (default 30)")
    ap.add_argument("--json", default=None, help="optional path to write a JSON report")
    ap.add_argument("--no-chart", action="store_true", help="skip chart rendering")
    args = ap.parse_args()

    ticker = args.ticker.upper()
    try:
        df = fetch_ohlcv(ticker, args.range, args.interval)
    except Exception as exc:
        print(f"ERROR fetching {ticker}: {exc}")
        sys.exit(1)

    atr = atr_series(df, args.atr)

    sh, sl = find_swings(df, k=args.fractal)
    pivots = build_pivots(df, sh, sl)
    labels = label_structure(pivots)
    trend = determine_trend(labels, pivots)
    events = detect_structure_events(df, pivots)
    bull_obs, bear_obs = detect_order_blocks(df, pivots, atr, disp_mult=args.disp)
    bull_fvg = mark_mitigated(df, detect_fvg(df)[0])
    bear_fvg = mark_mitigated(df, detect_fvg(df)[1])

    last_close = float(df["close"].iloc[-1])
    verdict, score, reasons, _ = compose_verdict(
        trend, events, bull_obs, bear_obs, bull_fvg, bear_fvg, last_close, args.lookback
    )

    print_report(df, pivots, labels, trend, events, bull_obs, bear_obs,
                 bull_fvg, bear_fvg, verdict, score, reasons, ticker, args.lookback)

    if args.json:
        report = build_json(ticker, df, pivots, labels, trend, events, bull_obs,
                            bear_obs, bull_fvg, bear_fvg, verdict, score)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        print(f"JSON report written to {args.json}")

    if not args.no_chart:
        out_path = os.path.join(IMAGE_DIR, f"{ticker}_smc.png")
        try:
            plot_chart(df, pivots, labels, events, bull_obs, bear_obs,
                       bull_fvg, bear_fvg, ticker, out_path)
            print(f"Chart saved to {out_path}")
        except Exception as exc:
            print(f"WARNING chart failed: {exc}")


if __name__ == "__main__":
    main()
