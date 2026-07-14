# invest-committee Install Guide (Investment Committee)

[繁體中文](INSTALL.md) | **English**

A six-stage pipeline for researching individual stocks the way an institution would. Covers **Taiwan / US / Hong Kong / China A-share** markets with automatic data-source routing by ticker.
Research support only — it never places orders. Reports are written in Traditional Chinese.

> Fastest path: run `./install.sh` (macOS / Linux) — it installs the skill, wires up the Taiwan data source, and creates your investor config. Its interactive prompts are currently Chinese-only; for an English-friendly path or Windows, follow "Manual install" below.

---

## 1. What this skill needs

| Requirement | Purpose | Required? |
|---|---|---|
| **Claude Code** (or an Agent Skills-compatible runtime) | Runs the skill itself | ✅ Required |
| **Docker** | Runs the twstock MCP (Taiwan market data) | Required for Taiwan stocks; skip if you only follow US/HK/China-A |
| **Python 3** | Technical indicator engine (`scripts/indicators.py`) | ✅ Required (preinstalled on most macOS/Linux) |
| **Futu OpenD** | US / HK / China-A quotes & financials | Optional (falls back to free sources without it) |

Data-source priority per market (the skill degrades gracefully):

| Market | 1st choice | 2nd choice | Last resort |
|---|---|---|---|
| Taiwan | twstock MCP | Futu OpenD | Web search (sources cited) |
| US | Futu OpenD | Yahoo Finance public API | Web search |
| HK / China-A | Futu OpenD | Free web sources | Web search |

**Bottom line**: Taiwan stocks only → Docker + twstock MCP is enough. Want real-time US/HK/China-A data → add Futu OpenD.

---

## 2. One-command install (macOS / Linux)

```bash
cd invest-committee
chmod +x install.sh
./install.sh
```

The script does four things (asking for confirmation at every step):
1. Copies the skill to `~/.claude/skills/invest-committee/`
2. Checks Docker and runs `claude mcp add` to wire up the twstock Taiwan data source
3. Creates your investor config directory `~/.invest-committee/` (profile.md, watchlist.md, reports/)
4. Prints next steps

> **Note**: the installer's prompts are in Chinese. If that's a blocker, the manual steps below take about two minutes.

Once installed, jump to [Section 5: Start using it](#5-start-using-it).

---

## 3. Manual install (incl. Windows)

### Step 1: Install the skill itself
Copy the whole `invest-committee/` folder into your skills directory:

- **macOS / Linux**: `~/.claude/skills/invest-committee/`
- **Windows**: `%USERPROFILE%\.claude\skills\invest-committee\`

After copying, that directory should contain `SKILL.md`, `references/`, `scripts/`, and `assets/`.

### Step 2: Taiwan data source — twstock MCP (Docker)
Make sure Docker is installed and running (`docker --version`). Then:

```bash
claude mcp add --scope user twstock -- docker run -i --rm --pull=always -e MCP_STDIO=1 ghcr.io/twjackysu/twsemcpserver:latest
```

Verify: restart Claude Code — `/mcp` should list `twstock` (or just ask "is twstock connected?").
The first run pulls the Docker image and takes a few minutes.

### Step 3 (optional): US / HK / China-A data source — Futu OpenD
Two ways:

- **Via the install-futu-opend skill (easiest)**: type `/install-futu-opend` in Claude Code — it detects your OS, downloads and installs OpenD, and upgrades the Python SDK.
- **Manually**: download OpenD for your platform from Futu's official site, sign in with your Futu account, and start it (default local port 11111).

The skill works without it — it falls back to Yahoo/web search and notes "Futu not connected" in the report.

### Step 4: Create your investor config directory
The skill looks for ① `~/.invest-committee/`, then ② `portfolio/` under the working directory. Option ① is recommended:

```bash
mkdir -p ~/.invest-committee/reports
cp assets/templates/profile.md   ~/.invest-committee/profile.md
cp assets/templates/watchlist.md ~/.invest-committee/watchlist.md
```

(On Windows use `%USERPROFILE%\.invest-committee\`.)

---

## 4. Fill in your investor profile

Edit `~/.invest-committee/profile.md` — it drives how position advice is calculated. The template is in Chinese; the fields are:

| Field | Meaning |
|---|---|
| 總投資資金 (total capital) | Set it to get position sizes in currency; leave as「未設定」(unset) to get percentages only |
| 單一部位上限 (max single position) | Max share of total capital in one stock (default 10%) |
| 風險承受度 (risk tolerance) | 低 (low) / 中 (medium) / 高 (high) |
| 預設投資週期 (default horizon) | 短線 (short-term) / 波段 (swing) / 長線 (long-term) |

`~/.invest-committee/watchlist.md`: your watchlist, used by the batch health-check mode.

---

## 5. Start using it

Just say it in Claude Code (the skill auto-triggers):

| You want | Say |
|---|---|
| Deep dive on one stock | "幫我分析台積電" / "Analyze NVDA in depth" |
| One angle only | "看 2330 技術面" (technicals) / "掃 0700 港股風險" (risk scan) |
| Watchlist health check | "健檢自選股" / "health-check my watchlist" |
| Compare two stocks | "比較台積電和聯電" / "Compare TSMC vs UMC" |

> Tip: if auto-trigger misses, say "use invest-committee to analyze …" explicitly.

Output: four analysis summaries (fundamentals / institutional views / flows & technicals / risk radar) plus an action plan with position sizing and stop-loss; the full version also ships an HTML dashboard. Every figure cites its source, missing data is labeled — never fabricated.

> Theme-level screening (e.g. "which AI supply-chain stock is most worth researching", no specific ticker) is out of scope — use a screening tool such as **serenity-skill** to build a shortlist first, then bring the tickers back here for deep dives.

---

## 💰 Token / cost control (important)

This is a deep-research tool — a full six-stage run fetches a lot of live data and uses roughly **150–200K tokens** per stock. Model routing is built in to keep costs down, and there are a few things you can do too:

**Built-in: stage-1 data fetching is delegated to a cheap model**
The skill hands "pure fetching" (candles, financials, flow data, indicator runs) to a cheap sub-model (default **Haiku**); your main session only receives a condensed data pack for analysis — raw data never floods the expensive model's context.
- To tune it: edit the「資料收集模型」(data-collection model) field in `~/.invest-committee/profile.md` (haiku = cheapest / sonnet = better judgment on web sources).

**What you can do (saves a lot)**
| Practice | Effect |
|---|---|
| **Run analysis on a strong model, let the skill outsource fetching** | Set Claude Code to Opus/Sonnet for judgment; fetching goes to Haiku sub-agents — the expensive model only reads condensed data |
| **Use single-stage mode when possible** | "看 X 技術面" (technicals only) runs 1 stage — far cheaper than a full six-stage deep dive |
| **Taiwan-first, or install Futu OpenD** | Without OpenD, US/HK/China-A analysis falls back to web search (the most expensive path); Taiwan-only (twstock) or OpenD installed cuts web searching drastically |
| **Batch health checks ride on cheap models** | Watchlist health checks fetch via cheap sub-agents (parallelizable); the main session only aggregates the verdicts |

> In one line: **expensive model for judgment, cheap model for grunt work** — and use single-stage mode when you don't need a full deep dive.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| Skill doesn't trigger | Confirm the folder is at `~/.claude/skills/invest-committee/` and restart Claude Code; or say "use invest-committee to analyze …" explicitly |
| No Taiwan market data | Make sure Docker is running; check `/mcp` shows twstock connected; the first image pull takes a few minutes |
| `claude mcp add` command not found | Install the Claude Code CLI first, or add it via `/mcp` inside an interactive `claude` session |
| Sparse US/HK/China-A data | That's the normal fallback when Futu isn't connected; install and sign in to Futu OpenD for full data |
| Indicator computation fails | Check `python3 --version` works; the skill reports errors honestly and never fills in guessed values |
| No Docker on Windows | Install Docker Desktop; or start with US stocks only (Futu/Yahoo) and add Taiwan once Docker is ready |

---

## File layout
```
invest-committee/
├── SKILL.md                      # skill core (six-stage pipeline + hard red lines + checkpoints)
├── README.md / README.zh-TW.md   # project intro (English / Traditional Chinese)
├── INSTALL.md / INSTALL.en.md    # install guide (Traditional Chinese / English)
├── install.sh                    # one-command installer
├── references/                   # per-stage playbooks, data-source routing, report templates
├── scripts/                      # indicators.py (technical indicators) + unit tests
└── assets/                       # dashboard templates + profile/watchlist templates
```

A research-support tool, not investment advice; trading decisions and outcomes are your own responsibility.
