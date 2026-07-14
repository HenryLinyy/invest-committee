#!/usr/bin/env python3
"""indicators.py 單元測試——全部用手算得出的固定 fixture"""
import unittest
import indicators as ind


def make_days(closes, high_off=1.0, low_off=1.0, start="2026-01-01"):
    """由收盤價序列建構 OHLCV 日資料（date 升冪）"""
    from datetime import date, timedelta
    d0 = date.fromisoformat(start)
    return [
        {"date": (d0 + timedelta(days=i)).isoformat(),
         "open": c, "high": c + high_off, "low": c - low_off,
         "close": c, "volume": 1000}
        for i, c in enumerate(closes)
    ]


class TestMA(unittest.TestCase):
    def test_ma5_of_linear_series(self):
        ma = ind.calculate_ma(list(range(1, 11)), 5)   # 1..10
        self.assertAlmostEqual(ma[-1], 8.0)             # (6+7+8+9+10)/5
        self.assertIsNone(ma[3])                        # 前 period-1 筆為 None


class TestRSI(unittest.TestCase):
    def test_all_up_series_rsi_100(self):
        rsi = ind.calculate_rsi(list(range(1, 31)), 14)
        self.assertEqual(rsi[-1], 100)


class TestATR(unittest.TestCase):
    def test_constant_series_atr_zero(self):
        n = 20
        flat = [10.0] * n
        r = ind.calculate_atr(flat, flat, flat, 14)     # high=low=close → TR=0
        self.assertEqual(r["atr"][-1], 0)


class TestBOLL(unittest.TestCase):
    def test_constant_window(self):
        r = ind.calculate_boll([10.0] * 25, 20, 2)
        self.assertAlmostEqual(r["upper"][-1], 10.0)
        self.assertAlmostEqual(r["middle"][-1], 10.0)
        self.assertAlmostEqual(r["lower"][-1], 10.0)
        self.assertEqual(r["percent_b"][-1], 0.5)       # 帶寬 0 → 中性


class TestMACD(unittest.TestCase):
    def test_constant_series_all_zero(self):
        r = ind.calculate_macd([10.0] * 60)
        self.assertAlmostEqual(r["dif"][-1], 0.0)
        self.assertAlmostEqual(r["macd"][-1], 0.0)


class TestKDJ(unittest.TestCase):
    def test_constant_series_neutral_50(self):
        flat = [10.0] * 20
        r = ind.calculate_kdj(flat, flat, flat)         # rsv=50 → k=d=j=50
        self.assertAlmostEqual(r["k"][-1], 50.0)
        self.assertAlmostEqual(r["j"][-1], 50.0)


class TestBias(unittest.TestCase):
    def test_bias20_of_linear_series(self):
        closes = [float(i) for i in range(1, 31)]       # 1..30
        b = ind.calculate_bias(closes, periods=[20])
        # MA20 = mean(11..30) = 20.5 → (30-20.5)/20.5*100
        self.assertAlmostEqual(b["bias_20"], (30 - 20.5) / 20.5 * 100, places=2)

    def test_insufficient_data_is_none(self):
        b = ind.calculate_bias([1.0, 2.0], periods=[250])
        self.assertIsNone(b["bias_250"])


class TestGaps(unittest.TestCase):
    def test_up_gap_detected_with_ascending_data(self):
        # day2 low(11.0) > day1 high(10.5) → 向上跳空缺口
        days = make_days([10.0, 12.0, 12.5, 12.4, 12.6], high_off=0.5, low_off=1.0)
        r = ind.detect_gaps(days, current_price=12.6)
        self.assertTrue(r["has_gaps"])
        self.assertEqual(len(r["up_gaps"]), 1)
        self.assertEqual(r["up_gaps"][0]["role"], "支撐位")

    def test_no_gap_in_continuous_data(self):
        days = make_days([10.0, 10.1, 10.2, 10.1, 10.3])
        r = ind.detect_gaps(days, current_price=10.3)
        self.assertFalse(r["has_gaps"])


class TestPipeline(unittest.TestCase):
    def test_perform_analysis_sorts_input(self):
        """輸入新到舊也要得到與舊到新相同的 MA 結果（驗證排序修正）"""
        import json, tempfile, os
        days = make_days([float(i) for i in range(1, 71)])
        payload = {"stock_code": "TEST", "market": "TW",
                   "current_price": 70.0, "historical": list(reversed(days))}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            json.dump(payload, f)
            path = f.name
        try:
            r = ind.perform_analysis(path)
            self.assertAlmostEqual(r["technical_indicators"]["ma"]["ma5"], 68.0)  # (66+..+70)/5
            self.assertIn("bias", r["technical_indicators"])
        finally:
            os.unlink(path)


class TestAmplitude(unittest.TestCase):
    def test_constant_series_zero_amplitude(self):
        days = make_days([100.0] * 7, high_off=0.0, low_off=0.0)
        r = ind.calculate_amplitude(days, period=5)
        self.assertAlmostEqual(r["amplitude_pct"], 0.0, places=4)

    def test_known_amplitude(self):
        # close 全 100，high=+2 low=-2 → 振幅=(102-98)/100=4%
        days = make_days([100.0] * 7, high_off=2.0, low_off=2.0)
        r = ind.calculate_amplitude(days, period=5)
        self.assertAlmostEqual(r["amplitude_pct"], 4.0, places=4)

    def test_insufficient_data_none(self):
        days = make_days([100.0] * 3, high_off=1.0, low_off=1.0)
        r = ind.calculate_amplitude(days, period=5)
        self.assertIsNone(r["amplitude_pct"])


if __name__ == "__main__":
    unittest.main()
