---
name: options-strategies
description: 'Use when trading options — strategy selection (direction × IV rank × risk tolerance), core strategy specs (covered call, spreads, condors, butterflies, straddles), greeks analysis, IV/skew/term structure, strike & expiration selection, position management (rolling, adjustments), earnings plays, and assignment/pin/liquidity risk.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [options, greeks, implied-volatility, covered-call, iron-condor, spreads, earnings, theta, delta, assignment]
---

# Options Strategies

This skill provides a structured decision framework for selecting, analyzing, and managing options strategies across all market conditions. It translates a directional view + volatility outlook into the optimal strategy, quantifies risk via the greeks, and manages positions through expiration or early exit.

## When to Use This Skill

- When the user has a directional or volatility view and wants to express it with options
- When evaluating whether to buy or sell options (premium payer vs. collector)
- When analyzing an options chain for a specific stock or ETF
- When constructing multi-leg strategies (spreads, condors, butterflies)
- When managing existing options positions (rolling, adjusting, closing)
- When planning earnings trades with IV expansion/crush dynamics
- When assessing greeks exposure on a portfolio of options positions
- When comparing the risk/reward of an options trade vs. stock/futures

## What This Skill Does

- **Strategy Selection**: Maps market outlook (direction + volatility + timeframe) to the optimal options strategy
- **Greeks Analysis**: Calculates and interprets delta, gamma, theta, vega, and rho for any position
- **IV Assessment**: Evaluates implied volatility rank/percentile to determine if options are cheap or expensive
- **Position Construction**: Determines strikes, expirations, and leg ratios for multi-leg strategies
- **Risk Quantification**: Calculates max loss, max gain, breakeven points, and probability of profit
- **Position Management**: Provides rolling, adjustment, and early exit decision frameworks
- **Earnings Play Design**: Structures pre-earnings and post-earnings strategies around IV dynamics

## How to Use

**Strategy Selection**
- What options strategy should I use for [ticker]? I'm [bullish/bearish/neutral] and expect [high/low] volatility.
- I want to generate income on my 100 shares of [ticker]. What are my options?

**Greeks Analysis**
- Analyze the greeks for a [strategy] on [ticker] with [strike] expiring [date].

**Earnings Plays**
- [Ticker] reports earnings on [date]. What options strategy captures the IV crush?

**Position Management**
- I'm holding a [strategy] on [ticker] that's [profitable/losing]. Should I roll, adjust, or close?

## Data Sources

**With MCP/CLI tools connected:**

- yFinance MCPs (tooyipjee, maxscheijen, Adity-star) — Options chains, IV data, historical prices, earnings dates
- OpenBB CLI — Options flow, unusual activity, options analytics
- tastytrade-cli — Options execution, portfolio greeks, position management
- Empyrical MCP — Portfolio-level risk metrics for options portfolios

**Without tool access:** Ask the user to provide:

- Underlying ticker, current price, and their directional view
- Options chain data (strikes, expirations, bid/ask, IV)
- Current IV rank or IV percentile (or recent IV range)
- Account size and risk tolerance
- Time horizon for the trade
- Earnings date (if relevant)

Proceed with analysis using provided data. Note where real-time chain data would improve recommendations.

## Methodology

### Step 1: Strategy Selection Decision Tree

Navigate this tree based on the user's market outlook:

```
MARKET VIEW
├── BULLISH
│   ├── High IV (IV Rank > 50)
│   │   ├── Conservative → Bull Put Spread (credit)
│   │   ├── Moderate → Short Put (cash-secured)
│   │   └── Aggressive → Bull Call Spread (debit) + Short Put
│   └── Low IV (IV Rank < 50)
│       ├── Conservative → Long Call (ITM, high delta)
│       ├── Moderate → Bull Call Spread (debit)
│       └── Aggressive → Long Call (OTM)
│
├── BEARISH
│   ├── High IV (IV Rank > 50)
│   │   ├── Conservative → Bear Call Spread (credit)
│   │   ├── Moderate → Short Call Spread + Long Put Spread
│   │   └── Aggressive → Bear Put Spread (debit)
│   └── Low IV (IV Rank < 50)
│       ├── Conservative → Long Put (ITM, high delta)
│       ├── Moderate → Bear Put Spread (debit)
│       └── Aggressive → Long Put (OTM)
│
├── NEUTRAL
│   ├── High IV (IV Rank > 50)
│   │   ├── Range-bound → Iron Condor / Iron Butterfly
│   │   ├── Slight bias → Jade Lizard / Broken Wing Butterfly
│   │   └── Income → Short Strangle (defined risk: Iron Condor)
│   └── Low IV (IV Rank < 50)
│       ├── Expecting breakout → Long Straddle / Long Strangle
│       ├── Calendar play → Calendar Spread / Diagonal
│       └── Butterfly → Long Butterfly (cheap with low IV)
│
└── VOLATILE (expecting big move, direction unknown)
    ├── High IV → Avoid or use ratio spreads
    ├── Low IV → Long Straddle / Long Strangle
    └── Pre-earnings → Calendar or Diagonal (sell short-dated, buy longer)
```

### Step 2: Core Strategy Specifications

**Income / Premium-Selling Strategies**

| Strategy | Legs | Max Profit | Max Loss | Best When |
|---|---|---|---|---|
| Covered Call | +100 shares, -1 OTM call | Premium + (strike - stock price) | Stock to $0 minus premium | Neutral-bullish, high IV |
| Cash-Secured Put | -1 OTM put, cash collateral | Premium received | Strike price - premium | Bullish, want to own at lower price |
| Bull Put Spread | -1 put (higher), +1 put (lower) | Net credit | Width - credit | Bullish, high IV |
| Bear Call Spread | -1 call (lower), +1 call (higher) | Net credit | Width - credit | Bearish, high IV |
| Iron Condor | Bull put spread + Bear call spread | Total credit | Width - credit (one side) | Neutral, high IV, range-bound |
| Iron Butterfly | -1 ATM put, -1 ATM call, +1 OTM put, +1 OTM call | Total credit | Width - credit | Neutral, high IV, pinning expected |
| Short Strangle | -1 OTM put, -1 OTM call | Total credit | Unlimited (undefined) | Neutral, high IV, small account NOT suitable |

**Directional Strategies**

| Strategy | Legs | Max Profit | Max Loss | Best When |
|---|---|---|---|---|
| Long Call | +1 call | Unlimited | Premium paid | Bullish, low IV |
| Long Put | +1 put | Strike - premium | Premium paid | Bearish, low IV |
| Bull Call Spread | +1 call (lower), -1 call (higher) | Width - debit | Debit paid | Bullish, moderate IV |
| Bear Put Spread | +1 put (higher), -1 put (lower) | Width - debit | Debit paid | Bearish, moderate IV |
| Diagonal Spread | +1 longer-dated, -1 shorter-dated (diff strikes) | Variable | Debit paid (approx) | Directional + time decay |

**Volatility Strategies**

| Strategy | Legs | Profits When | Max Loss | Best When |
|---|---|---|---|---|
| Long Straddle | +1 ATM call, +1 ATM put | Big move either direction | Total premium | Expecting vol expansion, low IV |
| Long Strangle | +1 OTM call, +1 OTM put | Big move either direction | Total premium | Expecting vol expansion, cheaper |
| Calendar Spread | -1 near-term, +1 same-strike far-term | Time passes, stock stays near strike | Debit paid | Neutral, low near-term IV |
| Butterfly Spread | +1 lower, -2 middle, +1 upper | Stock pins at middle strike | Debit paid | Neutral, expecting pinning |

### Step 3: Greeks Analysis Framework

The greeks measure how an option's price changes with respect to different variables:

**DELTA — Directional Risk**
- Definition: $ change in option price per $1 change in underlying
- Range: Calls 0 to +1, Puts 0 to -1
- Key levels:
  - ATM options: ~0.50 delta
  - Deep ITM: ~0.90-1.00 delta (behaves like stock)
  - Far OTM: ~0.05-0.10 delta (lottery ticket)
- Portfolio delta: Sum of all position deltas x contract multiplier
- Delta-neutral: Total portfolio delta ~ 0

**GAMMA — Acceleration of Delta**
- Definition: Rate of change of delta per $1 move in underlying
- Key insight: Gamma is highest for ATM options near expiration
- Risk: Short gamma positions face accelerating losses on large moves
- Gamma risk amplifies in the last 7-14 DTE (days to expiration)
- Management: Close short gamma positions before 14 DTE if possible

**THETA — Time Decay**
- Definition: $ lost per day from time passage (all else equal)
- Key insight: Theta accelerates as expiration approaches
- Decay curve:
  - 60-45 DTE: ~1.5% of premium per day
  - 45-30 DTE: ~2.5% of premium per day
  - 30-14 DTE: ~4% of premium per day
  - 14-0 DTE: ~6-10% of premium per day
- Sellers benefit from theta; buyers fight theta

**VEGA — Volatility Sensitivity**
- Definition: $ change in option price per 1% change in IV
- Key insight: Longer-dated options have higher vega
- Application:
  - High IV → sell options (collect rich premium, benefit from IV contraction)
  - Low IV → buy options (cheap premium, benefit from IV expansion)
- Vega is highest for ATM options

**RHO — Interest Rate Sensitivity**
- Definition: $ change per 1% change in risk-free rate
- Relevance: Minor for short-dated options; matters for LEAPS (>6 months)
- Rising rates: Benefits long calls, hurts long puts

**Portfolio Greeks Summary Table:**

| Position | Delta | Gamma | Theta | Vega |
|---|---|---|---|---|
| Long call | + | + | - | + |
| Short call | - | - | + | - |
| Long put | - | + | - | + |
| Short put | + | - | + | - |
| Long stock | +1 | 0 | 0 | 0 |

### Step 4: Implied Volatility Analysis

IV assessment determines whether options are "cheap" or "expensive" relative to history:

**IV RANK**
- Formula: (Current IV - 52-week Low IV) / (52-week High IV - 52-week Low IV)
- Range: 0% to 100%
- Interpretation:
  - 0-25%: LOW IV — options are cheap, favor buying strategies
  - 25-50%: BELOW AVERAGE — slight preference for buying
  - 50-75%: ABOVE AVERAGE — slight preference for selling
  - 75-100%: HIGH IV — options are expensive, favor selling strategies

**IV PERCENTILE**
- Definition: % of days in the past year with IV lower than current IV
- More robust than IV rank (not skewed by single IV spike)
- Interpretation: same directional guidance as IV rank

**VOLATILITY SMILE/SKEW**
- Definition: IV varies across strikes for the same expiration
- Equity skew: OTM puts have higher IV than OTM calls (crash protection)
- Skew steepness indicates:
  - Steep skew: Market pricing high downside risk → bearish sentiment
  - Flat skew: Market complacent about tail risk
- Trading skew:
  - Sell expensive skew (OTM puts) via put spreads
  - Buy cheap skew (OTM calls) when skew is flat before potential breakouts

**TERM STRUCTURE**
- Definition: IV across different expirations
- Contango: Near-term IV < far-term IV (normal, stable market)
- Backwardation: Near-term IV > far-term IV (fear, event-driven)
- Calendar spreads profit from contango normalization

### Step 5: Strike and Expiration Selection

**Strike selection by strategy goal:**

| Goal | Strike Selection | Delta Target |
|---|---|---|
| High probability income | 1-2 standard deviations OTM | 0.15-0.25 delta |
| Balanced risk/reward | 0.5-1 standard deviation OTM | 0.30-0.40 delta |
| Directional conviction | ATM or slightly ITM | 0.45-0.60 delta |
| Cheap directional bet | 1.5-2 standard deviations OTM | 0.10-0.20 delta |
| Stock replacement | Deep ITM | 0.70-0.85 delta |

**Expiration selection guidelines:**

PREMIUM SELLERS (theta positive):
- Ideal DTE: 30-45 days
- Rationale: Theta decay accelerates while gamma risk is manageable
- Avoid: <14 DTE (gamma risk too high), >60 DTE (capital tied up too long)

PREMIUM BUYERS (theta negative):
- Ideal DTE: 60-90 days (for swing trades)
- Rationale: Slower time decay, more time for thesis to play out
- LEAPS: 6-12 months for long-term directional views
- Avoid: <30 DTE unless scalping (time decay destroys value)

EARNINGS PLAYS:
- Pre-earnings: Enter 7-14 days before, target IV expansion
- Post-earnings: Enter day of, capture IV crush
- Calendar: Sell pre-earnings weekly, buy post-earnings monthly

SPREAD WIDTH:
- Vertical spreads: Width = max loss you are willing to accept + credit
- Iron condors: Wing width typically 3-5 strikes ($3-$5 wide per side)
- Butterflies: Wings typically 5-10 points apart depending on price

### Step 6: Position Management

**When to roll an options position:**

```
ROLLING RULES
  1. ROLL when trade is profitable and you want to extend duration
     - Roll when the short option reaches 50% of max profit
     - Roll to same or further expiration, same or better strike
  2. ROLL when trade is challenged (tested) but thesis intact
     - Roll out in time (further expiration) for additional credit
     - Roll out AND away from the tested side if possible
  3. DO NOT ROLL if:
     - The resulting position has worse risk/reward than a new trade
     - Total credits collected approach max loss (diminishing returns)
     - Underlying thesis has changed
  4. MAXIMUM ROLLS: 2 times per position. After 2 rolls, close and re-evaluate.
```

**PROFIT TARGETS BY STRATEGY**
- Iron condors / credit spreads: Close at 50% of max profit
- Short puts / covered calls: Close at 50-75% of max profit
- Long options: Take profits at 50-100% gain on premium
- Straddles / strangles: Take profits at 25-50% gain (IV expansion)
- Calendars: Close at 25-50% gain or when near-term expires

**LOSS LIMITS**
- General rule: Close at 2x credit received (e.g., received $2.00, close at $4.00 loss)
- Alternatively: Close when the loss equals the width of the spread minus original credit
- Never hold to expiration hoping for recovery — manage mechanically

**Adjustment techniques:**

IRON CONDOR ADJUSTMENTS:
- If put side tested:
  1. Roll put spread down and out for credit
  2. Add a long put below for disaster protection
  3. Close put side, keep call side running (becomes bear call spread)
- If call side tested:
  1. Roll call spread up and out for credit
  2. Close call side, keep put side running (becomes bull put spread)

VERTICAL SPREAD ADJUSTMENTS:
- If tested:
  1. Roll entire spread out in time for credit
  2. Widen the spread (accept more risk) for more credit
  3. Add an opposite spread to convert to iron condor

LONG OPTION ADJUSTMENTS:
- If profitable:
  1. Sell an OTM option against it (convert to vertical spread, lock in some profit)
  2. Roll up/down to a higher/lower strike, banking some profit
- If losing:
  1. Sell a closer-to-the-money option against it (reduce cost basis)
  2. Roll out in time if thesis is intact
  3. Close and re-enter at better levels

### Step 7: Earnings Play Framework

**PRE-EARNINGS IV EXPANSION**
- Strategy: Buy options 7-14 days before earnings
- Mechanism: IV typically rises 20-50% as earnings approach
- Exit: BEFORE earnings announcement (sell the IV expansion)
- Best with: Straddles, strangles, or calendars
- Risk: Stock moves against you faster than IV rises

**POST-EARNINGS IV CRUSH**
- Strategy: Sell options just before or at earnings
- Mechanism: IV drops 30-60% after earnings (uncertainty removed)
- Structures: Iron condors, short straddles, short strangles
- Risk: Stock moves more than the expected move (priced in via straddle)

**EXPECTED MOVE CALCULATION**
```
Expected Move = ATM Straddle Price x 0.85
(or use: Front-month ATM straddle price as approximation)

Example:
  Stock at $100, ATM straddle costs $8.00
  Expected move: ~$6.80 (+-6.8%)
  Iron condor: sell strikes outside $93.20 and $106.80
```

**EARNINGS PLAY CHECKLIST**
- [ ] Calculate expected move from straddle price
- [ ] Check historical earnings moves (does stock regularly exceed expected?)
- [ ] Assess IV rank — is current IV already elevated?
- [ ] Size position for max loss scenario (stock gaps beyond your strikes)
- [ ] Plan exit: pre-earnings (IV expansion play) or hold through (IV crush play)
- [ ] Never risk more than 1-2% of portfolio on a single earnings play

### Step 8: Options-Specific Risk Factors

**ASSIGNMENT RISK**
- American-style options can be exercised early
- Highest risk: Short ITM options near ex-dividend date
- Management: Close or roll short options that go ITM before ex-div
- Spread protection: Long option protects against assignment on short option

**PIN RISK**
- At expiration, stock hovers near a short strike
- Risk: Uncertain assignment — may or may not be assigned
- Management: Close positions before 3:00 PM ET on expiration day
- Never let short options expire at-the-money

**LIQUIDITY RISK**
- Wide bid-ask spreads increase cost of entry and exit
- Rules:
  - Bid-ask spread < 10% of option price (liquid enough)
  - Open interest > 100 contracts per strike (minimum)
  - Prefer weekly options on liquid names (SPY, QQQ, AAPL, etc.)
  - Avoid illiquid options on small-cap stocks

**EARLY EXERCISE CONSIDERATIONS**
- Calls: Rarely exercise early unless deep ITM before ex-dividend
- Puts: May exercise early if deep ITM and time value < interest savings
- Spreads: Assignment on short leg may leave you with naked long — manage immediately

**MAX LOSS SCENARIOS**
- Always calculate and accept max loss before entering:
  - Vertical spread: Width - credit received
  - Iron condor: Width of wider side - total credit
  - Long option: Premium paid (100% loss possible)
  - Naked short: Theoretically unlimited (short calls) or substantial (short puts)
- NEVER sell naked options without understanding and accepting worst-case

## Anti-Patterns

DO NOT do these — they are the most common options trading mistakes:

- **Selling naked options without margin capacity**: Naked short calls have unlimited risk. Naked short puts can require buying stock at the strike. Always know your max loss and ensure margin covers worst case.
- **Buying OTM options as lottery tickets**: Far OTM options with <14 DTE have very low probability of profit. Time decay destroys value rapidly. If buying OTM, give yourself 60+ DTE.
- **Ignoring IV rank when choosing strategy**: Buying options when IV rank is >75% means you are overpaying. Selling options when IV rank is <25% means you are collecting thin premium. Match strategy to IV environment.
- **Holding through earnings without planning**: IV crush after earnings can destroy 30-60% of an option's value overnight. Have a clear pre-earnings vs. post-earnings plan.
- **Not closing at profit targets**: Greed turns winners into losers. Close credit spreads at 50% max profit. The last 50% of profit carries disproportionate risk.
- **Rolling indefinitely**: Rolling a losing position 3, 4, 5 times turns a small loss into a large one. Maximum 2 rolls, then close and re-evaluate.
- **Trading illiquid options**: Wide bid-ask spreads mean you lose money on entry and exit. Stick to options with open interest >100 and tight spreads.
- **Ignoring position sizing**: Options provide leverage. A 100-share equivalent options position on a $200 stock controls $20,000 of stock. Size options trades based on max loss, not premium paid.

## Validation Checkpoints

**Input Validation**
- Underlying ticker, current price, and directional view confirmed
- IV rank or IV percentile assessed (or historical IV range provided)
- Options chain data available (strikes, expirations, bid/ask)
- Account size and buying power known
- Time horizon for the trade defined
- Earnings date checked (if within expiration window)
- Liquidity verified (bid-ask spread, open interest)

**Output Validation**
- Strategy selected with clear rationale (direction + IV + risk tolerance)
- All legs specified: strikes, expirations, quantities, debit/credit
- Max profit, max loss, and breakeven points calculated
- Greeks reported for the combined position (delta, theta, vega at minimum)
- Probability of profit estimated (if data available)
- Profit target and loss limit defined with specific prices
- Rolling/adjustment plan documented for if the trade is challenged
- Position size validated through Risk Management framework
- Max loss as % of portfolio confirmed within risk tolerance

## Example

User: "AAPL is at $185 and I think it stays range-bound for the next month. IV rank is 72%. What strategy should I use with my $80,000 portfolio?"

### Options Strategy: AAPL Neutral / High IV

**Strategy Selection**
- View: Neutral (range-bound)
- IV Rank: 72% (HIGH — favor selling premium)
- Decision Tree: Neutral → High IV → Range-bound → Iron Condor

**Position Construction: Iron Condor**
- Sell 175 Put / Buy 170 Put (bull put spread, $5 wide)
- Sell 195 Call / Buy 200 Call (bear call spread, $5 wide)
- Expiration: 35 DTE (optimal theta decay window)
- Credit received: $1.85 (combined)
- Contracts: 2 (based on risk sizing below)

**Risk Metrics**
- Max profit: $1.85 x 100 x 2 = $370 (if AAPL stays between $175-$195)
- Max loss: ($5.00 - $1.85) x 100 x 2 = $630 (if AAPL breaks either side)
- Breakeven: $173.15 (lower) / $196.85 (upper)
- Probability of profit: ~68% (based on delta of short strikes)
- Width of range: $175-$195 = $20 (10.8% of stock price)

**Greeks (combined position, 2 contracts)**
- Delta: +0.02 (nearly neutral)
- Theta: +$4.20/day (collecting ~$4/day in time decay)
- Vega: -$8.50 (benefits from IV contraction — aligned with high IV rank)
- Gamma: -0.03 (short gamma — risk if stock makes large move)

**Risk Validation (via risk-management)**
- Max loss: $630 = 0.79% of $80,000 portfolio (under 2% limit)
- Buying power required: ~$1,000 (margin for one side)
- Portfolio impact: Minimal

**Management Plan**
- Profit target: Close at 50% max profit ($0.93 credit to buy back) = ~$185 profit
- Loss limit: Close if loss reaches 2x credit ($3.70 to buy back) = ~$370 loss
- Adjustment: If one side tested, close that side and let the other expire
- Timeline: Close by 14 DTE regardless (avoid gamma risk)
- Earnings check: Confirm no AAPL earnings within 35 DTE window

**Recommendation**
APPROVED. Iron condor is well-suited for neutral view + high IV. Expected return: $185 (50% target) over 17-21 days. Max risk: $630 (0.79% of portfolio).

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
