---
name: volume-profile
description: 'Use when analyzing price-by-volume distribution — VPVR, Point of Control, value area (VAH/VAL), HVN/LVN, auction market theory, delta/cumulative delta and footprint order flow for support/resistance and trade framing.'
metadata:
  author: DucklingGod
  version: 1.0.0
  category: finance
  tags: [volume-profile, market-profile, vpvr, point-of-control, value-area, auction-market-theory, order-flow, delta, footprint, support-resistance, trading, stocks, crypto, forex]
---

# Volume Profile & Auction Market Theory

Volume Profile (VPVR — Volume Profile Visible Range) is a way of representing traded volume along the **price axis** instead of the time axis. Where a classic volume histogram shows "how much traded at each moment," a volume profile shows **"how much traded at each price."** It is derived from Market Profile, the tool J. Peter Steidlmayer designed for the Chicago Board of Trade in 1985, and it operationalizes Auction Market Theory (AMT): markets are two-way auctions whose job is to *facilitate trade*, and price moves to advertise opportunity, spends time where value is accepted, and leaves quickly where value is rejected.

The outputs — Point of Control (POC), Value Area (VAH/VAL), High Volume Nodes (HVN), Low Volume Nodes (LVN), and the order-flow extensions (delta, cumulative delta, footprint) — give an objective, distribution-based read of where institutions have transacted, where liquidity pools sit, and whether the market is in **balance** (rotation within value) or **imbalance** (directional search for new value).

## When to Use This Skill

- When asked to analyze volume by price level, VPVR, Volume Profile, Market Profile, or "where is the liquidity"
- When identifying institutional support/resistance zones, magnets, and "fast travel" price levels
- When framing a trade: where is price relative to POC and value area, and what are the nearest HVN/LVN
- When a user asks about Point of Control, Value Area High/Low, High/Low Volume Nodes
- When asked about auction market theory, balance vs imbalance, acceptance vs rejection
- When asked about order flow: delta, cumulative delta, footprint charts, absorption, stacked imbalances
- When combining volume structure with technical analysis (confluence scoring, trade setups)

## What This Skill Does

- Fetches ~1 year of daily OHLCV from Yahoo Finance (Python `urllib`, no API key)
- Builds a Volume Profile: fixed-width price bins, volume allocated per-day proportional to the overlap of the day's high-low range with each bin
- Computes **POC** (highest-volume price bin), **Value Area** (tightest range around POC containing 70% of volume → VAH/VAL), **HVN**, **LVN**, and **liquidity gaps** (zero-volume bins)
- Reports **current price context**: above/below POC by %, inside/outside value area, distance to VAH/VAL, nearest HVN/LVN above and below
- Saves a matplotlib chart (price line + horizontal volume histogram on the right, value area shaded, POC/VAH/VAL/current-price lines) to `C:/Users/iHC/AppData/Local/hermes/cache/images/{TICKER}_volprofile.png`
- Documents the order-flow layer (delta, cumulative delta, footprint imbalance) with formulas and reference functions in the script — note these require bid/ask or tick data, which daily OHLCV does not carry

## How to Use

```bash
PY="C:/Users/iHC/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
SCRIPT="C:/Users/iHC/Documents/trading-edge/skills/volume-profile/scripts/volume_profile.py"

"$PY" "$SCRIPT" --ticker MU                     # default: 1y daily, 60 bins
"$PY" "$SCRIPT" --ticker AAPL --bins 80 --value-area 0.70
"$PY" "$SCRIPT" --ticker BTC-USD --bin-size 500 # explicit bin width in $
"$PY" "$SCRIPT" --ticker MU --output /tmp/mu_vp.png
```

Run it whenever a ticker needs a volume-structure read. The terminal output includes a `RESULT_JSON:` line for machine parsing. Exit codes: `0` success, `1` data/network error, `2` bad arguments.

## Data Sources

- **Primary**: Yahoo Finance chart API — `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d` (JSON: `chart.result[0].timestamp` + `.indicators.quote[0]` open/high/low/close/volume; skip rows with `None` close). Fetch with Python `urllib` and header `{'User-Agent': 'Mozilla/5.0'}` — **curl fails for foreign hosts on this machine**.
- **Coverage**: stocks, ETFs, crypto (`BTC-USD`), forex (`EURUSD=X`), indices (`^GSPC`) — any symbol Yahoo resolves.
- **Limits**: daily OHLCV has **no bid/ask split**, so true delta and footprint charts are impossible from this feed. For those, you need tick/level-2 data (e.g., a data vendor or exchange feed). The script documents the delta/cumulative-delta/footprint functions as reference implementations to run on such datasets.
- Free alternatives for verification: TradingView volume profile studies, Sierra Chart "Volume Profile" study, NinjaTrader 8.

## Methodology

### 1. Auction Market Theory (the foundation)

Markets are **two-way auctions** that exist to facilitate trade. Price moves to attract participation; participants accept prices they consider fair and reject prices they consider unfair. Three inputs drive the auction:

| Input | Role |
|---|---|
| **Price** | Advertises opportunity (the "advertisement" of the auction) |
| **Time** | Regulates how long the market accepts a level |
| **Volume** | Measures how much activity occurred at each price |

The market oscillates between two regimes:

- **Balance**: buyers and sellers agree on value; price rotates inside a range and volume concentrates there (the Value Area). Expect mean-reversion / rotation behavior.
- **Imbalance**: agreement breaks; one side becomes aggressive and price trends through Low Volume Nodes to discover a new value area. Expect continuation behavior.

Key behavioral concepts:
- **Acceptance**: price spends time and prints volume at a level → the level is "fair value," likely revisited.
- **Rejection**: price visits a level and leaves with little volume (a "single print") → the level is unfair; expect a fast move through it next time.
- **Initiative activity**: aggressive participants pushing price into new territory (trend fuel).
- **Responsive activity**: participants fading price at the edges of value (counter-trend fuel that builds HVNs).

### 2. Market Profile vs Volume Profile

Market Profile (Steidlmayer, CBOT 1985) bins a session by **time** — each half-hour gets a letter, and the letters printed at each price level are **TPOs (Time Price Opportunities)**. The POC of a Market Profile is the price with the most TPOs (most time spent). Volume Profile replaces time with **volume**: the POC is the price with the most contracts/shares traded. Everything else (value area, HVN/LVN, finished vs unfinished auctions) transfers over. Volume Profile is generally preferred on liquid instruments because volume, not time, is what institutions actually transact.

### 3. Building the profile (VPVR) — step by step

1. **Fetch** ~1y of daily OHLCV.
2. **Define price bins**: `p_min = min(low)`, `p_max = max(high)`, `bin_size = (p_max − p_min) / N` with default `N = 60` bins (or pass an explicit `--bin-size` in dollars). Bin *k* covers `[p_min + k·Δp, p_min + (k+1)·Δp]`; its center is `c_k = p_min + (k + ½)·Δp`.
3. **Allocate volume**: each day's volume is spread across every bin its `[low, high]` range touches, weighted by overlap length:

   ```
   V_k = Σ_d  V_d · overlap([low_d, high_d], bin_k) / (high_d − low_d)
   ```

   A day that traded exactly one bin's worth of range puts all its volume there; a huge-range day spreads thin. This is the standard OHLCV-only approximation of true volume-at-price (tick data would let you count actual prints per price).
4. **Point of Control**: `POC = argmax_k V_k` — the single most-traded price, the market's "center of gravity," the price of maximum agreement. Price tends to return to and rotate around it during balance phases.
5. **Value Area** (default 70% of volume, ~one standard deviation of the distribution):
   - Start with the POC bin included.
   - Repeatedly add the adjacent bin (above or below) **with the higher volume** until included volume ≥ `target × total volume`.
   - `VAH` = upper edge of the highest included bin; `VAL` = lower edge of the lowest included bin.
   - The VA is the **acceptance zone**: price inside it is "value"; price outside is "discount/premium" and is expected to be drawn back or to trigger a value-area shift. VAH/VAL act as support/resistance. A wide VA = broad participation; a narrow VA = thin participation.
6. **High Volume Nodes (HVN)**: bins with `V_k ≥ hvn_mult × mean(V_nonzero)` (default `hvn_mult = 1.5`). The POC is always an HVN. HVNs are liquidity magnets — price rotates around them; treat them as support/resistance and "rest zones."
7. **Low Volume Nodes (LVN)**: bins with `V_k ≤ lvn_mult × mean(V_nonzero)` (default `lvn_mult = 0.5`). LVNs are **fast-travel zones** — price crosses them quickly (little resting liquidity), so they make poor support but good targets/paths during imbalance moves.
8. **Liquidity gaps**: bins with zero volume inside the traded range. Extreme LVNs; the market "single-printed" through them. Gaps are the first places price accelerates through.
9. **Current price context**: report `% above/below POC`, inside/outside VA, distance to VAH/VAL, and nearest HVN/LVN above and below — this is the actionable snapshot for framing a trade.

### 4. Reading profile shapes

- **P-shape / b-shape**: POC near the bottom/top with a fat body — range-bound, responsive behavior; expect rotation.
- **D-shape**: two value areas (an old one and a developing one) — transition from balance to imbalance.
- **Unfinished auction at the extreme**: high volume at the profile edge (an HVN at the extreme) implies interest remains there — price is likely to revisit to finish the auction (could reverse, or continue through).
- **Finished auction at the extreme**: volume tails off toward the extreme (single prints) — rejection; the move away from value is likely to continue.
- **80% Rule (Market Profile)**: if price leaves the value area and does not return within ~30 minutes (or ~1–2 bars on daily), the move out of value has an elevated probability of continuing to the next HVN.

### 5. Order flow extensions (need tick/level-2 data)

These are the next layer down — reading *who is aggressive* inside each bar. They cannot be computed from daily OHLCV (no bid/ask split), but the concepts and formulas belong to the same framework:

- **Delta** per bar: `Δ_i = (volume traded at the ask)_i − (volume traded at the bid)_i = aggressive buys − aggressive sells`. Positive delta = net buying initiative; negative = net selling initiative. The *size* of delta vs total volume measures conviction.
- **Cumulative Delta**: `CD_i = Σ_{j=1..i} Δ_j`. Rising CD = sustained net buying pressure; falling CD = net selling. A **divergence** — price making new highs while CD fails to (or falls) — signals waning initiative (absorption/distribution); price making new lows while CD rises signals accumulation.
- **Footprint chart**: each bar is expanded into a grid of price levels showing `bid × ask` (buy volume vs sell volume) printed at each level. Reading rules:
  - **Imbalance** at a level: `I_p = (buy_p − sell_p) / (buy_p + sell_p)`; `|I| > ~0.5` at several consecutive levels = **stacked imbalance** — strong initiative, often the start of a move; extremes at the end of a trend can mark exhaustion.
  - **Absorption**: large total volume at a level with *little price movement* — one side is absorbing the other's aggression; the absorbing side often wins next.
  - **Stop hunts / liquidity sweeps**: an imbalance spike into an HVN/LVN then reversal = engineered liquidity grab.
  - **POC of the footprint bar** (highest-volume price inside the bar) shows where the bar's value was actually made.

### 6. Confluence

- **VWAP**: `VWAP = Σ (price × volume) / Σ volume`. The session/weekly VWAP is institutional fair value; price below VWAP = "cheap," above = "expensive" *while the market is in balance*. In imbalance, VWAP loses meaning.
- **Prior-period levels**: yesterday's VAH/VAL/POC are the first references for today's session (opening inside/outside value, POC-return trades).
- **Volume profile + technical analysis**: use profile levels as objective S/R and score them with the technical-analysis skill's confluence framework.

## Anti-Patterns

- **Treating LVNs as support/resistance**: LVNs are where price moves *fast*, not where it stops. Longs "at support" on an LVN get run over during imbalance.
- **Ignoring the timeframe of the profile**: a 1-year composite profile hides recent shifts. Market memory is short — the most recent value areas matter most. Check a recent-range profile (e.g., last 3 months) alongside the 1y view.
- **Fighting the POC**: POC is a magnet during balance but a pivot during imbalance. A breakout of the value area on expanding delta is *not* a fade-the-POC signal.
- **Over-optimizing bin size**: 5 bins is a blur; 500 bins is noise. Keep ~40–100 bins for daily data, or use an explicit dollar width proportional to the instrument's tick/ATR.
- **Assuming the 70% value area is magic**: 68–70% is a convention (≈1σ), not a law. Some platforms use 68.2%; be consistent and always report the achieved percentage.
- **Reading delta/footprint from OHLCV**: impossible — bid/ask volume is required. Don't fabricate "delta" from daily candles.
- **Chasing unfinished auctions blindly**: treat ambiguous extremes as finished auctions (rejection) until proven otherwise; unfinished auctions must be visually unambiguous.
- **No validation**: never trust a profile without sanity checks (see below). A bad row of data or a degenerate range silently poisons the output.

## Validation Checkpoints

- [ ] Fetch succeeded: bars ≈ 250 for `range=1y&interval=1d`; date range covers the full lookback.
- [ ] `p_max > p_min`; `bin_count ≥ 2`; no NaN/None rows survived.
- [ ] Total allocated volume ≈ sum of raw volumes (allocation is a partition of each day's volume).
- [ ] Value area includes ≥ 70% of total volume (script prints the achieved %; a value area that hits 100% because of a degenerate distribution is a warning sign).
- [ ] POC price lies between VAL and VAH, and POC bin volume is the max of the profile.
- [ ] HVN list contains the POC; liquidity gaps (zero bins) exist only *inside* the traded range, not above/below it.
- [ ] Chart renders: price line on the left, horizontal histogram on the right, shared price axis; VA band spans VAL–VAH; POC/VAH/VAL/current-price lines visible.
- [ ] `RESULT_JSON` parses and its numbers match the human-readable summary.

## Example

```bash
"$PY" "$SCRIPT" --ticker MU
```

```
=== Volume Profile: MU (2025-08-16 → 2026-08-15, 251 bars) ===
Profile range      : 84.28 – 287.34 (60 bins × 3.38)
POC                : 128.85
Value area (70%)   : 105.12 – 156.40 (70.1% of volume)
HVN (>=1.5x avg)   : 105.12, 128.85, 156.40, 178.02
LVN (<=0.5x avg)   : 91.98, 193.40, 218.10, 242.80, 265.50
Liquidity gaps     : 2
Last close         : 149.60 (+16.1% vs POC, inside value area)
Nearest HVN above  : 156.40
Nearest HVN below  : 128.85
Nearest LVN above  : 193.40
Nearest LVN below  : 91.98
Chart saved        : C:/Users/iHC/AppData/Local/hermes/cache/images/MU_volprofile.png
```

**Reading it**: price is inside value, above the POC (buyers in control on balance), with the VAH at 156.40 as the first resistance/magnet and the POC at 128.85 as the nearest rotational support. A move through the LVN at 193.40 would be expected to be quick (thin liquidity) — a low-probability stop to place, a high-probability target zone once initiative is confirmed.

## References

- Steidlmayer, J. P. & Hawkins, S. B. (2003). *Steidlmayer on Markets: Trading with Market Profile*. Wiley.
- Dalton, J. F. (1993). *Mind Over Markets: Power Trading with Market Generated Information*. Traders Press.
- Villahermosa, R. (2020). *Wyckoff 2.0: Structures, Volume Profile and Order Flow*.
- CME Group — Market Profile / auction market theory educational materials.
- Sierra Chart & NinjaTrader 8 documentation — Volume Profile and order-flow study definitions.

*Educational tooling only — not financial advice. Past structure does not guarantee future behavior.*
