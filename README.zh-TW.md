# invest-committee（投資委員會）

[English](README.md) | **繁體中文**

> 散戶自用的機構級個股研究流程 —— 一句「幫我分析台積電」，跑完六階段研究管線，產出含部位建議的行動計畫與 dashboard。

這是一個 [Claude Code](https://claude.com/claude-code) Agent Skill。支援 **台股 / 美股 / 港股 / A股**，依代碼自動路由資料源。僅供研究參考，不執行任何下單。輸出繁體中文。

## 它會做什麼

六階段管線：**資料收集 → 基本面成長品質 → 機構觀點共識 → 資金籌碼技術擇時 → 風險雷達 → 行動計畫**。

| 模式 | 觸發例 |
|---|---|
| 單股深度分析 | 「幫我分析台積電」「深度分析 NVDA」 |
| 單環節速查 | 「看 2330 技術面」「掃 NVDA 風險」 |
| 自選股健檢 | 「健檢自選股」（逐檔掃 watchlist） |
| 個股比較 | 「比較台積電和聯電」 |
| 當沖劇本（限台股） | 「力成當沖」「6239 當沖劇本」 |

完整版報告另附視覺化 dashboard（HTML），含部位建議、進出場價位與風險清單。

## 設計原則（紅線）

- **不編造數值**：所有價格／財報／籌碼數字必須有來源，查無就標「未獲取」。
- **不下單**：只做研究，絕不呼叫任何交易 API。
- **指標不心算**：技術指標一律由 `scripts/indicators.py` 實算。
- **不隱藏資料缺口**：來源退級、資料過期會在報告中明講。

## 安裝

```bash
cd invest-committee
chmod +x install.sh
./install.sh
```

腳本會裝 skill、掛台股資料源（twstock MCP，需 Docker）、建立你的投資設定檔，每步都會先問你確認。手動安裝、Windows、以及美/港/A股資料源（Futu OpenD，選裝）見 **[INSTALL.md](INSTALL.md)**。

需求：Claude Code、Python 3；分析台股需 Docker；美/港/A股即時資料選裝 Futu OpenD（不裝會自動退回免費源）。

> 💰 這是深度研究工具，一次完整六階段分析 token 用量偏高（實測約 15–20 萬）。省錢設定見 [INSTALL.md](INSTALL.md) 的「省 token / 控制費用」一節。

## 免責聲明

本工具僅供研究與學習參考，**非投資建議**；所有輸出不構成任何買賣邀約，下單決策與盈虧請自行負責。

## 授權

[MIT](LICENSE) © 2026 HenryLinyy
