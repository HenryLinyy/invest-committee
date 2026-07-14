# invest-committee 安裝指南（投資委員會）

像機構一樣研究個股的六階段研究管線，支援 **台股 / 美股 / 港股 / A股**，依代碼自動路由。
僅供研究參考，不執行任何下單。輸出繁體中文。

> 最快路徑：跑 `./install.sh`（macOS / Linux），它會自動裝 skill、加台股資料源、建好你的投資設定檔。想手動或用 Windows，看下面「手動安裝」。

---

## 1. 這個 skill 需要什麼

| 需求 | 用途 | 必裝? |
|---|---|---|
| **Claude Code**（或相容 Agent Skills 的 runtime） | 執行 skill 本體 | ✅ 必裝 |
| **Docker** | 跑台股資料源 twstock MCP | 分析台股必裝；只看美/港/A股可略 |
| **Python 3** | 技術指標計算（`scripts/indicators.py`） | ✅ 必裝（macOS/Linux 通常內建） |
| **Futu OpenD**（富途） | 美 / 港 / A股行情與財報 | 選裝（不裝則退回免費源）|

各市場資料源優先序（skill 會自動退回）：

| 市場 | 優先 1 | 優先 2 | 最後手段 |
|---|---|---|---|
| 台股 | twstock MCP | 富途 OpenD | 網搜（標出處） |
| 美股 | 富途 OpenD | Yahoo Finance 公開 API | 網搜 |
| 港股 / A股 | 富途 OpenD | 免費網源 | 網搜 |

**結論**：只想分析台股 → 裝 Docker + twstock MCP 就夠。要美/港/A股即時資料 → 再加 Futu OpenD。

---

## 2. 一鍵安裝（macOS / Linux 推薦）

```bash
cd invest-committee
chmod +x install.sh
./install.sh
```

腳本會做四件事（每步會問你確認）：
1. 複製 skill 到 `~/.claude/skills/invest-committee/`
2. 檢查 Docker，並執行 `claude mcp add` 掛上 twstock 台股資料源
3. 建立你的投資設定目錄 `~/.invest-committee/`（含 profile.md、watchlist.md、reports/）
4. 印出「下一步：填設定檔 + 怎麼開始用」

裝完直接跳到 [第 5 節：開始使用](#5-開始使用)。

---

## 3. 手動安裝（含 Windows）

### 步驟 1：安裝 skill 本體
把整個 `invest-committee/` 資料夾複製到你的 skills 目錄：

- **macOS / Linux**：`~/.claude/skills/invest-committee/`
- **Windows**：`%USERPROFILE%\.claude\skills\invest-committee\`

複製後，該目錄下應有 `SKILL.md`、`references/`、`scripts/`、`assets/`。

### 步驟 2：台股資料源 — twstock MCP（Docker）
先確認 Docker 已安裝並在執行（`docker --version`）。然後：

```bash
claude mcp add --scope user twstock -- docker run -i --rm --pull=always -e MCP_STDIO=1 ghcr.io/twjackysu/twsemcpserver:latest
```

驗證：重開 Claude Code，`/mcp` 應看到 `twstock`（或問「twstock 有連上嗎」）。
第一次會拉 Docker image，需要幾分鐘。

### 步驟 3（選裝）：美 / 港 / A股資料源 — Futu OpenD
兩種方式：

- **用 install-futu-opend skill（最簡單）**：在 Claude Code 裡輸入 `/install-futu-opend`，它會自動偵測作業系統、下載安裝 OpenD 並升級 Python SDK。
- **手動**：到富途官網下載對應平台的 OpenD，登入富途帳號後啟動（預設本機 port 11111）。

不裝也能用——skill 會自動退回 Yahoo/網搜並在報告註明「富途未連線」。

### 步驟 4：建立投資設定目錄
skill 依序找 ① `~/.invest-committee/` ② 工作目錄下的 `portfolio/`。建議用第 ①：

```bash
mkdir -p ~/.invest-committee/reports
cp assets/templates/profile.md   ~/.invest-committee/profile.md
cp assets/templates/watchlist.md ~/.invest-committee/watchlist.md
```

（Windows 用 `%USERPROFILE%\.invest-committee\`。）

---

## 4. 填你的投資設定檔

編輯 `~/.invest-committee/profile.md`（決定部位建議怎麼算）：

| 欄位 | 說明 |
|---|---|
| 總投資資金 | 填了才會給金額；留「未設定」則只給 % |
| 單一部位上限 | 單股佔總資金最大比例（預設 10%） |
| 風險承受度 | 低／中／高 |
| 預設投資週期 | 短線／波段／長線 |

`~/.invest-committee/watchlist.md`：填你的自選股（之後可「健檢自選股」批次掃描）。

---

## 5. 開始使用

在 Claude Code 裡直接說（skill 會自動觸發）：

| 你想做 | 這樣說 |
|---|---|
| 單股深度分析 | 「幫我分析台積電」「開投資委員會看 NVDA」 |
| 只看某一面 | 「看 2330 技術面」「掃 0700 港股風險」「600519 基本面如何」 |
| 自選股健檢 | 「健檢自選股」 |
| 兩檔比較 | 「比較台積電和聯電」 |

產出：四大分析小結（基本面／機構觀點／資金技術／風險雷達）＋含部位建議與停損的行動計畫，完整版另附視覺化 dashboard。所有數值標來源，缺資料標「未獲取」，絕不編造。

> 題材級選股（如「AI 供應鏈哪檔最值得研究」，沒有具體代碼）不歸本 skill——請先用 **serenity-skill** 掃產業鏈卡點取得名單，再帶回本 skill 逐檔深研。

---

## 💰 省 token / 控制費用（重要）

這是深度研究工具，一次完整六階段分析會抓大量即時資料，**token 用量偏高**（實測全跑一檔約 15–20 萬 token）。內建了模型路由來省錢，也有幾個你能做的：

**內建：階段 1 抓資料自動委派便宜模型**
skill 會把「純抓取」（K線、財報、籌碼、跑指標）委派給便宜的子模型（預設 **Haiku**），主 session 只收整理好的精簡資料包再做分析——大量原始資料不會灌進貴模型的 context。
- 想調：改 `~/.invest-committee/profile.md` 的「資料收集模型」（haiku 最省／sonnet 較會判斷網搜來源）。

**你能做的（省很多）**
| 做法 | 效果 |
|---|---|
| **主 session 用強模型跑分析、讓 skill 外包抓取** | 把 Claude Code 設成 Opus/Sonnet 做判斷，抓資料交給 Haiku 子 agent——貴模型只吃精簡資料 |
| **能單環節就別全跑** | 說「看 X **技術面**」「掃 X **風險**」只跑 1 階段，比「幫我分析 X」全六階段省一大截 |
| **台股優先，或補裝 Futu OpenD** | 沒裝 OpenD 時分析美/港/A股會整條退**網搜**（最燒）；只做台股（twstock）或裝好 OpenD 可大幅減少網搜 |
| **健檢批次交給便宜模型** | 「健檢自選股」每檔抓取都走便宜子 agent（可並行），主 session 只彙整燈號 |

> 一句話：**貴模型做判斷，便宜模型做苦力**；不需要深研時用單環節模式。

## 6. 疑難排解

| 症狀 | 處理 |
|---|---|
| skill 沒被觸發 | 確認資料夾在 `~/.claude/skills/invest-committee/`、重開 Claude Code；或直接說「用 invest-committee 分析…」 |
| 台股抓不到資料 | 確認 Docker 在跑；`/mcp` 看 twstock 是否連上；第一次拉 image 需等幾分鐘 |
| `claude mcp add` 找不到指令 | 需先安裝 Claude Code CLI；或在互動式 `claude` 裡用 `/mcp` 加 |
| 美/港/A股資料少 | 那是富途未連線的退回行為，屬正常；要完整資料請裝 Futu OpenD 並登入 |
| 指標計算失敗 | 確認 `python3 --version` 可用；skill 會如實回報錯誤、不以心算補值 |
| Windows 沒有 Docker | 裝 Docker Desktop；或先只用美股（Futu/Yahoo），台股功能待 Docker 就緒 |

---

## 檔案結構
```
invest-committee/
├── SKILL.md              # skill 本體（六階段管線 + 紅線黑名單 + 檢查點）
├── INSTALL.md            # 本檔
├── install.sh            # 一鍵安裝腳本
├── references/           # 各階段口徑、資料源路由、報告模板
├── scripts/              # indicators.py（技術指標）+ 單元測試
└── assets/               # dashboard 模板 + profile/watchlist 範本
```

研究支援工具，非投資建議；買賣決策與盈虧由你自負。
