#!/usr/bin/env python3
"""
invest-committee 技術指標計算腳本（純計算、stdlib-only）

移植自「股票個股分析 v3」analyze_stock.py，修改：
1. 資料順序統一為 date 升冪（載入時強制排序），修正原版缺口偵測
   假設新到舊、均線假設舊到新的順序矛盾。
2. 去除 numpy 依賴（np.std → statistics.pstdev，同為母體標準差）。
3. 新增多週期乖離率 calculate_bias（5/10/20/60/120/250 日）。
4. analyze_volume 移除 A 股「1手=100股」換算，只輸出量比與訊號。

輸入 JSON 格式（--data_file）：
{
  "stock_code": "2330",
  "market": "TW",
  "current_price": 1050.0,          # 可省略，預設用最後一根收盤
  "data_source": "twstock MCP",
  "fetch_time": "2026-07-09",
  "historical": [
    {"date": "2026-05-02", "open": 980.0, "high": 990.0,
     "low": 975.0, "close": 985.0, "volume": 21000000}
  ]                                  # 順序不限，腳本自行依 date 排序
}

用法：python3 indicators.py --data_file <path> [--output <path>]
"""

import json
import argparse
import statistics
import sys


# ========== 技術指標計算函式 ==========

def calculate_ma(data, period):
    """計算移動平均線"""
    if len(data) < period:
        return [None] * len(data)
    ma = []
    for i in range(len(data)):
        if i < period - 1:
            ma.append(None)
        else:
            ma.append(sum(data[i - period + 1:i + 1]) / period)
    return ma


def calculate_ema(data, period):
    """計算指數移動平均線"""
    if len(data) < period:
        return [None] * len(data)
    multiplier = 2 / (period + 1)
    ema_data = []
    sma = sum(data[:period]) / period
    ema_data.append(sma)
    for i in range(1, len(data)):
        if i < period:
            ema_data.append(sum(data[:i + 1]) / (i + 1))
        else:
            ema_value = (data[i] - ema_data[-1]) * multiplier + ema_data[-1]
            ema_data.append(ema_value)
    return ema_data


def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    """計算 MACD 指標"""
    if len(close_prices) < slow:
        return {
            'dif': [None] * len(close_prices),
            'dea': [None] * len(close_prices),
            'macd': [None] * len(close_prices)
        }
    ema_fast = calculate_ema(close_prices, fast)
    ema_slow = calculate_ema(close_prices, slow)
    dif = []
    for i in range(len(close_prices)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            dif.append(ema_fast[i] - ema_slow[i])
        else:
            dif.append(None)
    dif_valid = [d if d is not None else 0 for d in dif]
    dea = calculate_ema(dif_valid, signal)
    macd = []
    for i in range(len(close_prices)):
        if dif[i] is not None and dea[i] is not None:
            macd.append((dif[i] - dea[i]) * 2)
        else:
            macd.append(None)
    return {'dif': dif, 'dea': dea, 'macd': macd}


def calculate_rsi(close_prices, period=14):
    """計算 RSI 指標"""
    if len(close_prices) < period + 1:
        return [None] * len(close_prices)
    deltas = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]
    rsi = [None] * len(close_prices)
    for i in range(period, len(deltas)):
        gains = [d if d > 0 else 0 for d in deltas[i - period + 1:i + 1]]
        losses = [-d if d < 0 else 0 for d in deltas[i - period + 1:i + 1]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            rsi[i + 1] = 100
        else:
            rs = avg_gain / avg_loss
            rsi[i + 1] = 100 - (100 / (1 + rs))
    return rsi


def calculate_boll(close_prices, period=20, num_std=2):
    """計算布林帶（BOLL）"""
    if len(close_prices) < period:
        return {
            'upper': [None] * len(close_prices),
            'middle': [None] * len(close_prices),
            'lower': [None] * len(close_prices),
            'bandwidth': [None] * len(close_prices),
            'percent_b': [None] * len(close_prices)
        }
    upper, middle, lower, bandwidth, percent_b = [], [], [], [], []
    for i in range(len(close_prices)):
        if i < period - 1:
            upper.append(None)
            middle.append(None)
            lower.append(None)
            bandwidth.append(None)
            percent_b.append(None)
        else:
            window = close_prices[i - period + 1:i + 1]
            sma = sum(window) / period
            std = statistics.pstdev(window)
            u = sma + num_std * std
            l = sma - num_std * std
            upper.append(round(u, 4))
            middle.append(round(sma, 4))
            lower.append(round(l, 4))
            bw = (u - l) / sma * 100 if sma > 0 else 0
            bandwidth.append(round(bw, 2))
            pb = (close_prices[i] - l) / (u - l) if (u - l) > 0 else 0.5
            percent_b.append(round(pb, 4))
    return {
        'upper': upper, 'middle': middle, 'lower': lower,
        'bandwidth': bandwidth, 'percent_b': percent_b
    }


def calculate_kdj(high_prices, low_prices, close_prices, n=9, m1=3, m2=3):
    """計算 KDJ 指標"""
    length = len(close_prices)
    if length < n:
        return {
            'k': [None] * length,
            'd': [None] * length,
            'j': [None] * length
        }
    rsv, k_vals, d_vals, j_vals = [], [], [], []
    for i in range(length):
        if i < n - 1:
            rsv.append(None)
        else:
            window_high = max(high_prices[i - n + 1:i + 1])
            window_low = min(low_prices[i - n + 1:i + 1])
            if window_high == window_low:
                rsv.append(50.0)
            else:
                rsv.append((close_prices[i] - window_low) / (window_high - window_low) * 100)
    k_val, d_val = 50.0, 50.0
    for i in range(length):
        if rsv[i] is None:
            k_vals.append(None)
            d_vals.append(None)
            j_vals.append(None)
        else:
            k_val = (m1 - 1) / m1 * k_val + 1 / m1 * rsv[i]
            d_val = (m2 - 1) / m2 * d_val + 1 / m2 * k_val
            j_val = 3 * k_val - 2 * d_val
            k_vals.append(round(k_val, 2))
            d_vals.append(round(d_val, 2))
            j_vals.append(round(j_val, 2))
    return {'k': k_vals, 'd': d_vals, 'j': j_vals}


def calculate_atr(high_prices, low_prices, close_prices, period=14):
    """計算 ATR（平均真實波幅）"""
    if len(close_prices) < period + 1:
        return {'atr': [None] * len(close_prices), 'atr_pct': [None] * len(close_prices)}
    true_ranges = [high_prices[0] - low_prices[0]]
    for i in range(1, len(close_prices)):
        tr = max(
            high_prices[i] - low_prices[i],
            abs(high_prices[i] - close_prices[i - 1]),
            abs(low_prices[i] - close_prices[i - 1])
        )
        true_ranges.append(tr)
    atr_vals = [None] * len(close_prices)
    atr_pct = [None] * len(close_prices)
    for i in range(period, len(close_prices)):
        atr_val = sum(true_ranges[i - period + 1:i + 1]) / period
        atr_vals[i] = round(atr_val, 4)
        if close_prices[i] > 0:
            atr_pct[i] = round(atr_val / close_prices[i] * 100, 2)
    return {'atr': atr_vals, 'atr_pct': atr_pct}


def calculate_bias(close_prices, periods=(5, 10, 20, 60, 120, 250)):
    """多週期乖離率：(close - MA_n) / MA_n * 100；資料不足該期輸出 None"""
    out = {}
    if not close_prices:
        return {f"bias_{n}": None for n in periods}
    close = close_prices[-1]
    for n in periods:
        if len(close_prices) < n:
            out[f"bias_{n}"] = None
            continue
        ma_n = sum(close_prices[-n:]) / n
        out[f"bias_{n}"] = round((close - ma_n) / ma_n * 100, 2) if ma_n else None
    return out


def calculate_fibonacci_support_resistance(high_price, low_price, current_price):
    """斐波那契回撤法計算支撐位和壓力位"""
    diff = high_price - low_price
    levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    supports, resistances = [], []
    for ratio in levels:
        price = round(high_price - diff * ratio, 2)
        if price < current_price:
            supports.append({'price': price, 'method': 'fibonacci', 'ratio': ratio})
        elif price > current_price:
            resistances.append({'price': price, 'method': 'fibonacci', 'ratio': ratio})
    supports.sort(key=lambda x: x['price'], reverse=True)
    resistances.sort(key=lambda x: x['price'])
    return supports[:3], resistances[:3]


def calculate_support_resistance(historical_data, current_price):
    """多演算法計算支撐位和壓力位（historical_data 需 date 升冪）"""
    if not historical_data:
        return {'support_levels': [], 'resistance_levels': []}

    lows = [item['low'] for item in historical_data]
    highs = [item['high'] for item in historical_data]
    recent_high = max(highs[-20:]) if len(highs) >= 20 else max(highs)
    recent_low = min(lows[-20:]) if len(lows) >= 20 else min(lows)

    # 方法1：前高前低法（局部極值）
    pivot_supports = []
    for i in range(2, len(lows) - 2):
        if lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and lows[i] < lows[i + 1] and lows[i] < lows[i + 2]:
            if lows[i] < current_price:
                pivot_supports.append({'price': round(lows[i], 2), 'date': historical_data[i]['date'], 'method': '前高前低'})

    pivot_resistances = []
    for i in range(2, len(highs) - 2):
        if highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and highs[i] > highs[i + 1] and highs[i] > highs[i + 2]:
            if highs[i] > current_price:
                pivot_resistances.append({'price': round(highs[i], 2), 'date': historical_data[i]['date'], 'method': '前高前低'})

    pivot_supports.sort(key=lambda x: abs(x['price'] - current_price))
    pivot_resistances.sort(key=lambda x: abs(x['price'] - current_price))

    # 方法2：斐波那契回撤
    fib_supports, fib_resistances = calculate_fibonacci_support_resistance(recent_high, recent_low, current_price)

    all_supports = pivot_supports[:2] + fib_supports[:2]
    all_resistances = pivot_resistances[:2] + fib_resistances[:2]

    # 標註強度（依距現價遠近）
    for s in all_supports:
        dist_pct = (current_price - s['price']) / current_price * 100
        if dist_pct < 2:
            s['strength'] = '強'
        elif dist_pct < 5:
            s['strength'] = '中'
        else:
            s['strength'] = '弱'
    for r in all_resistances:
        dist_pct = (r['price'] - current_price) / current_price * 100
        if dist_pct < 2:
            r['strength'] = '強'
        elif dist_pct < 5:
            r['strength'] = '中'
        else:
            r['strength'] = '弱'

    return {
        'support_levels': all_supports[:4],
        'resistance_levels': all_resistances[:4],
        'recent_high': round(recent_high, 2),
        'recent_low': round(recent_low, 2)
    }


def classify_gap(gap_info, historical_data, gap_index, current_price):
    """缺口類型分類：普通/突破/持續/竭盡（historical_data 需 date 升冪）"""
    gap_pct = gap_info.get('gap_pct', 0)
    is_up = gap_info.get('role') == '支撐位'

    # 升冪順序下：缺口前 = 較早 = 索引小；缺口後 = 較晚 = 索引大
    before_gap = historical_data[max(0, gap_index - 10):gap_index]
    after_gap = historical_data[gap_index:min(gap_index + 6, len(historical_data))]

    if not before_gap or not after_gap:
        return '普通缺口'

    before_high = max(d['high'] for d in before_gap)
    before_low = min(d['low'] for d in before_gap)
    before_range = (before_high - before_low) / before_low * 100 if before_low > 0 else 0

    # 突破缺口：缺口前橫盤整理（波幅<10%），缺口幅度明顯
    if before_range < 10 and gap_pct > 2:
        return '突破缺口'

    # 持續缺口：處於明顯趨勢中，缺口方向與趨勢一致
    if len(before_gap) >= 5:
        before_closes = [d['close'] for d in before_gap]
        trend_up = before_closes[-1] > before_closes[0]
        trend_down = before_closes[-1] < before_closes[0]
        if (is_up and trend_up) or (not is_up and trend_down):
            if gap_pct > 1:
                return '持續缺口'

    # 竭盡缺口：缺口後價格很快反向
    after_closes = [d['close'] for d in after_gap]
    if len(after_closes) >= 3:
        if is_up and after_closes[-1] < after_closes[0]:
            return '竭盡缺口'
        if not is_up and after_closes[-1] > after_closes[0]:
            return '竭盡缺口'

    return '普通缺口'


def detect_gaps(historical_data, current_price):
    """識別 K 線缺口並分類（historical_data 需 date 升冪：i-1 是前一日）"""
    if len(historical_data) < 2:
        return {'up_gaps': [], 'down_gaps': [], 'filled_up_gaps': [], 'filled_down_gaps': [], 'has_gaps': False}

    up_gaps, down_gaps, filled_up_gaps, filled_down_gaps = [], [], [], []

    for i in range(1, len(historical_data)):
        today = historical_data[i]
        yesterday = historical_data[i - 1]

        if today['low'] > yesterday['high']:
            gap_size = today['low'] - yesterday['high']
            gap_pct = (gap_size / yesterday['high']) * 100
            gap_info = {
                'date': today['date'],
                'yesterday_date': yesterday['date'],
                'yesterday_high': round(yesterday['high'], 2),
                'today_low': round(today['low'], 2),
                'gap_size': round(gap_size, 2),
                'gap_pct': round(gap_pct, 2),
                'price_range': [round(yesterday['high'], 2), round(today['low'], 2)],
                'role': '支撐位'
            }
            gap_info['gap_type'] = classify_gap(gap_info, historical_data, i, current_price)

            if today['low'] < current_price:
                up_gaps.append(gap_info)
            else:
                filled_up_gaps.append(gap_info)

        elif today['high'] < yesterday['low']:
            gap_size = yesterday['low'] - today['high']
            gap_pct = (gap_size / yesterday['low']) * 100
            gap_info = {
                'date': today['date'],
                'yesterday_date': yesterday['date'],
                'yesterday_low': round(yesterday['low'], 2),
                'today_high': round(today['high'], 2),
                'gap_size': round(gap_size, 2),
                'gap_pct': round(gap_pct, 2),
                'price_range': [round(today['high'], 2), round(yesterday['low'], 2)],
                'role': '壓力位'
            }
            gap_info['gap_type'] = classify_gap(gap_info, historical_data, i, current_price)

            if today['high'] > current_price:
                down_gaps.append(gap_info)
            else:
                filled_down_gaps.append(gap_info)

    has_gaps = len(up_gaps) > 0 or len(down_gaps) > 0
    return {
        'up_gaps': up_gaps, 'down_gaps': down_gaps,
        'filled_up_gaps': filled_up_gaps, 'filled_down_gaps': filled_down_gaps,
        'has_gaps': has_gaps,
        'has_filled_gaps': len(filled_up_gaps) > 0 or len(filled_down_gaps) > 0,
        'total_gaps_count': len(up_gaps) + len(down_gaps) + len(filled_up_gaps) + len(filled_down_gaps)
    }


def analyze_weekly_trend(historical_data):
    """基於日線資料合成週線並分析趨勢（historical_data 需 date 升冪）"""
    if len(historical_data) < 20:
        return {'trend': '資料不足', 'description': '日線資料不足20天，無法合成週線'}

    weekly_data = []
    for i in range(0, len(historical_data) - 4, 5):
        week = historical_data[i:i + 5]
        weekly_data.append({
            'date': week[-1]['date'],
            'open': week[0]['open'],
            'close': week[-1]['close'],
            'high': max(d['high'] for d in week),
            'low': min(d['low'] for d in week),
            'volume': sum(d['volume'] for d in week)
        })

    if len(weekly_data) < 5:
        return {'trend': '資料不足', 'description': '週線資料不足，無法判斷週線趨勢'}

    weekly_closes = [d['close'] for d in weekly_data]
    w_ma5 = calculate_ma(weekly_closes, 5)

    if not w_ma5 or w_ma5[-1] is None:
        return {'trend': '震盪', 'description': '週線趨勢不明確'}

    current = weekly_closes[-1]
    ma5_val = w_ma5[-1]

    if current > ma5_val and len(weekly_closes) >= 3 and weekly_closes[-1] > weekly_closes[-3]:
        return {'trend': '週線向上', 'description': f'週線收盤價({current:.2f})在週線MA5({ma5_val:.2f})上方，週線趨勢向上', 'strength': '強'}
    elif current < ma5_val and len(weekly_closes) >= 3 and weekly_closes[-1] < weekly_closes[-3]:
        return {'trend': '週線向下', 'description': f'週線收盤價({current:.2f})在週線MA5({ma5_val:.2f})下方，週線趨勢向下', 'strength': '強'}
    else:
        return {'trend': '週線震盪', 'description': '週線趨勢不明，處於整理狀態', 'strength': '中'}


def analyze_ma_trend(ma5, ma10, ma20, ma60):
    """分析均線排列趨勢"""
    if not all([ma5, ma10, ma20, ma60]):
        return {'trend': '資料不足', 'description': '資料不足，無法判斷趨勢'}
    vals = [ma5[-1], ma10[-1], ma20[-1], ma60[-1]]
    if not all(vals):
        return {'trend': '資料不足', 'description': '資料不足，無法判斷趨勢'}
    if vals[0] > vals[1] > vals[2] > vals[3]:
        return {'trend': '多頭排列', 'description': 'MA5 > MA10 > MA20 > MA60，趨勢向上', 'strength': '強'}
    elif vals[0] < vals[1] < vals[2] < vals[3]:
        return {'trend': '空頭排列', 'description': 'MA5 < MA10 < MA20 < MA60，趨勢向下', 'strength': '強'}
    elif vals[0] > vals[1] > vals[2]:
        return {'trend': '短期向上', 'description': '短期均線向上，中長期趨勢待確認', 'strength': '中'}
    elif vals[0] < vals[1] < vals[2]:
        return {'trend': '短期向下', 'description': '短期均線向下，中長期趨勢待確認', 'strength': '中'}
    else:
        return {'trend': '震盪', 'description': '均線排列不明確，市場處於震盪狀態', 'strength': '弱'}


def analyze_macd_signal(macd_data):
    """分析 MACD 訊號"""
    dif, dea, macd = macd_data['dif'], macd_data['dea'], macd_data['macd']
    if not all([dif, dea, macd]):
        return {'signal': '資料不足', 'description': '資料不足'}
    if not all([dif[-1], dea[-1], macd[-1]]) and (dif[-1] is None or dea[-1] is None or macd[-1] is None):
        return {'signal': '資料不足', 'description': '資料不足'}
    signals = []
    if dif[-2] is not None and dea[-2] is not None:
        if dif[-2] <= dea[-2] and dif[-1] > dea[-1]:
            signals.append('金叉')
        if dif[-2] >= dea[-2] and dif[-1] < dea[-1]:
            signals.append('死叉')
    if macd[-1] > 0:
        if len(macd) > 1 and macd[-2] is not None and macd[-2] > 0 and macd[-1] > macd[-2]:
            signals.append('紅柱放大')
        elif len(macd) > 1 and macd[-2] is not None and macd[-2] > 0 and macd[-1] < macd[-2]:
            signals.append('紅柱縮小')
    elif macd[-1] < 0:
        if len(macd) > 1 and macd[-2] is not None and macd[-2] < 0 and macd[-1] < macd[-2]:
            signals.append('綠柱放大')
        elif len(macd) > 1 and macd[-2] is not None and macd[-2] < 0 and macd[-1] > macd[-2]:
            signals.append('綠柱縮小')
    if not signals:
        signals.append('無明顯訊號')
    return {'signal': signals, 'dif': round(dif[-1], 4), 'dea': round(dea[-1], 4), 'macd': round(macd[-1], 4)}


def analyze_rsi_signal(rsi_data):
    """分析 RSI 訊號"""
    if not rsi_data or rsi_data[-1] is None:
        return {'signal': '資料不足', 'value': None, 'description': '資料不足'}
    rsi_latest = rsi_data[-1]
    if rsi_latest >= 80:
        return {'value': round(rsi_latest, 2), 'signal': '嚴重超買', 'description': f'RSI={rsi_latest:.2f}，嚴重超買區域'}
    elif rsi_latest >= 70:
        return {'value': round(rsi_latest, 2), 'signal': '超買', 'description': f'RSI={rsi_latest:.2f}，超買區域'}
    elif rsi_latest <= 20:
        return {'value': round(rsi_latest, 2), 'signal': '嚴重超賣', 'description': f'RSI={rsi_latest:.2f}，嚴重超賣區域'}
    elif rsi_latest <= 30:
        return {'value': round(rsi_latest, 2), 'signal': '超賣', 'description': f'RSI={rsi_latest:.2f}，超賣區域'}
    else:
        return {'value': round(rsi_latest, 2), 'signal': '正常', 'description': f'RSI={rsi_latest:.2f}，正常區間'}


def analyze_boll_signal(boll_data, current_price):
    """分析布林帶訊號"""
    if not boll_data['upper'] or boll_data['upper'][-1] is None:
        return {'signal': '資料不足', 'description': '資料不足'}
    upper = boll_data['upper'][-1]
    middle = boll_data['middle'][-1]
    lower = boll_data['lower'][-1]
    bw = boll_data['bandwidth'][-1]
    pb = boll_data['percent_b'][-1]

    signals = []
    if current_price >= upper:
        signals.append('觸及上軌，短期偏強但注意回調')
    elif current_price <= lower:
        signals.append('觸及下軌，短期偏弱但注意反彈')
    elif current_price > middle:
        signals.append('運行在中軌上方，偏強')
    else:
        signals.append('運行在中軌下方，偏弱')

    if bw is not None:
        if bw > 20:
            signals.append('帶寬較大，波動劇烈')
        elif bw < 5:
            signals.append('帶寬收窄，可能變盤')

    return {
        'signal': signals,
        'upper': round(upper, 2),
        'middle': round(middle, 2),
        'lower': round(lower, 2),
        'bandwidth': bw,
        'percent_b': round(pb, 4) if pb is not None else None
    }


def analyze_kdj_signal(kdj_data):
    """分析 KDJ 訊號"""
    k, d, j = kdj_data['k'], kdj_data['d'], kdj_data['j']
    if not all([k, d, j]) or k[-1] is None:
        return {'signal': '資料不足', 'description': '資料不足'}
    signals = []
    if k[-2] is not None and d[-2] is not None:
        if k[-2] <= d[-2] and k[-1] > d[-1]:
            signals.append('金叉')
        if k[-2] >= d[-2] and k[-1] < d[-1]:
            signals.append('死叉')
    if j[-1] > 100:
        signals.append('J值超買（>100）')
    elif j[-1] < 0:
        signals.append('J值超賣（<0）')
    elif k[-1] > 80 and d[-1] > 80:
        signals.append('KD超買區域')
    elif k[-1] < 20 and d[-1] < 20:
        signals.append('KD超賣區域')
    if not signals:
        signals.append('無明顯訊號')
    return {'signal': signals, 'k': k[-1], 'd': d[-1], 'j': j[-1]}


def calculate_amplitude(historical_data, period=5):
    """最近 period 日的日內振幅平均：(high-low)/前一日收盤 ×100（當沖波動用）。"""
    if len(historical_data) < period + 1:
        return {"amplitude_pct": None}
    amps = []
    for i in range(len(historical_data) - period, len(historical_data)):
        prev_close = historical_data[i - 1]["close"]
        if prev_close:
            hi = historical_data[i]["high"]
            lo = historical_data[i]["low"]
            amps.append((hi - lo) / prev_close * 100)
    if not amps:
        return {"amplitude_pct": None}
    return {"amplitude_pct": round(sum(amps) / len(amps), 2)}


def analyze_volume(historical_data):
    """分析成交量（輸出量比與訊號；不做市場別的手/張換算）"""
    if len(historical_data) < 5:
        return {'description': '資料不足'}
    volumes = [item['volume'] for item in historical_data]
    avg_volume = sum(volumes[-5:]) / min(5, len(volumes))
    latest_volume = volumes[-1]
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
    if volume_ratio >= 2:
        signal, desc = '放量', '成交量顯著放大'
    elif volume_ratio >= 1.5:
        signal, desc = '溫和放量', '成交量適度放大'
    elif volume_ratio <= 0.5:
        signal, desc = '縮量', '成交量顯著萎縮'
    else:
        signal, desc = '正常', '成交量正常'
    return {'description': desc, 'volume_ratio': round(volume_ratio, 2),
            'signal': signal, 'latest_volume': latest_volume,
            'amplitude_5_pct': calculate_amplitude(historical_data, 5)['amplitude_pct']}


def multi_period_resonance(daily_trend, weekly_trend):
    """多週期共振判斷"""
    daily_bull = daily_trend.get('trend', '') in ['多頭排列', '短期向上']
    daily_bear = daily_trend.get('trend', '') in ['空頭排列', '短期向下']
    weekly_bull = weekly_trend.get('trend', '') == '週線向上'
    weekly_bear = weekly_trend.get('trend', '') == '週線向下'

    if daily_bull and weekly_bull:
        return {'resonance': '多週期共振看多', 'confidence': '高', 'description': '日線和週線趨勢同時向上，多頭訊號可信度較高'}
    elif daily_bear and weekly_bear:
        return {'resonance': '多週期共振看空', 'confidence': '高', 'description': '日線和週線趨勢同時向下，空頭訊號可信度較高'}
    elif daily_bull and weekly_bear:
        return {'resonance': '週期矛盾（日多週空）', 'confidence': '中', 'description': '日線向上但週線向下，短期反彈可能在週線壓力位受阻'}
    elif daily_bear and weekly_bull:
        return {'resonance': '週期矛盾（日空週多）', 'confidence': '中', 'description': '日線向下但週線向上，回調可能在週線支撐位獲得支撐'}
    else:
        return {'resonance': '無明顯共振', 'confidence': '低', 'description': '多週期訊號不一致，趨勢不明確'}


def perform_analysis(data_file):
    """執行完整技術分析"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"錯誤：讀取資料檔失敗 - {str(e)}", file=sys.stderr)
        return None

    historical_data = data.get('historical', [])
    if not historical_data:
        print("錯誤：沒有歷史資料", file=sys.stderr)
        return None

    # 強制 date 升冪，消除來源順序差異
    historical_data.sort(key=lambda d: d['date'])

    close_prices = [item['close'] for item in historical_data]
    high_prices = [item['high'] for item in historical_data]
    low_prices = [item['low'] for item in historical_data]
    current_price = data.get('current_price') or close_prices[-1]

    ma5 = calculate_ma(close_prices, 5)
    ma10 = calculate_ma(close_prices, 10)
    ma20 = calculate_ma(close_prices, 20)
    ma60 = calculate_ma(close_prices, 60)
    macd_data = calculate_macd(close_prices)
    rsi_data = calculate_rsi(close_prices)
    boll_data = calculate_boll(close_prices)
    kdj_data = calculate_kdj(high_prices, low_prices, close_prices)
    atr_data = calculate_atr(high_prices, low_prices, close_prices)
    bias = calculate_bias(close_prices)

    support_resistance = calculate_support_resistance(historical_data, current_price)
    gap_analysis = detect_gaps(historical_data, current_price)
    ma_trend = analyze_ma_trend(ma5, ma10, ma20, ma60)
    weekly_trend = analyze_weekly_trend(historical_data)
    resonance = multi_period_resonance(ma_trend, weekly_trend)
    macd_signal = analyze_macd_signal(macd_data)
    rsi_signal = analyze_rsi_signal(rsi_data)
    boll_signal = analyze_boll_signal(boll_data, current_price)
    kdj_signal = analyze_kdj_signal(kdj_data)
    volume_analysis = analyze_volume(historical_data)

    return {
        'stock_code': data.get('stock_code'),
        'market': data.get('market', ''),
        'current_price': current_price,
        'analysis_time': data.get('fetch_time', ''),
        'data_source': data.get('data_source', ''),
        'data_days': len(historical_data),
        'technical_indicators': {
            'ma': {
                'ma5': round(ma5[-1], 2) if ma5 and ma5[-1] is not None else None,
                'ma10': round(ma10[-1], 2) if ma10 and ma10[-1] is not None else None,
                'ma20': round(ma20[-1], 2) if ma20 and ma20[-1] is not None else None,
                'ma60': round(ma60[-1], 2) if ma60 and ma60[-1] is not None else None,
            },
            'bias': bias,
            'macd': macd_signal,
            'rsi': rsi_signal,
            'boll': boll_signal,
            'kdj': kdj_signal,
            'atr': {
                'atr': atr_data['atr'][-1],
                'atr_pct': atr_data['atr_pct'][-1]
            }
        },
        'support_resistance': support_resistance,
        'gap_analysis': gap_analysis,
        'trend_analysis': {
            'daily': ma_trend,
            'weekly': weekly_trend,
            'resonance': resonance
        },
        'volume_analysis': volume_analysis
    }


def main():
    parser = argparse.ArgumentParser(description='invest-committee 技術指標計算')
    parser.add_argument('--data_file', required=True, help='K線資料 JSON 檔路徑')
    parser.add_argument('--output', help='分析結果輸出檔路徑（可選）')
    args = parser.parse_args()

    analysis_result = perform_analysis(args.data_file)

    if analysis_result:
        result_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        print(result_json)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
