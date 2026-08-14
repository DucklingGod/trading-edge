---
name: fundamental-analysis
description: 'Use when valuing stocks or crypto from fundamentals — valuation ratios, DCF, tokenomics, macro context, earnings analysis, comparable ranking, and an undervalued/fair/overvalued verdict with confidence level and target range.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [fundamental-analysis, valuation, dcf, tokenomics, earnings, macro, crypto, equities]
---

# Fundamental Analysis

This skill evaluates the intrinsic value of equities and crypto assets by analyzing financial statements, valuation ratios, tokenomics, macroeconomic context, and protocol-level metrics. It answers the question: "Is this asset cheap, fairly priced, or expensive relative to its fundamentals?" Fundamental analysis provides the conviction layer — technical analysis times the entry, but fundamentals determine whether the asset is worth owning at all.

## When to Use This Skill

- When evaluating whether to invest in a stock or crypto asset
- When comparing multiple assets in the same sector or category
- Before earnings announcements to assess expected impact
- When analyzing tokenomics of a new crypto project
- When assessing macro conditions that affect portfolio allocation
- When building a DCF or relative valuation model
- When evaluating protocol revenue and usage metrics for DeFi tokens
- When deciding sector allocation based on macro environment
- When a position has moved significantly and you need to reassess fair value

## What This Skill Does

- **Equity Valuation**: Calculates P/E, P/S, P/B, PEG, EV/EBITDA, and DCF fair value estimates
- **Crypto Fundamental Assessment**: Analyzes tokenomics, protocol revenue, active users, developer activity, and governance
- **Macro Context Analysis**: Evaluates interest rates, inflation, USD strength, and yield curve impact on asset classes
- **Sector Analysis**: Determines how different sectors respond to current macro regime
- **Earnings Analysis**: Assesses EPS beats/misses, revenue growth trends, guidance quality, and forward estimates
- **Comparable Analysis**: Ranks assets against sector peers using standardized metrics
- **Valuation Verdict**: Produces an undervalued/fair/overvalued rating with confidence level and price target range

## How to Use

**Equity Valuation**
- Run fundamental analysis on AAPL
- What is the fair value of NVDA using DCF and comparable analysis?

**Crypto Fundamentals**
- Analyze the tokenomics and fundamentals of ETH
- Compare L1 fundamentals: ETH vs SOL vs AVAX

**Macro Context**
- How do current macro conditions affect tech stocks and crypto?

**Earnings Analysis**
- Analyze MSFT earnings: did they beat expectations? What does guidance look like?

## Data Sources

**With MCP/CLI tools connected:**

- yFinance MCPs (tooyipjee, maxscheijen, Adity-star) — Financial statements, earnings data, valuation ratios, historical prices
- Financial Reports MCP — SEC filings, 10-K, 10-Q, earnings transcripts
- OpenBB CLI — Comprehensive financial data, screening, economic calendar
- CoinGecko MCP / CoinGecko Price MCP — Token metrics, market cap, FDV, supply data, volume
- DeFiLlama — Protocol TVL, revenue, fees, user counts, chain comparisons
- Token Terminal (via web fetch) — Protocol revenue, P/F ratios, developer activity
- Messari (via web fetch) — Token profiles, governance, tokenomics breakdowns
- FRED / economic data (via OpenBB) — Interest rates, CPI, GDP, unemployment

**Without tool access:** Ask the user to provide:

- Financial statements (income statement, balance sheet, cash flow) or key metrics
- Current price, market cap, and shares outstanding (or token supply)
- Sector and peer company/protocol names for comparables
- Recent earnings results and guidance (if applicable)
- Token supply schedule, unlock dates, and burn mechanisms (for crypto)
- Current macro data: Fed funds rate, CPI, 10Y yield

Proceed with analysis using provided data. Note which inputs are sourced vs. estimated.

## Methodology

### Step 1: Asset Classification and Framework Selection

Before running any numbers, classify the asset to determine which valuation framework applies:

```
ASSET TYPE ROUTING

Equity (stock)
  ├── Growth stock (revenue growth >20% YoY) → P/S, PEG, DCF with high growth assumptions
  ├── Value stock (P/E < sector median, low growth) → P/E, P/B, EV/EBITDA, dividend yield
  ├── GARP (growth at reasonable price) → PEG, EV/EBITDA, DCF
  └── Pre-profit / IPO → P/S, revenue multiple, TAM analysis

Crypto
  ├── L1 blockchain (ETH, SOL, AVAX) → FDV/Revenue, active addresses, dev activity, fee revenue
  ├── DeFi protocol (AAVE, UNI, MKR) → P/F ratio, TVL, revenue/fees, token buybacks
  ├── Infrastructure (LINK, GRT, FIL) → Usage metrics, integration count, revenue
  └── Meme / community token → NOT suitable for fundamental analysis (see memecoin-trading)
```

### Step 2: Equity Valuation Ratios

Calculate and interpret the core valuation multiples:

**Price-to-Earnings (P/E)**
```
P/E = Share Price / Earnings Per Share (EPS)
Forward P/E = Share Price / Estimated Next-12-Month EPS
```

Interpretation:
- P/E < 10 → Potentially undervalued OR earnings declining
- P/E 10-20 → Fair range for mature companies
- P/E 20-40 → Growth premium — justified only if growth supports it
- P/E > 40 → Expensive — needs exceptional growth to justify
- P/E negative → Unprofitable — use P/S instead

**CRITICAL**: Always compare P/E to:
1. Company's own 5-year average P/E
2. Sector median P/E
3. Growth rate (via PEG ratio)

**Price-to-Sales (P/S)**
```
P/S = Market Cap / Annual Revenue
EV/Revenue = Enterprise Value / Annual Revenue
```

Useful when: Company is unprofitable or has volatile earnings.

Interpretation by sector:
- SaaS / cloud software: 3-15x revenue (high gross margins justify premium)
- Hardware / manufacturing: 0.5-3x revenue
- Retail / e-commerce: 0.5-2x revenue
- Biotech (pre-revenue): Based on TAM and pipeline probability

**Price-to-Book (P/B)**
```
P/B = Share Price / Book Value Per Share
Book Value = Total Assets - Total Liabilities
```

Interpretation:
- P/B < 1.0 → Trading below liquidation value — deep value or value trap
- P/B 1-3 → Normal range for most companies
- P/B > 5 → Asset-light business or significant intangibles

Most useful for: Banks, insurance, REITs, asset-heavy businesses.
Less useful for: Tech, SaaS, biotech (intangible assets dominate).

**PEG Ratio**
```
PEG = P/E / Annual EPS Growth Rate (%)
```
Example: P/E = 30, EPS growth = 25% → PEG = 30 / 25 = 1.2

Interpretation:
- PEG < 1.0 → Undervalued relative to growth (the sweet spot)
- PEG 1.0-1.5 → Fairly valued
- PEG 1.5-2.0 → Getting expensive
- PEG > 2.0 → Growth premium is stretched

**WARNING**: PEG is only meaningful when growth is positive and sustainable.
Do NOT use PEG for cyclical companies or one-time growth spikes.

**EV/EBITDA**
```
Enterprise Value = Market Cap + Total Debt - Cash
EBITDA = Operating Income + Depreciation + Amortization
EV/EBITDA = Enterprise Value / EBITDA
```

Interpretation by sector:
- Tech: 12-25x (capital-light)
- Industrial: 6-12x
- Energy: 4-8x
- Utilities: 8-12x (stable cash flows)
- Consumer staples: 10-15x

Advantage over P/E: Capital structure-neutral, ignores tax differences.
Best for: Comparing companies with different debt levels or in M&A analysis.

### Step 3: Discounted Cash Flow (DCF) Modeling

DCF is the gold standard for intrinsic value. Build a simplified model:

**STEP-BY-STEP DCF**

1. **PROJECT FREE CASH FLOW (FCF) for 5-10 years**
   ```
   FCF = Operating Cash Flow - Capital Expenditures
   ```
   - Year 1-3: Use analyst consensus or recent growth rate
   - Year 4-7: Taper growth toward sector average
   - Year 8-10: Taper toward GDP growth rate (2-3%)

2. **CALCULATE TERMINAL VALUE**
   ```
   Terminal Value = FCF_final × (1 + terminal_growth) / (discount_rate - terminal_growth)
   ```
   Terminal growth rate: 2-3% (never above long-term GDP growth)

3. **DISCOUNT TO PRESENT VALUE**
   ```
   PV = Σ [FCF_t / (1 + r)^t] + [Terminal Value / (1 + r)^n]
   ```
   Discount rate (r):
   - WACC for equities (typically 8-12%)
   - Higher for crypto (15-25% to reflect risk)

4. **CALCULATE PER-SHARE VALUE**
   ```
   Intrinsic Value = Total PV / Shares Outstanding
   Margin of Safety = (Intrinsic Value - Current Price) / Intrinsic Value
   ```

**DECISION FRAMEWORK:**
- Margin of Safety > 30% → Strong buy signal
- Margin of Safety 10-30% → Moderate buy signal
- Margin of Safety 0-10% → Fairly valued, wait for better entry
- Margin of Safety < 0% → Overvalued, avoid or consider short

**DCF Sensitivity Table (always provide):**

Example: NVDA DCF sensitivity (price per share)

| Discount Rate \ Terminal Growth | 1.5% | 2.0% | 2.5% | 3.0% |
|---|---|---|---|---|
| 8% | $185 | $210 | $245 | $295 |
| 9% | $155 | $175 | $200 | $235 |
| 10% | $135 | $150 | $170 | $195 |
| 11% | $118 | $130 | $148 | $168 |
| 12% | $105 | $115 | $130 | $148 |

Current price: $140 → Fair value at 10% / 2.5% = $170 (18% upside)

### Step 4: Crypto Fundamental Analysis

Crypto assets require a different framework since most do not have traditional financial statements.

**Tokenomics Analysis**

SUPPLY ANALYSIS:
- Total Supply: Maximum tokens that will ever exist
- Circulating Supply: Tokens currently in circulation
- FDV: Fully Diluted Valuation = Total Supply × Price
- Market Cap: Circulating Supply × Price
- FDV/MCap Ratio: If > 3x, significant dilution risk from unlocks

SUPPLY SCHEDULE CHECKS:
- Cliff unlocks: Large token releases on specific dates (bearish events)
- Vesting schedule: Monthly/quarterly team/investor unlocks
- Inflation rate: Annual new supply creation (staking rewards, mining)
- Burn mechanism: Does the protocol burn tokens? (ETH EIP-1559, BNB quarterly burns)
- Net emission: Inflation rate minus burn rate = actual dilution

RED FLAGS:
- FDV/MCap > 5x → Massive future dilution
- Team/VC allocation > 40% → Insider-heavy distribution
- No cliff passed yet → Selling pressure incoming
- Unclear or modifiable supply → Governance risk

**Protocol Revenue and Usage**

REVENUE METRICS (from DeFiLlama / Token Terminal):
- Fees/day: Total fees generated by the protocol
- Revenue/day: Fees that accrue to token holders (after expenses)
- P/F Ratio: FDV / Annualized Fees (like P/S for crypto)
- P/Revenue Ratio: FDV / Annualized Revenue to token holders

USAGE METRICS:
- Daily Active Addresses: Unique wallets interacting with protocol
- Transaction Count: Daily transactions on the network
- TVL (Total Value Locked): Capital deposited in DeFi protocols
- TVL/MCap Ratio: If > 1.0, more value locked than market cap (potentially undervalued)

DEVELOPER ACTIVITY (from GitHub / Electric Capital):
- Active developers: Monthly unique contributors
- Commit frequency: Code commits per week
- Ecosystem projects: Number of projects building on the protocol

GROWTH RATES: Calculate 30d, 90d, 180d growth for all metrics above.
Accelerating metrics = bullish; decelerating = bearish.

**Crypto Comparable Analysis**

L1 BLOCKCHAIN COMPARISON TABLE

| Metric | ETH | SOL | AVAX | Interpretation |
|---|---|---|---|---|
| FDV | $400B | $80B | $15B | Scale context |
| Fees/day | $8M | $500K | $100K | Revenue generation |
| P/F Ratio | 137x | 438x | 411x | ETH cheapest on fees |
| Active Addr/day | 500K | 1.2M | 50K | SOL leads usage |
| Dev Count | 2,500 | 1,200 | 400 | ETH leads dev activity |
| TVL | $60B | $8B | $1.2B | ETH dominates TVL |

DEFI PROTOCOL COMPARISON TABLE

| Metric | AAVE | MKR | UNI | Interpretation |
|---|---|---|---|---|
| FDV | $2B | $2.5B | $6B | UNI premium |
| Revenue/day | $800K | $500K | $2M | UNI leads |
| P/Revenue | 6.8x | 13.7x | 8.2x | AAVE cheapest |
| TVL | $12B | $8B | $5B | AAVE leads |
| Token Accrual | Yes | Yes | No | UNI lacks accrual mechanism |

### Step 5: Macro Context Analysis

Macro conditions directly affect asset valuations. Assess the current regime:

**MACRO REGIME CLASSIFICATION**

- **Rate Environment:**
  - Rising rates → Negative for growth/tech, positive for banks, negative for crypto
  - Stable rates → Neutral, focus on earnings
  - Falling rates → Positive for growth/tech, positive for crypto, negative for USD

- **Inflation:**
  - High (>4%) → Commodities, energy, TIPS, real assets benefit
  - Moderate (2-4%) → Goldilocks for equities
  - Low (<2%) → Growth stocks benefit, deflationary risk

- **USD Strength:**
  - Strong USD → Negative for crypto, negative for international earnings
  - Weak USD → Positive for crypto, positive for commodities, EM equities

- **Yield Curve:**
  - Normal (10Y > 2Y) → Healthy economy, favor cyclicals
  - Flat → Late cycle, favor defensive
  - Inverted (2Y > 10Y) → Recession signal (12-18 month lead), favor cash and quality

**Sector Rotation Framework:**

| Economic Phase | Leading Sectors | Lagging Sectors | Crypto Impact |
|---|---|---|---|
| Early expansion | Tech, consumer discretionary, small caps | Utilities, staples | Bullish (risk-on) |
| Mid expansion | Industrials, materials, financials | Defensive | Moderately bullish |
| Late expansion | Energy, materials, healthcare | Tech, growth | Volatile, selective |
| Contraction | Utilities, staples, healthcare, cash | Cyclicals | Bearish (risk-off) |
| Recovery | Financials, real estate, tech | Staples | Strongly bullish |

### Step 6: Earnings Analysis Framework

For publicly traded companies, earnings are the primary valuation driver:

**EARNINGS ASSESSMENT CHECKLIST**

1. **BEAT/MISS ANALYSIS**
   - EPS beat/miss: Actual EPS vs. consensus estimate (% surprise)
   - Revenue beat/miss: Actual revenue vs. consensus
   - Whisper number: Unofficial "real" expectation (often higher than consensus)
   - Strong beat: EPS >5% above consensus AND revenue beat
   - Weak beat: EPS beat but revenue miss (accounting-driven, less bullish)
   - Quality miss: Revenue miss but strong guidance (forward-looking)
   - Bad miss: Both miss with lowered guidance (bearish)

2. **REVENUE QUALITY**
   - Organic growth rate: Revenue growth excluding acquisitions
   - Recurring revenue %: SaaS → ARR/MRR growth, retention rates
   - Customer growth: Net new customers or subscriber adds
   - ARPU trend: Revenue per user — expanding or contracting?
   - Geographic mix: Diversified or concentrated?

3. **MARGIN ANALYSIS**
   - Gross margin trend: Expanding → pricing power; Contracting → cost pressure
   - Operating margin: Improving → operational leverage; Declining → SGA bloat
   - FCF margin: Cash generation relative to revenue

4. **GUIDANCE IMPACT**
   - Raised guidance: Management confident → bullish signal
   - Maintained guidance: Neutral (market expects raises after beats)
   - Lowered guidance: Management cautious → bearish signal
   - Withdrawn guidance: Extreme uncertainty (rare, very bearish)

5. **POST-EARNINGS FRAMEWORK**
   - Strong fundamentals + sell-off → Buy opportunity (market overreaction)
   - Weak fundamentals + rally → Be cautious (sugar high, consider selling)
   - Strong + strong rally → Momentum intact, hold/add
   - Weak + sell-off → Correct reaction, avoid catching the knife

### Step 7: Synthesize the Valuation Verdict

Combine all analyses into a final assessment:

**VALUATION VERDICT FORMAT**

```
Asset: [Name]
Current Price: [Price]
Asset Type: [Equity growth / equity value / L1 blockchain / DeFi protocol / etc.]

VALUATION SUMMARY
  DCF Fair Value:         $X (margin of safety: Y%)
  Relative Valuation:     P/E at Zx vs sector median of Wx
  Comparable Ranking:     #N out of M peers
  Crypto Metrics:         P/F ratio at Xx vs category median of Yx (if applicable)

FUNDAMENTAL SCORE: [1-10]
  Revenue/usage growth:    [1-10]
  Profitability/cash flow: [1-10]
  Competitive position:    [1-10]
  Macro alignment:         [1-10]
  Tokenomics quality:      [1-10] (crypto only)

VERDICT: [UNDERVALUED / FAIRLY VALUED / OVERVALUED]
CONFIDENCE: [LOW / MEDIUM / HIGH]
CATALYST TIMELINE: [Near-term / Medium-term / Long-term]

TARGET RANGE: $X - $Y (base case - bull case)

KEY RISKS:
  1. [Risk 1]
  2. [Risk 2]
  3. [Risk 3]
```

## Anti-Patterns

DO NOT do these — they are common fundamental analysis mistakes:

- **Single-metric valuation**: Never value an asset using only P/E or only one ratio. Always triangulate with at least 3 methods (e.g., P/E + EV/EBITDA + DCF, or P/F + TVL analysis + dev activity).
- **Ignoring macro context**: A stock can be "cheap" on fundamentals and still fall 40% in a bear market. Always layer macro analysis on top of individual asset analysis.
- **Stale data**: Financial data goes stale quickly. Always verify the date of the most recent earnings report and check for any material events since then.
- **FDV blindness in crypto**: Comparing market caps without considering fully diluted valuation leads to massively overvaluing tokens with upcoming unlocks.
- **Confusing revenue with token price**: Protocol revenue going up does not automatically mean the token should go up — only if that revenue accrues to token holders.
- **Terminal growth rate > 3%**: In a DCF, terminal growth above long-term GDP growth is economically impossible at scale. This is the most common DCF manipulation.
- **Anchoring to analyst targets**: Analyst price targets cluster around current price and adjust slowly. They are lagging indicators, not leading ones.
- **Applying equity frameworks to meme tokens**: Meme coins and community tokens have no cash flows, no revenue, and no traditional fundamentals. Do not attempt to calculate P/E or DCF for DOGE.

## Validation Checkpoints

**Input Validation**
- Asset correctly classified (equity growth/value, crypto L1/DeFi/infrastructure)
- Financial data sourced and dated (most recent quarter/annual)
- Peer group defined (3-5 comparable assets)
- Macro regime identified (rate environment, inflation, USD strength)
- For crypto: supply schedule, unlock dates, and token accrual mechanism verified

**Output Validation**
- At least 3 valuation methods applied and compared
- DCF includes sensitivity table with range of assumptions
- All ratios compared to both historical average and peer median
- Macro alignment assessed (is this the right macro regime for this asset?)
- Key risks identified (minimum 3)
- For crypto: FDV/MCap dilution risk addressed
- Valuation verdict includes confidence level and catalyst timeline
- Position sizing deferred to Risk Management (this skill does NOT size positions)

## Example

User: "Run fundamental analysis on AAVE token"

### Fundamental Analysis: AAVE

**Asset Classification**
- Type: DeFi Protocol (lending/borrowing)
- Category: Blue-chip DeFi
- Comparable peers: MKR (MakerDAO), COMP (Compound)

**Tokenomics**
- Circulating Supply: 14.9M AAVE
- Total Supply: 16M AAVE (93% circulating — minimal dilution risk)
- FDV/MCap Ratio: 1.07x (excellent — nearly fully diluted)
- Safety Module: 3.5M AAVE staked (23% of supply locked)
- Token utility: Governance + fee discount + Safety Module staking rewards

**Protocol Metrics**
- TVL: $12.2B (largest lending protocol)
- Revenue/day: $820K (annualized: $299M)
- Fees/day: $1.4M (annualized: $511M)
- P/F Ratio: FDV $2.1B / $511M fees = 4.1x
- P/Revenue: FDV $2.1B / $299M revenue = 7.0x
- Active markets: 8 chains (Ethereum, Polygon, Arbitrum, Optimism, Avalanche, Base, BSC, Metis)

**Comparable Analysis**

| Metric | AAVE | MKR | COMP |
|---|---|---|---|
| FDV | $2.1B | $2.5B | $450M |
| TVL | $12.2B | $8.0B | $2.1B |
| P/F Ratio | 4.1x | 13.7x | 8.5x |
| P/Revenue | 7.0x | 15.2x | 14.1x |
| Multi-chain | 8 chains | 5 chains | 4 chains |
| Revenue trend | +45% QoQ | +20% QoQ | -5% QoQ |

AAVE is the cheapest on both P/F and P/Revenue among lending peers, while leading on TVL, multi-chain deployment, and revenue growth.

**Macro Alignment**
- Current regime: Moderate rates, crypto market in expansion phase
- DeFi lending benefits from: higher rates (lending yields attract capital), growing on-chain activity
- Risk factor: regulatory uncertainty around DeFi lending protocols

**Fundamental Score: 8/10**
- Revenue/usage growth: 9/10 (strong QoQ acceleration)
- Profitability: 8/10 (protocol is profitable, revenue accrues partially to stakers)
- Competitive position: 9/10 (market leader in DeFi lending by TVL)
- Macro alignment: 7/10 (favorable but regulatory risk)
- Tokenomics quality: 8/10 (low dilution, staking lock-up, governance utility)

**Verdict: UNDERVALUED** — Confidence: HIGH
- Catalyst: Protocol fee switch expansion + multi-chain TVL growth
- Target range: $180 - $240 (current: $140) — Upside: 28% - 71% based on peer re-rating to average P/F

**Key Risks**
1. Regulatory action against DeFi lending protocols (SEC classification risk)
2. Smart contract exploit on any deployed chain (historical: flash loan attacks)
3. Competitor protocols offering higher yields or better UX pulling TVL

**Next Step**
- → Pass to risk-management for position sizing and stop-loss placement
- → Use technical-analysis for optimal entry timing

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
