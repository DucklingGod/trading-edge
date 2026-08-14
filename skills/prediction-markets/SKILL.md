---
name: prediction-markets
description: 'Use when trading prediction markets (Polymarket, Kalshi) or estimating event probabilities — probability from first principles (base rate/Fermi/reference class), edge vs market price, platform mechanics, Kelly sizing, bias detection, arbitrage, bet portfolio construction.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [prediction-markets, polymarket, kalshi, probability, kelly-criterion, arbitrage, forecasting, bias, betting]
---

# Prediction Markets

This skill provides a structured methodology for trading prediction markets — platforms where contracts pay out based on real-world event outcomes. It covers probability estimation from first principles, edge identification against market prices, platform-specific mechanics, bet sizing with Kelly criterion, and common cognitive biases that distort forecasting accuracy.

## When to Use This Skill

- When the user wants to trade on Polymarket, Kalshi, or other prediction platforms
- When estimating the probability of a real-world event
- When evaluating whether a prediction market is mispriced
- When sizing bets on event contracts using Kelly criterion
- When building a portfolio of prediction market positions
- When arbitraging price discrepancies across platforms
- When assessing resolution criteria and counterparty risk
- When the user asks "will X happen?" or "what are the odds of Y?"

## What This Skill Does

- **Probability Estimation**: Derives independent probability estimates using base rates, reference classes, and Fermi estimation
- **Edge Identification**: Compares independent estimate to market price to find mispriced contracts
- **Platform Analysis**: Navigates Polymarket CLOB, Kalshi event contracts, and their specific mechanics
- **Bet Sizing**: Applies Kelly criterion to determine optimal position size given estimated edge
- **Bias Detection**: Identifies and corrects for common forecasting biases
- **Portfolio Construction**: Manages a diversified book of prediction market positions
- **Arbitrage Detection**: Finds cross-platform and intra-market pricing inconsistencies

## How to Use

**Probability Estimation**
- What is the probability that [event] happens by [date]?
- Is the Polymarket contract for [event] at [price] fairly priced?

**Edge Identification**
- The market says [event] is 65% likely. I think it's 80%. Should I bet?

**Platform Trading**
- How do I trade [event] on Polymarket? What are the mechanics?
- Compare Polymarket and Kalshi pricing for [event].

**Portfolio of Bets**
- I have $5,000 to deploy across prediction markets. Build me a portfolio.

## Data Sources

**With MCP/CLI tools connected:**

- Polymarket CLI (pmcli) — Market data, order book depth, contract details, trading
- Onfinance Polymarket MCP — Polymarket analytics, market trends, liquidity data
- Kalshi CLI — Event contract data, order placement, position management
- CoinGecko MCP — Crypto price data (relevant for crypto-outcome markets)
- Hive Crypto MCP — Sentiment and social data for crypto-related predictions

**Without tool access:** Ask the user to provide:

- The specific event and resolution criteria
- Current market price (contract price in cents or probability %)
- Resolution date and any interim checkpoints
- Their independent probability estimate and reasoning
- Capital available for prediction market trading
- Platform (Polymarket, Kalshi, or other)

Proceed with analysis using provided data. Note where real-time market data would improve recommendations.

## Methodology

### Step 1: Probability Estimation Framework

Build an independent probability estimate **BEFORE** looking at the market price. This prevents anchoring bias.

**Method A: Base Rate Analysis**

```
BASE RATE ESTIMATION
  1. Identify the reference class: What category of events is this?
  2. Find the historical base rate: How often do events in this class happen?
  3. Adjust for specifics: What makes THIS event different from the base rate?

  Example: "Will the Fed cut rates at the next meeting?"
    Reference class: All FOMC meetings
    Base rate: Fed cuts rates at ~15% of all meetings (historically)
    Adjustments:
      + Inflation declining toward target (+20%)
      + Unemployment rising (+10%)
      + Forward guidance suggests openness to cuts (+15%)
      - Some inflation metrics still sticky (-5%)
    Adjusted estimate: 15% + 20% + 10% + 15% - 5% = 55%
```

**Method B: Fermi Estimation (Decomposition)**

```
FERMI ESTIMATION
  Break the question into smaller, estimable components.

  Example: "Will Company X acquire Company Y by year-end?"
    P(acquirer is interested) = 70% (based on public statements, strategic fit)
    P(target is willing at reasonable price) = 50% (based on board dynamics)
    P(regulatory approval) = 80% (based on market concentration)
    P(financing available) = 90% (based on acquirer's balance sheet)
    P(no deal-breaking due diligence issue) = 85%

    Combined: 0.70 x 0.50 x 0.80 x 0.90 x 0.85 = 21.4%
```

**Method C: Reference Class Forecasting**

```
REFERENCE CLASS FORECASTING
  1. Identify the broadest relevant reference class
  2. Narrow to the most specific reference class with sufficient data
  3. Use the specific class base rate as the starting point
  4. Adjust by +-5-15% based on unique factors (avoid over-adjustment)

  Example: "Will this tech startup IPO by 2027?"
    Broad class: All venture-backed startups → ~5% IPO rate
    Narrow class: Series C+ tech startups → ~15% IPO rate
    Specific class: Series C+ AI startups → ~20% IPO rate (recent trend)
    Unique adjustments: Strong revenue growth (+5%), competitive market (-3%)
    Estimate: 22%
```

**Method D: Superforecaster Aggregation Heuristic**

```
AGGREGATION APPROACH
  1. Generate 3+ independent estimates using different methods
  2. Weight by method reliability for this type of question
  3. Average (or extremize if estimates cluster)

  Example:
    Base rate method: 55%
    Fermi decomposition: 48%
    Expert analogy: 60%
    Weighted average: (55 x 0.4) + (48 x 0.3) + (60 x 0.3) = 54.4%

  EXTREMIZATION (when forecasters agree):
    If all estimates cluster near 55%, extremize slightly:
    Extremized = 50% + (avg - 50%) x 1.2 = 50% + 4.4% x 1.2 = 55.3%
```

### Step 2: Edge Identification

Compare your independent estimate to the market price:

```
EDGE CALCULATION
  Your estimate: P_you
  Market price: P_market
  Edge = P_you - P_market

  Edge thresholds for action:
    |Edge| < 5%:   NO TRADE — within noise, market likely efficient
    |Edge| 5-10%:  SMALL POSITION — possible edge, low confidence
    |Edge| 10-20%: MODERATE POSITION — meaningful edge
    |Edge| > 20%:  LARGE POSITION — check your work (you might be wrong)
                   Edges > 20% are rare in liquid markets — verify reasoning
```

**EDGE QUALITY ASSESSMENT**

- **High-quality edge:**
  - Based on information the market hasn't fully priced
  - Supported by quantitative data, not just intuition
  - Edge is in your area of expertise
  - Market liquidity is thin (small markets are less efficient)
- **Low-quality edge:**
  - Based on gut feeling or narrative
  - Market is highly liquid with sophisticated participants
  - You have no domain expertise
  - Your estimate relies heavily on one assumption

### Step 3: Platform Mechanics

**Polymarket**

```
POLYMARKET STRUCTURE
  Type: Decentralized prediction market on Polygon
  Order book: Central Limit Order Book (CLOB) — hybrid on/off-chain
  Contracts: Binary outcomes (YES/NO), priced $0.00-$1.00
  Settlement: $1.00 for correct outcome, $0.00 for incorrect
  Collateral: USDC
  Fees: 0% maker / 0% taker (as of current implementation)
  Minimum order: Varies by market

POLYMARKET TRADING MECHANICS
  - Buy YES at $0.65 → You pay $0.65, win $1.00 if YES (profit: $0.35)
  - Buy NO at $0.35 → You pay $0.35, win $1.00 if NO (profit: $0.65)
  - YES price + NO price ~ $1.00 (deviations = arbitrage opportunity)
  - Limit orders available on the CLOB
  - Market orders fill against the book (check depth for slippage)

POLYMARKET CONSIDERATIONS
  - Resolution criteria: Read carefully — some markets have nuanced resolution
  - Resolution source: Who determines the outcome? (UMA oracle, admin, etc.)
  - Liquidity: Check order book depth — thin markets have high slippage
  - No KYC required (crypto-native), but US users face regulatory restrictions
  - Counterparty risk: Smart contract risk on Polygon
```

**Kalshi**

```
KALSHI STRUCTURE
  Type: CFTC-regulated event contract exchange (US-based)
  Contracts: Binary event contracts, priced $0.01-$0.99
  Settlement: $1.00 for correct outcome, $0.00 for incorrect
  Collateral: USD (bank account or debit card)
  Fees: Varies (typically $0.01-0.07 per contract per side)
  Minimum: $1 per contract

KALSHI TRADING MECHANICS
  - Contracts structured as YES/NO binary events
  - Limit and market orders available
  - Portfolio margining available for related contracts
  - Real-time settlement on event resolution
  - API available for programmatic trading

KALSHI CONSIDERATIONS
  - CFTC-regulated: Legal and compliant for US traders
  - KYC required: Full identity verification
  - Fees impact: Factor in fees when calculating edge (need higher edge)
  - Market depth: Some markets are thin — check liquidity before sizing
  - Resolution: Clear, pre-defined resolution criteria
  - Categories: Weather, economics, politics, finance, AI, culture
```

### Step 4: Bet Sizing with Kelly Criterion

```
KELLY CRITERION FOR BINARY OUTCOMES

  f* = (p x b - q) / b

  Where:
    f* = fraction of bankroll to wager
    p  = your estimated probability of winning
    q  = 1 - p (probability of losing)
    b  = net odds received (payout / cost - 1)

  Example:
    Your estimate: 70% chance of YES
    Market price: $0.55 (YES)
    Payout if correct: $1.00
    b = ($1.00 - $0.55) / $0.55 = 0.818
    f* = (0.70 x 0.818 - 0.30) / 0.818 = (0.573 - 0.30) / 0.818 = 33.4%

  PRACTICAL KELLY ADJUSTMENTS
    Full Kelly:    f* (too aggressive — high variance, risk of ruin)
    Half Kelly:    f* / 2 (RECOMMENDED — good balance of growth and safety)
    Quarter Kelly: f* / 4 (conservative — for uncertain edges)

  WHEN TO USE EACH
    Quarter Kelly: Edge estimate is uncertain, limited domain knowledge
    Half Kelly:    Moderate confidence in edge, diversified portfolio
    Full Kelly:    NEVER in practice (theoretical maximum growth)

  EXAMPLE WITH HALF KELLY
    Full Kelly suggests 33.4%
    Half Kelly: 16.7% of prediction market bankroll
    If bankroll is $5,000: bet $835 on this contract
```

**Portfolio Kelly (multiple simultaneous bets):**

```
PORTFOLIO OF BETS
  When holding multiple positions, reduce individual sizing:
    Adjusted size = Half-Kelly x (1 / sqrt(N))
    Where N = number of active positions

  Example: 5 active positions
    Individual adjustment: 1 / sqrt(5) = 0.447
    If Half-Kelly suggests 16.7%: Adjusted = 16.7% x 0.447 = 7.5% per bet

  CORRELATION ADJUSTMENT
    Correlated outcomes (e.g., related political markets):
      Treat correlated bets as ONE position for sizing purposes
      Sum of correlated positions should not exceed single-bet Kelly
    Uncorrelated outcomes:
      Can hold at full adjusted Kelly per position
```

### Step 5: Bias Detection and Correction

**COMMON FORECASTING BIASES**

1. **ANCHORING BIAS**
   - Problem: Your estimate anchors to the market price
   - Fix: Form your estimate BEFORE checking the market price
   - Check: Would your estimate change if the market were 20% different?

2. **FAVORITE-LONGSHOT BIAS**
   - Problem: Overvaluing low-probability events, undervaluing high-probability
   - Pattern: 5% probability events trade at 8-12%, 90% events trade at 85-88%
   - Edge: Sell longshots (short low-probability YES contracts); buy near-certainties (buy high-probability YES contracts)

3. **RECENCY BIAS**
   - Problem: Overweighting recent events in probability estimation
   - Fix: Always start with the base rate, then adjust (not the other way)
   - Check: Would your estimate be different if the most recent data point were removed?

4. **NARRATIVE BIAS**
   - Problem: Compelling stories feel more probable than they are
   - Fix: Assign probabilities to the COMPONENTS, not the narrative
   - Check: Is your estimate driven by a story or by data?

5. **OVERCONFIDENCE**
   - Problem: Believing your edge is larger than it is
   - Fix: Use Quarter-Kelly or Half-Kelly sizing
   - Check: For calibration — are your 80% confidence events correct ~80% of the time?

6. **CONJUNCTION FALLACY**
   - Problem: Multi-step outcomes feel as likely as single-step outcomes
   - Fix: Multiply probabilities — P(A and B) = P(A) x P(B|A)
   - Check: Does your estimate require multiple things to go right?

7. **AVAILABILITY BIAS**
   - Problem: Easy-to-recall events seem more likely
   - Fix: Use base rates from data, not memorable examples
   - Check: Is your estimate influenced by a dramatic recent event?

**DEBIASING CHECKLIST**
- [ ] Formed estimate before checking market price
- [ ] Started with base rate, adjusted incrementally
- [ ] Checked for narrative-driven reasoning
- [ ] Multiplied probabilities for conjunctive events
- [ ] Applied outside view (reference class) not just inside view
- [ ] Considered the opposite outcome — what would make it happen/not happen?
- [ ] Confidence interval: what range of probabilities is reasonable?

### Step 6: Cross-Platform Arbitrage

```
ARBITRAGE DETECTION
  Compare pricing across platforms for the same event:

  Example:
    Polymarket YES: $0.62
    Kalshi YES:     $0.58
    Spread: $0.04

  ARBITRAGE TYPES
  1. Direct arbitrage: Same event, different prices
     Buy cheap, sell expensive (if you have accounts on both)
     Profit = spread - fees - execution risk

  2. Synthetic arbitrage: YES + NO should sum to ~$1.00
     If YES = $0.55 and NO = $0.40:
     Buy both for $0.95, guaranteed $1.00 payout = $0.05 profit

  3. Related-market arbitrage: Outcomes that are mutually exclusive
     If P(A wins) + P(B wins) + P(C wins) > 100% for a 3-candidate race
     Sell overpriced outcomes, buy underpriced

  ARBITRAGE CONSIDERATIONS
  - Fees: Kalshi fees can eat 2-7% of the spread
  - Settlement timing: Capital locked until resolution
  - Counterparty risk: Smart contract risk vs. exchange risk
  - Regulatory risk: Using both platforms may have compliance implications
  - Execution risk: Prices move between legs of the arbitrage
```

### Step 7: Portfolio Construction for Prediction Markets

```
PORTFOLIO RULES
  1. Bankroll: Allocate a fixed amount to prediction markets (e.g., 5-10% of total portfolio)
  2. Diversification: Minimum 5-10 uncorrelated bets at any time
  3. Max single bet: Never more than 15% of prediction market bankroll on one outcome
  4. Category diversification: Spread across politics, economics, crypto, weather, culture
  5. Time diversification: Mix near-term (1-4 weeks) and longer-term (1-6 months) contracts

POSITION MANAGEMENT
  - Review all positions weekly for updated probability estimates
  - If your estimate changes, adjust position size (add or trim)
  - If edge has evaporated (market moved to your estimate), close position
  - If new information contradicts your thesis, close immediately
  - Track hit rate: are your confident bets (>60% edge) resolving correctly?

BANKROLL MANAGEMENT
  - Start with fixed bankroll, do not add more if losing
  - If bankroll drops 25%, pause and review forecasting accuracy
  - If bankroll drops 50%, stop trading and conduct full review
  - Profit withdrawal: Take 50% of profits above starting bankroll quarterly
  - Reinvestment: Other 50% compounds in the bankroll
```

## Anti-Patterns

DO NOT do these — they are the most common prediction market trading mistakes:

- **Anchoring to market price**: Looking at the market price before forming your own estimate guarantees you will anchor. Always estimate independently first.
- **Treating prediction markets like sports betting**: These are not "picks." Edge comes from rigorous probability estimation, not hot takes or gut feelings.
- **Ignoring resolution criteria**: Contracts have specific resolution criteria. "Will X happen?" may resolve differently than you expect. Read the fine print before trading.
- **Oversizing on "sure things"**: Markets priced at 90-95% still lose 5-10% of the time. A 95% contract can still lose, and if you bet your entire bankroll, you are wiped out.
- **Narrative-driven betting**: "I just feel like this will happen" is not an edge. Decompose into components, use base rates, and quantify.
- **Ignoring fees and capital lockup**: Kalshi fees of $0.03-0.07 per contract mean you need a larger edge to be profitable. Capital locked until resolution reduces annual returns.
- **Revenge betting after a loss**: A correct bet can still lose (that is what probability means). Losing a 70% bet does not mean your model is wrong — it means you were in the 30%.
- **Correlated bets without adjustment**: Five bets on related political outcomes are not five independent bets. Size them as one combined position.

## Validation Checkpoints

**Input Validation**
- Event clearly defined with specific resolution criteria
- Resolution date and source identified
- Current market price obtained (both YES and NO sides)
- Platform identified (Polymarket, Kalshi, other)
- Order book depth checked for liquidity
- Independent probability estimate formed BEFORE checking market price
- Estimation method documented (base rate, Fermi, reference class)
- Bankroll size for prediction markets defined

**Output Validation**
- Independent estimate stated with confidence range
- Edge calculated (estimate minus market price)
- Edge meets minimum threshold (>5% for action)
- Kelly criterion applied with appropriate fraction (Half or Quarter)
- Position size within bankroll limits (max 15% single bet)
- Bias checklist completed (anchoring, narrative, overconfidence)
- Resolution criteria confirmed as matching user's intended bet
- Cross-platform comparison done (if available)
- Max loss quantified and acceptable per Risk Management framework
- Exit conditions defined (price target, new information triggers)

## Example

User: "Polymarket has 'Fed cuts rates in June 2026' at $0.42 (42%). I think it's more likely. Should I buy?"

### Prediction Market Analysis: Fed Rate Cut June 2026

**Step 1: Independent Probability Estimate (formed before checking market)**

*Base Rate Analysis*
- Historical: Fed cuts at ~15% of meetings overall
- When hiking cycle paused 6+ months: ~40% chance of cut within 6 months
- When inflation is 2.5-3.5% and trending down: ~50% in relevant meetings

*Fermi Decomposition*
- P(inflation continues declining toward 2%) = 60%
- P(labor market softening enough to justify cut) = 55%
- P(no external shock preventing cut) = 85%
- P(June specifically, not delayed to July/Sept) = 50%
- Combined: 0.60 x 0.55 x 0.85 x 0.50 = 14.0%
- But these are not fully independent, adjust upward: ~30%

*Reference Class (post-hiking pause environments)*
- Similar macro setups historically: 35-45% probability of cut within 3 months of "first viable meeting"
- Estimate: 40%

*Aggregated Estimate*
- Base rate: 40%
- Fermi: 30%
- Reference class: 40%
- Weighted average: 37%

**Step 2: Edge Assessment**
- My estimate: 37%
- Market price: 42% (YES at $0.42)
- Edge: 37% - 42% = -5%
- Direction: Market is ABOVE my estimate — I would lean NO, not YES

**Step 3: Recommendation**
CONTRARY TO USER'S INSTINCT — my analysis suggests the market is slightly OVERPRICING the probability of a June cut.

If anything, consider:
- Buy NO at $0.58 (small position, edge is only ~5%)
- Quarter-Kelly sizing due to low confidence edge

Kelly calculation (for NO side):
- p = 0.63 (my estimate of NO)
- b = ($1.00 - $0.58) / $0.58 = 0.724
- f* = (0.63 x 0.724 - 0.37) / 0.724 = 8.5%
- Quarter-Kelly: 2.1% of prediction bankroll
- If bankroll is $5,000: position = ~$105

**Step 4: Bias Check**
- [x] Estimated before checking market
- [x] Used base rates, not narrative
- [!] User's instinct ("I think it's more likely") may reflect narrative bias — compelling story of rate cuts
- [x] Conjunction checked: multiple conditions must align

**Alternative**: If the user has specific information not in my analysis (e.g., insider Fed communication, breaking economic data), their higher estimate may be justified. Ask what drives their conviction above the base rate.

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
