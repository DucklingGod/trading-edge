---
name: on-chain-analysis
description: 'Use when analyzing blockchain data for trading signals — whale tracking, exchange flows (in/out), smart money wallets, protocol health (TVL/fees/users/dev), token distribution & unlocks, noise filtering, and a composite on-chain signal dashboard.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [on-chain, blockchain, whale-tracking, exchange-flows, smart-money, token-distribution, defi, protocol-health, crypto]
---

# On-Chain Analysis

This skill provides a systematic framework for analyzing blockchain data to generate trading signals that are not visible through price charts alone. On-chain analysis reveals what wallets are doing — whale accumulation, exchange deposit/withdrawal patterns, smart money positioning, and protocol health metrics — before those actions are reflected in price. When combined with technical analysis, on-chain data adds a unique information edge.

## When to Use This Skill

- When tracking large wallet (whale) movements for potential market-moving trades
- When analyzing exchange inflows/outflows to gauge sell or buy pressure
- When evaluating a protocol's fundamental health (TVL, fees, users, developer activity)
- When identifying smart money wallets and following their trades
- When assessing token holder distribution and concentration risk
- When monitoring DeFi liquidity changes, large LP movements, or governance votes
- When filtering signal from noise in on-chain metrics
- When building a conviction case for or against a crypto asset

## What This Skill Does

- **Whale Tracking**: Identifies and monitors large wallet movements, exchange deposits/withdrawals, and accumulation patterns
- **Exchange Flow Analysis**: Computes net exchange flows to determine buying vs. selling pressure
- **Smart Money Following**: Identifies consistently profitable wallets and tracks their current positions
- **Protocol Health Assessment**: Evaluates TVL trends, fee revenue, active users, and developer activity
- **Token Distribution Analysis**: Maps holder concentration, whale vs. retail ratios, and unlock schedules
- **Signal Filtering**: Separates actionable on-chain signals from noise using statistical thresholds
- **DeFi Monitoring**: Tracks liquidity changes, large LP movements, and governance activity

## How to Use

**Whale Tracking**
- Track whale movements for [token] over the past 7 days — any large accumulation or distribution?

**Exchange Flow Analysis**
- Analyze exchange net flows for [token] — is there buying or selling pressure?

**Protocol Health Check**
- On-chain health check for [protocol] — TVL, fees, users, developer activity

**Smart Money Tracking**
- Find the most profitable wallets trading [token] and show their current positions

**Token Distribution**
- Analyze token holder distribution for [token] — whale concentration and unlock schedule

## Data Sources

**With MCP/CLI tools connected:**

- Whale Tracker MCP — Real-time large transaction alerts, whale wallet monitoring, exchange flow tracking
- CoinGecko MCP / CoinGecko Price MCP — Token fundamentals, market cap, volume, holder counts
- DeFiLlama — TVL data across all chains/protocols, fee revenue, yield data, protocol comparisons
- DexScreener — DEX trading volume, liquidity depth, token pair analytics
- Hive Crypto MCP — On-chain analytics, wallet profiling, transaction analysis
- Binance MCP (TermiX, snjyor) — Exchange-specific flow data, funding rates, open interest
- Solana-specific: Jupiter Talk MCP, Solana Agent Kit — Solana on-chain data, wallet tracking

**Without tool access:** Ask the user to provide:

- Token/protocol name and chain (Ethereum, Solana, BSC, etc.)
- Known whale wallet addresses (if tracking specific wallets)
- Exchange flow data (from Glassnode, CryptoQuant, Nansen, or similar)
- TVL data (from DeFiLlama directly)
- Token holder distribution data (from Etherscan, Solscan, etc.)

Proceed with analysis using provided data. Note which metrics are observed vs. inferred.

## Methodology

### Step 1: Classify the On-Chain Analysis Objective

Before diving into data, determine what question you are trying to answer.

**ANALYSIS OBJECTIVES:**

1. **DIRECTIONAL SIGNAL** → "Should I buy or sell?"
   - Primary metrics: Exchange flows, whale accumulation/distribution, smart money positions
2. **PROTOCOL EVALUATION** → "Is this protocol healthy and growing?"
   - Primary metrics: TVL, fees, users, developer commits, token velocity
3. **RISK ASSESSMENT** → "What are the hidden risks?"
   - Primary metrics: Holder concentration, unlock schedules, smart contract risk, liquidity depth
4. **TIMING** → "When should I enter/exit?"
   - Primary metrics: Whale movement timing, exchange flow spikes, liquidity shifts

### Step 2: Whale Tracking Framework

Whales are wallets that hold a significant percentage of a token's supply or make large transactions relative to daily volume.

**Whale Definition Thresholds:**

| Asset Category | Whale Threshold (Holdings) | Large Transaction Threshold |
|---|---|---|
| BTC | > 1,000 BTC | > 100 BTC per tx |
| ETH | > 10,000 ETH | > 1,000 ETH per tx |
| Large-cap alt (top 20) | > 0.1% of supply | > 0.01% of supply per tx |
| Mid-cap alt (top 100) | > 0.5% of supply | > 0.05% of supply per tx |
| Small-cap / DeFi token | > 1% of supply | > 0.1% of supply per tx |
| Memecoin | > 2% of supply | > 0.2% of supply per tx |

**Whale Activity Classification:**

ACCUMULATION SIGNALS (Bullish):
- Whale wallets receiving tokens from exchanges (withdrawal)
- Multiple whale wallets adding to positions over 7-14 days
- New whale wallets appearing (fresh accumulation)
- Whale wallets moving tokens to cold storage / multisig
- Score: +2 per whale accumulating, +5 if >3 whales accumulating simultaneously

DISTRIBUTION SIGNALS (Bearish):
- Whale wallets depositing tokens to exchanges (preparing to sell)
- Multiple whale wallets reducing positions over 7-14 days
- Whale wallets breaking tokens into smaller wallets (obfuscation before selling)
- Large transfers to OTC desks or market makers
- Score: -2 per whale distributing, -5 if >3 whales distributing simultaneously

NEUTRAL:
- Whale-to-whale transfers (reshuffling, not selling)
- Exchange hot wallet rebalancing (operational, not directional)
- Protocol treasury movements (governance-approved, expected)

**Whale Tracking Process:**

1. Identify top 20 holders for the token (exclude exchange wallets, bridges, contracts)
2. Monitor their transactions over the past 7/14/30 days
3. Classify each transaction: accumulation, distribution, or neutral
4. Compute net whale flow: Sum(accumulation) - Sum(distribution)
5. Compare to historical average whale flow → z-score
6. If z-score > 2.0 (accumulation): Bullish signal
7. If z-score < -2.0 (distribution): Bearish signal

### Step 3: Exchange Flow Analysis

Exchange flows are one of the most reliable on-chain signals. Tokens moving TO exchanges suggest selling intent. Tokens moving OFF exchanges suggest accumulation.

```
Net Exchange Flow Calculation:

Net Flow = Exchange Inflows - Exchange Outflows

Positive Net Flow (more going IN): Bearish — selling pressure building
Negative Net Flow (more going OUT): Bullish — accumulation / cold storage
```

**SIGNAL THRESHOLDS (relative to 30-day average daily flow):**

| Net Flow vs 30d Avg | Signal | Strength |
|---|---|---|
| > +3 std dev | Strong Sell Pressure | Very Bearish |
| > +2 std dev | Elevated Sell Pressure | Bearish |
| > +1 std dev | Mild Sell Pressure | Slightly Bearish |
| -1 to +1 std dev | Normal Range | Neutral |
| < -1 std dev | Mild Accumulation | Slightly Bullish |
| < -2 std dev | Strong Accumulation | Bullish |
| < -3 std dev | Extreme Accumulation | Very Bullish |

**Exchange Flow Decision Tree:**

1. Calculate 7-day rolling net exchange flow
2. Compare to 30-day rolling average
3. Check if flow is concentrated in few large txs (whale) or many small txs (retail)
   - Whale-driven flow: Higher signal quality (informed money)
   - Retail-driven flow: Lower signal quality (often reactive/late)
4. Cross-reference with price action:
   - Price falling + exchange outflows → smart money buying the dip (bullish)
   - Price rising + exchange inflows → distribution into strength (bearish)
   - Price falling + exchange inflows → capitulation (could be bottoming signal if extreme)
   - Price rising + exchange outflows → genuine accumulation (bullish continuation)

**Exchange Reserve Tracking:**

```
Total Exchange Reserve = Sum of all tokens held on known exchange wallets

Declining reserve over 30+ days → supply squeeze forming (bullish)
Rising reserve over 30+ days → supply overhang building (bearish)

Key thresholds:
  - BTC exchange reserve < 2.3M BTC: historically bullish (supply shock zone)
  - ETH exchange reserve declining + staking increasing: bullish structural change
  - Altcoin exchange reserve spike (>20% in 7 days): large holder preparing to sell
```

### Step 4: Smart Money Identification and Following

Smart money wallets are those with consistently profitable trading histories. Following them can provide an informational edge.

**Smart Money Wallet Identification Process:**

1. **COLLECT**: Gather all wallets that have traded the target token in the past 90 days
2. **FILTER**: Remove bots, MEV wallets, exchange wallets, bridge wallets, contract wallets
3. **SCORE**: For remaining wallets, calculate:
   - Win rate: % of trades that were profitable
   - Average return per trade
   - Profit factor: Total profits / Total losses
   - Trade frequency: Must have >10 trades to be statistically meaningful
4. **RANK**: `Score = Win_Rate × 0.3 + Avg_Return × 0.3 + Profit_Factor × 0.2 + Consistency × 0.2`
   - Consistency = % of months with positive returns
5. **QUALIFY**: Smart money wallet must meet ALL:
   - Win rate > 60%
   - Profit factor > 2.0
   - At least 20 trades in 90 days
   - Active in last 14 days
   - Portfolio value > $100K (filters out dust/noise)

**Smart Money Signal Generation:**

- **STRONG BUY SIGNAL**: 3+ qualified smart money wallets buying the same token within 48 hours + combined purchase > 0.5% of token's daily volume + none selling other tokens to fund (conviction buying, not rotation)
- **MODERATE BUY SIGNAL**: 1-2 qualified smart money wallets buying, or smart money adding to existing positions
- **STRONG SELL SIGNAL**: 3+ qualified smart money wallets selling within 48 hours, or closing positions entirely (not just partial profits)
- **CAUTION**: Smart money following has a delay — by the time you see the tx, price may have moved. Best used as confirmation, not primary signal. Always cross-reference with technical analysis and exchange flows.

### Step 5: Protocol Health Metrics

For evaluating whether a protocol/token has strong fundamentals (useful for medium/long-term positions).

**Protocol Health Scorecard:**

**METRIC 1: TVL (Total Value Locked)**
- 30-day TVL trend: Rising (+2), Flat (0), Declining (-2)
- TVL relative to market cap: TVL/MCap > 1.0 (+2), 0.5-1.0 (+1), < 0.5 (0)
- TVL concentration: Top 3 wallets < 30% of TVL (+1), > 50% (-1)
- Organic vs incentivized: TVL that stays after incentives end = organic = higher quality

**METRIC 2: Fee Revenue**
- 30-day fee trend: Rising (+2), Flat (0), Declining (-2)
- Fee/TVL ratio (capital efficiency): Higher is better
- Annualized fee revenue / Fully diluted valuation = Protocol P/E
- Protocol P/E < 20: Undervalued, P/E > 100: Overvalued or growth-priced

**METRIC 3: Active Users (DAU/MAU)**
- 30-day unique active addresses: Rising (+2), Flat (0), Declining (-2)
- DAU/MAU ratio > 0.3: Strong engagement (+2)
- DAU/MAU ratio < 0.1: Low retention (-1)
- New vs returning users: High new user growth (+1), declining new users (-1)

**METRIC 4: Developer Activity**
- GitHub commits (30d): > 100 (+2), 30-100 (+1), < 30 (0), 0 (-3)
- Active contributors: > 10 (+2), 3-10 (+1), < 3 (-1)
- Commit quality: Bug fixes + features (+1), only docs/CI (0)
- New repos/tooling being built: Ecosystem expansion (+2)

**METRIC 5: Token Velocity**
- Transfer volume / Market cap (30-day average)
- High velocity (>1.0): Token is used transactionally (good for fee-generating protocols)
- Low velocity (<0.1): Token is held speculatively (common for governance tokens)
- Sudden velocity spike: Potential distribution or utilization change

**Health Score Calculation:**

```
Total Score = Σ(all metric scores above)
Max possible = +15, Min possible = -10

| Score | Health Rating | Implication |
|-------|---------------|-------------|
| 10-15 | Excellent | Strong fundamental support for price |
| 5-9   | Good | Fundamentals support current valuation |
| 0-4   | Neutral | No strong fundamental edge |
| -5 to -1 | Weak | Fundamentals deteriorating |
| < -5  | Poor | High risk of price decline |
```

### Step 6: Token Distribution and Holder Analysis

Analyze who holds the token and whether the distribution poses risks.

**Distribution Risk Framework:**

**CONCENTRATION METRICS:**
- Top 10 holder %: < 30% (healthy), 30-50% (moderate risk), > 50% (high risk)
- Top 100 holder %: < 60% (healthy), > 80% (very concentrated)
- Gini coefficient: 0 = perfect equality, 1 = one holder has everything
  - Typical crypto Gini: 0.8-0.9 (high concentration is normal, but extreme = risky)

**HOLDER CATEGORY BREAKDOWN:**

| Category | Typical % | Watch For |
|---|---|---|
| Team/Founders | 10-20% | Vesting schedule, lock status |
| Investors/VCs | 10-25% | Cliff dates, selling patterns |
| Treasury/DAO | 10-30% | Governance proposals to sell |
| Exchange wallets | 5-20% | Rising = selling pressure |
| Smart contracts | 5-40% | Staking, LP, lending |
| Retail (<$10K) | 10-30% | Growing = adoption signal |

**UNLOCK SCHEDULE RISK:**
- Next 30 days: What % of supply unlocks? > 5% = bearish pressure risk
- Next 90 days: What cumulative % unlocks? > 15% = significant supply increase
- Historical unlock impact: Did previous unlocks cause >10% price drops?
- Cliff vs linear vesting: Cliff unlocks are higher risk (sudden supply shock)

**Token Distribution Decision Matrix:**

| Concentration Risk | Unlock Risk (30D) | Signal |
|---|---|---|
| Low (<30% top 10) | Low (<2%) | Safe to hold |
| Low | High (>5%) | Reduce position pre-unlock |
| High (>50% top 10) | Low | Monitor whale wallets closely |
| High | High | Avoid or short into unlock |

### Step 7: Signal vs. Noise Filtering

Not all on-chain activity is meaningful. Apply these filters to separate signal from noise.

**Noise Sources to Filter Out:**

1. **EXCHANGE REBALANCING** — Hot wallet → cold wallet transfers within same exchange. How to identify: Same entity label, regular cadence, round amounts. Action: Exclude from flow analysis.
2. **BRIDGE TRANSFERS** — Cross-chain bridges move large volumes that are NOT buy/sell signals. How to identify: Known bridge contract addresses. Action: Exclude from flow analysis, but note chain preference shifts.
3. **SMART CONTRACT INTERACTIONS** — Staking, unstaking, LP deposits/withdrawals, lending/borrowing. These are DeFi operations, not trading signals per se. Action: Separate from "trading" flows, analyze as protocol usage metrics.
4. **DUST ATTACKS / AIRDROP SPAM** — Tiny amounts sent to many wallets. How to identify: Value < $1, sent to thousands of addresses. Action: Ignore completely.
5. **SELF-TRANSFERS** — Wallet sending to itself (wallet migration, gas optimization). How to identify: Same entity sending and receiving. Action: Exclude from analysis.

**Signal Quality Scoring:**

- **HIGH QUALITY (act on):** Large whale transaction (>0.1% supply) to/from exchange — confirmed, not rebalancing; 3+ smart money wallets aligned on same direction within 48h; exchange outflows sustained over 7+ days (not a single spike); TVL + fees + users all trending same direction for 30+ days
- **MEDIUM QUALITY (confirm with other data):** Single whale transaction (could be rebalancing); smart money wallet buying but small size; exchange flow spike (single day — could reverse); TVL rising but driven by incentives
- **LOW QUALITY (noise, ignore unless extreme):** Small wallet movements; single-day metrics without trend; social-media-amplified whale alerts (often misleading); metrics that historically have <0.1 correlation with price

### Step 8: Construct On-Chain Signal Dashboard

Compile all on-chain signals into a structured dashboard for decision-making.

```
## On-Chain Signal Dashboard: [Token]
### Whale Activity (7-day)
- Net whale flow: [Accumulation/Distribution/Neutral]
- Whale flow z-score: [X.X] → [Signal interpretation]
- Notable whale txs: [list top 3]

### Exchange Flows (7-day)
- Net exchange flow: [+X / -X tokens]
- Flow z-score vs 30d avg: [X.X] → [Signal]
- Exchange reserve trend (30d): [Rising/Declining/Flat]
- Flow composition: [Whale-driven / Retail-driven]

### Smart Money
- Smart money wallets tracked: [N]
- Current consensus: [Buying/Selling/Mixed]
- Notable positions: [list top 3]

### Protocol Health (if applicable)
- TVL: $[X]M, 30d trend: [+X% / -X%]
- Fees (30d): $[X]M, trend: [direction]
- DAU: [X]K, trend: [direction]
- Dev activity: [X] commits, [Y] contributors
- Health score: [X/15] — [Rating]

### Token Distribution
- Top 10 holder concentration: [X%] → [Risk level]
- Next unlock: [Date], [X%] of supply
- Holder trend (30d): [Growing/Shrinking]

### Composite On-Chain Score
- Bullish signals: [count]
- Bearish signals: [count]
- Net on-chain bias: [Bullish/Bearish/Neutral] (confidence: [High/Medium/Low])
```

## Anti-Patterns

DO NOT do these — they are common on-chain analysis mistakes:

- **Reacting to single whale transactions**: One large transfer is not a signal. It could be exchange rebalancing, OTC settlement, or wallet migration. Require pattern confirmation (multiple txs, sustained trend).
- **Ignoring entity labeling**: A "whale alert" of 10,000 BTC moving to Coinbase sounds bearish — unless it is Coinbase's own cold wallet rebalancing. Always verify entity labels before interpreting flows.
- **Treating TVL in isolation**: TVL can be inflated by token price increases (TVL rises because the token in the pool is worth more, not because more capital entered). Always check TVL in token terms, not just USD terms.
- **Following smart money without context**: Smart money wallets may be hedging, providing liquidity, or running market-neutral strategies. A "buy" could be one leg of a paired trade. Check if they have corresponding shorts or hedges.
- **Confusing DeFi operations with trading**: Staking, unstaking, LP deposits, and lending are NOT buy/sell signals. They indicate protocol usage but not directional conviction.
- **Overlooking unlock schedules**: The largest predictable sell pressure in crypto comes from token unlocks. Missing an upcoming cliff unlock can result in holding through 20-40% price drops.
- **Recency bias on metrics**: One day of strong exchange outflows does not make a trend. Require at least 7 days of sustained directional flow before treating it as a signal.

## Validation Checkpoints

**Input Validation**
- Token/protocol name and chain specified
- Data sources identified (which MCP tools or user-provided data)
- Timeframe for analysis defined (7d, 30d, 90d)
- Known exchange wallet addresses excluded from holder analysis
- Entity labeling applied to large wallets (exchange, bridge, protocol, whale)

**Output Validation**
- Whale activity classified with z-scores and thresholds cited
- Exchange flow analysis with net flow direction and statistical significance
- Noise filtered (exchange rebalancing, bridges, dust attacks excluded)
- Protocol health scored with all 5 metric categories if applicable
- Token distribution risk assessed with unlock schedule
- Smart money consensus reported if wallet tracking available
- Composite on-chain score generated with bull/bear signal counts
- Signals cross-referenced with price action for context
- All signals flagged as high/medium/low quality

## Example

User: "Analyze on-chain data for ETH — whale activity, exchange flows, and protocol health over the past 30 days."

### On-Chain Signal Dashboard: ETH

**Whale Activity (30-day)**
- Net whale flow: Accumulation
- Whale flow z-score: +2.4 → Strong accumulation (above +2.0 threshold)
- Notable whale txs:
  1. 0x7a25...3f1d deposited 15,000 ETH to Lido staking (long-term hold signal)
  2. 0x3b8c...9e2a withdrew 8,000 ETH from Coinbase to cold storage
  3. 0x9d1f...4c7b accumulated 12,000 ETH over 3 separate transactions across 10 days

**Exchange Flows (30-day)**
- Net exchange flow: -285,000 ETH (outflows exceed inflows)
- Flow z-score vs 30d avg: -2.1 → Strong accumulation signal
- Exchange reserve trend (30d): Declining 3.2% (from 16.8M to 16.3M ETH)
- Flow composition: 65% whale-driven, 35% retail → high quality signal

**Smart Money**
- Smart money wallets tracked: 14 qualified wallets
- Current consensus: 9 buying, 2 selling, 3 neutral → Bullish (64% buy)
- Notable positions:
  1. Top wallet (72% win rate) added 4,200 ETH at avg $3,380
  2. Second wallet (68% win rate) increased ETH staking allocation by 30%
  3. Third wallet (65% win rate) moved ETH from lending to staking (longer duration)

**Protocol Health (Ethereum Network)**
- TVL: $48.2B, 30d trend: +8.2%
- Fees (30d): $412M, trend: Rising (L2 activity driving base layer fees)
- DAU: 425K, trend: +12% (driven by restaking protocols)
- Dev activity: 1,842 commits, 312 contributors (top in crypto)
- Health score: 13/15 — Excellent

**Token Distribution**
- Top 10 holder concentration: 24.8% → Low risk (includes Ethereum Foundation, staking contracts)
- Next unlock: N/A (ETH has no vesting/unlock schedule)
- Holder trend (30d): Wallets holding >32 ETH growing +4.1% (staking demand)

**Composite On-Chain Score**
- Bullish signals: 6 (whale accumulation, exchange outflows, smart money buying, TVL rising, dev activity, staker growth)
- Bearish signals: 0
- Net on-chain bias: Bullish (confidence: High)

**Recommendation**
Strong on-chain support for ETH. Whale accumulation and sustained exchange outflows at statistically significant levels. Protocol fundamentals excellent. No distribution signals detected. On-chain data supports a long bias — cross-reference with technical analysis for entry timing, and validate position size through Risk Management before executing.

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
