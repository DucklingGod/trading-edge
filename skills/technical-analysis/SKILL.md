---
name: technical-analysis
description: 'Use when analyzing price charts — indicators (RSI, MACD, MAs, Bollinger, ATR, OBV, Stochastic), support/resistance, chart patterns, multi-timeframe analysis, confluence scoring (0-100), and structured trade setups with entry/stop/target.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [technical-analysis, trading, indicators, chart-patterns, multi-timeframe, confluence, crypto, forex, stocks]
---

# Technical Analysis

This skill provides a systematic framework for analyzing price charts, computing technical indicators, identifying chart patterns, and generating trade setups with quantified confidence scores. It uses multi-timeframe analysis to establish directional bias on higher timeframes and precise entries on lower timeframes, then aggregates multiple signals into a single confluence score to rank trade quality.

## When to Use This Skill

- When analyzing any asset's price chart for trade opportunities
- When a user asks about specific indicators (RSI, MACD, moving averages, etc.)
- When identifying support and resistance levels
- When looking for chart pattern formations
- When performing multi-timeframe analysis for trade entries
- When building a scored trade setup with confluence from multiple signals
- When evaluating whether a crypto asset is overbought/oversold
- When analyzing funding rates, volume profile, or liquidation levels (crypto-specific)

## What This Skill Does

- **Indicator Computation**: Calculates RSI, MACD, SMA, EMA, VWAP, Bollinger Bands, ATR, OBV, and Stochastic oscillator with proper parameters
- **Chart Pattern Recognition**: Identifies head & shoulders, double tops/bottoms, triangles, flags, wedges, and other classical patterns
- **Support/Resistance Mapping**: Finds key price levels from historical pivots, volume nodes, and round numbers
- **Multi-Timeframe Analysis**: Establishes bias on higher timeframes, then refines entry on lower timeframes
- **Confluence Scoring**: Combines multiple indicator signals into a 0-100 confidence score
- **Trade Setup Generation**: Produces structured trade setups with entry, stop, target, and confidence rating
- **Crypto-Specific Analysis**: Incorporates funding rates, volume profile, and liquidation heatmaps

## How to Use

**Full Technical Analysis**
- Run technical analysis on [asset] — identify trend, key levels, and trade setups

**Specific Indicator Check**
- What does the RSI and MACD say about [asset] on the 4H timeframe?

**Chart Pattern Scan**
- Are there any chart patterns forming on [asset]? Check daily and 4H charts.

**Multi-Timeframe Analysis**
- Multi-timeframe analysis for [asset] — weekly, daily, 4H for a swing trade setup

**Confluence Score**
- Score the current trade setup for going long [asset] at [price] — how many signals align?

## Data Sources

**With MCP/CLI tools connected:**

- yFinance MCPs (tooyipjee, maxscheijen, Adity-star) — Historical OHLCV data, indicator computation, stock/ETF/crypto prices
- CoinGecko MCP / CoinGecko Price MCP — Crypto prices, volume, market cap, historical data
- Binance MCP (TermiX, snjyor) — Real-time crypto OHLCV, funding rates, order book depth, liquidation data
- OpenBB CLI — Advanced charting, screeners, multi-asset technical analysis
- DexScreener — DEX token price charts, volume, liquidity data
- Bybit MCP / OKX MCP — Additional exchange data, open interest, funding rates

**Without tool access:** Ask the user to provide:

- OHLCV data for the asset (at least 50 bars on the desired timeframe)
- Current price and recent price range
- Timeframe(s) of interest (1H, 4H, Daily, Weekly)
- Any specific indicators they want analyzed
- Known support/resistance levels

Proceed with analysis using provided data. State which computations are approximate vs. exact.

## Methodology

### Step 1: Determine Market Context and Trend

Before computing any indicators, establish the market regime on the highest relevant timeframe.

**Trend Identification Decision Tree:**

1. Is price above the 200-period SMA?
   - YES → Long-term bullish bias
   - NO → Long-term bearish bias
2. Is the 50-SMA above the 200-SMA?
   - YES → Confirmed uptrend (Golden Cross territory)
   - NO → Confirmed downtrend (Death Cross territory)
3. Is price making Higher Highs (HH) and Higher Lows (HL)?
   - YES → Active uptrend
   - NO → Check for Lower Highs (LH) and Lower Lows (LL) → Active downtrend
4. None of the above clearly?
   - Range-bound / consolidation — switch to mean-reversion framework

**Market Regime Classification:**

| Regime | Characteristics | Preferred Strategy |
|---|---|---|
| Strong Trend | ADX > 25, clear HH/HL or LL/LH, price > 20 EMA | Trend-following, momentum |
| Weak Trend | ADX 15-25, choppy HH/HL | Reduced size trend trades |
| Range-bound | ADX < 15, price oscillating between S/R | Mean reversion, fade extremes |
| Volatile/Chaotic | ATR expanding rapidly, no structure | Reduce size or sit out |

### Step 2: Compute Core Indicators

Calculate these indicators in order. Each has specific signal conditions.

**2A: Moving Averages**
```
SMA(period) = Sum(Close, period) / period
EMA(period) = Close × K + EMA_prev × (1 - K), where K = 2 / (period + 1)
VWAP = Cumulative(Price × Volume) / Cumulative(Volume)  [intraday reset daily]
```

Key Periods:
- Fast: 8-EMA, 20-EMA (short-term momentum)
- Medium: 50-SMA (intermediate trend)
- Slow: 200-SMA (long-term trend)
- VWAP: Intraday institutional reference price

Signals:
- Bullish: Price > 20 EMA > 50 SMA > 200 SMA (stacked bullish)
- Bearish: Price < 20 EMA < 50 SMA < 200 SMA (stacked bearish)
- Cross: Golden Cross (50 crosses above 200) / Death Cross (50 crosses below 200)

**2B: RSI (Relative Strength Index)**
```
RSI(14) = 100 - [100 / (1 + RS)]
RS = Average Gain(14) / Average Loss(14)
```

Zones:
- > 70: Overbought — potential sell/short signal (in trending markets, can stay >70)
- < 30: Oversold — potential buy/long signal (in downtrends, can stay <30)
- 40-60: Neutral zone

Advanced Signals:
- Bullish divergence: Price makes lower low, RSI makes higher low → reversal signal
- Bearish divergence: Price makes higher high, RSI makes lower high → reversal signal
- Hidden bullish divergence: Price makes higher low, RSI makes lower low → trend continuation
- Failure swing: RSI breaks above/below a prior RSI peak/trough → strong momentum shift

**2C: MACD (Moving Average Convergence Divergence)**
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

Signals:
- Bullish cross: MACD crosses above Signal (buy)
- Bearish cross: MACD crosses below Signal (sell)
- Zero line cross: MACD crosses above/below zero (trend change)
- Histogram expansion: Momentum increasing
- Histogram contraction: Momentum fading — potential reversal ahead
- Divergence (same logic as RSI): bullish (price lower low + MACD higher low) / bearish (price higher high + MACD lower high)

**2D: Bollinger Bands**
```
Middle Band = SMA(20)
Upper Band = SMA(20) + 2 × StdDev(20)
Lower Band = SMA(20) - 2 × StdDev(20)
Bandwidth = (Upper - Lower) / Middle × 100
```

Signals:
- Price touches lower band in uptrend → buy the dip
- Price touches upper band in downtrend → short the rally
- Squeeze (Bandwidth < 4%): Volatility contraction → expect breakout
- Walking the band: Price hugging upper/lower band → strong trend, do NOT fade

**2E: ATR (Average True Range)**
```
True Range = Max(High - Low, |High - Prev Close|, |Low - Prev Close|)
ATR(14) = SMA(True Range, 14)
```

Usage:
- Stop-loss distance: 1.5-3.0 × ATR from entry
- Volatility filter: ATR expanding = trending, ATR contracting = consolidating
- Position sizing: Risk$ / ATR = units (see risk-management skill)
- Breakout confirmation: Breakout candle range > 1.5 × ATR = strong breakout

**2F: OBV (On-Balance Volume)**
```
If Close > Prev Close: OBV = Prev OBV + Volume
If Close < Prev Close: OBV = Prev OBV - Volume
If Close = Prev Close: OBV = Prev OBV
```

Signals:
- OBV rising while price rising → trend confirmed by volume
- OBV divergence: OBV falling while price rising → distribution, likely reversal
- OBV breakout: OBV breaks to new high/low before price → leading indicator

**2G: Stochastic Oscillator**
```
%K(14) = (Close - Lowest Low(14)) / (Highest High(14) - Lowest Low(14)) × 100
%D = SMA(%K, 3)
```

Zones:
- > 80: Overbought
- < 20: Oversold

Signals:
- Bullish: %K crosses above %D below 20 → buy
- Bearish: %K crosses below %D above 80 → sell
- Best in range-bound markets — unreliable in strong trends

### Step 3: Identify Chart Patterns

Scan for these classical patterns. Each has a specific measured move target.

| Pattern | Type | Target Calculation | Reliability |
|---|---|---|---|
| Head & Shoulders | Reversal | Neckline - (Head - Neckline) | High (70%+) |
| Inverse H&S | Reversal | Neckline + (Neckline - Head) | High (70%+) |
| Double Top | Reversal | Support - (Peak - Support) | Moderate (65%) |
| Double Bottom | Reversal | Resistance + (Resistance - Trough) | Moderate (65%) |
| Ascending Triangle | Continuation | Flat top + (Flat top - Rising trendline start) | Moderate (65%) |
| Descending Triangle | Continuation | Flat bottom - (Falling trendline start - Flat bottom) | Moderate (65%) |
| Symmetrical Triangle | Neutral | Direction of breakout × height of triangle base | Lower (55%) |
| Bull Flag | Continuation | Flagpole height added to breakout point | High (68%) |
| Bear Flag | Continuation | Flagpole height subtracted from breakdown point | High (68%) |
| Rising Wedge | Bearish | Breakdown to wedge base | Moderate (62%) |
| Falling Wedge | Bullish | Breakout to wedge base | Moderate (62%) |
| Cup & Handle | Bullish | Cup depth added to breakout | High (70%) |

Pattern validation rules:
- Pattern must form over at least 10 bars (not 2-3 bar "patterns")
- Volume should confirm: declining volume during pattern, expanding on breakout
- Breakout candle should close beyond the pattern boundary (not just wick)
- Wait for retest of breakout level for higher-probability entry

### Step 4: Map Support and Resistance

Methods for finding S/R levels (use all, then cluster):

1. **HISTORICAL PIVOTS** — Swing highs/lows from the past 50-200 bars. More touches = stronger level. Score: 1 point per touch, 2 points if touch + bounce with volume.
2. **VOLUME PROFILE (VPVR)** — High-Volume Nodes (HVN) act as magnet (support/resistance); Low-Volume Nodes (LVN) act as breakout zone; Point of Control (POC) = strongest S/R.
3. **ROUND NUMBERS** — Psychological levels: $10, $50, $100, $1000, $10000, $50000 (BTC). Add half-levels for crypto: $25K, $35K, $75K.
4. **MOVING AVERAGES AS DYNAMIC S/R** — 20 EMA (short-term), 50 SMA (intermediate), 200 SMA (major trend-defining).
5. **FIBONACCI RETRACEMENTS** — Key levels: 0.236, 0.382, 0.500, 0.618, 0.786. Most reliable: 0.618 and 0.382. Draw from swing low to swing high (uptrend) or high to low (downtrend).

**S/R Level Strength Scoring:**

| Factor | Points |
|---|---|
| Price touch (bounce) | +1 per touch |
| High volume at level | +2 |
| Confluence with Fibonacci | +2 |
| Confluence with round number | +1 |
| Confluence with moving average | +2 |
| Level held on higher timeframe | +3 |
| Recent (within 30 bars) | +1 |
| Old (>100 bars) but respected | +2 |

Levels scoring 5+ are "strong." Levels scoring 8+ are "major."

### Step 5: Multi-Timeframe Analysis (MTF)

This is the most important step for generating high-quality entries. The principle: **Higher timeframe determines direction, lower timeframe determines entry.**

**SWING TRADING (hold 2-14 days):** Bias TF: Weekly · Setup TF: Daily · Entry TF: 4H
**DAY TRADING (hold minutes to hours):** Bias TF: Daily · Setup TF: 4H/1H · Entry TF: 15m/5m
**SCALPING (hold seconds to minutes):** Bias TF: 1H · Setup TF: 15m · Entry TF: 1m/5m
**POSITION TRADING (hold weeks to months):** Bias TF: Monthly · Setup TF: Weekly · Entry TF: Daily

**MTF Alignment Rules:**
- All three timeframes must agree on direction for a high-confidence trade
- If bias TF and setup TF disagree, NO TRADE (or reduce size by 50%)
- Entry TF is ONLY for timing — never override the higher TF bias
- A setup on the bias TF is worth 3x a setup on the entry TF alone

### Step 6: Crypto-Specific Indicators

These indicators are unique to crypto markets and add significant edge.

**Funding Rates (Perpetual Futures)**
- Positive funding rate (>0.01% per 8h): Longs pay shorts → market over-leveraged long. Extremely positive (>0.05%) → potential long squeeze, bearish
- Negative funding rate (<-0.01% per 8h): Shorts pay longs → over-leveraged short. Extremely negative (<-0.05%) → potential short squeeze, bullish
- Neutral zone: -0.01% to +0.01% → no leverage signal

**Liquidation Heatmaps**
- Large liquidation clusters above price → price may be pulled up (magnet effect)
- Large liquidation clusters below price → price may be pulled down
- After liquidation cascade: price often reverses (forced selling/buying exhausted)

**Open Interest (OI)**
- Rising OI + Rising Price → New longs entering, bullish continuation
- Rising OI + Falling Price → New shorts entering, bearish continuation
- Falling OI + Rising Price → Short covering rally (weak, may reverse)
- Falling OI + Falling Price → Long liquidation (weak, may bounce)

### Step 7: Build Confluence Score

Aggregate all signals into a single 0-100 confidence score for the trade setup.

**CONFLUENCE SCORING TABLE (Long Setup Example)**

| Signal | Points | Max |
|---|---|---|
| Price > 200 SMA | +10 | 10 |
| Price > 50 SMA > 200 SMA | +5 | 5 |
| RSI 30-50 (oversold bounce) | +10 | 10 |
| RSI bullish divergence | +10 | 10 |
| MACD bullish cross | +10 | 10 |
| MACD above zero line | +5 | 5 |
| Price at strong S/R support | +10 | 10 |
| Bullish chart pattern present | +10 | 10 |
| Volume confirms (OBV rising) | +5 | 5 |
| Bollinger squeeze + breakout | +5 | 5 |
| Higher TF trend agrees | +10 | 10 |
| Funding rate supports direction | +5 | 5 |
| Stochastic oversold cross up | +5 | 5 |
| **TOTAL POSSIBLE** | | **100** |

**CONFIDENCE RATING:**
- 80-100: A+ setup — maximum position size (per risk-management)
- 65-79: A setup — standard position size
- 50-64: B setup — reduced position size (50-75% of standard)
- 35-49: C setup — minimal position size (25-50%) or pass
- < 35: NO TRADE — insufficient confluence

For short setups: Invert the bullish signals (e.g., Price < 200 SMA = +10, RSI > 70 overbought = +10, etc.)

### Step 8: Generate Structured Trade Setup Output

Every analysis must conclude with this structured output format:

```
## Trade Setup: [LONG/SHORT] [Asset] — [Timeframe]

### Confluence Score: [XX/100] — Grade [A+/A/B/C/F]

### Market Context
- Regime: [Trending/Range-bound/Volatile]
- Higher TF Bias: [Bullish/Bearish/Neutral]
- Key Narrative: [brief description]

### Entry
- Entry Price: $X.XX
- Entry Type: [Limit at support / Stop-entry above resistance / Market]
- Entry Trigger: [specific condition that must occur]

### Risk (see risk-management skill for sizing)
- Stop-Loss: $X.XX ([method]: [X.X] × ATR / below [level])
- Risk per Unit: $X.XX
- R:R Ratio: X.X:1

### Targets
- Target 1: $X.XX (partial: take 50% off)
- Target 2: $X.XX (move stop to breakeven)
- Target 3: $X.XX (trail stop)

### Supporting Signals
1. [Signal 1]: [value/condition] — [bullish/bearish] [+X points]
2. [Signal 2]: [value/condition] — [bullish/bearish] [+X points]
...

### Invalidation
- Setup invalid if: [specific condition, e.g., "price closes below $X on daily"]
- Time invalidation: [setup expires after X bars/days if not triggered]

### Crypto-Specific (if applicable)
- Funding Rate: [X.XX%] → [interpretation]
- OI Trend: [rising/falling] → [interpretation]
- Liquidation Levels: [above/below at $X]
```

## Anti-Patterns

DO NOT do these — they destroy technical analysis edge:

- **Indicator overload**: Using 10+ indicators that all say the same thing (e.g., RSI + Stochastic + CCI are all momentum oscillators). Use one from each category: trend, momentum, volume, volatility.
- **Curve-fitting parameters**: Changing indicator periods to make past signals look perfect (e.g., "RSI(7) works better on this chart"). Stick to standard periods (14 for RSI, 12/26/9 for MACD, 20 for Bollinger) unless backtested on out-of-sample data.
- **Ignoring the higher timeframe**: A 5m buy signal means nothing if the daily chart is in a downtrend. Always check at least one timeframe higher.
- **Trading every pattern**: Not every head-and-shoulders is real. Require volume confirmation + breakout close beyond the neckline. Patterns without volume are noise.
- **Anchoring to a bias**: Seeing only bullish signals because you want to buy. Score the bearish case too — if bearish confluence is also high, the setup is ambiguous.
- **Ignoring regime**: RSI overbought is NOT a sell signal in a strong uptrend. Bollinger upper band touch is NOT a short signal during a momentum move. Match strategy to regime.
- **No invalidation level**: Every setup must have a clear point where it is wrong. "It could still work" is not analysis.

## Validation Checkpoints

**Input Validation**
- Asset and timeframe(s) specified
- Sufficient historical data available (minimum 200 bars for SMA/EMA, 50 bars for patterns)
- OHLCV data is clean (no gaps, correct timezone)
- Higher timeframe data available for MTF analysis
- Market hours/session context known (crypto = 24/7, equities = market hours)

**Output Validation**
- Market regime identified with supporting evidence
- At least 3 indicators computed from different categories (trend, momentum, volume)
- Support/resistance levels mapped with strength scores
- Multi-timeframe alignment assessed
- Confluence score calculated with itemized scoring
- Trade setup in structured format with entry, stop, target
- Invalidation conditions defined
- R:R ratio meets minimum for strategy type (see Risk Management)
- Crypto-specific indicators included if analyzing crypto asset

## Example

User: "Run technical analysis on BTC/USDT — looking for a swing trade setup on the daily chart."

### Trade Setup: LONG BTC/USDT — Daily

**Confluence Score: 72/100 — Grade A**

**Market Context**
- Regime: Trending (ADX = 28, above 25 threshold)
- Higher TF Bias: Bullish (Weekly: price > 50 SMA > 200 SMA, making HH/HL)
- Key Narrative: BTC pulled back to 50 SMA on daily after making new highs. Funding rates neutral, suggesting spot-driven rally rather than leveraged.

**Entry**
- Entry Price: $64,200 (limit order at 50 SMA + daily demand zone)
- Entry Type: Limit at dynamic support
- Entry Trigger: Daily candle prints bullish engulfing or hammer at $64,000-$64,500 zone

**Risk**
- Stop-Loss: $61,100 (2.5 × ATR(14) below entry; ATR = $1,240)
- Risk per Unit: $3,100
- R:R Ratio: 2.9:1

**Targets**
- Target 1: $70,000 (prior swing high — take 40% off, +$5,800)
- Target 2: $73,200 (1.618 Fibonacci extension — take 30% off, move stop to $64,200)
- Target 3: $78,500 (measured move from consolidation range — trail stop at 2× ATR)

**Supporting Signals**
1. Weekly trend: Price > 50 > 200 SMA, HH/HL structure — bullish [+10]
2. Daily 50 SMA: Price pulling back to dynamic support — bullish [+10]
3. RSI(14): 42 — pulling back from overbought, not yet oversold — neutral [+5]
4. RSI hidden bullish divergence: Price HL, RSI LL on daily — continuation signal [+10]
5. MACD: Still above zero line, histogram contracting — momentum slowing but trend intact [+5]
6. Volume: OBV holding above its 20-period MA — accumulation intact [+5]
7. Bollinger Bands: Price at lower band in uptrend — buy-the-dip signal [+5]
8. Support zone: $63,800-$64,500 (3 prior bounces, 0.382 Fib, 50 SMA confluence) — strong (score 8) [+10]
9. Funding rate: +0.005% (neutral, no extreme) — no signal [+0]
10. OI declining + price declining: Long liquidation, weak sellers — potential bounce [+5]
11. Stochastic: %K at 25, approaching oversold — supportive [+2]
12. Bull flag: 3-week flag pattern on daily, flagpole = $12K — target $76K [+5]

**Invalidation**
- Setup invalid if: Daily close below $60,000 (200 SMA and flag bottom)
- Time invalidation: If entry not triggered within 5 daily bars, reassess

**Crypto-Specific**
- Funding Rate: +0.005% → Neutral (no leverage signal)
- OI Trend: Declining 8% over 3 days → longs being flushed (contrarian bullish)
- Liquidation Levels: $58K large long liquidation cluster, $72K large short cluster (price magnet above)

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
