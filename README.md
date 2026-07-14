# invest-committee (Investment Committee)

**English** | [繁體中文](README.zh-TW.md)

> Institutional-grade stock research for retail investors — say "analyze TSMC" and a six-stage research pipeline returns an action plan with position sizing, entry/exit levels, and a visual dashboard.

An Agent Skill for [Claude Code](https://claude.com/claude-code). Covers **Taiwan / US / Hong Kong / China A-share** markets, auto-routing data sources by ticker. Research support only — it never places orders.

> **Language note**: analysis reports are generated in **Traditional Chinese (zh-TW)** — the skill was built for Taiwanese retail investors. The pipeline and methodology are market-agnostic.

## What it does

Six-stage pipeline: **data collection → fundamentals & growth quality → institutional consensus → money flow & technical timing → risk radar → action plan**.

| Mode | Example prompt |
|---|---|
| Deep dive on one stock | "幫我分析台積電" / "Analyze NVDA in depth" |
| Single-angle quick check | "看 2330 技術面" (technicals) / "掃 NVDA 風險" (risk scan) |
| Watchlist health check | "健檢自選股" — batch-scans your watchlist |
| Head-to-head comparison | "比較台積電和聯電" / "Compare TSMC vs UMC" |
| Day-trade playbook (Taiwan only) | "6239 當沖劇本" |

> Tip: if auto-trigger misses, say "use invest-committee to analyze …" explicitly.

Full reports ship with an HTML dashboard: position sizing, entry/exit levels, stop-loss, and a risk checklist.

## Design principles (hard red lines)

- **No fabricated numbers** — every price/financial/flow figure needs a source; missing data is labeled as such, never guessed.
- **No order execution** — research only; the skill never calls any trading API.
- **No mental math for indicators** — all technical indicators are computed by `scripts/indicators.py`.
- **No hidden data gaps** — source downgrades and stale data are disclosed in the report.

## Install

```bash
cd invest-committee
chmod +x install.sh
./install.sh
```

The installer copies the skill, wires up the Taiwan market data source (twstock MCP via Docker), and creates your investor profile — asking for confirmation at every step. **Its prompts are currently in Chinese**; English speakers may prefer the two-minute manual steps in **[INSTALL.en.md](INSTALL.en.md)**.

Requirements: Claude Code and Python 3; Docker for Taiwan stocks; optional Futu OpenD for US/HK/China-A real-time data (falls back to free sources without it).

> 💰 This is a deep-research tool — a full six-stage run uses roughly **150–200K tokens**. Cost-control tips (built-in cheap-model delegation for data fetching, single-stage mode) are in [INSTALL.en.md](INSTALL.en.md).

## Disclaimer

For research and educational purposes only — **not investment advice**. Nothing in the output constitutes an offer to buy or sell any security. Trading decisions and outcomes are your own responsibility.

## License

[MIT](LICENSE) © 2026 HenryLinyy
