---
name: invest-committee
description: 散戶自用的機構級個股研究流程（投資委員會）。融合基本面成長品質、機構觀點共識、資金籌碼技術擇時、風險雷達四大分析與完整行動計畫產出，支援台股/美股/港股/A股依代碼自動路由。當用戶要求分析個股（「幫我分析台積電」「深度分析 NVDA」「看 0700 港股」「分析 A股 600519」）、開投資委員會、健檢自選股、掃描個股風險、看技術面、比較兩檔股票、看某檔台股當沖／當沖劇本／比較兩檔當沖（「力成當沖」「6239 當沖劇本」）時使用。
---

# invest-committee（投資委員會）

像機構一樣研究個股：六階段管線產出含部位建議的行動計畫。僅供研究參考，不執行任何下單。輸出繁體中文。

## 🔴 紅線黑名單（絕不做 — 每次輸出前逐條自檢）

1. 🚫 **不編造數值**：任何價格／財報／籌碼數字必須有來源；查無 → 標「未獲取」，嚴禁用「較高／大概／約」搪塞或憑記憶填數。
2. 🚫 **不下單、不代做買賣決策**：本 skill 只做研究，絕不呼叫任何下單／交易 API；行動計畫一律附「僅供研究參考，非投資建議，下單與盈虧自負」。
3. 🚫 **不猜代碼、不猜市場**：查無個股或市場判定不了 → 請使用者確認，絕不自行替換成相近標的。
4. 🚫 **指標不心算**：技術指標一律取 `scripts/indicators.py` 輸出；腳本失敗 → 如實回報，絕不心算或估算補值。
5. 🚫 **不整段照抄研報／新聞**：改寫總結並標出處，不原文搬運。
6. 🚫 **不隱藏資料缺口**：來源退級、資料過期、K線不足一律在報告中明講，不粉飾成完整結論。

## §1 模式判定（先做）

| 模式 | 觸發例 | 行為 |
|---|---|---|
| 單股深度 | 「幫我分析台積電」「開投資委員會看 NVDA」 | 跑完整六階段 → 完整版報告＋dashboard |
| 單環節 | 「看 NVDA 技術面」「掃 2330 風險」「2330 基本面如何」 | 只跑對應階段（2-5 其一）＋精簡結論，不跑全管線 |
| 自選股健檢 | 「健檢自選股」 | 讀 watchlist 逐檔跑精簡版（風險雷達＋資金技術重大變化）→ 健檢精簡版報告 |
| 個股比較 | 「比較台積電和聯電」 | 兩檔各跑階段 2-5 核心 → 比較版報告 |
| 當沖 | 「力成當沖」「看 2408 當沖」「當沖劇本 6239」「比較力成和南亞科當沖」 | 走當沖管線（見 §8）→ 單股當沖卡或雙股並排＋裁定 |

觸發詞含「當沖／現沖／隔日沖／當沖劇本」→ 當沖模式（**限台股**）；句含 2 個標的＋「比較／和／vs」→ 雙股當沖。命中當沖詞就走 §8，不進六階段。

市場路由與代碼判定規則：讀 [references/data-sources.md](references/data-sources.md) §1。判斷不了市場時追問一次，不猜。

**題材級問題不歸本 skill**：若使用者問的是題材／產業層級的選股問題（如「AI 供應鏈哪檔最值得研究」「台股半導體幫我找標的」——沒有具體代碼），先建議改用 **serenity-skill** 掃產業鏈卡點、取得優先研究名單，再把名單帶回本 skill 逐檔深度分析或加入 watchlist。本 skill 從「有具體標的」才開始。

## §2 前置動作

0. 定位資料目錄（依序找，先中先用）：① `~/.invest-committee/` ② 目前工作目錄下的 `portfolio/`。都不存在 → 用 [assets/templates/](assets/templates/) 的範本建立 `~/.invest-committee/`（含 profile.md、watchlist.md、reports/），提示使用者填寫。
1. 讀 `<資料目錄>/profile.md`（總資金、單一部位上限、風險承受度、預設週期、資料收集模型）。缺檔或缺欄 → 用「上限 10%／承受度中／波段／資料收集模型 haiku」預設並提示。
2. 投資週期：任務有指定（短線/波段/長線）用指定值；否則用 profile 預設。
3. 健檢模式：讀 `<資料目錄>/watchlist.md` 逐列處理；表空 → 請使用者先填自選股。

## §3 六階段管線

單環節模式只跑對應階段；健檢模式每檔只跑階段 1、4（資金部分）、5。

**成本原則（省 token）**：階段 1 是純抓取（低推理、大量工具輸出），委派給便宜模型的子 agent 執行，把原始工具輸出留在它的 context；主 session（你跑分析用的較強模型，如 Opus）只收精簡資料包，再做階段 2-6 的判斷。這樣貴模型不被大量 K線／財報／網頁灌爆。

**階段 1：快照與資料收集（委派）** — 讀 [references/data-sources.md](references/data-sources.md)。
- **委派抓取**：runtime 支援指定子 agent 模型時，spawn 一個「資料收集子 agent」（模型取 profile 的「資料收集模型」，預設 **Haiku**；該市場需靠網搜判斷來源品質時改用 **Sonnet**）。交付它：依市場用 ToolSearch 一次批量載入 twstock 工具、取行情／公司基本資料／財務／籌碼、把 K線組成 §5 的 JSON 落地 scratchpad、跑 `scripts/indicators.py`，**只回傳精簡資料包**（數值＋來源表＋指標輸出＋「未獲取」缺漏清單），不回傳整段原始工具輸出。
- **子 agent 硬規則**：嚴守 §4 與 🔴 紅線黑名單——只回報抓到的值＋來源，缺的標「未獲取」，**絕不估算或編造，也不做任何分析判斷**（判斷全留給主 session）。主 session 收到資料包後應快掃缺漏清單，關鍵欄位缺太多才補抓。
- **不委派**：runtime 不支援指定子 agent 模型，或單環節只查單一數值的輕量請求 → 主 session 直接抓。
- 健檢批次：每檔的資料收集都走便宜子 agent（可並行），主 session 只彙整燈號與重大變化。

**階段 2：基本面與成長品質** — 讀 [references/stage-fundamental.md](references/stage-fundamental.md)。產出固定三行小結。

**階段 3：機構觀點與共識** — 讀 [references/stage-consensus.md](references/stage-consensus.md)。產出固定三行小結。

**階段 4：資金籌碼與技術擇時** — 讀 [references/stage-technical.md](references/stage-technical.md)。先跑 `scripts/indicators.py`，指標值一律取腳本輸出。產出固定三行小結。

**階段 5：風險雷達** — 讀 [references/stage-risk.md](references/stage-risk.md)。四維評分＋燈號，輸出前跑自洽校驗。

**階段 6：投資委員會結論** — 讀 [references/stage-action.md](references/stage-action.md)。Bull/Bear 對辯後依公式產出行動計畫表。
> 🔴 **CHECKPOINT（輸出行動計畫前自檢）**：建議部位不得超過 profile 的單一部位上限；超過 → 下修至上限並註明。行動計畫結尾必附「僅供研究參考，非投資建議，下單與盈虧自負」。

## §4 資料紀律（強制）

1. 所有數值必須有明確來源；缺資料一律標「未獲取」，嚴禁編造或用「較高」「大概」等模糊詞搪塞。
2. 網搜取得的資料逐條標註出處（網站名＋日期）。
3. 來源失敗自動退到下一優先級，且報告註明退回原因；富途 OpenD 未連線 → 改用免費源並註明。
4. 查無個股 → 請使用者確認代碼（含市場、簡稱、全稱），不自行猜測替代。
5. 非交易日 → 報告開頭標註「資料截至：YYYY-MM-DD（最近交易日）」。
6. 研報/新聞觀點改寫總結，不整段照抄。

## §5 輸出

- 報告結構依 [references/report-template.md](references/report-template.md)（完整版／健檢精簡版／比較版）。
- 完整版另產 dashboard：依 report-template.md 的「Dashboard 產出流程」，用 [assets/dashboard-template.html](assets/dashboard-template.html) 替換 token 後輸出（runtime 支援檔案 render 工具如 SendUserFile 就 render；否則存檔到 `<資料目錄>/reports/` 並回傳路徑）。
- 排程觸發的健檢：報告另存 `<資料目錄>/reports/YYYY-MM-DD.md`，並推送燈號總表摘要（runtime 支援推播則推播，否則摘要寫入報告檔開頭）。互動分析不落檔。

## §6 錯誤處理（三段式：一線修復 → 仍失敗兜底）

| 觸發條件 | 一線修復 | 仍失敗兜底 |
|---|---|---|
| 查無個股 | 請使用者確認代碼（市場＋簡稱＋全稱） | 使用者無法確認 → 終止該股分析，不猜測替代標的 |
| OpenD 未連線 | 退回免費源（Yahoo／網搜）＋報告註明；提示 install-futu-opend skill | 免費源也失敗 → 見下「全來源失敗」列 |
| twstock 工具失敗 | 改用網搜並標註來源與原因 | 網搜也無資料 → 該欄標「未獲取」，不以估值搪塞 |
| **全來源失敗（某數據所有來源都拿不到）** | 換下一優先級來源逐一嘗試 | 全數失敗 → 該區塊標「未獲取」，報告開頭列出缺漏清單，**不生成該區塊的結論** |
| K線不足（新上市） | 用可得天數計算，長週期指標標「未獲取（資料不足）」 | 天數 < 最短指標窗 → 技術面整段標「資料不足，暫不評分」 |
| indicators.py 執行失敗 | 如實回報錯誤，不改用心算補數值 | 重試仍失敗 → 階段 4 技術擇時標「未計算」，行動計畫註明「缺技術面輸入」 |
| dashboard 產出失敗（模板/render） | 重試一次；仍失敗改附純文字報告 | 一律先交付文字報告，dashboard 缺失在結尾註明，不因視覺產物失敗而卡住整份輸出 |

## §7 資源索引

| 資源 | 用途 |
|---|---|
| [references/data-sources.md](references/data-sources.md) | 市場路由、來源優先序、twstock 工具對照、K線 JSON 格式 |
| [references/stage-fundamental.md](references/stage-fundamental.md) | 階段 2 口徑 |
| [references/stage-consensus.md](references/stage-consensus.md) | 階段 3 口徑 |
| [references/stage-technical.md](references/stage-technical.md) | 階段 4 口徑 |
| [references/stage-risk.md](references/stage-risk.md) | 階段 5 評分公式 |
| [references/stage-action.md](references/stage-action.md) | 階段 6 行動計畫規則 |
| [references/stage-daytrading.md](references/stage-daytrading.md) | 當沖模式口徑（§8） |
| [references/report-template.md](references/report-template.md) | 報告模板＋dashboard 流程 |
| [scripts/indicators.py](scripts/indicators.py) | 技術指標計算：`python3 scripts/indicators.py --data_file <json>`（輸入格式見 data-sources.md §5） |
| [assets/dashboard-template.html](assets/dashboard-template.html) | 波段版 dashboard 模板（token 清單見檔頭註解） |
| [assets/daytrading-dashboard.html](assets/daytrading-dashboard.html) | 當沖版 dashboard 模板（token 清單見檔頭註解） |

## §8 當沖管線（限台股）

當沖模式不進六階段，跑以下聚焦管線。口徑與規則讀 [references/stage-daytrading.md](references/stage-daytrading.md)。

1. **資料收集（委派便宜模型，同 §3 階段 1）**：日K ≥60、當日＋近 5 日三大法人、成交量/值、月營收 YoY、PE/PB、當沖適性 gate 三項；有 watchlist 持倉時取成本。指標一律取 `indicators.py`（含 `amplitude_5_pct` 5 日均振幅）。
2. **🔴 當沖適性 Gate**（stage-daytrading §1）：查當日沖銷名單／暫停當沖預告／處置股。不可（或受限）當沖 → 頂部警示、只給觀察、**不出進出場劇本**。
3. **波動與流動性**（ATR%／5日均振幅／量比／成交值；量縮→非好獵場）。
4. **技術決戰帶**（indicators.py 的支撐壓力＋缺口 → 標多空分界價區）。
5. **當日籌碼**（當日三大法人方向與近 5 日連續性）。
6. **五維雷達**（沿用，當沖語境技術/資金/波動優先）。
7. **當沖劇本**（多空各一：觸發→目標→**日內停損 ≤0.5×ATR**；做劇本不做信仰）＋**部位集中度警示**（讀 profile＋watchlist）。

輸出：單股當沖卡或雙股並排＋委員會裁定，用 [assets/daytrading-dashboard.html](assets/daytrading-dashboard.html)（台股紅漲綠跌），存 `<資料目錄>/reports/daytrading_<代碼>_<日期>.html`。**能力邊界聲明必附**（日K-based，不含分時/五檔，要 tick 接富途）。
