# invest-committee (Investment Committee)

**English** | [繁體中文](README.zh-TW.md)

> Turn “analyze TSMC” into a source-cited investment-committee memo: fundamentals, institutional consensus, technical levels, risk flags, and a position-sizing action plan.

An [Agent Skill for Claude Code](https://claude.com/claude-code) that helps retail investors research **specific stocks** with more discipline. It covers **Taiwan / US / Hong Kong / China A-share** markets and routes data sources by ticker. It supports research only — it never places orders.

> **Language note:** reports are currently generated in **Traditional Chinese (zh-TW)**. The workflow and methodology are market-agnostic.

## Three things you can rely on

- **Every figure needs a source.** Prices, financials, and flow data are cited; unavailable values are labeled as missing.
- **Data gaps are visible.** Stale data, source fallbacks, and insufficient candle history are disclosed instead of presented as a complete conclusion.
- **Research never becomes execution.** The skill does not call trading APIs; its output is research support, not investment advice.

## Try this first (one stage)

In Claude Code, say:

```text
Analyze NVDA technicals
```

This runs only the relevant technical-analysis stage, so it is a faster and lower-token way to see whether the workflow fits you. When you are ready, try a full deep dive with “Analyze NVDA in depth.”

## What are you trying to do?

| Your goal | Say this in Claude Code |
|---|---|
| Research one stock from fundamentals through risk | “幫我分析台積電” / “Analyze NVDA in depth” |
| Check only technicals or risk | “看 2330 技術面” / “掃 NVDA 風險” |
| Check the health of a watchlist | “健檢自選股” |
| Compare two candidate stocks | “比較台積電和聯電” / “Compare TSMC vs UMC” |
| Build a Taiwan day-trading playbook | “力成當沖” / “6239 當沖劇本” |

A full analysis delivers a source-cited research report and an HTML dashboard with position sizing, entry/exit levels, stop-loss, and a risk checklist. Day-trading support is Taiwan-only.

> If auto-triggering misses, say “use invest-committee to analyze …” explicitly. Theme- or industry-level stock screening is outside this skill’s scope; build a concrete ticker list first, then research each name here.

## The six-stage workflow

**Data collection → fundamentals & growth quality → institutional consensus → money flow & technical timing → risk radar → action plan**

Technical indicators are calculated by `scripts/indicators.py`, never estimated mentally. When a primary source is unavailable, the workflow falls back through available sources and records why in the report.

## Fastest start

```bash
git clone https://github.com/HenryLinyy/invest-committee.git
cd invest-committee
chmod +x install.sh
./install.sh
```

The installer adds the skill, wires up the Taiwan data source (twstock MCP), and creates an investor profile, asking for confirmation at every step.

Requirements: Claude Code and Python 3. Taiwan market data requires Docker. Real-time US/HK/China-A data can optionally use Futu OpenD; without it, the skill falls back to free sources.

For manual and Windows installation, data-source details, and token controls, see [INSTALL.en.md](INSTALL.en.md).

> 💰 A full six-stage research run uses roughly **150–200K tokens**. For a cheaper first pass, use a focused request such as “Analyze NVDA technicals” or “掃 NVDA 風險”; see [INSTALL.en.md](INSTALL.en.md) for cost controls.

## Disclaimer

For research and educational purposes only — **not investment advice**. Nothing in the output constitutes an offer to buy or sell any security. Trading decisions and outcomes are your own responsibility.

## License

[MIT](LICENSE) © 2026 HenryLinyy
