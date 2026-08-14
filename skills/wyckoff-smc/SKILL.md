---
name: wyckoff-smc
description: 'Use when analyzing price action for institutional footprints — Wyckoff accumulation/distribution phases and events (spring, upthrust, SOS, SOW), Smart Money Concepts (market structure, BOS/CHoCH, order blocks, fair value gaps, liquidity sweeps) — to form a directional bias and locate high-probability entry zones.'
metadata:
  author: DucklingGod
  version: 1.0.0
  category: finance
  tags: [wyckoff, smart-money-concepts, smc, ict, market-structure, order-blocks, fair-value-gap, liquidity, swing-trading, price-action, institutional]
---

# Wyckoff Method & Smart Money Concepts (wyckoff-smc)

A dual-framework skill for reading the "footprint" of large operators on a price chart. The **Wyckoff Method** (Richard D. Wyckoff, 1910s–1930s, systematized by Hank Pruden and Bruce Fraser) explains *why* markets move: a "Composite Man" accumulates at low prices and distributes at high prices, leaving identifiable phases and events. **Smart Money Concepts (SMC)**, popularized by Michael Huddleston (ICT) and the SMC community (2010s+), modernizes the same idea with operational terminology: market structure (HH/HL/LH/LL), BOS, CHoCH/MSS, order blocks, fair value gaps, and liquidity sweeps. SMC is, at its core, "modern Wyckoff" — the spring is a liquidity sweep, the SOS is a bullish BOS, the upthrust is a sell-side liquidity grab. This skill teaches both vocabularies and ships a working Python scanner (`scripts/smc_scan.py`) that labels structure, detects BOS/CHoCH, order blocks, FVGs and liquidity sweeps on daily data and renders an annotated chart.

## When to Use This Skill

- When asked to analyze market structure, trend health, or "smart money" behavior on any freely traded asset (stocks, ETFs, crypto, forex, futures)
- When a user mentions Wyckoff, accumulation, distribution, spring, upthrust, shakeout, SOS, SOW, LPS, UTAD
- When a user mentions SMC/ICT terms: market structure, BOS, CHoCH, MSS, order block, breaker block, FVG / imbalance, liquidity sweep, BSL/SSL, killzone, PD array, OTE
- When forming a directional bias ("is this in markup or markdown?", "is this a bull or bear regime?") before an entry decision
- When locating entry zones after a structural shift (retest of order block or FVG)
- When combining price action with volume to judge supply/demand balance (Wyckoff's three laws)

## What This Skill Does

- **Wyckoff analysis**: identifies trading ranges, phases A–E of accumulation and distribution, and key events (PS, SC, AR, ST, Spring, SOS, LPS, BU / PSY, BC, UT, SOW, LPSY, UTAD)
- **SMC structure labeling**: detects swing highs/lows (fractal pivots), labels HH/HL/LH/LL, and derives a bullish / bearish / ranging regime
- **BOS & CHoCH detection**: flags the most recent break of structure (continuation) and change of character (regime shift), with pending levels for the next break
- **Order block detection**: finds the last opposing candle before a displacement move that breaks structure; marks proximal/distal lines and mean threshold
- **Fair value gap detection**: identifies 3-candle imbalances (bullish/bearish FVG) and tracks which are still unmitigated
- **Liquidity sweep detection**: flags sweeps of buy-side (BSL) and sell-side (SSL) liquidity — Wyckoff's spring/upthrust in modern clothing
- **Verdict generation**: combines structure + BOS/CHoCH + FVG + OB + sweep confluence into a directional bias with a confirmation score
- **Charting**: renders a candlestick chart annotating swing points, structure labels, BOS/CHoCH, order block zones, FVG zones and sweeps

## How to Use

**Full scan with chart (recommended)**

```bash
python scripts/smc_scan.py MU
python scripts/smc_scan.py BTC-USD --interval 1d --range 1y
python scripts/smc_scan.py AAPL --fractal 2 --atr 14 --lookback 15 --json out.json
```

The script prints a plain-text structure report and saves `{TICKER}_smc.png` to the Hermes image cache (`C:/Users/iHC/AppData/Local/hermes/cache/images/`).

**Prompt examples**

- "Run a Wyckoff/SMC scan on MU — is it accumulating or distributing? Where are the order blocks and FVGs?"
- "Label the market structure on NVDA daily: HH/HL/LH/LL, last BOS and CHoCH, and give me the next key levels."
- "Did AAPL just sweep sell-side liquidity below the last swing low? Any spring-like action?"
- "Find the last bullish order block on TSLA and the nearest unmitigated FVG — is price likely to retest them?"

**CLI options**

| Flag | Default | Meaning |
| --- | --- | --- |
| `--range` | `1y` | Yahoo data range (e.g. `6mo`, `1y`, `2y`, `5y`, `max`) |
| `--interval` | `1d` | Bar interval (`1d`, `1wk`, `1mo`) |
| `--fractal` | `2` | Fractal window `k` (bars on each side to confirm a pivot) |
| `--atr` | `14` | ATR period used for displacement thresholds |
| `--lookback` | `15` | Recent bars scanned for structure breaks / sweeps |
| `--disp` | `1.0` | Displacement multiple of ATR required for an order block impulse |
| `--json` | none | Also write a machine-readable JSON report |
| `--no-chart` | off | Skip chart rendering |

## Data Sources

- **Primary**: Yahoo Finance chart API — `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d` (JSON: `chart.result[0].timestamp` + `.indicators.quote[0]` open/high/low/close/volume). Free, no API key. Use a browser `User-Agent` header; skip rows with `None` close.
- **Volume confirmation (Wyckoff)**: any OHLCV source with volume (Yahoo, Binance, exchange APIs). Volume is optional in the scanner but central to the Wyckoff methodology — always read volume/spread alongside the structure output.
- **Point & figure (cause/effect projections)**: P&F charting tools for the Wyckoff horizontal count (optional, advanced).

## Methodology

### Part 1 — Wyckoff Method

**The Composite Man.** Wyckoff's heuristic: study all price fluctuations "as if they were the result of one man's operations." This Composite Man accumulates inventory at low prices, advertises via broad-market activity, marks price up, and distributes at high prices to the public. Retail traders get fleeced when they fight this operator; they profit when they trade in his direction.

**The three laws.**
1. **Supply and Demand** — determines price direction. Compare price spread and volume bar-by-bar: widening spread + rising volume = strong effort; price progress vs. volume tells you who is winning.
2. **Cause and Effect** — the accumulation/distribution *within a trading range is the cause*; the subsequent trend is the *effect*. The horizontal P&F point count measures the cause and projects the effect's extent.
3. **Effort vs. Result** — divergence between volume (effort) and price progress (result) warns of trend change (e.g., several high-volume narrow-range bars failing to make new highs = distribution).

**The price cycle**: accumulation (markup preparation) → markup → distribution → markdown → back to accumulation. Trading ranges (TRs) are where the previous trend halts and large operators build cause.

**Accumulation events** (after a downtrend):

| Event | Meaning |
| --- | --- |
| PS (Preliminary Support) | First significant buying after a prolonged decline; widening spread, rising volume |
| SC (Selling Climax) | Climactic panicky selling absorbed by big interests; wide spread, huge volume, often closes well off the low |
| AR (Automatic Rally) | Relief rally after SC (short covering + demand), defines the TR's upper boundary |
| ST (Secondary Test) | Retest of SC area on diminished spread/volume; confirms supply is drying up; often multiple STs |
| Spring / Shakeout | Price breaks below TR support, then quickly reverses back inside — a bear trap that tests remaining supply (low volume on the spring is bullish). A terminal shakeout is a late, deeper spring |
| SOS (Sign of Strength) | Strong advance on widening spread and higher volume — validates the spring/analysis |
| LPS (Last Point of Support) | Shallow pullback after SOS on diminished spread/volume — the last safe buy zone before markup |
| BU (Back-Up) | Pullback to former resistance (the "creek") after a SOS "jump across the creek" |

**Accumulation phases**: **A** — stop the downtrend (PS, SC, AR, ST). **B** — build cause; wide swings early, diminishing down-volume as supply is absorbed; multiple STs; longest phase. **C** — test for supply: spring/shakeout (or a higher test when no spring occurs — Schematic #2). **D** — confirmation: SOS and LPS; price reaches at least the top of the TR. **E** — markup: price leaves the TR, demand in full control; re-accumulation "stepping stones" may form higher.

**Distribution events** (after an uptrend): **PSY** (Preliminary Supply) — first significant selling; **BC** (Buying Climax) — climactic public buying filled by big interests near the top (often on great news); **AR** (Automatic Reaction) — selloff after BC defining TR's lower boundary; **ST** (Secondary Test) — retest of BC area; may take the form of an **UT** (Upthrust) — brief break above resistance that reverses back inside; **SOW** (Sign of Weakness) — down-move to/below TR support on increased spread & volume; **LPSY** (Last Point of Supply) — feeble rally after SOW on narrow spread — last distribution before markdown; **UTAD** (Upthrust After Distribution) — late bull trap above TR resistance; not a required element (Schematic #1 has it, #2 does not).

**Distribution phases**: **A** — stop the uptrend (PSY, BC, AR, ST). **B** — build cause to the downside; net selling; SOWs on expanding spread/volume. **C** — test for demand via UT/UTAD (bull trap). **D** — confirmation: SOW and LPSY; price reaches at least the bottom of the TR. **E** — markdown: price leaves the TR, supply in full control.

**Trade logic**: buy at/near an LPS after a confirmed SOS following a low-volume spring; sell at/near an LPSY after a confirmed SOW following a UT/UTAD. Always use the market's phase to decide whether to be long, short, or flat. Volume is mandatory confirmation: a spring on *low* volume that holds is the classic high-probability accumulation trigger.

### Part 2 — Smart Money Concepts (SMC)

**Core premise**: institutions need liquidity to fill large orders; price therefore moves *toward* liquidity pools (previous highs/lows with resting stops), breaks them (sweep), then reverses in the true direction. The golden rule: *don't look for the breakout — look for the sweep*; the real move goes opposite the sweep.

**Market structure.** Mark swing highs and swing lows (external pivots — ignore internal noise). Then:
- **Bullish structure**: sequence of HH + HL (each new high exceeds the prior; each pullback holds above the prior low)
- **Bearish structure**: sequence of LH + LL (each rally fails below the prior high; each low breaks the prior low)
- **Range**: oscillation between a high and a low without new breaks

**BOS (Break of Structure)** — continuation. In an uptrend, price closes above the last swing high; in a downtrend, closes below the last swing low. Each BOS confirms the trend is healthy. A bullish BOS after accumulation is Wyckoff's SOS by another name.

**CHoCH (Change of Character)** — the *first* break against the prevailing trend: in an uptrend, close below the last higher low; in a downtrend, close above the last lower high. The "HH/HL pattern failed" signal. A valid CHoCH must break the swing that produced the last BOS.

**MSS (Market Structure Shift)** — the same level as a CHoCH but broken *with displacement* (large, strong-bodied candles piercing the level decisively). A "violent CHoCH" with higher conviction. Soft wick break → CHoCH; violent body break → MSS.

**Order Block (OB).** Strict definition — the **last opposing candle before an impulsive move with displacement that breaks structure**. Three mandatory conditions: (1) last candle opposite the impulse direction (last bearish candle before a bullish impulse = bullish OB; last bullish before a bearish impulse = bearish OB); (2) the impulse shows displacement (large-bodied candle, typically ≥ 1× ATR); (3) the move confirms with a BOS. Mark the zone open-to-low (bullish) or open-to-high (bearish) — the ICT standard. Key levels: **proximal line** (edge nearest the impulse — first touch), **distal line** (opposite edge — invalidation/stop placement), **mean threshold** (50% — partial-invalidation reference). Entry options: aggressive limit at proximal; conservative stop-order on confirmation candle; best-practice: confirm a CHoCH/MSS on a lower timeframe inside the zone. **Breaker Block** = an OB that fails *after* a liquidity sweep, flipping polarity on retest. **Mitigation Block** = an OB that fails *without* a sweep (failure swing), flipping polarity on retest.

**Fair Value Gap (FVG) / imbalance.** With three consecutive candles, if candle 1's high is below candle 3's low → **bullish FVG** (zone = high₁ → low₃); if candle 1's low is above candle 3's high → **bearish FVG** (zone = low₁ → high₃). Candle 2 is the displacement candle that created the gap. FVGs act as magnets: price tends to return to at least the 50% (**Consequent Encroachment / CE**) before continuing. Only FVGs that form after a BOS/CHoCH are tradable — isolated ones are noise. Advanced: BPR (overlapping bull+bear FVG), liquidity void (very large gap).

**Liquidity & sweeps.** **BSL** (buy-side liquidity) = buy stops resting above highs (from short sellers); **SSL** (sell-side liquidity) = sell stops below lows (from long holders). **External range liquidity** = breakout stops at range extremes/equal highs-lows; **internal range liquidity** = FVGs and order blocks inside the range. **Liquidity sweep** = price spikes through a level (taking stops) then closes back inside — a stop hunt. In Wyckoff language: a sweep of a range low = **spring**; a sweep of a range high = **upthrust**. **Inducement** = the minor swing low/high swept just before the true POI, trapping novices. **Draw on Liquidity (DOL)** = the most obvious liquidity magnet (PDH/PDL, weekly highs) — your final target; no DOL, no trade. **Killzones** (London/NY opens) and **PD arrays** (buy only in discount, sell only in premium; OTE = 62–79% retracement of the last impulse) refine timing and location.

### Part 3 — Scanner Implementation (how the script maps theory to code)

1. **Fetch & clean**: urllib GET on the Yahoo chart API with `User-Agent: Mozilla/5.0`; parse timestamps + OHLCV; drop rows with `None` close; forward-fill remaining gaps.
2. **Fractal pivots**: index `i` is a swing high if `high[i] > high[i±1..k]` (strictly) and a swing low if `low[i] < low[i±1..k]`; `k` = `--fractal` (default 2). Merge into one chronological alternating sequence, keeping the more extreme pivot when two of the same type collide.
3. **Structure labels**: relabel the last ~6 pivots in isolation — each high vs. prior high → HH/LH; each low vs. prior low → HL/LL. Regime: last two labels both in {HH,HL} → BULLISH; both in {LH,LL} → BEARISH; else RANGE.
4. **BOS/CHoCH**: walk bars forward; track the most recent confirmed swing high/low; on a *close* above the last swing high (bullish regime) → BOS; close below last swing low (bullish regime) → CHoCH. Mirrored in bearish regimes. Report the most recent event + the pending levels that would trigger the next BOS/CHoCH.
5. **Order blocks**: candle `i` opposite-colored to candle `i+1`; require `|body(i+1)| ≥ disp × ATR(i)` (displacement) and a close-based BOS over a pre-existing swing within `lookahead` bars. Zone = open→low (bullish) / open→high (bearish).
6. **FVGs**: scan all triples; keep unmitigated ones (no later bar has traded back into the zone); report the most recent few.
7. **Liquidity sweeps**: within the lookback window, a wick beyond a prior swing high that closes back below it = buy-side sweep (upthrust-like); wick below a swing low closing back above = sell-side sweep (spring-like).
8. **Verdict**: bias = current regime; confirmation count from aligned {BOS/CHoCH, unmitigated FVG, OB near price, sweep}; print key levels (next BOS trigger, CHoCH invalidation) and save the annotated chart.

## Anti-Patterns

- **Trading against structure**: never take longs in a confirmed LH/LL bearish regime just because price "looks cheap" — that is Wyckoff's "catching a falling knife" and SMC's "buying in premium."
- **Spring/UTAD confirmation-free**: a spring or upthrust alone is not a trade. Wyckoff requires the SOS/SOW confirmation (or at minimum a successful low-volume test); SMC requires the displacement + BOS. Fake springs are common.
- **Labeling internal noise**: a CHoCH must break the *external* swing that produced the last BOS — internal highs/lows create fake signals. Use body closes, not wicks, for CHoCH.
- **Order blocks without the 3 conditions**: "a candle before a rally" is not an OB. Without displacement and a confirmed BOS you are trading noise.
- **Ignoring volume (the SMC trap)**: SMC largely dropped volume analysis; Wyckoff never did. On any chart where volume is available, use the law of effort vs. result to filter structure breaks (breakout on shrinking volume = suspect).
- **Overtrading mediocre zones**: a disciplined SMC trader can wait days for one clean OB+FVG+sweep confluence. No confluence → no trade.
- **Treating the scanner output as a signal, not a map**: the scanner labels what *has happened*. It is a bias/context tool — combine with Wyckoff volume context, higher-timeframe alignment, and risk management before executing.
- **Fighting the sweep**: the most common retail mistake — entering on the breakout that is actually the sweep. Wait for the reversal confirmation back inside the range.

## Validation Checkpoints

- [ ] Data fetched: ≥ 100 bars, no `None` closes, sane price range for the ticker
- [ ] Pivots alternate H/L and no two adjacent pivots share a type after cleanup
- [ ] Structure labels are internally consistent (HH must be a higher *high* than the prior high; HL a higher *low* than the prior low)
- [ ] Regime matches the last two labels (HH+HL → BULLISH, LH+LL → BEARISH)
- [ ] Every reported BOS/CHoCH references a real prior swing level (check the printed level appears in the pivot list)
- [ ] Every order block has: opposite-color candle, |body| ≥ disp×ATR, and a BOS within lookahead bars
- [ ] Every FVG satisfies the strict 3-candle inequality (candle1 wick vs candle3 wick); unmitigated FVGs have no later overlap
- [ ] Liquidity sweeps show a wick beyond the level AND a close back inside
- [ ] Chart renders with all annotations and is saved under `C:/Users/iHC/AppData/Local/hermes/cache/images/{TICKER}_smc.png`
- [ ] Spot-check the verdict by eye on the chart: the annotated events must be visible where the report claims they are

## Example

**Prompt**: "Run a Wyckoff/SMC scan on MU — what's the structure, and where are the order blocks and FVGs?"

**Command**: `python scripts/smc_scan.py MU`

**Output (abridged)**:

```
=== SMC Structure Scan: MU (2025-08-15 -> 2026-08-15) ===
Bars: 252 | Last close: 148.23 | Regime: BULLISH (HH/HL sequence intact)
Swing points: 18 highs, 19 lows (fractal k=2)
Last structure labels: HH, HL, HH, HL, HH
Structural events (last 30 bars):
  - 2026-07-28 BOS (bullish continuation): close 146.10 > swing high 144.85
  - 2026-06-30 CHoCH (bearish shift): close 128.40 < swing low 129.75  -> later recovered
Pending levels: next BOS above 152.60 | CHoCH invalidation below 143.10
Order blocks:
  - Bullish OB [143.55 - 145.20] on 2026-07-27 (last bearish candle, disp 1.3x ATR, BOS +)
  - Bearish OB [138.90 - 140.35] on 2026-06-12 (mitigated)
Fair value gaps (unmitigated, recent):
  - Bullish FVG [144.20 - 145.60] on 2026-07-29 (CE 144.90)
Liquidity: sell-side sweep of 2026-07-21 low (spring-like), recovered same bar
VERDICT: BULLISH bias — 4/4 confirmations aligned (structure + BOS + FVG + OB below)
Chart saved: C:/Users/iHC/AppData/Local/hermes/cache/images/MU_smc.png
```

**Interpretation**: price is in markup (Wyckoff Phase E / bullish SMC regime). Longs are only considered on a retest of the bullish OB or the unmitigated FVG (internal liquidity), targeting the next external high (DOL). A close below 143.10 would be the first CHoCH — stand aside.

## References

- Wyckoff Analytics (Hank Pruden, Bruce Fraser, Roman Bogomazov): "The Wyckoff Method" — schematics, phases A–E, events, three laws, nine tests — wyckoffanalytics.com/wyckoff-method
- Richard D. Wyckoff, *The Richard D. Wyckoff Course in Stock Market Science and Technique* (1931); *Studies in Tape Reading* (1910)
- Ruben Villahermosa, *The Wyckoff Methodology in Depth* and "Smart Money Concepts: Complete Guide" — tradingwyckoff.com/en/smart-money-concepts
- Inner Circle Trader (Michael Huddleston) — original source of order blocks, FVG, PD arrays, OTE, killzones, Power of 3 (2010s YouTube)
- Linda Raschke & Laurence Connors, *Street Smarts* (1995) — Turtle Soup, the functional precursor of the liquidity sweep
- City Traders Imperium, TrendSpider, Backtrex, Daily Price Action — SMC structure/BOS/CHoCH practical breakdowns
