---
name: portfolio-management
description: 'Use when constructing, rebalancing, or evaluating multi-asset portfolios — allocation frameworks (equal weight/risk parity/mean-variance/Black-Litterman), core-satellite construction, rebalancing triggers, correlation monitoring, performance attribution, and risk-adjusted metrics.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [portfolio, allocation, rebalancing, risk-parity, black-litterman, correlation, performance, attribution, sharpe, drawdown]
---

# Portfolio Management

This skill provides the comprehensive framework for constructing, maintaining, and evaluating multi-asset portfolios. It operates at the **portfolio level** — above individual trade decisions — handling how capital is allocated across assets, when to rebalance, how to measure performance, and how to manage the interactions between positions. Every portfolio decision must still pass through Risk Management validation.

## When to Use This Skill

- When constructing a new portfolio from scratch
- When deciding how to allocate capital across assets and strategies
- When rebalancing an existing portfolio (calendar-based or threshold-triggered)
- When evaluating portfolio performance and attribution
- When assessing diversification and correlation between holdings
- When integrating multiple asset classes (crypto, equities, stablecoins, DeFi)
- When the user asks "how is my portfolio doing?" or "should I rebalance?"
- When optimizing risk-adjusted returns across the entire portfolio

## What This Skill Does

- **Allocation Framework Selection**: Recommends equal weight, risk parity, mean-variance, or Black-Litterman based on user context
- **Portfolio Construction**: Builds core-satellite or barbell portfolios with specific allocation targets
- **Rebalancing Engine**: Determines when and how to rebalance using calendar, threshold, or tactical triggers
- **Correlation Monitoring**: Tracks rolling correlations and warns of correlation breakdown/convergence
- **Performance Attribution**: Decomposes returns into asset allocation, security selection, and timing effects
- **Risk Reporting**: Calculates Sharpe, Sortino, max drawdown, alpha/beta, and information ratio
- **Multi-Asset Integration**: Coordinates across crypto, equities, stablecoins, and DeFi yield positions
- **Tax Awareness**: Flags tax-loss harvesting opportunities and wash sale considerations

## How to Use

**Portfolio Construction**
- Build me a portfolio with $100,000 across crypto and equities. Moderate risk tolerance.
- What allocation strategy should I use for a crypto-only portfolio?

**Rebalancing**
- My portfolio has drifted from targets. Should I rebalance?
- Rebalance my portfolio using threshold-based rebalancing at 5% drift.

**Performance Review**
- How is my portfolio performing? Give me a full performance report.
- What's driving my portfolio returns this month?

**Optimization**
- Optimize my portfolio for maximum Sharpe ratio with these assets: [list].

## Data Sources

**With MCP/CLI tools connected:**

- Empyrical MCP — Portfolio analytics (Sharpe, Sortino, max drawdown, VaR, beta)
- yFinance MCPs (tooyipjee, maxscheijen, Adity-star) — Historical prices, returns, dividends for equities/ETFs
- OpenBB CLI — Portfolio optimization, factor analysis, risk decomposition
- CoinGecko MCP / CoinGecko Price MCP — Crypto asset prices, correlations, market cap weights
- DeFiLlama MCP — DeFi protocol yields, TVL for DeFi allocation
- Binance MCP / Bybit MCP / OKX MCP — Exchange holdings, position data

**Without tool access:** Ask the user to provide:

- Current portfolio holdings with quantities and current values
- Target allocation or risk tolerance (conservative/moderate/aggressive)
- Total portfolio value
- Time horizon and investment goals
- Any constraints (no leverage, no specific assets, tax considerations)
- Historical returns if available (for performance attribution)

Proceed with analysis using provided data. Note where real-time price data would improve calculations.

## Methodology

### Step 1: Allocation Framework Selection

Choose the allocation methodology based on user sophistication, data availability, and portfolio goals:

```
ALLOCATION FRAMEWORK DECISION TREE
Available data?
├── Only asset list (no historical data)
│   └── EQUAL WEIGHT — simple, robust, no estimation error
│
├── Historical returns and volatility
│   ├── No views/opinions on future returns
│   │   └── RISK PARITY — allocate based on risk contribution
│   │
│   └── Have views on expected returns
│       ├── High confidence in estimates
│       │   └── MEAN-VARIANCE (Markowitz) — classic optimization
│       │
│       └── Moderate confidence, want to blend with market
│           └── BLACK-LITTERMAN — blend views with equilibrium
│
└── Minimum viable: Use EQUAL WEIGHT as starting point, refine later
```

**Framework A: Equal Weight**

```
EQUAL WEIGHT ALLOCATION
  Formula: Weight_i = 1/N for each of N assets

  Advantages:
    - No estimation error (does not require return/vol estimates)
    - Historically competitive with optimized portfolios
    - Simple to implement and rebalance

  Disadvantages:
    - Ignores risk differences between assets
    - Gives same weight to volatile and stable assets
    - Not optimal if you have strong views

  Best for: Beginners, small portfolios, limited data availability
  Typical use: 5-10 assets, each getting 10-20% allocation
```

**Framework B: Risk Parity**

```
RISK PARITY ALLOCATION
  Goal: Each asset contributes EQUAL RISK to the portfolio

  Formula:
    Weight_i = (1/sigma_i) / Sum(1/sigma_j) for all assets j

    Where sigma_i = annualized volatility of asset i

  Example (3 assets):
    BTC:  sigma = 60% → 1/sigma = 1.67
    ETH:  sigma = 75% → 1/sigma = 1.33
    SPY:  sigma = 15% → 1/sigma = 6.67
    Total: 9.67
    Weights: BTC = 17.3%, ETH = 13.8%, SPY = 68.9%

  Advantages:
    - More balanced risk than equal weight
    - Lower drawdowns than market-cap weighting
    - Does not require expected return estimates

  Disadvantages:
    - Overweights low-vol assets (may be bonds/stablecoins)
    - Requires leverage to achieve market-level returns
    - Assumes volatility is a good measure of risk

  Best for: Multi-asset portfolios mixing crypto and traditional assets
```

**Framework C: Mean-Variance (Markowitz)**

```
MEAN-VARIANCE OPTIMIZATION
  Goal: Maximize return for a given level of risk (efficient frontier)

  Inputs required:
    - Expected returns for each asset (mu vector)
    - Covariance matrix (Sigma matrix)
    - Risk-free rate

  Optimization:
    Maximize: Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio StdDev
    Subject to: Sum of weights = 1, 0 <= weight_i <= max_weight

  CRITICAL WARNINGS:
    - Extremely sensitive to expected return estimates
    - Small changes in inputs → large changes in weights
    - Tends to produce concentrated portfolios
    - Use constraints: max weight per asset (e.g., 25%)
    - Use constraints: min weight per asset (e.g., 2%)

  Best for: Sophisticated users with reliable return forecasts
  Practical tip: Use ROBUST optimization or add regularization
```

**Framework D: Black-Litterman**

```
BLACK-LITTERMAN MODEL
  Goal: Blend your views with market equilibrium weights

  Process:
    1. Start with market-cap equilibrium returns (implied by current prices)
    2. Express your views: "BTC will outperform ETH by 5%"
    3. Set confidence in your views (tau parameter, typically 0.025-0.05)
    4. Blend to get posterior expected returns
    5. Optimize using blended returns (more stable than pure Markowitz)

  View types:
    Absolute: "I expect BTC to return 30% annualized" (P = [1,0,...], Q = [0.30])
    Relative: "BTC will outperform ETH by 10%" (P = [1,-1,0,...], Q = [0.10])

  Advantages:
    - More stable than pure mean-variance
    - Allows you to express views with confidence levels
    - Falls back to market equilibrium where you have no views
    - Produces diversified portfolios

  Best for: Users with specific market views who want a disciplined framework
```

### Step 2: Portfolio Construction Templates

**Core-Satellite Approach**

```
CORE-SATELLITE PORTFOLIO
  Core (60-80%): Low-cost, diversified, buy-and-hold
    - BTC and ETH (crypto core)
    - S&P 500 ETF (equity core)
    - Investment-grade bonds or stablecoins (stability core)
  Satellite (20-40%): Active, higher-conviction, tactical
    - Alt-L1 tokens (SOL, AVAX, etc.)
    - DeFi yield farming
    - Momentum or mean-reversion trades
    - Options strategies
    - Prediction market positions

  Rebalancing: Core = quarterly, Satellite = as needed
```

**Barbell Strategy**

```
BARBELL PORTFOLIO
  Conservative End (70-80%): Ultra-safe, capital preservation
    - Stablecoins earning yield (USDC in DeFi, T-bills)
    - BTC in cold storage
    - Money market funds

  Aggressive End (20-30%): High-risk, high-reward
    - Early-stage tokens
    - Leveraged positions (with strict limits)
    - Options strategies (defined risk)
    - Small-cap crypto

  NOTHING in the middle: Avoid medium-risk, medium-return assets
  Rationale: The safe end protects capital; the aggressive end captures upside
```

**Multi-Asset Integration Template**

```
MULTI-ASSET PORTFOLIO (example allocations)

Conservative:
  40% Stablecoins (earning yield: T-bills, DeFi lending)
  25% BTC
  15% ETH
  10% S&P 500 ETF
  10% Investment-grade bonds

Moderate:
  20% Stablecoins (earning yield)
  25% BTC
  20% ETH
  15% Alt-L1 (SOL, AVAX, etc.)
  10% S&P 500 ETF
  5%  DeFi yield (LP positions)
  5%  Satellite trades (momentum, options)

Aggressive:
  10% Stablecoins (dry powder)
  20% BTC
  20% ETH
  20% Alt-L1 and mid-cap crypto
  10% DeFi yield (concentrated LP)
  10% Satellite trades
  5%  Options strategies
  5%  Prediction markets / speculation
```

### Step 3: Rebalancing Framework

```
REBALANCING TRIGGERS (choose one or combine)

1. CALENDAR-BASED
   Frequency: Monthly, quarterly, or semi-annually
   Advantages: Simple, disciplined, removes emotion
   Disadvantages: May rebalance when not needed, may miss needed rebalances
   Best for: Passive, long-term investors

2. THRESHOLD-BASED (RECOMMENDED)
   Trigger: Rebalance when any asset drifts >5% from target weight
   Example: Target 25% BTC → Rebalance if BTC drifts to <20% or >30%
   Advantages: Rebalances only when needed, captures mean reversion
   Disadvantages: Requires monitoring
   Best for: Most active portfolios

3. TACTICAL
   Trigger: Rebalance based on signals (momentum, valuation, sentiment)
   Example: Reduce crypto allocation when Fear & Greed > 80
   Advantages: Can improve returns by timing allocation shifts
   Disadvantages: Introduces bias, easy to overtrade
   Best for: Experienced investors with disciplined signal framework
```

**REBALANCING EXECUTION**
1. Calculate current weights vs. target weights
2. Identify positions to sell (overweight) and buy (underweight)
3. Run trades through risk-management validation
4. Execute trades, preferring limit orders
5. Verify post-rebalance weights match targets (within 0.5%)

Transaction cost awareness:
- Only rebalance if the benefit exceeds transaction costs
- Use "rebalancing bands" — only rebalance the assets that drifted most
- Combine with new cash contributions to reduce selling

### Step 4: Correlation Monitoring

```
CORRELATION FRAMEWORK

ROLLING CORRELATION
  Window: 30-day and 90-day rolling correlation
  Recalculate: Weekly
  Key pairs to monitor:
    BTC <-> ETH: typically 0.75-0.90 (highly correlated)
    BTC <-> SPY: typically 0.30-0.60 (variable)
    BTC <-> Gold: typically -0.10 to 0.30 (low)
    ETH <-> SOL: typically 0.70-0.85 (highly correlated)
    Crypto <-> Tech: typically 0.40-0.70 (moderate)

CORRELATION BREAKDOWN DETECTION
  Warning signs (correlation regime shift):
    - 30-day correlation diverges from 90-day by >0.20
    - Correlation between historically uncorrelated assets rises >0.60
    - All correlations converge toward 1.0 (crisis behavior)

  When correlations spike (crisis mode):
    - Diversification FAILS when you need it most
    - Reduce total portfolio exposure (cash up)
    - Treat highly correlated positions as a single position for sizing
    - Example: If BTC/ETH/SOL correlation = 0.90+, treat combined crypto
      allocation as ONE position, not three

CORRELATION-ADJUSTED POSITION SIZING
  If two positions have correlation rho:
    Combined risk ~ sqrt(w1^2 x sigma1^2 + w2^2 x sigma2^2 + 2 x w1 x w2 x sigma1 x sigma2 x rho)

  Practical rule:
    rho > 0.70: Treat as single position — combined weight <= single position max
    rho 0.30-0.70: Reduce max combined weight by 25%
    rho < 0.30: Positions are diversifying — standard limits apply
```

### Step 5: Performance Attribution

```
PERFORMANCE ATTRIBUTION FRAMEWORK

TOTAL RETURN DECOMPOSITION
  Total Return = Asset Allocation Return + Security Selection Return + Timing Return

  1. ASSET ALLOCATION EFFECT
     How much return came from being in the right asset classes?
     AA_effect = Sum(Portfolio_weight_i - Benchmark_weight_i) x Benchmark_return_i
     Example: Overweighting crypto by 10% when crypto returned 50%
              AA_effect = 10% x 50% = +5.0% contribution

  2. SECURITY SELECTION EFFECT
     How much return came from picking the right assets within each class?
     SS_effect = Sum(Benchmark_weight_i x (Portfolio_return_i - Benchmark_return_i))
     Example: Your crypto picks returned 70% vs. crypto benchmark 50%
              SS_effect = 30% x (70% - 50%) = +6.0% contribution

  3. INTERACTION / TIMING EFFECT
     Residual: Total - AA - SS
     Captures the combined effect of being in the right class AND picking well
```

**ATTRIBUTION REPORTING TEMPLATE**

| Category | Weight | Return | Contribution | Attribution |
|---|---|---|---|---|
| Crypto | 35% | +42% | +14.7% | AA: +2.1%, SS: +3.5% |
| Equities | 30% | +12% | +3.6% | AA: -0.5%, SS: +0.8% |
| DeFi | 15% | +25% | +3.75% | AA: +1.2%, SS: +1.0% |
| Stables | 20% | +5% | +1.0% | AA: -0.3%, SS: +0.1% |
| TOTAL | 100% | -- | +23.05% | -- |

### Step 6: Risk-Adjusted Performance Metrics

**SHARPE RATIO**
```
Formula: (Portfolio Return - Risk-Free Rate) / Portfolio StdDev
Interpretation:
  < 0:   Negative risk-adjusted return (underperforming risk-free)
  0-0.5: Poor risk-adjusted return
  0.5-1: Acceptable
  1-2:   Good
  > 2:   Excellent (verify — may indicate insufficient data or look-back bias)
Period: Calculate on monthly returns, annualize
```

**SORTINO RATIO**
```
Formula: (Portfolio Return - Risk-Free Rate) / Downside StdDev
Better than Sharpe: Only penalizes downside volatility, not upside
Interpretation: Same scale as Sharpe, but typically higher
Use when: Portfolio has asymmetric returns (options, crypto)
```

**MAX DRAWDOWN**
```
Formula: (Peak Value - Trough Value) / Peak Value
Critical metric: Maximum peak-to-trough decline
Recovery time: How long from trough back to peak
Acceptable levels:
  Conservative: Max DD < 10%
  Moderate: Max DD < 20%
  Aggressive: Max DD < 35%
  Crypto-heavy: Max DD < 50% (but this is painful)
```

**ALPHA AND BETA**
```
Beta: Portfolio sensitivity to benchmark
  beta = Cov(Portfolio, Benchmark) / Var(Benchmark)
  beta = 1: Moves with benchmark
  beta > 1: More volatile than benchmark
  beta < 1: Less volatile than benchmark
Alpha: Excess return above beta-adjusted benchmark return
  alpha = Portfolio Return - (Risk-Free + beta x (Benchmark Return - Risk-Free))
  Positive alpha = outperformance after risk adjustment
```

**INFORMATION RATIO**
```
Formula: (Portfolio Return - Benchmark Return) / Tracking Error
Measures: Consistency of outperformance
Interpretation:
  > 0.5: Good active management
  > 1.0: Excellent active management
  < 0: Underperforming the benchmark
```

**CALMAR RATIO**
```
Formula: Annualized Return / Max Drawdown
Measures: Return per unit of tail risk
Good: > 1.0 (return exceeds worst drawdown)
```

### Step 7: Tax-Loss Harvesting Awareness

*Tax awareness only — consult a tax professional.*

```
CONCEPT
  Sell losing positions to realize capital losses
  Use losses to offset capital gains, reducing tax liability
  Reinvest in similar (but not "substantially identical") assets

BASIC RULES (US)
  - Short-term losses offset short-term gains first
  - Long-term losses offset long-term gains first
  - Net losses can offset up to $3,000 of ordinary income per year
  - Excess losses carry forward indefinitely

WASH SALE RULE
  Cannot buy a "substantially identical" security within 30 days
  (before or after the sale = 61-day window)
  Crypto: Wash sale rules currently DO NOT apply to crypto (as of 2024)
          However, this may change — monitor regulatory updates
  Equities: Wash sale rules strictly apply

HARVESTING TRIGGERS
  - Position has unrealized loss > 10%
  - A suitable replacement asset exists (similar exposure, not identical)
  - Realized gains exist that need offsetting
  - Year-end (December) — annual tax-loss harvesting review

TAX LOT MANAGEMENT
  Track cost basis for each purchase lot (FIFO, LIFO, specific identification)
  Use specific identification to choose highest-cost lots for selling
  Automated tracking: Most exchanges provide cost basis reports
```

IMPORTANT: This skill provides awareness only. Tax optimization requires a qualified tax professional. Do not make tax decisions based solely on this framework.

### Step 8: Portfolio Review Schedule

```
REVIEW CADENCE

DAILY (5 minutes)
  - Check portfolio value and daily P&L
  - Monitor any positions with active stops
  - Check for major news events affecting holdings

WEEKLY (30 minutes)
  - Review position weights vs. targets (threshold rebalancing check)
  - Check correlation changes (30-day rolling)
  - Review any DeFi positions for yield changes or risks
  - Update sentiment read via sentiment-analysis

MONTHLY (2 hours)
  - Full performance attribution
  - Calculate risk metrics (Sharpe, Sortino, max drawdown)
  - Rebalance if threshold-based trigger hit
  - Review each position: is the thesis still intact?
  - Update expected returns / views if using Black-Litterman

QUARTERLY (half day)
  - Comprehensive portfolio review
  - Performance attribution vs. benchmark
  - Tax-loss harvesting review
  - Allocation framework reassessment
  - Strategy review: which strategies are working / not working?
  - Risk parameter review: are limits appropriate?
```

## Anti-Patterns

DO NOT do these — they are the most common portfolio management mistakes:

- **Over-rebalancing**: Rebalancing too frequently generates transaction costs and taxes without improving returns. Use 5% threshold minimum — do not rebalance for 1-2% drifts.
- **Ignoring correlation during construction**: A portfolio of 10 highly correlated crypto assets is not diversified. It is one large crypto bet split into 10 pieces. Check correlations before adding assets.
- **Chasing performance**: Increasing allocation to recent winners and cutting recent losers is the opposite of rebalancing. Rebalancing means selling winners and buying losers — it is uncomfortable but effective.
- **No benchmark**: Without a benchmark, you cannot measure performance objectively. Define your benchmark at portfolio construction time (e.g., 60% BTC + 40% SPY, or a custom blend).
- **Ignoring total return**: Comparing only price appreciation while ignoring yield (DeFi, staking, dividends) understates returns for income-generating portfolios.
- **Over-optimization**: Heavily optimized portfolios (Markowitz with no constraints) produce extreme weights that do not perform out-of-sample. Always use position limits and regularization.
- **Emotional allocation changes**: "I feel like crypto is going to pump" is not a portfolio management signal. Use your chosen framework (risk parity, Black-Litterman) and adjust only when your data-driven views change.
- **Not tracking DeFi positions as part of portfolio**: DeFi yield positions, LP tokens, and staked assets are portfolio positions. Include them in total allocation, correlation analysis, and performance attribution.

## Validation Checkpoints

**Input Validation**
- Complete list of current holdings with quantities and values
- Total portfolio value confirmed
- Target allocation defined (or framework selected for calculation)
- Risk tolerance stated (conservative / moderate / aggressive)
- Time horizon specified
- Benchmark defined for performance measurement
- Constraints documented (leverage, excluded assets, tax considerations)
- Historical price data available for key assets (correlation/optimization)

**Output Validation**
- Target weights sum to 100% (within rounding)
- No single position exceeds maximum weight constraint
- Correlation analysis completed for the portfolio
- Risk metrics calculated (Sharpe, max drawdown at minimum)
- Rebalancing trades specified if rebalancing was triggered
- All trades passed through Risk Management validation
- Performance attribution completed with specific methodology cited
- Tax implications flagged for any recommended sells
- Next review date and cadence documented

## Example

User: "I have $200,000. Build me a moderate-risk portfolio across crypto and equities."

### Portfolio Construction: Moderate Risk, $200,000

**Framework: Risk Parity (multi-asset, balanced risk contribution)**

**Target Allocation**

| Asset | Weight | $ Amount | Risk Contribution | Rationale |
|---|---|---|---|---|
| BTC | 20% | $40,000 | 33% of risk | Core crypto, highest liquidity |
| ETH | 12% | $24,000 | 22% of risk | Smart contract platform exposure |
| SOL | 3% | $6,000 | 8% of risk | Alt-L1 satellite, high vol → low weight |
| S&P 500 (VOO) | 30% | $60,000 | 15% of risk | Equity core, lower vol → higher weight |
| Int'l Equity (VXUS) | 10% | $20,000 | 7% of risk | Geographic diversification |
| Stablecoins (yield) | 15% | $30,000 | 5% of risk | Stability + 4-5% yield |
| DeFi Yield (ETH LP) | 5% | $10,000 | 8% of risk | Satellite income |
| Satellite (trades) | 5% | $10,000 | 2% of risk | Active trading allocation |

**Risk Metrics (estimated, based on trailing 1-year data)**
- Expected annual return: 18-24%
- Expected volatility: 22-28%
- Estimated Sharpe: 0.65-0.85
- Expected max drawdown: 20-30%
- Crypto allocation risk: 63% of total risk (from 35% of capital)

**Correlation Matrix (simplified)**

| | BTC | ETH | SOL | VOO | Stable |
|---|---|---|---|---|---|
| BTC | 1.00 | | | | |
| ETH | 0.82 | 1.00 | | | |
| SOL | 0.75 | 0.80 | 1.00 | | |
| VOO | 0.45 | 0.42 | 0.38 | 1.00 | |
| Stable | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |

**Rebalancing Plan**
- Method: Threshold-based, 5% drift trigger
- Check: Weekly (automated if possible)
- Rebalance: Sell overweight, buy underweight
- New cash: Direct to most underweight positions first

**Risk Management Integration**
- Per-trade risk within satellite: 1% of total ($2,000 max loss per trade)
- Max total crypto: 40% (current: 35%)
- Max single asset: 30% (current: VOO at 30% — at limit)
- Portfolio heat monitoring per risk-management framework

**Performance Benchmark**
- Custom: 35% BTC + 30% SPY + 15% USDC yield + 12% ETH + 8% other
- Review: Monthly performance vs. benchmark

**Next Steps**
1. Fund accounts (exchange for crypto, brokerage for equities)
2. Execute initial purchases via limit orders
3. Set up stablecoin yield (Aave, Compound, or similar)
4. Schedule weekly rebalancing check
5. First full review: 30 days from portfolio inception

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
