---
name: harmonic-patterns
description: 'Use when scanning charts for harmonic price patterns — Gartley, Bat, Butterfly, Crab, AB=CD with Fibonacci ratio validation, XABCD swing structure, pattern completion at D, and trade setups with invalidation.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [harmonic-patterns, gartley, bat, butterfly, crab, abcd, fibonacci, xabcd, price-action]
---

# Harmonic Patterns

This skill provides a systematic framework for identifying and trading harmonic price patterns — precise geometric price structures defined by Fibonacci ratio relationships. Harmonic patterns combine swing structure (XABCD) with Fibonacci retracement/extension validation to find high-probability reversal zones (the "D" point) before the move happens.

## When to Use This Skill

- When scanning charts for reversal opportunities at Fibonacci confluence zones
- When a market has made a clear 3-leg move and you need to assess the final leg target
- When combining price action with Fibonacci levels for high-conviction entries
- When the user asks "is there a Gartley/Bat/Butterfly forming on [ticker]?"
- When validating whether a suspected pattern is valid (ratio checks)
- When setting entry/stop/target around the D point completion zone

## What This Skill Does

- **Swing Structure Detection**: Identifies XABCD swing points from price data
- **Pattern Recognition**: Detects Gartley, Bat, Butterfly, Crab, and AB=CD structures
- **Fibonacci Validation**: Verifies each leg against the required ratio ranges
- **D-Point Projection**: Computes the expected completion zone for the pattern
- **Trade Setup Generation**: Produces entry/stop/target around the PRZ (Potential Reversal Zone)
- **Invalidation Rules**: Defines when a pattern is no longer valid

## How to Use

- Scan [ticker] for harmonic patterns — is a Gartley forming?
- What's the PRZ for the current Bat pattern on [ticker]?
- Validate this XABCD structure: X=100, A=90, B=95, C=92 — is it a valid pattern?
- Show me the last 5 completed harmonic patterns on [ticker]

## Data Sources

**With MCP/CLI tools connected:**
- yFinance MCPs — Historical OHLCV for swing detection
- CoinGecko MCP — Crypto price data for harmonic scanning
- Binance MCP — Crypto OHLCV data
- OpenBB CLI — Charting and screening

**Without tool access:** Ask the user to provide:
- OHLCV data (at least 100 bars) or a recent swing list (X, A, B, C swing prices)
- Current price and recent range
- Timeframe of interest

Proceed with analysis using provided data. Note which computations are approximate vs. exact.

## Methodology

### Step 1: Identify Swing Points (XABCD)

A harmonic pattern requires 5 swing points: X → A → B → C → D.

**Swing detection (fractal method):**
- A swing HIGH is a bar whose high is higher than the k bars on both sides
- A swing LOW is a bar whose low is lower than the k bars on both sides
- Use k=2-5 depending on timeframe (larger k = fewer, more significant swings)

**Pattern structure rules:**
- X and A are opposite swings (if X is a low, A is a high)
- B is opposite to A
- C is opposite to B
- D is the projected point where the pattern completes (unconfirmed until price reaches it)

### Step 2: Pattern Ratio Requirements

Each pattern has specific Fibonacci requirements. **All must be met** for a valid pattern:

**AB=CD (simplest, building block of all others)**

| Leg | Ratio Requirement |
|---|---|
| AB | Any |
| BC retracement of AB | 0.382 - 0.886 |
| CD = AB | 1.000 (equal legs) — or CD = 1.272/1.618 of AB (extended AB=CD) |
| Time symmetry | AB time ≈ CD time (preferred, not required) |

**GARTLEY (bullish: X low, A high, B low, C high, D low)**

| Leg | Ratio Requirement | Notes |
|---|---|---|
| XA | Any | Initial leg |
| AB retracement of XA | 0.618 | Must be deep (0.618 is the defining feature) |
| BC retracement of AB | 0.382 - 0.886 | Shallow to deep |
| CD projection of BC | 1.272 - 1.618 | Extension of BC |
| **D retracement of XA** | **0.786** | **The critical validation — D must be at 0.786 of XA** |

**BAT**

| Leg | Ratio Requirement |
|---|---|
| AB retracement of XA | 0.382 - 0.500 (shallow!) |
| BC retracement of AB | 0.382 - 0.886 |
| CD projection of BC | 1.272 - 1.618 |
| **D retracement of XA** | **0.886** |

**BUTTERFLY**

| Leg | Ratio Requirement |
|---|---|
| AB retracement of XA | 0.786 (deep) |
| BC retracement of AB | 0.382 - 0.886 |
| CD projection of BC | 1.272 - 2.618 |
| **D extension of XA** | **1.272** (extends BEYOND X!) |

**CRAB (deepest)**

| Leg | Ratio Requirement |
|---|---|
| AB retracement of XA | 0.382 - 0.618 |
| BC retracement of AB | 0.382 - 0.886 |
| CD projection of BC | 2.240 - 3.618 |
| **D extension of XA** | **1.618** |

**Pattern summary table:**

| Pattern | AB/XA | BC/AB | CD/BC | D/XA |
|---|---|---|---|---|
| AB=CD | any | 0.382-0.886 | 1.000 (or 1.272/1.618) | — |
| Gartley | 0.618 | 0.382-0.886 | 1.272-1.618 | 0.786 |
| Bat | 0.382-0.500 | 0.382-0.886 | 1.272-1.618 | 0.886 |
| Butterfly | 0.786 | 0.382-0.886 | 1.272-2.618 | 1.272 |
| Crab | 0.382-0.618 | 0.382-0.886 | 2.240-3.618 | 1.618 |

**Bullish patterns** (D is a LOW — buy zone): X low → A high → B low → C high → D low
**Bearish patterns** (D is a HIGH — sell zone): inverted (X high → A low → B high → C low → D high)

### Step 3: Tolerance and Validation

- **Ratio tolerance**: ±3-5% (0.618 ± 3% = 0.599-0.637). Tight tolerance = more valid but rarer patterns
- **Confluence check (what makes a GREAT pattern):**
  - D sits at MULTIPLE Fibonacci levels simultaneously (e.g., D = 0.786 XA AND 1.618 BC AND 0.618 AB)
  - D aligns with a supply/demand zone, round number, or previous S/R
  - D aligns with a 50% retracement of the overall XA leg
  - The longer the XA leg, the more significant the pattern
- **Time symmetry**: Gartley/Bat patterns often have AB time ≈ CD time — a useful extra filter

### Step 4: Trade Setup at the PRZ (Potential Reversal Zone)

Once the pattern is validated, plan the trade at D:

**ENTRY**
- Limit order at the D zone (the calculated PRZ)
- For bullish (buy) patterns: place buy limit slightly above the D low (wait for a reversal candle)
- For bearish (sell) patterns: place sell limit slightly below the D high

**STOP-LOSS**
- Bullish: below the D swing low by 1× ATR or a fixed % (never inside the PRZ)
- Bearish: above the D swing high by 1× ATR or a fixed %
- Rule: if price closes through the D level without reversing, the pattern is invalid — exit immediately

**TARGETS**
- Target 1: B (the midpoint of the structure) — take partial profits
- Target 2: A (the starting swing) — take more
- Target 3: X (full reversal) — let the remainder run
- Minimum R:R: 2:1 (harmonic patterns are high-conviction only if the R:R clears this)

**INVALIDATION**
- Price breaks the D level by more than the stop distance
- The A→D leg structure breaks (e.g., a new extreme beyond X in a Butterfly continuation)
- A new swing invalidates the XABCD sequence before D completes

### Step 5: Anti-Patterns for Harmonic Trading

- **Pattern-fitting**: Finding patterns that "almost" fit by loosening ratios. The ratios are the definition — if they don't meet spec, it's not the pattern.
- **Trading every pattern**: Require confluence (2+ ratio confirmations + S/R zone + R:R ≥ 2:1). Most valid patterns are low-conviction on their own.
- **Ignoring the trend**: Harmonic patterns are reversal tools. A bullish Gartley in a strong downtrend fails more often — check the higher timeframe.
- **No invalidation**: A harmonic trade without a defined invalidation level is a guess, not a plan.
- **Chasing D**: The entry must be AT the zone — buying after price has already reversed 2% past D is no longer the pattern trade.

## Validation Checkpoints

**Input Validation**
- Swing points identified from actual price data (not eyeballed)
- All 4 legs (AB, BC, CD, XA) computed
- Pattern type classified by the D/XA ratio (the primary identifier)
- Tolerance stated (±%)
- Higher timeframe trend noted

**Output Validation**
- Every ratio within spec for the claimed pattern
- D zone projected with the confluence of 2+ ratios
- Entry/stop/target stated with R:R ≥ 2:1
- Invalidation level defined
- Trend context included in the recommendation

## Example

User: "Scan MU for harmonic patterns."

### MU Harmonic Scan (daily)

**Swing detected:** X=1200 → A=740 → B=1050 → C=900 (recent)

**Candidate: Bullish Bat forming**
- AB retracement of XA: (1200-1050)/(1200-740) = 0.326 — within 0.382-0.500? NO (0.326 < 0.382) → Bat invalid
- Candidate: Bullish Gartley?
- AB/XA = 0.326 — Gartley requires 0.618 → INVALID

**Scan result: No valid pattern on current swings** — the recent B was too shallow.

**What would create a pattern:** If price pulls back to ~$985 (0.382 of XA 740-1200), a new B swing at 0.382 would make a valid Bat candidate (AB/XA = 0.382-0.500 zone). Watch that level.

*Verification note: ratios computed from actual swing prices; pattern requires ALL ratios in spec.*
