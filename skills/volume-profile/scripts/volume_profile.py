#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
volume_profile.py — Volume Profile (VPVR) analysis for a single ticker.

Fetches ~1 year of daily OHLCV from Yahoo Finance and builds a Volume Profile:

  * price bins with each day's volume allocated proportionally to the
    overlap of the day's high-low range with each bin
  * Point of Control (POC) — the price bin with the most volume
  * Value Area (VAH / VAL) — the tightest range around the POC containing
    the target fraction (default 70%) of total volume
  * High Volume Nodes (HVN) / Low Volume Nodes (LVN) / liquidity gaps
  * current price context vs POC, value area, and nearest HVN/LVN
  * a matplotlib chart: price line (left) + horizontal volume histogram
    (right) saved as PNG

Order-flow functions (delta, cumulative delta, footprint imbalance) are
included as documented reference implementations, but they REQUIRE bid/ask
or tick-level data that the daily Yahoo endpoint does not provide. The
main VPVR pipeline only needs OHLCV.

MIT License. Educational purposes only — not financial advice.

Usage:
  python volume_profile.py --ticker MU
  python volume_profile.py --ticker AAPL --range 1y --interval 1d --bins 60
  python volume_profile.py --ticker MU --output /tmp/mu_vp.png

Exit codes: 0 success | 1 data/network error | 2 invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

DEFAULT_OUTPUT = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "hermes", "cache", "images",
    "{TICKER}_volprofile.png",
)


# --------------------------------------------------------------------------
# Data fetching (Python urllib — curl is unreliable for foreign hosts)
# --------------------------------------------------------------------------

def fetch_ohlcv(ticker: str, range_: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV bars from the Yahoo Finance chart API.

    Returns a DataFrame with columns: date, open, high, low, close, volume.
    Rows with None closes are skipped (market-closed placeholders).
    """
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{urllib.parse.quote(ticker)}?range={range_}&interval={interval}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Yahoo Finance HTTP {exc.code} for ticker {ticker}") from exc
    except Exception as exc:  # network / timeout / parse
        raise RuntimeError(f"Network error fetching {ticker}: {exc}") from exc

    if payload.get("chart", {}).get("error"):
        raise RuntimeError(f"Yahoo Finance API error: {payload['chart']['error']}")

    try:
        result = payload["chart"]["result"][0]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"No chart data returned for ticker {ticker}") from exc

    timestamps = result.get("timestamp") or []
    quote = result.get("indicators", {}).get("quote", [{}])[0]

    rows = []
    for i, ts in enumerate(timestamps):
        try:
            o, h, l, c, v = (
                quote["open"][i], quote["high"][i],
                quote["low"][i], quote["close"][i], quote["volume"][i],
            )
        except (KeyError, TypeError, IndexError):
            continue
        if c is None or o is None or h is None or l is None or v is None:
            continue  # skip null bars
        rows.append((datetime.fromtimestamp(ts), float(o), float(h), float(l), float(c), float(v)))

    if not rows:
        raise RuntimeError(f"No valid OHLCV rows for ticker {ticker}")

    return pd.DataFrame(rows, columns=["date", "open", "high", "low", "close", "volume"])


# --------------------------------------------------------------------------
# Volume Profile construction (VPVR)
# --------------------------------------------------------------------------

def build_profile(
    df: pd.DataFrame,
    bin_count: int = 60,
    bin_size: float | None = None,
) -> dict:
    """Build a Volume Profile from daily OHLCV.

    Volume allocation: a day that traded from low_d to high_d distributes its
    volume across every bin its range touches, weighted by the overlap length:

        V_k += V_d * overlap([low_d, high_d], bin_k) / (high_d - low_d)

    This is the standard OHLCV-only approximation of the true volume-at-price
    distribution (which would require tick data).
    """
    lo = float(df["low"].min())
    hi = float(df["high"].max())
    if not hi > lo:
        raise RuntimeError("Degenerate price range (high == low); cannot build a profile.")

    if bin_size and bin_size > 0:
        bin_count = int(max(2, math.ceil((hi - lo) / bin_size)))
    bin_count = int(bin_count)

    edges = np.linspace(lo, hi, bin_count + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    volume = np.zeros(bin_count)

    for row in df.itertuples(index=False):
        day_lo, day_hi, day_vol = float(row.low), float(row.high), float(row.volume)
        if day_vol <= 0 or not day_hi > day_lo:
            continue
        frac = (hi - lo) / bin_count
        i0 = int(np.clip(np.floor((day_lo - lo) / frac), 0, bin_count - 1))
        i1 = int(np.clip(np.floor((day_hi - lo) / frac), 0, bin_count - 1))
        for k in range(i0, i1 + 1):
            overlap = max(0.0, min(day_hi, edges[k + 1]) - max(day_lo, edges[k]))
            volume[k] += day_vol * overlap / (day_hi - day_lo)

    poc_idx = int(np.argmax(volume))

    return {
        "price_min": lo,
        "price_max": hi,
        "bin_size": (hi - lo) / bin_count,
        "bin_count": bin_count,
        "bin_centers": centers,
        "bin_volume": volume,
        "total_volume": float(volume.sum()),
        "n_days": len(df),
        "first_date": df["date"].iloc[0],
        "last_date": df["date"].iloc[-1],
        "poc_index": poc_idx,
        "poc_price": float(centers[poc_idx]),
    }


def value_area(volume: np.ndarray, poc_idx: int, target: float = 0.70) -> dict:
    """Find the Value Area by expanding outward from the POC.

    Standard algorithm: repeatedly add the adjacent bin (above or below) with
    the higher volume until the included volume reaches `target` of the total.
    VAH = upper edge of the highest included bin; VAL = lower edge of the
    lowest included bin.
    """
    n = len(volume)
    total = float(volume.sum())
    target_vol = total * target
    included = np.zeros(n, dtype=bool)
    included[poc_idx] = True
    acc = float(volume[poc_idx])
    lo_i = hi_i = poc_idx

    while acc < target_vol and (lo_i > 0 or hi_i < n - 1):
        vol_up = volume[hi_i + 1] if hi_i < n - 1 else -1.0
        vol_down = volume[lo_i - 1] if lo_i > 0 else -1.0
        if vol_up >= vol_down:
            hi_i += 1
            included[hi_i] = True
            acc += float(volume[hi_i])
        else:
            lo_i -= 1
            included[lo_i] = True
            acc += float(volume[lo_i])

    return {
        "val_index": lo_i,
        "vah_index": hi_i,
        "included": included,
        "volume_included": acc,
        "total_volume": total,
        "pct_included": acc / total if total > 0 else 0.0,
    }


def find_nodes(
    volume: np.ndarray,
    poc_idx: int,
    hvn_mult: float = 1.5,
    lvn_mult: float = 0.5,
) -> dict:
    """Classify High Volume Nodes, Low Volume Nodes and liquidity gaps.

    Thresholds are multiples of the mean volume of NON-ZERO bins:
      HVN  : volume >= hvn_mult * mean_nonzero   (the POC is always an HVN)
      LVN  : volume <= lvn_mult * mean_nonzero   (zero-volume bins qualify)
      gaps : volume == 0 (extreme LVN — 'single print' / fast-travel zones)
    """
    nz = volume[volume > 0]
    mean_nonzero = float(nz.mean()) if len(nz) else 0.0
    n = len(volume)
    hvn = sorted({int(i) for i in range(n) if volume[i] >= hvn_mult * mean_nonzero})
    if poc_idx not in hvn:
        hvn = sorted(hvn + [int(poc_idx)])
    lvn = [int(i) for i in range(n) if volume[i] <= lvn_mult * mean_nonzero]
    gaps = [int(i) for i in range(n) if volume[i] <= 0.0]
    return {"hvn": hvn, "lvn": lvn, "gaps": gaps, "mean_nonzero": mean_nonzero}


def nearest_level(centers: np.ndarray, price: float, indices, above: bool) -> float | None:
    """Nearest bin center above (above=True) or below (above=False) `price`."""
    best = None
    for i in indices:
        c = float(centers[i])
        if above and c > price:
            best = c if best is None else min(best, c)
        elif not above and c < price:
            best = c if best is None else max(best, c)
    return best


def price_context(
    close: float,
    centers: np.ndarray,
    edges: np.ndarray,
    prof: dict,
    va: dict,
    nodes: dict,
) -> dict:
    """Describe where current price sits relative to the profile."""
    poc = prof["poc_price"]
    val = float(edges[va["val_index"]])
    vah = float(edges[va["vah_index"] + 1])
    in_va = val <= close <= vah

    return {
        "last_close": close,
        "poc_price": poc,
        "above_poc_pct": (close - poc) / poc * 100.0,
        "in_value_area": bool(in_va),
        "val": val,
        "vah": vah,
        "dist_to_val_pct": (close - val) / close * 100.0,
        "dist_to_vah_pct": (vah - close) / close * 100.0,
        "nearest_hvn_above": nearest_level(centers, close, nodes["hvn"], above=True),
        "nearest_hvn_below": nearest_level(centers, close, nodes["hvn"], above=False),
        "nearest_lvn_above": nearest_level(centers, close, nodes["lvn"], above=True),
        "nearest_lvn_below": nearest_level(centers, close, nodes["lvn"], above=False),
    }


# --------------------------------------------------------------------------
# Order flow reference implementations (need bid/ask or tick data)
# --------------------------------------------------------------------------

def compute_delta(bid_volume: np.ndarray, ask_volume: np.ndarray) -> np.ndarray:
    """Delta per bar: aggressive buys minus aggressive sells.

    delta_i = sum(buys executed at the ask)_i - sum(sells executed at the bid)_i

    Requires order-flow data (bid/ask volume per bar). Not computable from
    daily OHLCV — provided as a reference for tick/level-2 datasets.
    """
    return np.asarray(ask_volume, dtype=float) - np.asarray(bid_volume, dtype=float)


def compute_cumulative_delta(delta: np.ndarray) -> np.ndarray:
    """Cumulative delta: running sum of bar deltas from the series start.

    Rising cumulative delta = net buying pressure over the period;
    falling = net selling pressure. Divergence between price and cumulative
    delta hints at waning initiative (absorption / distribution).
    """
    return np.cumsum(np.asarray(delta, dtype=float))


def footprint_imbalance(buy_volume: np.ndarray, sell_volume: np.ndarray) -> np.ndarray:
    """Per-price-level imbalance inside a footprint bar, in [-1, 1].

    I_p = (buy_p - sell_p) / (buy_p + sell_p)
    |I_p| > ~0.5 is a stacked imbalance; extremes often mark exhaustion.
    """
    denom = np.asarray(buy_volume, dtype=float) + np.asarray(sell_volume, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        imb = (np.asarray(buy_volume, dtype=float) - np.asarray(sell_volume, dtype=float)) / denom
    return np.where(denom == 0, 0.0, imb)


# --------------------------------------------------------------------------
# Charting
# --------------------------------------------------------------------------

def plot_profile(df: pd.DataFrame, prof: dict, va: dict, nodes: dict, ctx: dict,
                 out_path: str, ticker: str, range_: str, interval: str) -> str:
    """Price line + horizontal volume histogram sharing the price axis."""
    edges = np.linspace(prof["price_min"], prof["price_max"], prof["bin_count"] + 1)
    centers = prof["bin_centers"]
    volume = prof["bin_volume"]
    poc = prof["poc_price"]
    val, vah = ctx["val"], ctx["vah"]
    last = ctx["last_close"]
    bin_size = prof["bin_size"]

    colors = []
    for k in range(prof["bin_count"]):
        if k in nodes["hvn"]:
            colors.append("#d62728" if k == prof["poc_index"] else "#ff7f0e")
        elif k in nodes["lvn"]:
            colors.append("#999999")
        else:
            colors.append("#4d9de0")

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(1, 2, width_ratios=[2.2, 1.0], wspace=0.04)
    ax_price = fig.add_subplot(gs[0, 0])
    ax_prof = fig.add_subplot(gs[0, 1], sharey=ax_price)

    dates = df["date"].to_numpy()
    closes = df["close"].to_numpy()

    ax_price.plot(dates, closes, color="#1f77b4", lw=1.2, label="Close")
    ax_price.fill_between(dates, df["low"].to_numpy(), df["high"].to_numpy(),
                          color="#1f77b4", alpha=0.08, lw=0)

    # Value area band
    for ax in (ax_price, ax_prof):
        ax.axhspan(val, vah, color="#2ca02c", alpha=0.10, zorder=0)
        ax.axhline(poc, color="#d62728", ls="--", lw=1.3, zorder=3)
        ax.axhline(vah, color="#2ca02c", ls=":", lw=1.1, zorder=3)
        ax.axhline(val, color="#2ca02c", ls=":", lw=1.1, zorder=3)
        ax.axhline(last, color="#8b4513", ls="-", lw=1.0, zorder=3)

    # Horizontal volume histogram on the right
    ax_prof.barh(centers, volume, height=bin_size * 0.92, color=colors,
                 edgecolor="none", zorder=2)

    ax_price.annotate(f"last {last:.2f}", xy=(dates[-1], last),
                      xytext=(6, 6), textcoords="offset points",
                      color="#8b4513", fontsize=9, fontweight="bold")
    ax_price.annotate(f"POC {poc:.2f}", xy=(dates[0], poc),
                      xytext=(6, -12), textcoords="offset points",
                      color="#d62728", fontsize=9, fontweight="bold")
    ax_price.annotate(f"VAH {vah:.2f}", xy=(dates[0], vah),
                      xytext=(6, 4), textcoords="offset points",
                      color="#2ca02c", fontsize=9)
    ax_price.annotate(f"VAL {val:.2f}", xy=(dates[0], val),
                      xytext=(6, -14), textcoords="offset points",
                      color="#2ca02c", fontsize=9)

    ax_price.set_title(
        f"{ticker} — Volume Profile ({range_} / {interval})  |  "
        f"POC {poc:.2f}  VA {val:.2f}–{vah:.2f}  "
        f"({ctx['pct_included'] * 100:.1f}% vol)",
        fontsize=11,
    )
    ax_price.set_ylabel("Price")
    ax_prof.set_xlabel("Volume")
    ax_prof.yaxis.set_tick_params(labelleft=False)
    ax_prof.grid(axis="x", alpha=0.25)
    ax_price.grid(alpha=0.25)
    ax_price.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax_price.xaxis.set_major_locator(mdates.AutoDateLocator())

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def summarize(prof: dict, va: dict, nodes: dict, ctx: dict) -> dict:
    """Collapse everything into a JSON-serializable summary."""
    edges = np.linspace(prof["price_min"], prof["price_max"], prof["bin_count"] + 1)
    va_range = [float(edges[va["val_index"]]), float(edges[va["vah_index"] + 1])]
    return {
        "ticker": prof["ticker"],
        "period": [prof["first_date"].strftime("%Y-%m-%d"),
                   prof["last_date"].strftime("%Y-%m-%d")],
        "bars": prof["n_days"],
        "profile_range": [round(prof["price_min"], 4), round(prof["price_max"], 4)],
        "bin_size": round(prof["bin_size"], 4),
        "bin_count": prof["bin_count"],
        "total_volume": round(prof["total_volume"], 0),
        "poc_price": round(prof["poc_price"], 4),
        "value_area": [round(va_range[0], 4), round(va_range[1], 4)],
        "value_area_pct_volume": round(va["pct_included"] * 100, 2),
        "hvn_prices": [round(float(prof["bin_centers"][i]), 4) for i in nodes["hvn"]],
        "lvn_prices": [round(float(prof["bin_centers"][i]), 4) for i in nodes["lvn"]],
        "liquidity_gap_count": len(nodes["gaps"]),
        "last_close": round(ctx["last_close"], 4),
        "price_vs_poc_pct": round(ctx["above_poc_pct"], 2),
        "in_value_area": ctx["in_value_area"],
        "nearest_hvn_above": round(ctx["nearest_hvn_above"], 4) if ctx["nearest_hvn_above"] else None,
        "nearest_hvn_below": round(ctx["nearest_hvn_below"], 4) if ctx["nearest_hvn_below"] else None,
        "nearest_lvn_above": round(ctx["nearest_lvn_above"], 4) if ctx["nearest_lvn_above"] else None,
        "nearest_lvn_below": round(ctx["nearest_lvn_below"], 4) if ctx["nearest_lvn_below"] else None,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Volume Profile (VPVR) analysis: POC, value area, HVN/LVN from Yahoo daily OHLCV.",
    )
    parser.add_argument("--ticker", default="MU", help="Yahoo ticker symbol (default: MU)")
    parser.add_argument("--range", dest="range_", default="1y", help="Lookback range (default: 1y)")
    parser.add_argument("--interval", default="1d", help="Bar interval (default: 1d)")
    parser.add_argument("--bins", type=int, default=60, help="Number of price bins (default: 60)")
    parser.add_argument("--bin-size", type=float, default=None, help="Explicit bin width ($), overrides --bins")
    parser.add_argument("--value-area", type=float, default=0.70, help="Value area volume fraction (default: 0.70)")
    parser.add_argument("--hvn-mult", type=float, default=1.5, help="HVN threshold: x mean non-zero bin volume (default: 1.5)")
    parser.add_argument("--lvn-mult", type=float, default=0.5, help="LVN threshold: x mean non-zero bin volume (default: 0.5)")
    parser.add_argument("--output", default=None, help=f"Chart output path (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args(argv)

    if args.bins < 2:
        print("error: --bins must be >= 2", file=sys.stderr)
        return 2
    if not 0.0 < args.value_area < 1.0:
        print("error: --value-area must be in (0, 1)", file=sys.stderr)
        return 2

    out_path = args.output or DEFAULT_OUTPUT.replace("{TICKER}", args.ticker.upper())

    try:
        df = fetch_ohlcv(args.ticker, range_=args.range_, interval=args.interval)
        prof = build_profile(df, bin_count=args.bins, bin_size=args.bin_size)
        prof["ticker"] = args.ticker.upper()
        va = value_area(prof["bin_volume"], prof["poc_index"], target=args.value_area)
        va["pct_included"] = va["pct_included"]
        nds = find_nodes(prof["bin_volume"], prof["poc_index"],
                         hvn_mult=args.hvn_mult, lvn_mult=args.lvn_mult)
        edges = np.linspace(prof["price_min"], prof["price_max"], prof["bin_count"] + 1)
        ctx = price_context(float(df["close"].iloc[-1]), prof["bin_centers"], edges,
                            prof, va, nds)
        ctx["pct_included"] = va["pct_included"]
        saved = plot_profile(df, prof, va, nds, ctx, out_path,
                             args.ticker.upper(), args.range_, args.interval)
        summary = summarize(prof, va, nds, ctx)
    except (RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    s = summary
    print(f"=== Volume Profile: {s['ticker']} ({s['period'][0]} → {s['period'][1]}, {s['bars']} bars) ===")
    print(f"Profile range      : {s['profile_range'][0]:,.2f} – {s['profile_range'][1]:,.2f} "
          f"({s['bin_count']} bins × {s['bin_size']:,.4f})")
    print(f"POC                : {s['poc_price']:,.2f}")
    print(f"Value area (70%)   : {s['value_area'][0]:,.2f} – {s['value_area'][1]:,.2f} "
          f"({s['value_area_pct_volume']:.1f}% of volume)")
    print(f"HVN (>=1.5x avg)   : {', '.join(f'{p:,.2f}' for p in s['hvn_prices'])}")
    print(f"LVN (<=0.5x avg)   : {', '.join(f'{p:,.2f}' for p in s['lvn_prices'])}")
    print(f"Liquidity gaps     : {s['liquidity_gap_count']}")
    print(f"Last close         : {s['last_close']:,.2f} "
          f"({s['price_vs_poc_pct']:+.2f}% vs POC, {'inside' if s['in_value_area'] else 'OUTSIDE'} value area)")
    print(f"Nearest HVN above  : {s['nearest_hvn_above']:,.2f}" if s['nearest_hvn_above'] else "Nearest HVN above  : none")
    print(f"Nearest HVN below  : {s['nearest_hvn_below']:,.2f}" if s['nearest_hvn_below'] else "Nearest HVN below  : none")
    print(f"Nearest LVN above  : {s['nearest_lvn_above']:,.2f}" if s['nearest_lvn_above'] else "Nearest LVN above  : none")
    print(f"Nearest LVN below  : {s['nearest_lvn_below']:,.2f}" if s['nearest_lvn_below'] else "Nearest LVN below  : none")
    print(f"Chart saved        : {saved}")
    print("RESULT_JSON: " + json.dumps(summary))

    return 0


if __name__ == "__main__":
    sys.exit(main())
