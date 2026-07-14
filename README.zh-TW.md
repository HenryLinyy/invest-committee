# invest-committee（投資委員會）

[English](README.md) | **繁體中文**

<p align="center">
  <img src="assets/conclava.jpg" alt="Conclava 頭像" width="220">
</p>

> 一句「幫我分析台積電」，產出一份可追溯資料來源的投資委員會報告：基本面、機構觀點、籌碼與技術、風險燈號，以及受部位上限約束的行動計畫。

這是一個 [Claude Code](https://claude.com/claude-code) Agent Skill，協助散戶用更有紀律的方式研究**具體個股**。支援 **台股 / 美股 / 港股 / A 股**，會依代碼自動路由資料來源；只做研究，不執行任何下單。

## 你可以信任的三件事

- **每個數字有來源**：價格、財報與籌碼數值都要能追溯；拿不到就標示「未獲取」。
- **資料缺口會明講**：資料過期、來源退級或 K 線不足，會直接列在報告裡，不假裝結論完整。
- **研究不代替下單**：skill 不會呼叫交易 API；輸出僅供研究參考，非投資建議。

## 先試這句（約 1 個環節）

在 Claude Code 輸入：

```text
看 2330 技術面
```

它只會跑對應的技術面環節，比完整六階段研究更快、token 用量也更低。確認輸出符合你的研究習慣後，再試「幫我分析台積電」。

## 你想解決什麼問題？

| 你的情境 | 在 Claude Code 裡這樣說 |
|---|---|
| 把一檔股票從基本面到風險完整研究 | 「幫我分析台積電」「深度分析 NVDA」 |
| 只想先確認技術面或風險 | 「看 2330 技術面」「掃 NVDA 風險」 |
| 快速檢查持有或追蹤清單 | 「健檢自選股」 |
| 比較兩檔候選股 | 「比較台積電和聯電」 |
| 準備台股當沖劇本 | 「力成當沖」「6239 當沖劇本」 |

完整分析會交付附來源的研究報告，以及 HTML dashboard；內容包含部位建議、進出場價位、停損與風險清單。當沖功能僅限台股。

> 若沒有自動觸發，直接說「use invest-committee to analyze …」。題材或產業層級的選股不在本 skill 範圍內；請先建立具體標的清單，再逐檔研究。

## 六階段研究流程

**資料收集 → 基本面與成長品質 → 機構觀點共識 → 資金籌碼與技術擇時 → 風險雷達 → 行動計畫**

技術指標一律由 `scripts/indicators.py` 實算，不靠心算或猜測補值。資料來源不可用時會依序退回可用來源，並在報告中說明原因。

## 最快開始

```bash
git clone https://github.com/HenryLinyy/invest-committee.git
cd invest-committee
chmod +x install.sh
./install.sh
```

安裝腳本會安裝 skill、掛載台股資料源（twstock MCP）並建立投資設定檔，每一步都會先詢問確認。

需求：Claude Code 與 Python 3。台股資料需要 Docker；美／港／A 股的即時資料可選裝 Futu OpenD，未安裝時會退回免費來源。

手動安裝、Windows 支援、資料來源與省 token 設定，請見 [INSTALL.md](INSTALL.md)。

> 💰 完整六階段研究約使用 **15–20 萬 tokens**。若只需要一個角度，優先使用「看 X 技術面」或「掃 X 風險」；詳見 [INSTALL.md](INSTALL.md) 的省 token／控制費用說明。

## 免責聲明

本工具僅供研究與學習參考，**非投資建議**；所有輸出不構成任何買賣邀約。下單決策與盈虧請自行負責。

## 授權

[MIT](LICENSE) © 2026 HenryLinyy
