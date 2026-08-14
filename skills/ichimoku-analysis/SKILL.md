---
name: ichimoku-analysis
description: 'Use when analyzing trend direction, momentum, support/resistance, and trade signals with Ichimoku Kinko Hyo (Ichimoku Cloud) — computes Tenkan-sen, Kijun-sen, Senkou Spans A/B, Chikou Span, cloud status, TK cross, kumo twist, composite verdict, and saves a chart.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [ichimoku, ichimoku-kinko-hyo, ichimoku-cloud, kumo, tenkan-sen, kijun-sen, chikou-span, senkou-span, technical-analysis, trend, trading, finance]
---

# Ichimoku Kinko Hyo (Ichimoku Cloud) Analysis

Ichimoku Kinko Hyo ("one-glance equilibrium chart", 一目均衡表) is a five-line technical analysis system developed in the late 1930s by the Japanese journalist Goichi Hosoda (pen name Ichimoku Sanjin) and publicly released in the late 1960s. It is designed to show trend direction, momentum, and dynamic support/resistance in a single view: two lines form a forward-projected "cloud" (kumo) whose edges act as future support and resistance, while a lagging line confirms trend strength against past price. It works best in trending markets and is a poor tool in sideways chop.

## When to Use This Skill

- When asked to determine the **trend direction** of an asset (bullish/bearish/neutral) with a single comprehensive indicator
- When evaluating **momentum** via the Tenkan-sen/Kijun-sen relationship and TK crosses
- When identifying **dynamic support and resistance** levels (cloud edges, Kijun-sen, Span B)
- When looking for **trade entries/exits**: kumo breakouts, TK-cross pullbacks, Chikou-span confirmations
- When used as a **trend filter** on a higher timeframe before trading a lower timeframe
- When asked for an **Ichimoku-specific analysis** (Tenkan-sen value, cloud thickness, kumo twist, etc.) of a ticker like MU, AAPL, BTC-USD
- When a quick, code-driven technical read of an asset is needed without opening a charting platform

## What This Skill Does

- **Fetches 1 year of daily OHLCV** for any Yahoo Finance ticker (equities, ETFs, crypto `BTC-USD`, forex `EURUSD=X`) using Python `urllib` with a browser User-Agent (curl fails on this host for foreign hosts — the skill never uses curl)
- **Computes all five Ichimoku components** with the classic parameters (9 / 26 / 52 / displacement 26):
  - Tenkan-sen (conversion line), Kijun-sen (base line), Senkou Span A, Senkou Span B, Chikou Span (lagging span)
- **Evaluates the Kumo**: price position vs cloud (above/inside/below), cloud color/bias, cloud thickness (now vs 20-day average), cloud slope
- **Detects signals**: fresh TK cross (bullish/bearish, with cloud-location context), kumo twist (impending or currently in the cloud), Chikou-span confirmation vs price
- **Prints a compact analysis table + verdict** with a composite score (−7..+7) mapped to STRONG BULLISH → STRONG BEARISH
- **Saves a matplotlib chart** (candlesticks + shaded kumo + all five spans + volume) to `C:/Users/iHC/AppData/Local/hermes/cache/images/{TICKER}_ichimoku.png`

## How to Use

Run the script with the Hermes Python (pandas/numpy/matplotlib installed):

```
"C:/Users/iHC/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" \
  "C:/Users/iHC/Documents/trading-edge/skills/ichimoku-analysis/scripts/ichimoku.py" MU
```

Options:

- `--range 1y|6mo|3mo|2y` — history window (default `1y`; the script requires at least 78 bars: 52 for Span B + 26 displacement)
- `--no-chart` — skip saving the PNG (analysis table only)

Typical agent prompts this skill answers:

- "Run an Ichimoku analysis on MU and tell me if it's above or below the cloud"
- "Is the TK cross on AAPL fresh, and is it above the cloud?"
- "What's the cloud thickness and kumo twist status for BTC-USD?"
- "Where are the key Ichimoku support/resistance levels for NVDA?"

After the run, the agent should read the verdict, quote the table values in its reply, and reference the saved chart path if the user wants to see it.

## Data Sources

- **Yahoo Finance chart API** (primary): `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d` (fallback host `query2.finance.yahoo.com`)
  - JSON layout: `chart.result[0].timestamp` (epoch seconds) and `.indicators.quote[0]` arrays for `open/high/low/close/volume`
  - **Must** send header `User-Agent: Mozilla/5.0` — requests without a browser UA are often rejected
  - Rows with null `close` are dropped; stray nulls are forward-filled; duplicate timestamps are de-duplicated
  - The final (in-progress) daily bar can be revised intraday by the feed — two fetches minutes apart may show a slightly different last close. This is normal, not a bug
- **Free, no API key required**; reasonable for one-off analysis (heavy programmatic use should switch to a licensed feed)
- Cross-checking (optional): TradingView, StockCharts, or any platform's Ichimoku overlay should reproduce the same values within rounding

## Methodology

### Step 1 — Data preparation

Fetch daily OHLCV, drop rows with a null close, forward-fill stray nulls, drop duplicate timestamps, and require at least 78 bars (`52 + 26`). The classic parameters assume daily bars; the same code works on any timeframe if the period counts are kept.

### Step 2 — The midpoint building block

All Ichimoku lines are constructed from the **midpoint of a rolling high/low range**, not from closes:

```
Midpoint(n) = ( HighestHigh(n) + LowestLow(n) ) / 2
```

where `HighestHigh(n)` / `LowestLow(n)` are the highest high and lowest low over the last `n` periods.

### Step 3 — Tenkan-sen (conversion line, fast signal line)

```
Tenkan-sen = Midpoint(9) = (HH(9) + LL(9)) / 2
```

Short-term equilibrium; used as a signal line and minor support/resistance. Rising/falling → short-term trend; flat → ranging.

### Step 4 — Kijun-sen (base line, medium-term equilibrium)

```
Kijun-sen = Midpoint(26) = (HH(26) + LL(26)) / 2
```

Medium-term equilibrium, the single most important line after the cloud. Acts as confirmation, dynamic support/resistance, and a trailing stop reference.

### Step 5 — Senkou Span A (leading span 1, cloud edge)

```
Span A_raw = (Tenkan-sen + Kijun-sen) / 2
Span A (plotted) = Span A_raw shifted +26 periods into the future
```

The fast edge of the cloud. Because it is plotted 26 periods ahead, the value under today's candle reflects data from 26 sessions ago — this forward projection is what makes the cloud a *leading* indicator of future support/resistance.

### Step 6 — Senkou Span B (leading span 2, cloud edge)

```
Span B_raw = Midpoint(52) = (HH(52) + LL(52)) / 2
Span B (plotted) = Span B_raw shifted +26 periods into the future
```

The slow edge of the cloud (longer lookback → reacts more slowly → stronger support/resistance). The projected cloud for the next ~26 sessions starts at the current raw span values.

### Step 7 — Chikou Span (lagging span, trend confirmation)

```
Chikou Span = Close shifted −26 periods (plotted in the past)
```

Each day's close is drawn 26 sessions back on the chart. The last plotted Chikou point sits 26 bars behind the current candle, so the live confirmation test is: **current close vs close 26 sessions ago** (Chikou above price = bullish confirmation).

### Step 8 — Kumo (the cloud)

- The cloud is the fill between plotted Span A and Span B.
- **Cloud color/bias**: Span A ≥ Span B → bullish (green) cloud; Span A < Span B → bearish (red) cloud.
- **Price vs cloud**: above = bullish regime (cloud is support); below = bearish regime (cloud is resistance); inside = chop/transition.
- **Thickness** `|Span A − Span B|`: thick cloud = strong support/resistance (hard to break); thin cloud = weak zone, prone to breakouts. Compare current thickness to the 20-day average thickness.
- **Cloud slope**: rising leading edge = strengthening trend; falling = weakening.
- **Kumo twist**: when raw Span A and Span B cross, the cloud color flips ~26 sessions later in the projected region. A twist in the near-term cloud signals a potential trend change / consolidation. The script reports an *impending* twist (raw cross within the last 5 bars) or a twist *currently entering* the cloud (raw cross ~26 bars ago).

### Step 9 — Signal synthesis (what the script prints)

| Signal | Bullish | Neutral | Bearish |
|---|---|---|---|
| Price vs cloud | +2 above | 0 inside | −2 below |
| Tenkan vs Kijun | +1 Tenkan above | — | −1 Tenkan below |
| Cloud color | +1 Span A ≥ Span B | — | −1 Span A < Span B |
| Chikou vs price | +1 above | — | −1 below |
| Fresh TK cross (≤5 bars) | +2 bullish cross | 0 none | −2 bearish cross |

- **TK cross strength depends on location**: cross above the cloud = strong bullish signal; inside the cloud = neutral; below the cloud = weak.
- **Verdict mapping**: +6..+7 STRONG BULLISH · +3..+5 BULLISH · +1..+2 MILD BULLISH · 0 NEUTRAL/CHOP · −1..−2 MILD BEARISH · −3..−5 BEARISH · −6..−7 STRONG BEARISH.
- **Key levels reported**: cloud top/bottom (current), Kijun-sen (dynamic support/resistance), and the projected cloud range for the next ~26 sessions.

### Step 10 — Chart rendering

Candlesticks (green up / red down) with the five lines overlaid: Tenkan (blue), Kijun (red), Span A (light green), Span B (purple), Chikou (yellow dotted). The cloud is shaded green where Span A ≥ Span B and red where Span A < Span B, with `interpolate=True` to bridge the leading NaN region. A volume panel sits below; the verdict is embedded in the title. Saved at 150 dpi to the Hermes image cache.

## Anti-Patterns

- **Using Ichimoku in chop/sideways markets** — the cloud is a trend system; in ranges it whipsaws. When price is inside the cloud, treat signals as noise and wait for a cloud breakout.
- **Ignoring the displacement**: comparing today's price against *raw* (unshifted) Span A/B values is wrong — the plotted cloud is shifted 26 periods. The script handles this; hand calculations must too.
- **Trading a bare TK cross** without cloud position and Chikou confirmation — the weakest setup. Best signals align price-vs-cloud, TK cross, and Chikou together.
- **Reading the Chikou signal at the wrong bar**: the Chikou line ends 26 bars before the last candle; its live value is the close 26 sessions ago, compared with today's close.
- **Running with fewer than 78 bars** (or a short `3mo` range) — Span B and the displacement need 52 + 26 periods; otherwise the cloud is incomplete and the analysis is invalid.
- **Overriding parameters (9/26/52) without a stated reason** — the classic values are the system's design; arbitrary changes break comparability with other charts.
- **Treating the cloud as guaranteed support/resistance** — it is a probabilistic zone. Thick clouds hold more often; thin clouds break. Always combine with volume/price action confirmation.
- **Using a single timeframe in isolation** — a daily-cloud read says nothing about the weekly context. For higher-quality setups, stack timeframes (weekly bias → daily entry).
- **Ignoring the lag**: all five lines are midpoint/lag constructions — signals confirm *after* moves begin. Ichimoku is not a leading reversal oracle; it filters and frames trends.
- **Assuming the last bar is frozen** — Yahoo's in-progress daily bar can update intraday; re-running minutes later may show a slightly different last close. Don't chase the delta.

## Validation Checkpoints

- **Span A identity**: plotted Span A at index `i` equals `(Tenkan[i−26] + Kijun[i−26]) / 2` (spot-check a few indices).
- **Span B identity**: plotted Span B at index `i` equals `Midpoint(52)` computed at index `i−26`.
- **Chikou identity**: Chikou at index `i` equals `close[i−26]`; the last plotted Chikou value equals the close 26 sessions ago.
- **Rolling windows**: `Tenkan = (HH(9) + LL(9)) / 2` over the last 9 bars — verify against a manual max/min over the same 9 rows (the script's pandas rolling and a numpy slice must agree).
- **Cross-check on a charting platform**: Tenkan/Kijun/Spans on TradingView for the same ticker should match within rounding (platforms may vary on whether the in-progress bar is included).
- **Cloud color logic**: Span A ≥ Span B ⇔ green/bullish cloud; Span A < Span B ⇔ red/bearish cloud — the fill on the PNG must match the reported bias.
- **Verdict consistency**: recompute the score from the printed component values; e.g., above cloud (+2) + Tenkan>Kijun (+1) + bull cloud (+1) + Chikou above (+1) + fresh bull TK cross (+2) = +7 STRONG BULLISH.
- **Chart sanity**: the cloud fill must be absent in the first 26 bars (leading NaN region), the Chikou line must end 26 bars before the last candle, and the PNG must exist at the reported path with a non-trivial file size.

## Example

Command:

```
"C:/Users/iHC/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" ichimoku.py MU
```

Illustrative output (live feed — exact values drift as the in-progress bar is revised):

```
==============================================================
 ICHIMOKU KINKO HYO — MU   (daily · 252 bars)
==============================================================
 Last close : $964.87   (2026-08-14)
--------------------------------------------------------------
 Component                    Value   Slope(5d)   Role
 Tenkan-sen (9)             $905.50      +71.12   signal line
 Kijun-sen (26)             $874.83      -26.43   base / confirmation
 Senkou Span A            $1,049.93      -30.42   cloud edge (fast, +26)
 Senkou Span B              $871.62      +26.17   cloud edge (slow, +26)
 Chikou Span                $991.64               close 26 bars ago
--------------------------------------------------------------
 Cloud analysis
   Position vs cloud : INSIDE  price inside cloud — chop / transition
   Cloud color / bias: BULLISH (Span A >= Span B)
   Cloud thickness   : $178.31   (20d avg $205.56) → thin
--------------------------------------------------------------
 Signals
   TK cross          : BEARISH (FRESH)
   Kumo twist        : none in the near window
   Chikou vs price   : BELOW price → bearish confirmation
--------------------------------------------------------------
 Key levels
   Cloud top/bottom  : $1,049.93 / $871.62
   Kijun-sen (dyn S/R): $874.83
   Projected cloud   : $890.16 – $996.44 (next ~26 sessions)
--------------------------------------------------------------
 VERDICT: MILD BEARISH   (composite score -1/7)
==============================================================
Chart saved: C:/Users/iHC/AppData/Local/hermes/cache/images/MU_ichimoku.png
```

How to read this example: price has climbed sharply into the cloud (Tenkan +71 in 5 sessions, fresh bearish TK cross), Chikou sits below price, and the cloud is thin — a transition/chop zone where the trend is being decided. The correct posture is **stand aside or reduce risk** until price clears the cloud top ($1,049.93) with Chikou confirmation (bullish) or loses Kijun ($874.83) (bearish continuation). The projected cloud ($890–$996) marks the battleground for the next month.

Script reference: `scripts/ichimoku.py` — `fetch_ohlcv(ticker, rng)` (urllib → DataFrame), `compute_ichimoku(df)` (all five components), `analyze(df, ind)` (signals + score + verdict dict), `print_table(...)` (compact table), `plot_chart(...)` (PNG). Run `python ichimoku.py --help` for options.
