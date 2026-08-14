---
name: sentiment-composite
description: 'Use when assessing market mood — composite sentiment score (-100 to +100) from fear & greed, funding rates, social, news, on-chain flows, and positioning; plus contrarian signals at sentiment extremes.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [sentiment, fear-greed, funding-rates, social-sentiment, news, on-chain, contrarian, crypto, equities]
---

# Sentiment Analysis

This skill constructs a composite sentiment score by combining multiple independent sentiment indicators — from quantitative funding rates to qualitative social media analysis — into a single actionable framework. Sentiment is a **secondary signal**: it confirms or contradicts directional analysis from technical or fundamental methods and identifies extreme conditions where contrarian positioning has an edge.

## When to Use This Skill

- When assessing overall market mood before entering a trade
- When looking for contrarian signals at sentiment extremes
- When analyzing funding rates for crypto positioning data
- When evaluating social media sentiment around a specific asset
- When determining if the crowd is overly bullish or bearish
- When news events are driving price action and you need to assess impact
- When combining sentiment with technical or fundamental analysis
- When monitoring on-chain flows for institutional vs. retail behavior

## What This Skill Does

- **Composite Scoring**: Combines 6+ independent sentiment indicators into a single score (-100 to +100)
- **Fear & Greed Interpretation**: Maps index readings to actionable trading signals
- **Funding Rate Analysis**: Extracts positioning data from perpetual futures funding
- **Social Sentiment Parsing**: Processes Twitter/X, Reddit, and Telegram signal from noise
- **News Sentiment Assessment**: Evaluates headline and event-driven sentiment shifts
- **On-Chain Sentiment**: Interprets exchange flows, stablecoin flows, and long/short ratios
- **Regime Classification**: Classifies current market into euphoria, optimism, neutral, fear, or capitulation
- **Contrarian Signal Detection**: Identifies when extreme sentiment creates actionable contrarian opportunities

## How to Use

**Overall Market Sentiment**
- What is the current market sentiment for crypto / equities?
- Run a full sentiment analysis on [asset].

**Specific Indicator**
- What are Bitcoin funding rates telling us right now?
- Analyze social sentiment for [ticker] on Twitter and Reddit.

**Contrarian Signals**
- Is the market too bullish? Should I be cautious?
- Everyone is bearish on [asset]. Is this a contrarian buy signal?

## Data Sources

**With MCP/CLI tools connected:**

- Crypto Sentiment MCP — Aggregated crypto sentiment scores, Fear & Greed index
- CoinGecko MCP / CoinGecko Price MCP — Market data, social stats, developer activity
- CoinMarketCap MCP — Market cap data, exchange volumes, social metrics
- Hive Crypto MCP — Crypto social sentiment, influencer tracking
- Binance MCP / Bybit MCP / OKX MCP — Funding rates, long/short ratios, open interest
- DeFiLlama MCP — TVL flows, protocol sentiment via capital movement
- yFinance MCPs — Equity sentiment via options flow, put/call ratio, short interest

**Without tool access:** Ask the user to provide:

- Current Fear & Greed index reading (crypto or equity)
- Funding rates for the asset(s) in question
- Any social media observations (trending topics, sentiment of posts)
- Recent news headlines affecting the asset
- Exchange flow data if available (deposits/withdrawals)
- Their subjective read on market mood

Proceed with analysis using provided data. Note which indicators are based on data vs. qualitative assessment.

## Methodology

### Step 1: Composite Sentiment Score Construction

Build the composite score from 6 independent indicator categories. Each category produces a sub-score from -100 (extreme fear/bearish) to +100 (extreme greed/bullish).

```
COMPOSITE SENTIMENT SCORE

  Score = Sum(Weight_i x SubScore_i) for all categories

  Category Weights (must sum to 100%):
    Fear & Greed Index:    20%
    Funding Rates:         20%
    Social Sentiment:      15%
    News Sentiment:        15%
    On-Chain Flows:        20%
    Positioning Data:      10%

  Final score range: -100 to +100
```

**Score interpretation:**

| Composite Score | Regime | Signal | Action |
|---|---|---|---|
| +75 to +100 | Euphoria | Extreme greed | **STRONG CONTRARIAN SELL** signal |
| +50 to +75 | Greed | Bullish crowd | CAUTION — reduce position sizes |
| +25 to +50 | Optimism | Mildly bullish | Trend-following OK, tighten stops |
| -25 to +25 | Neutral | No strong signal | Rely on technical/fundamental analysis |
| -50 to -25 | Fear | Mildly bearish | Watch for bottoming signals |
| -75 to -50 | High Fear | Bearish crowd | START building contrarian long positions |
| -100 to -75 | Capitulation | Extreme fear | **STRONG CONTRARIAN BUY** signal |

### Step 2: Fear & Greed Index Analysis

**CRYPTO FEAR & GREED INDEX (0-100 scale)**
- Source: alternative.me or similar aggregators
- Components: Volatility (25%), volume (25%), social (15%), dominance (10%), trends (10%), surveys (15%)

Interpretation:
- 0-24: EXTREME FEAR — historically excellent buy zone
- 25-44: FEAR — good accumulation zone
- 45-55: NEUTRAL — no sentiment signal
- 56-74: GREED — caution, trend may be extended
- 75-100: EXTREME GREED — historically excellent sell zone

Conversion to sub-score: `SubScore = (Index - 50) × 2`
Example: Index at 20 → SubScore = (20 - 50) × 2 = -60

**EQUITY FEAR & GREED (CNN Fear & Greed Index)**
- Components: Put/call ratio, market momentum, stock price breadth, junk bond demand, VIX, safe haven demand, stock price strength
- Same 0-100 scale, same interpretation framework

**HISTORICAL BACKTEST**
- Crypto: Buying when Fear & Greed < 20 has yielded average 30-day returns of **+18%** (BTC, 2018-2024)
- Crypto: Buying when Fear & Greed > 80 has yielded average 30-day returns of **-8%** (BTC, 2018-2024)
- Note: These are averages — individual instances vary widely

### Step 3: Funding Rate Analysis

Funding rates in perpetual futures reveal crowd positioning:

**FUNDING RATE INTERPRETATION**

- **Positive funding (longs pay shorts):**
  - Mild positive (0.01-0.03%): Normal bull market conditions
  - High positive (0.03-0.10%): Overleveraged longs, correction risk
  - Extreme positive (>0.10%): DANGER — long squeeze likely imminent
  - Sub-score: Map 0% → 0, 0.05% → +50, 0.10%+ → +100

- **Negative funding (shorts pay longs):**
  - Mild negative (-0.01 to -0.03%): Normal bear market conditions
  - High negative (-0.03 to -0.10%): Overleveraged shorts, bounce likely
  - Extreme negative (<-0.10%): DANGER — short squeeze likely imminent
  - Sub-score: Map 0% → 0, -0.05% → -50, -0.10%+ → -100

**FUNDING RATE CONTEXT** — always check:
1. **Duration**: Sustained high/low funding (>3 days) is more significant
2. **Open interest**: Rising OI + extreme funding = higher squeeze probability
3. **Cross-exchange**: Consistent across Binance, Bybit, OKX = stronger signal
4. **Divergence**: If price is flat but funding is extreme = tension building

**ACTIONABLE LEVELS (BTC as reference)**
- Funding > 0.05% for 3+ days: Reduce long exposure, consider short hedge
- Funding < -0.05% for 3+ days: Reduce short exposure, consider long entry
- Funding > 0.10%: Do NOT open new longs on leverage
- Funding < -0.10%: Do NOT open new shorts on leverage

### Step 4: Social Sentiment Analysis

**SOCIAL SIGNAL PROCESSING**

**TWITTER/X ANALYSIS**
- Metrics to track:
  - Mention volume: Abnormal spike (>3× average) = attention event
  - Sentiment polarity: Ratio of bullish to bearish mentions
  - Influencer alignment: When >70% of crypto influencers agree = contrarian flag
  - Hashtag velocity: Rate of trending topic acceleration
- Signal quality hierarchy:
  1. On-chain analysts with track records (HIGH weight)
  2. Institutional accounts and researchers (MEDIUM-HIGH weight)
  3. Experienced traders with history (MEDIUM weight)
  4. General crypto twitter (LOW weight — mostly noise)
  5. Engagement-farming accounts (ZERO weight — ignore entirely)

**REDDIT ANALYSIS**
- Subreddits: r/cryptocurrency, r/Bitcoin, r/ethtrader, r/wallstreetbets
- Metrics: post sentiment ratio, comment sentiment in top posts, daily active discussion volume, upvote patterns
- Signal: Reddit sentiment is a lagging indicator — useful for extremes only

**TELEGRAM ANALYSIS**
- Monitor: Alpha groups, whale alert channels, project communities
- Signal types: whale alerts, alpha calls, FUD/FOMO cycles
- Warning: High manipulation risk in Telegram — verify signals independently

**NOISE FILTERING RULES**
- Ignore accounts <6 months old
- Ignore posts with engagement-to-content ratio anomalies (bot activity)
- Weight verified accounts higher (but verification is not credibility)
- Discount any post with price targets ("BTC to $200K!") — low signal
- Focus on reasoning quality, not follower count
- Aggregate across platforms — single-platform signals are unreliable

**SOCIAL SENTIMENT SUB-SCORE**
- Bullish consensus > 80%: SubScore = +75 to +100 (contrarian bearish signal)
- Bullish consensus 60-80%: SubScore = +25 to +75
- Mixed 40-60%: SubScore = -25 to +25
- Bearish consensus 60-80%: SubScore = -25 to -75
- Bearish consensus > 80%: SubScore = -75 to -100 (contrarian bullish signal)

### Step 5: News Sentiment Assessment

**EVENT CLASSIFICATION**
- **Tier 1 — Market-moving (immediate impact):** Fed rate decisions, CPI/PPI releases, regulatory actions (SEC lawsuits, bans, approvals), major hack/exploit events, ETF approvals/rejections, geopolitical shocks
- **Tier 2 — Significant (hours to days):** Protocol upgrades, forks, major partnerships, quarterly earnings, exchange listings/delistings
- **Tier 3 — Noise (ignore or discount):** Influencer opinions, price predictions, routine dev updates, repetitive narratives

**NEWS SENTIMENT SCORING** — for each Tier 1/2 event in the last 7 days:
- Strong positive: +20 to +30 (ETF approval, major adoption)
- Moderate positive: +10 to +20 (partnership, protocol upgrade)
- Neutral: 0
- Moderate negative: -10 to -20 (regulatory warning, hack)
- Strong negative: -20 to -30 (exchange collapse, ban)

`News Sub-Score = Sum of event scores, capped at ±100`
Decay: Reduce score by 30% per week (news impact fades)

**HEADLINE VS. REALITY CHECK**
- "Buy the rumor, sell the news": Positive events often priced in before announcement
- "Sell the fear, buy the recovery": Negative events often overshoot initially
- Check: Has price already moved significantly before the headline?
  - If yes: Fade the move (contrarian to headline sentiment)
  - If no: Follow the sentiment (early reaction phase)

### Step 6: On-Chain Sentiment Indicators (Crypto-specific)

**EXCHANGE FLOWS**
- Net inflows to exchanges: BEARISH (coins moved to sell)
- Net outflows from exchanges: BULLISH (coins moved to cold storage)
- Magnitude: Normal ±0.1% of circulating supply/day · Significant ±0.5% · Extreme ±1.0% → strong signal

**STABLECOIN FLOWS**
- Stablecoins TO exchanges: BULLISH (buying power arriving)
- Stablecoins FROM exchanges: BEARISH (buying power leaving)
- Total stablecoin market cap rising: macro bullish · falling: macro bearish

**LONG/SHORT RATIO** (Binance, Bybit, OKX aggregate)
- Ratio > 1.5: CAUTION (crowded long) · 0.8-1.2: NEUTRAL · < 0.7: CAUTION (crowded short)

**WHALE BEHAVIOR**
- Whale accumulation: BULLISH · distribution: BEARISH · new whale addresses: BULLISH
- Track: addresses holding >1000 BTC, >10,000 ETH

**OPEN INTEREST**
- Rising OI + rising price: Strong sustainable trend → BULLISH
- Rising OI + falling price: Shorts building → BEARISH (until squeeze)
- Falling OI + rising price: Short covering → WEAKLY BULLISH (may fade)
- Falling OI + falling price: Long capitulation → BEARISH (until exhaustion)

**ON-CHAIN SUB-SCORE CALCULATION** — weight each of the 5 indicators equally (20% each), score each -100..+100, aggregate.

### Step 7: Sentiment Regime Classification

After computing the composite score, classify the market regime:

**EUPHORIA (Score +75 to +100)**
- Characteristics: "This time is different" narrative dominant; leverage at multi-month highs; mainstream media overwhelmingly positive; new participant influx; social >85% bullish
- Trading response: Begin scaling out of longs; tighten all stops; do NOT initiate new longs; consider small contrarian shorts (defined risk); reduce leverage to minimum

**OPTIMISM (Score +25 to +75)**
- Characteristics: healthy uptrend with normal pullbacks; funding mildly positive; social 60-75% bullish; increasing but not extreme volume
- Trading response: trend-following appropriate; normal sizing; maintain stops at technical levels; develop exit plans for core positions

**NEUTRAL (Score -25 to +25)**
- Characteristics: no dominant narrative; mixed signals; range-bound price; balanced funding/social
- Trading response: rely on technical/fundamental analysis; mean-reversion may work; reduce sizes; watch for regime transition

**FEAR (Score -75 to -25)**
- Characteristics: negative headlines dominating; funding turning negative; social 60-75% bearish; exchange inflows increasing
- Trading response: identify accumulation targets; small sizes (DCA into fear); limit buys at support; keep cash reserves

**CAPITULATION (Score -100 to -75)**
- Characteristics: "Crypto is dead" narratives; funding extremely negative; social >85% bearish; high-volume selling, market-wide liquidations; VIX > 35 (equities)
- Trading response: **STRONGEST CONTRARIAN BUY SIGNAL**; accumulate in tranches (3-5 entries over days/weeks); expect volatility (positions may go further negative first); historical average recovery from capitulation: **+40% within 90 days (BTC)**

## Anti-Patterns

DO NOT do these — they are the most common sentiment analysis mistakes:

- **Using sentiment as a primary signal**: Sentiment is a secondary/confirming indicator. Never trade solely on sentiment — always combine with technical or fundamental analysis.
- **Acting on single indicators**: One social media post or one funding rate snapshot is not a signal. Require confirmation across multiple independent indicators.
- **Confusing volume with quality**: High social media volume means attention, not direction. A trending ticker can be bullish or bearish — analyze the content, not just the count.
- **Following influencer calls**: Influencers have incentives misaligned with your portfolio. They may be paid promoters, front-running their audience, or simply wrong. Use their output as one data point, never as a trading signal.
- **Ignoring time decay of sentiment**: Sentiment signals have a shelf life. A capitulation event from 2 weeks ago is not the same as capitulation happening now. Use the most recent 3-7 days of data.
- **Contrarian trading without confirmation**: "Everyone is bullish so I should short" is simplistic. Contrarian signals require EXTREME readings (>75 or <-75), not merely strong readings. The crowd can be right for extended periods.
- **Over-weighting news**: News creates short-term sentiment shifts that frequently reverse. Wait 24-48 hours for the "news digestion" period before acting on major headlines.
- **Ignoring the macro backdrop**: Sentiment analysis during a macro bull market is different from a macro bear market. Bullish sentiment in a bull market is normal, not extreme. Calibrate against the current regime.

## Validation Checkpoints

**Input Validation**
- At least 3 of 6 indicator categories have data available
- Data is recent (within 24-48 hours for most indicators)
- Asset or market scope is clearly defined (BTC, crypto broad, equities, specific token)
- Multiple data sources consulted (not relying on a single platform)
- Historical context available (what is "normal" for this indicator?)
- User's existing position known (to assess bias in their question)

**Output Validation**
- Composite score calculated with weights and sub-scores shown
- Regime classification stated with supporting evidence
- All 6 indicator categories assessed (or noted as unavailable)
- Contrarian signals flagged only at extreme levels (>75 or <-75)
- Actionable recommendation includes specific position management guidance
- Sentiment signal explicitly labeled as secondary (not primary) signal
- Time horizon specified for the sentiment read (short-term vs. structural)
- Caveat: extreme sentiment can persist longer than expected
- Risk management cross-reference included per Risk Management framework

## Example

User: "What is the current sentiment for Bitcoin? Is it safe to go long?"

### Bitcoin Sentiment Analysis

**Composite Sentiment Score: +62 (GREED / OPTIMISM)**

| Category | Score | Weight | Weighted |
|---|---|---|---|
| Fear & Greed Index | +70 (Index: 72) | 20% | +14.0 |
| Funding Rates | +55 (0.035% avg) | 20% | +11.0 |
| Social Sentiment | +65 (72% bullish) | 15% | +9.75 |
| News Sentiment | +50 (ETF inflow headlines) | 15% | +7.50 |
| On-Chain Flows | +60 (exchange outflows, stablecoin inflows) | 20% | +12.0 |
| Positioning Data | +75 (L/S ratio 1.4) | 10% | +7.50 |
| **Composite** | | | **+61.75** |

**Regime: OPTIMISM (approaching GREED boundary)**

**Indicator Details**
- Fear & Greed: 72 — approaching greed territory but not extreme
- Funding: 0.035% — longs paying shorts, moderately crowded
- Social: 72% bullish Twitter/X sentiment — elevated but not extreme
- News: Positive ETF flow headlines, no major negative catalysts
- On-Chain: Net exchange outflows (accumulation), stablecoin inflows (buying power)
- Positioning: L/S ratio 1.4 — longs outnumber shorts, getting crowded

**Assessment:** Sentiment is BULLISH but NOT at contrarian-sell extremes. The composite score of +62 is in the upper optimism range, approaching greed but not in the euphoria danger zone (>+75).

**Recommendation**
- Going long is NOT contrarian-stupid, but it is NOT a high-conviction entry
- Sentiment supports existing longs but does not favor aggressive new longs
- If entering long: use 50-75% of normal position size
- Tighten stop-loss to protect against sentiment reversal
- Set alerts for composite score crossing +75 (reduce exposure)
- Combine with technical analysis — is there a pullback entry?
- WARNING: Do not add leverage at this sentiment level (funding already elevated at 0.035%)
- Re-assess sentiment in 3-5 days for trend shift

**Sentiment is a SECONDARY signal** — this analysis should CONFIRM or CONTRADICT a directional view from technical-analysis or fundamental-analysis. Do not trade on sentiment alone.

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
