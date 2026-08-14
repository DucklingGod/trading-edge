---
name: trade-risk-management
description: 'Use before ANY trade — mandatory risk gatekeeper: position sizing (fixed fractional/ATR/Kelly/equal risk), stop-loss design, R:R validation, portfolio risk checks (concentration/correlation/heat), drawdown management, leverage framework, and agent guardrails with kill switches.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [risk-management, position-sizing, stop-loss, risk-reward, drawdown, leverage, kelly-criterion, agent-guardrails, portfolio-risk]
---

# Risk Management

This skill is the **mandatory gatekeeper** for all trade workflows. No position should be opened, sized, or modified without passing through the risk validation framework defined here. It covers the full risk hierarchy — from per-trade sizing to portfolio-level exposure limits — and includes special guardrails for autonomous trading agents.

## When to Use This Skill

- Before opening ANY new position (mandatory)
- When sizing a position for a specific trade setup
- When setting or adjusting stop-loss levels
- When evaluating risk/reward of a proposed trade
- When assessing portfolio-level risk exposure
- When managing a drawdown or losing streak
- When evaluating leverage on any position
- When an autonomous agent is about to execute a trade
- When reviewing risk parameters for an existing strategy

## What This Skill Does

- **Position Sizing**: Calculates optimal position size using Kelly Criterion, fixed fractional, or volatility-adjusted methods
- **Stop-Loss Design**: Determines stop-loss placement using ATR, technical levels, or time-based methods
- **Risk/Reward Assessment**: Validates minimum R:R ratios by strategy type
- **Portfolio Risk Check**: Enforces concentration limits, correlation-adjusted exposure, and max drawdown thresholds
- **Drawdown Management**: Applies position reduction schedules during drawdowns
- **Leverage Framework**: Assesses leverage risk with liquidation price calculations
- **Agent Guardrails**: Enforces autonomous agent-specific risk limits and kill switches
- **Risk Validation Gate**: Runs mandatory pre-trade checklist — blocks execution if any critical check fails

## How to Use

**Position Sizing**
- Size a position for [asset] with entry at [price] and stop at [stop price]
- How much [asset] should I buy with a $50,000 portfolio risking 2% per trade?

**Risk Assessment**
- Assess risk/reward for going long [asset] at [entry] targeting [target] with stop at [stop]
- Portfolio risk check — show my current exposure and concentration

**Drawdown Management**
- I'm down 15% this month. What should I adjust?

**Agent Risk Check**
- Validate this agent trade: buy 0.5 BTC at $67,000 with 3x leverage

## Data Sources

**With MCP/CLI tools connected:**

- Empyrical MCP — Portfolio risk metrics (Sharpe, Sortino, max drawdown, VaR)
- yFinance MCPs (tooyipjee, maxscheijen, Adity-star) — Historical volatility, price data for ATR calculation
- CoinGecko MCP / CoinGecko Price MCP — Crypto asset volatility, correlation data
- Binance MCP / Bybit MCP / OKX MCP — Real-time position data, margin levels, liquidation prices
- OpenBB CLI — Portfolio analytics, risk decomposition
- DexScreener / DeFiLlama — DeFi protocol TVL, liquidity depth for slippage estimation

**Without tool access:** Ask the user to provide:

- Portfolio size (total capital)
- Current open positions and their sizes
- Entry price, stop-loss level, and target for the proposed trade
- Asset's recent volatility (or approximate ATR)
- Current drawdown percentage (if any)
- Leverage being used (if any)

Proceed with full analysis using provided data. Note which metrics are calculated vs. user-provided.

## Methodology

### Step 1: Establish the Risk Hierarchy

Risk is managed at four levels. Higher levels override lower levels.

```
Portfolio Level (max 20-25% total risk budget)
  └── Asset-Class Level (max allocation per asset class)
       └── Strategy Level (max allocation per strategy)
            └── Per-Trade Level (max 1-2% risk per trade)
```

**Hard limits by account type:**

| Level | Conservative | Moderate | Aggressive |
|---|---|---|---|
| Per-trade risk | 0.5% | 1-2% | 2-3% |
| Max correlated exposure | 5% | 10% | 15% |
| Max single-asset exposure | 10% | 20% | 30% |
| Max total portfolio heat | 10% | 20% | 30% |
| Max drawdown before pause | 10% | 15% | 25% |

### Step 2: Calculate Position Size

Choose the appropriate sizing method based on the strategy:

**Method A: Fixed Fractional (Default — Simplest)**
```
Position Size = (Account × Risk%) / (Entry - Stop)

Example:
  Account: $100,000
  Risk per trade: 1% = $1,000
  Entry: $50.00
  Stop: $47.00
  Risk per unit: $3.00
  Position Size: $1,000 / $3.00 = 333 shares
  Position Value: 333 × $50.00 = $16,650 (16.65% of account)
```

**Method B: Volatility-Adjusted (ATR-Based)**
```
Stop Distance = N × ATR(14)  [typically N = 1.5 to 3.0]
Position Size = (Account × Risk%) / (N × ATR)

Example:
  Account: $100,000
  Risk per trade: 1% = $1,000
  BTC ATR(14): $2,500
  N = 2.0
  Stop Distance: 2.0 × $2,500 = $5,000
  Position Size: $1,000 / $5,000 = 0.2 BTC
```

**Method C: Kelly Criterion (For Strategies with Known Edge)**
```
Kelly% = (Win% × Avg_Win / Avg_Loss - Loss%) / (Avg_Win / Avg_Loss)
Half-Kelly (recommended) = Kelly% / 2

Example:
  Win rate: 55%
  Average win: $2,000
  Average loss: $1,000
  Win/Loss ratio: 2.0
  Kelly% = (0.55 × 2.0 - 0.45) / 2.0 = 0.325 = 32.5%
  Half-Kelly = 16.25%
```

WARNING: Full Kelly is extremely aggressive. Always use Half-Kelly or Quarter-Kelly in practice. Kelly requires accurate win rate and payoff estimates — if these are uncertain, default to Fixed Fractional.

**Method D: Equal Risk Contribution (Portfolio Context)**
```
Weight_i = (1 / Volatility_i) / Σ(1 / Volatility_j)
```
Useful for: Multi-asset portfolios where you want each position to contribute equal risk.

### Step 3: Determine Stop-Loss Placement

Select stop method based on strategy type:

| Strategy Type | Primary Stop Method | Backup Method |
|---|---|---|
| Trend-following | ATR trailing (2-3× ATR) | Swing low/high |
| Mean reversion | Fixed % (tight, 1-2%) | Time-based (3-5 bars) |
| Breakout | Below breakout level | ATR-based |
| DeFi yield | IL threshold + TVL drop | Smart contract risk event |
| Prediction markets | Probability threshold | Time-based (event deadline) |
| Scalping | Fixed ticks/pips | Time-based (seconds/minutes) |

**ATR-based stops (preferred for most strategies):**
```
Long Stop = Entry - (Multiplier × ATR14)
Short Stop = Entry + (Multiplier × ATR14)

Conservative: 3.0× ATR (wider, fewer stopped out)
Standard:     2.0× ATR (balanced)
Aggressive:   1.5× ATR (tighter, more stopped out)
```

**Trailing stop adjustment:**
```
Trailing Stop = Highest High since entry - (Multiplier × ATR14)
Update: Only move stop UP (longs) or DOWN (shorts), never against the trade
```

### Step 4: Validate Risk/Reward Ratio

**Minimum acceptable R:R by strategy type:**

| Strategy | Min R:R | Typical Win Rate | Expectancy Check |
|---|---|---|---|
| Trend-following | 2:1 | 35-45% | Wins are large, losses are small |
| Mean reversion | 1.5:1 | 55-65% | Higher win rate compensates |
| Breakout | 3:1 | 25-35% | Most breakouts fail — need large winners |
| Scalping | 1:1 | 60-70% | Volume of trades compensates |
| DeFi yield | 2:1 | N/A (yield vs IL) | Annual yield > expected IL + risk |
| Prediction markets | 1.5:1 | Depends on edge | Expected value must be positive |

**Expectancy formula:**
```
Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
Must be positive. If negative, DO NOT TAKE THE TRADE.

Example:
  Win rate: 40%, Avg win: $3,000
  Loss rate: 60%, Avg loss: $1,000
  Expectancy = (0.40 × $3,000) - (0.60 × $1,000) = $1,200 - $600 = $600
  Per-trade expected value: +$600 ✓
```

### Step 5: Portfolio-Level Risk Controls

Run these checks against the entire portfolio before approving a new trade:

**Portfolio Risk Checklist**

1. **CONCENTRATION CHECK**
   - No single position > 20% of portfolio (crypto: 10%)
   - No single sector/protocol > 30% of portfolio
   - Top 3 positions < 50% of portfolio

2. **CORRELATION CHECK**
   - Sum of highly correlated positions (ρ > 0.7) < 25% of portfolio
   - Example: BTC + ETH + SOL are highly correlated — treat as one bucket
   - Crypto + tech stocks often correlate — check cross-asset correlation

3. **PORTFOLIO HEAT**
   - Total open risk (sum of all position risk%) < 20% of portfolio
   - Calculation: Σ(position_size × distance_to_stop / portfolio_value)

4. **LIQUIDITY CHECK**
   - Position size < 1% of asset's daily volume (equities)
   - Position size < 0.5% of asset's daily volume (crypto)
   - DeFi: Position < 5% of pool liquidity

5. **MARGIN/LEVERAGE CHECK**
   - Total margin used < 50% of available margin
   - No single position using > 5x leverage (crypto: 3x max recommended)
   - Maintenance margin buffer > 50% above liquidation

### Step 6: Drawdown Management

When portfolio hits drawdown thresholds, automatically reduce risk:

| Drawdown | Action | New Per-Trade Risk |
|---|---|---|
| 0-5% | Normal trading | 1-2% |
| 5-10% | Reduce position sizes by 25% | 0.75-1.5% |
| 10-15% | Reduce position sizes by 50%, no new positions | 0.5-1% |
| 15-20% | Close weakest 50% of positions, paper trade only | 0% live |
| 20%+ | FULL STOP — close all positions, mandatory review | 0% |

**Recovery rules:**
- After a 10%+ drawdown, require 5 consecutive profitable paper trades before resuming live
- After a 20%+ drawdown, mandatory 2-week cooling period + strategy review
- Scale back into live trading at 50% normal size, increase by 25% every 5 profitable trades

### Step 7: Leverage Risk Framework

If leverage is being used, add these additional checks:

**LIQUIDATION DISTANCE**
```
Liq Price (Long) = Entry × (1 - 1/Leverage + Maintenance Margin%)
Liq Price (Short) = Entry × (1 + 1/Leverage - Maintenance Margin%)

MINIMUM: Liquidation price must be > 2× ATR away from current price
```

**LEVERAGE LIMITS BY ASSET CLASS**
- Large-cap crypto (BTC, ETH): Max 3x
- Mid-cap crypto (top 50): Max 2x
- Small-cap / meme coins: NO LEVERAGE (1x only)
- US equities: Max 2x (Reg-T)
- Futures: Follow exchange margins, max 5x effective
- DeFi (on-chain): Max 2x (IL + liquidation compound risk)

**LEVERAGE RISK MULTIPLIER**
- Adjust position size: Leveraged Size = Base Size / Leverage
- Example: 3x leverage → position is 1/3 of what unleveraged sizing suggests

### Step 8: Agent-Specific Risk Guardrails

When an autonomous trading agent is executing, apply these additional constraints:

**Agent Risk Limits (on top of all above rules)**

1. **PER-TRADE LIMIT**
   - Agent max per-trade risk: 0.5% (half of human limit)
   - Agent max position size: 5% of portfolio

2. **DAILY LIMITS**
   - Max daily loss: 2% of portfolio → auto-pause agent
   - Max trades per day: 10 (prevents runaway loops)
   - Max total daily volume: 10% of portfolio

3. **APPROVAL GATES**
   - Trades > 1% of portfolio: require human approval
   - New asset (never traded before): require human approval
   - Leverage > 2x: require human approval
   - Any trade outside predefined strategy parameters: require human approval

4. **KILL SWITCHES**
   - Drawdown > 5% in single session: auto-halt, notify human
   - 3 consecutive losses: pause for 1 hour, notify human
   - API error or unexpected response: halt immediately
   - Market volatility spike (>3 std dev move): pause, notify human

5. **AUDIT TRAIL**
   - Log every trade decision with reasoning
   - Log every risk check pass/fail
   - Log portfolio state before and after each trade

For comprehensive agent safety architecture, see Agent Trading Guardrails.

### Step 9: Mandatory Risk Validation Gate

THIS CHECKLIST MUST PASS BEFORE ANY TRADE IS EXECUTED. Every trade — manual or agent — must clear this gate. If any CRITICAL item fails, the trade is blocked.

**Pre-Trade Risk Validation**

**CRITICAL (any failure = trade blocked)**
- [ ] Position size ≤ max per-trade risk% of portfolio
- [ ] Stop-loss is defined and placed
- [ ] Risk/reward ratio meets minimum for strategy type
- [ ] Portfolio heat stays under limit with this trade added
- [ ] No single-asset concentration limit breached
- [ ] If leveraged: liquidation price > 2× ATR from current price
- [ ] If agent trade: within agent-specific risk limits
- [ ] Sufficient liquidity (position < volume threshold)

**WARNING (flag but allow if acknowledged)**
- [ ] Correlation check: not adding to already-correlated cluster
- [ ] Drawdown status: not in reduced-risk mode
- [ ] Timing: not trading into major news event / high-volatility period
- [ ] Slippage estimate: acceptable for position size

**INFO (log for audit)**
- [ ] Strategy type identified
- [ ] Entry rationale documented
- [ ] Time horizon specified
- [ ] Exit plan (target + stop) documented

## Anti-Patterns

DO NOT do these — they are the most common risk management failures:

- **Averaging down without a plan**: Adding to a losing position increases risk. Only add if the original thesis is intact AND a specific add-down level was pre-planned.
- **Revenge trading**: After a loss, immediately entering a new trade to "make it back." Always follow the drawdown management schedule.
- **Moving stops further away**: Once a stop is set, it can be tightened but NEVER widened. Moving a stop further from entry is equivalent to increasing risk after the trade is already going against you.
- **Risk of ruin**: Risking >5% per trade makes account recovery exponentially harder.
  - 10% loss requires 11.1% gain to recover
  - 25% loss requires 33.3% gain to recover
  - 50% loss requires 100% gain to recover
- **Ignoring correlation**: Having 5 "diversified" positions that are all correlated to BTC means you effectively have one large BTC bet.
- **Overleveraging on "high conviction"**: Conviction is not a risk parameter. Size positions based on math, not feelings.
- **No stop-loss**: Every position needs a defined exit point. "I'll watch it" is not a risk management strategy.

## Validation Checkpoints

**Input Validation**
- Portfolio size provided or fetched from connected exchange
- Entry price, stop-loss, and target clearly defined
- Asset volatility available (ATR or implied vol)
- Current portfolio positions known (for concentration checks)
- Strategy type identified (determines R:R minimums and stop methods)

**Output Validation**
- Position size calculated with specific method cited
- Dollar risk amount and percentage stated explicitly
- Stop-loss level and method documented
- R:R ratio calculated and meets minimum threshold
- Portfolio-level impact assessed (heat, concentration, correlation)
- All items in Risk Validation Gate checked
- If leveraged: liquidation price calculated and buffer confirmed
- If agent: agent-specific limits verified

## Example

User: "I want to go long ETH at $3,500 with my $50,000 portfolio. How should I size this?"

### Risk Assessment: Long ETH at $3,500

**Position Sizing (Volatility-Adjusted)**
- Portfolio: $50,000
- Risk per trade: 1% = $500
- ETH ATR(14): $180
- Stop method: 2× ATR below entry
- Stop price: $3,500 - (2 × $180) = $3,140
- Risk per unit: $3,500 - $3,140 = $360
- Position size: $500 / $360 = 1.39 ETH
- Position value: 1.39 × $3,500 = $4,861 (9.7% of portfolio)

**Risk/Reward Assessment**
- Target: $4,200 (2× ATR above entry or prior resistance)
- Reward per unit: $4,200 - $3,500 = $700
- Risk per unit: $360
- R:R = $700 / $360 = 1.94:1 ✓ (meets 1.5:1 minimum for trend-following)

**Portfolio Impact**
- Current portfolio heat: 8% (existing positions)
- New trade adds: 1% risk
- Post-trade heat: 9% ✓ (under 20% limit)
- ETH correlation with existing BTC position (ρ = 0.85): combined crypto = 14% ⚠️ (near 15% limit)
- Concentration: 9.7% in ETH ✓ (under 20% limit)

**Risk Validation Gate**
- [x] Position size (1%) ≤ max risk (2%) ✓
- [x] Stop-loss defined: $3,140 ✓
- [x] R:R (1.94:1) ≥ minimum (1.5:1) ✓
- [x] Portfolio heat (9%) < limit (20%) ✓
- [x] Concentration (9.7%) < limit (20%) ✓
- [x] Not leveraged ✓
- [x] Liquidity OK (ETH daily volume >> position size) ✓
- [⚠️] Correlation: crypto exposure at 14%, approaching 15% limit

**Recommendation**
APPROVED with WARNING: Position is within all risk parameters. Monitor total crypto exposure — one more correlated position would breach the 15% limit.

- Position: Buy 1.39 ETH at $3,500
- Stop-loss: $3,140 (2× ATR)
- Target: $4,200
- Risk: $500 (1% of portfolio)

*Disclaimer: This site is for educational purposes only. Not financial advice. Trading involves risk of loss. Always do your own research before making any investment decisions.*
