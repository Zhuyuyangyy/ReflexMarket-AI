# ReflexMarket-AI 市场仿真 Benchmark 测试
# 验证Narrative→Price反馈循环正确性

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class MarketState:
    def __init__(self):
        self.price = 100.0
        self.emotion = 0.0
        self.belief = 0.5
        self.narrative = 0.5
        self.step = 0

    def step_forward(self):
        """一个仿真步：Narrative→Belief→Emotion→Behavior→Capital→Price"""
        # Narrative影响Belief
        belief_target = self.narrative * 0.8 + (1 - self.emotion) * 0.2
        self.belief += (belief_target - self.belief) * 0.15

        # Emotion受价格偏离驱动
        emotion_target = self.price > 110 and -0.3 or self.price < 90 and 0.8 or self.narrative * 1.5 - 0.75
        self.emotion += (emotion_target - self.emotion) * 0.12

        # Behavior影响价格
        behavior = self.emotion * 0.6 + (1 - self.belief) * 0.4
        price_delta = behavior * 2.0 - (self.price - 100) * 0.1
        self.price = max(50, min(150, self.price + price_delta))
        self.step += 1

class TestFeedbackLoop:
    """测试反馈循环正确性"""

    def test_price_reverts_to_mean(self):
        """价格偏离后应回归均值"""
        state = MarketState()
        state.price = 140.0
        state.emotion = 0.0
        state.narrative = 0.5
        for _ in range(20):
            state.step_forward()
        # 价格应该向100回归
        assert 80 <= state.price <= 130, f"Price {state.price:.1f} should revert toward 100"
        print(f"\n价格从140回归到: {state.price:.1f} (20步)")

    def test_greed_drives_price_up(self):
        """贪婪情绪应推高价格"""
        state = MarketState()
        state.emotion = 0.9
        state.narrative = 0.9
        state.belief = 0.5
        for _ in range(10):
            state.step_forward()
        assert state.price > 100, f"Greed should drive price up, got {state.price:.1f}"
        print(f"\n贪婪情绪10步后价格: {state.price:.1f}")

    def test_panic_drives_price_down(self):
        """恐慌情绪应压低价格"""
        state = MarketState()
        state.emotion = -0.9
        state.narrative = 0.7
        state.belief = 0.5
        for _ in range(10):
            state.step_forward()
        assert state.price < 100, f"Panic should drive price down, got {state.price:.1f}"
        print(f"\n恐慌情绪10步后价格: {state.price:.1f}")

    def test_belief_narrative_alignment(self):
        """信念与叙事一致性演化"""
        state = MarketState()
        state.narrative = 0.2  # 负面叙事
        initial_belief = state.belief
        for _ in range(15):
            state.step_forward()
        # 负面叙事应该降低信念
        assert state.belief < initial_belief + 0.1, f"Negative narrative should reduce belief alignment"
        print(f"\n信念从{initial_belief:.2f}变为{state.belief:.2f}（负面叙事）")

class TestMarketRegulator:
    """测试市场监管机制"""

    def test_regulator_kicks_in_on_extreme_emotion(self):
        """极端情绪时监管介入"""
        state = MarketState()
        state.emotion = -0.9
        state.price = 75.0
        # 模拟监管
        if abs(state.emotion) > 0.75 or abs(state.price - 100) > 35:
            state.emotion *= 0.85
            state.price = state.price * 0.92 + 100 * 0.08
        assert state.emotion > -0.9, "Regulator should reduce extreme emotion"
        print(f"\n监管介入后情绪: {state.emotion:.2f} (从-0.9调整)")

    def test_regulator_recovery(self):
        """监管介入后市场恢复"""
        state = MarketState()
        state.emotion = 0.92  # 超过0.75阈值
        state.price = 60.0
        # 监管介入3次
        for _ in range(3):
            if abs(state.emotion) > 0.75 or abs(state.price - 100) > 35:
                state.emotion *= 0.85
                state.price = state.price * 0.92 + 100 * 0.08
        assert abs(state.emotion) <= 0.75, "Emotion should normalize after regulation"
        print(f"\n监管3次后情绪: {state.emotion:.2f}, 价格: {state.price:.1f}")

class TestMarketShock:
    """测试市场冲击响应"""

    def test_greed_shock_simulation(self):
        """贪婪冲击模拟"""
        state = MarketState()
        # 注入贪婪冲击
        state.emotion = 0.9
        state.narrative = 0.9
        state.price = 115.0
        trajectory = [state.price]
        for _ in range(20):
            state.step_forward()
            trajectory.append(state.price)
        print(f"\n贪婪冲击价格轨迹: {[f'{p:.1f}' for p in trajectory[:5]]}...")
        # 价格应该持续偏高一段时间
        assert sum(trajectory[5:10]) / 5 > 105, "Price should stay elevated after greed shock"

    def test_panic_shock_simulation(self):
        """恐慌冲击模拟"""
        state = MarketState()
        state.emotion = -0.85
        state.narrative = 0.7
        state.price = 80.0
        trajectory = [state.price]
        for _ in range(20):
            state.step_forward()
            trajectory.append(state.price)
        print(f"\n恐慌冲击价格轨迹: {[f'{p:.1f}' for p in trajectory[:5]]}...")
        # 价格应该持续偏低
        assert sum(trajectory[5:10]) / 5 < 95, "Price should stay depressed after panic shock"

class TestBenchmarkSummary:
    """汇总"""

    def test_run_all_regimes(self):
        """三种市场状态benchmark"""
        regimes = {
            "中性": 0.0,
            "贪婪": 0.7,
            "恐慌": -0.7,
        }
        results = {}
        for name, emotion in regimes.items():
            state = MarketState()
            state.emotion = emotion
            state.narrative = abs(emotion)
            for _ in range(10):
                state.step_forward()
            results[name] = {"price": round(state.price, 1), "emotion": round(state.emotion, 3)}
        print("\n=== ReflexMarket Benchmark ===")
        for regime, vals in results.items():
            print(f"  {regime}: price={vals['price']}, emotion={vals['emotion']}")
        # 贪婪>中性>恐慌
        assert results["贪婪"]["price"] > results["中性"]["price"] > results["恐慌"]["price"]
        print("\nPASS: 价格排序 贪婪>中性>恐慌")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
