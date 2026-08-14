# Trading Edge 📈 — Agent Skills for the Complete Trading Stack

A curated suite of **6 Agent Skills** covering the four pillars of disciplined trading — conviction, timing, market mood, and allocation. Built for any [Agent Skills](https://agentskills.io)-compatible tool (Claude Code, Cursor, Codex, Gemini CLI, Hermes, OpenClaw, and 30+).

[![Skills: 6](https://img.shields.io/badge/Skills-6-brightgreen) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

*Sibling repo of [insight-heist](https://github.com/DucklingGod/insight-heist) (data analysis). These two repos split cleanly: insight-heist turns raw data into findings; trading-edge turns findings into decisions.*

## What's Inside

| Skill | Pillar | Question it answers |
|---|---|---|
| `fundamental-analysis` | 🧠 Conviction | Is this asset cheap, fair, or expensive? (ratios, DCF, tokenomics, macro, earnings) |
| `technical-analysis` | 📈 Timing | When do I enter, where do I stop? (indicators, patterns, S/R, MTF, confluence scoring) |
| `sentiment-composite` | 🎭 Mood | What is the crowd doing — and when is it extreme? (-100..+100 composite score) |
| `portfolio-management` | 🏗️ Allocation | How do I size and balance the whole book? (frameworks, rebalancing, attribution, risk metrics) |
| `prediction-markets` | 🎲 Events | What are the real odds — and where is the market wrong? (probability, edge, Kelly sizing, biases, arbitrage) |
| `trade-risk-management` | 🛡️ Gatekeeper | Is this trade safe? (mandatory pre-trade gate: sizing, stops, R:R, portfolio risk, drawdown, leverage, agent guardrails) |

## The Stack

```
fundamental-analysis  →  is it worth owning?      (conviction layer)
technical-analysis    →  when and where to trade? (timing layer)
sentiment-composite   →  is the crowd an edge?    (overlay layer)
portfolio-management  →  how do I allocate?       (portfolio layer)
```

Every skill includes Anti-Patterns, Validation Checkpoints, and a worked example.

## Installation

### One-liner (any Agent Skills tool)

```
npx skills add https://github.com/DucklingGod/trading-edge
```

### Manual copy

Clone and copy `skills/*` into your agent's skills directory:

| Agent | Global skills dir |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Codex | `~/.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Hermes | `~/AppData/Local/hermes/skills/` (Windows) or `~/.local/share/hermes/skills/` (Linux) |

## Quick Start

- "Run fundamental analysis on SPCX — what is fair value?"
- "Technical analysis on BTC — swing trade setup on daily?"
- "What is current Bitcoin sentiment? Composite score please."
- "Build me a moderate-risk portfolio across crypto and equities."

## Example

Each skill ships with a full worked example:

- `fundamental-analysis`: AAVE valuation vs MKR/COMP (P/F, P/Revenue, tokenomics, verdict + target range)
- `technical-analysis`: BTC/USDT long setup — confluence score 72/100, entry/stop/targets/invalidation
- `sentiment-composite`: Bitcoin composite +62 (Optimism/Greed) with per-category breakdown
- `portfolio-management`: $200,000 moderate-risk risk-parity portfolio (weights, correlations, rebalancing)

## License

MIT — see [LICENSE](LICENSE). Author: DucklingGod.

*Not affiliated with Binance, Anthropic, or any vendor. Skills are educational — always verify results and manage risk before acting.*
