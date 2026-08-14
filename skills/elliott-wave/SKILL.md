---
name: elliott-wave
description: 'Use when analyzing wave structure on charts — Elliott Wave impulse/correction counting, 5-3 wave rules, Fibonacci relationships between waves, alternate labeling, and trade setups at wave 2/4 completion with invalidation.'
metadata:
  author: DucklingGod (community contribution)
  version: 1.0.0
  category: finance
  tags: [elliott-wave, wave-counting, impulse, correction, fibonacci, structure, technical-analysis]
---

# Elliott Wave

This skill provides a structured framework for Elliott Wave analysis — identifying the 5-3 wave structure of market movements, validating counts with the three hard rules and Fibonacci relationships, and using wave positions to time entries with defined invalidation. Elliott Wave is a **probabilistic structure framework**, not a crystal ball: correct counts still fail, so every wave trade needs a stop and an alternate count.

## When to Use This Skill

- When the user asks "what wave is this market in?" or "is this an impulse or a correction?"
- When identifying the current position in a larger trend structure
- When looking for wave-2 or wave-4 pullback entries in an impulse
- When assessing whether a trend is exhausting (wave 5) or continuing
- When combining Fibonacci retracements with wave structure
- When setting invalidation levels based on wave rules

## What This Skill Does

- **Impulse vs. Correction Classification**: Distinguishes 5-wave impulses from 3-wave corrections
- **Wave Counting**: Labels waves 1-5 and A-B-C from swing structure
- **Rule Validation**: Enforces the three hard Elliott rules
- **Fibonacci Relationship Checks**: Validates wave proportionality (retracements and extensions)
- **Count Probability Assessment**: Scores competing counts and picks the most likely
- **Trade Setup Generation**: Produces entries at wave-2/4 completions with invalidation at rule breaks

## How to Use

- What wave is [ticker] in right now?
- Label the waves on [ticker] daily — impulse or correction?
- Is wave 3 complete on [ticker]? Where does wave 4 pull back to?
- Validate this count: 5 up-waves then A-B-C — what next?

## Data Sources

**With MCP/CLI tools connected:**
- yFinance MCPs — Historical OHLCV for swing/wave detection
- CoinGecko / Binance MCP — Crypto data
- OpenBB CLI — Charting

**Without tool access:** Ask the user to provide:
- Swing points (the last 8-10 significant highs/lows)
- Current price and recent structure
- Timeframe of interest

Proceed with analysis using provided data. Note which counts are speculative vs. confirmed.

## Methodology

### Step 1: The Core Structure

**IMPULSE (trend):** 5 waves in the direction of the trend
- Waves 1, 3, 5 are motive (with the trend)
- Waves 2, 4 are corrective (against the trend)
- Wave 3 is almost always the longest and never the shortest

**CORRECTION (counter-trend):** 3 waves against the trend
- Zigzag (5-3-5): sharp, deep
- Flat (3-3-5): sideways, shallow
- Triangle (3-3-3-3-3): contracting/expanding, consolidation
- Combined (W-X-Y): complex corrections

### Step 2: The Three Hard Rules (invalidation triggers)

```
RULE 1: Wave 2 never retraces more than 100% of wave 1
        (if wave 2 exceeds the start of wave 1 → count is wrong)

RULE 2: Wave 3 is never the shortest of waves 1, 3, and 5
        (in price terms, not time)

RULE 3: Wave 4 never overlaps the price territory of wave 1
        (in a 5-wave impulse — overlap = not an impulse, likely a correction)
        NOTE: overlap allowed in the 5th wave of a diagonal (wedge)
```

**Guideline (not a rule):** Wave 4 usually retraces 0.236-0.382 of wave 3 (rarely deeper than 0.5).

### Step 3: Fibonacci Relationships

**Within an impulse:**
- Wave 2 often retraces 0.5-0.618 of wave 1
- Wave 3 often extends 1.618× wave 1 (or 2.618× for strong trends)
- Wave 4 often retraces 0.382 of wave 3
- Wave 5 often equals wave 1 (1.000) or is 0.618-1.618 of wave 1
- Wave 5 often ends at the 1.618 extension of waves 1-3

**Within a correction:**
- C often equals A (1.000) or 1.618× A
- C often retraces 0.618-0.786 of the prior impulse

**Projection targets (measured move):**
- After wave 2 completes → target wave 3 at 1.618× wave 1
- After wave 4 completes → target wave 5 at 1.000-1.618× wave 1 (from wave 4 low)
- After A-B completes → C target at 1.000-1.618× A

### Step 4: Counting Process

```
1. IDENTIFY the largest visible structure (from swing highs/lows)
2. CLASSIFY: is the last move 5 waves (impulse) or 3 waves (correction)?
3. If 5 waves up completed → expect 3-wave (A-B-C) correction down
4. If A-B-C down completed → expect a new 5-wave impulse up
5. ALTERNATE COUNT: always hold a second plausible count.
   The count is only "high confidence" when the alternate violates a hard rule.

COUNT SCORING (per count):
  +2 each hard rule satisfied
  +1 each Fibonacci relationship within tolerance
  +1 wave alternation (2 zigzag, 4 flat — or vice versa)
  +1 wave 3 clearly extended
  Score > 6 = preferred count; < 4 = uncertain, wait
```

### Step 5: Trade Setups

**LONG at wave 2 completion (most reliable setup):**
- Wave 1 confirmed (impulse structure), wave 2 retraces 0.5-0.618 of wave 1
- Entry: at the 0.618 retracement zone, with a reversal candle
- Stop: below the start of wave 1 (Rule 1 invalidation) or below the wave-2 low
- Target: 1.618× wave 1 (measured move for wave 3)
- R:R expectation: 3:1+

**LONG at wave 4 completion (trend continuation):**
- Waves 1-3 confirmed, wave 4 retraces 0.382 of wave 3
- Entry: 0.382 zone with reversal signal
- Stop: below wave 4 low (below wave 1 high if using Rule 3 as invalidation)
- Target: wave 5 = wave 1 projection, or 1.618 extension of 1-3

**AVOID:**
- Buying during wave 4 of a 5th-wave extension (late in the trend)
- Trading wave 5 without confirmation (most unreliable wave)
- Catching falling knives in A-C legs before C shows completion

**INVALIDATION (always state):**
- Bullish count invalid if price breaks below the start of wave 1 (impulse broken)
- Bearish count invalid if price breaks above the prior wave high

### Step 6: Anti-Patterns

- **Count-fitting**: Forcing swings into a preferred count. If the alternate fits equally well, you have no edge — wait.
- **Ignoring hard rules**: "I know wave 2 went too deep but the trend is up" — Rule 1 broken = the count is wrong, not the rule.
- **Trading wave 5 as if it's wave 3**: The most common subjective error. Wave 5 is exhaustion — small size or skip.
- **No alternate count**: Every Elliott trade needs a second scenario with its own invalidation. One-count-only analysis is guessing.
- **Applying wave counts to thin/illiquid markets**: Elliott works best in liquid, trending markets. Choppy ranges produce endless false counts.

## Validation Checkpoints

**Input Validation**
- Swings identified from actual price data
- Largest visible structure labeled
- Impulse vs correction classification attempted with reasons
- Timeframe stated (wave counts are timeframe-relative)

**Output Validation**
- All three hard rules checked against the proposed count
- Fibonacci relationships computed (2 retracement + 1 extension minimum)
- Alternate count proposed with its own invalidation
- Count score computed (preferred vs alternate)
- Trade setup includes entry, stop (at rule break), targets, R:R
- Wave position stated in the larger context (is this wave 3 of a 5th of a 3rd?)

## Example

User: "What wave is MU in on the daily?"

### MU Daily Wave Count

**Structure:** Major uptrend from 113.46 (52w low) — swing analysis shows 5 clear waves up: 113 → 420 → 260 → 950 → 740 (labeled candidates)

**Hard rules check:**
- Wave 2 (260) retraced 45% of wave 1 — did NOT exceed 113 start ✓ (Rule 1)
- Wave 3 (950) is clearly the longest ✓ (Rule 2)
- Wave 4 (740) did not overlap wave 1's high (420) ✓ (Rule 3)

**Count score:** Rules 3/3 (+6) + wave 2 ≈ 0.5 fib of wave 1 (+1) + alternation suspected (+1) = **8 — preferred count: impulse with wave 5 in progress**

**Implication:** Wave 5 targeting 1.000-1.618× wave 1 from wave 4 low: 740 + (420-113)×1.0 = ~1,047 (matches resistance zone ~1,011-1,055). After wave 5 completes → expect A-B-C correction.

**Alternate count:** If price breaks below 740 (wave 4 low), the count becomes corrective — a larger A-B-C down is underway. Invalidation: daily close < 740.

**Trade plan:** No new buys into wave 5 (exhaustion risk). Existing positions: tighten stops to 740. Consider profit-taking at the 1,047-1,100 zone.

*Note: wave counts are probabilistic — always trade with stops and an alternate count.*
