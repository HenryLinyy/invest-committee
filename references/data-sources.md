# 資料來源路由（invest-committee 階段 1 讀取）

## §1 市場路由

| 代碼形態 | 市場 | 範例 |
|---|---|---|
| 4-6 位數字（或 `.TW`/`.TWO` 結尾）、台股公司中文名 | 台股 | 2330、6488.TWO、台積電 |
| 1-5 位英文字母（可含 `.`） | 美股 | AAPL、NVDA、BRK.B |
| 4-5 位數字＋`.HK`（或港股慣稱） | 港股 | 0700.HK、騰訊 |
| 6 位數字且 60/68/00/30 開頭（或 `.SH`/`.SZ` 結尾） | A股 | 600519、300750.SZ |
| 判斷不了（如 4 位數字可能是台股或港股） | — | 追問使用者一次，不猜 |

注意：台股 4 位數字與港股代碼可能撞號。無 `.HK` 後綴且無港股語境時，4 位數字預設台股。

## §2 各市場來源優先序

| 市場 | 優先 1 | 優先 2 | 優先 3（最後手段） |
|---|---|---|---|
| 台股 | twstock MCP | 富途（OpenD 開啟時） | 網路搜尋（標註出處） |
| 美股 | 富途（OpenD 開啟時） | Yahoo Finance 公開 API | 網路搜尋 |
| 港股 | 富途（OpenD 開啟時） | 免費網源（Yahoo/新浪） | 網路搜尋 |
| A股 | 富途（OpenD 開啟時） | 免費網源（新浪/東方財富） | 網路搜尋 |

退回規則：來源失敗（連線錯誤、查無資料）→ 退下一優先序，且報告「資料來源」節必須註明實際使用的來源與退回原因。

## §3 台股 twstock 工具對照表（階段 → 工具）

工具皆為 deferred——分析開始時用 ToolSearch 一次批量載入本次需要的工具（`select:` 逗號分隔），不要逐個載入。

| 用途 | 工具名 |
|---|---|
| K線/歷史行情 | `get_stock_history` |
| 即時報價 | `get_realtime_quote` |
| 當日/月/年成交 | `get_stock_daily_trading`、`get_stock_monthly_trading`、`get_stock_yearly_trading` |
| 月均價（指標核對用） | `get_stock_monthly_average` |
| 估值（PE/PB/殖利率） | `get_stock_valuation_ratios`、`get_valuation_ratios_by_date` |
| 月營收 | `get_company_monthly_revenue` |
| 財報 | `get_company_balance_sheet`、`get_company_income_statement` |
| 獲利能力 | `get_company_profitability_analysis`、`get_company_eps_statistics` |
| 配息 | `get_company_dividend` |
| 三大法人（個股） | `get_twse_institutional_investors_by_stock` |
| 外資持股 | `get_top_foreign_holdings` |
| 融資券 | `get_margin_trading_info`、`get_margin_balance` |
| 大股東/董監 | `get_company_major_shareholders`、`get_company_board_shareholdings` |
| 董監質押 | `get_company_board_pledged_shares` |
| 處置股（上市/上櫃） | `get_market_disposal_stocks`、`get_otc_disposal_stocks` |
| 注意股 | `get_today_notice_stocks`、`get_abnormal_accumulated_notice_stocks` |
| 主管機關處分 | `get_company_sec_regulatory_penalties` |
| 資訊揭露違規 | `get_company_information_disclosure_violations` |
| 暫停交易 | `get_suspended_trading_stocks` |
| 重大訊息 | `get_company_major_news` |
| 公司基本資料 | `get_company_profile` |

## §4 富途偵測與退回

1. 分析美/港/A股（或台股需要富途補充資料）時，先依 **futuapi skill** 的方式檢查 OpenD 連線。
2. OpenD 可用 → 行情、K線、財報、分析師評級、目標價、機構持股走富途。
3. OpenD 不可用 → 不中斷分析：退回下一優先序，報告註明「富途未連線，改用 ○○」。可提示使用者 install-futu-opend skill 可安裝。

**Yahoo Finance OHLCV 端點**（美股免費退回用，無需金鑰）：

```
https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d
```

回傳 `chart.result[0]`：`timestamp[]` 與 `indicators.quote[0]` 的 `open/high/low/close/volume[]`，逐筆組成日資料。

## §5 K線 JSON 落地格式（餵給 scripts/indicators.py）

取得 K 線後組成以下 JSON 存到 session scratchpad，再執行
`python3 <skill路徑>/scripts/indicators.py --data_file <json路徑>`：

```json
{
  "stock_code": "2330",
  "market": "TW",
  "current_price": 1050.0,
  "data_source": "twstock MCP",
  "fetch_time": "2026-07-09",
  "historical": [
    {"date": "2026-05-02", "open": 980.0, "high": 990.0,
     "low": 975.0, "close": 985.0, "volume": 21000000}
  ]
}
```

- `historical` 順序不限（腳本自行依 date 升冪排序）；建議 ≥120 個交易日（長線分析 250 日）。
- `current_price` 可省略，預設用最後一根收盤價。
- 價格單位用該市場原幣別，volume 用股數（不換算手/張）。
