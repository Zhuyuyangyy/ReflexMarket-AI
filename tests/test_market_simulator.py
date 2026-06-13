"""
Unit tests for MarketReflexivitySimulator
Tests all core simulation methods with edge cases.
"""

import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

for p in [PROJECT_ROOT, BACKEND_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.agents.market_simulator import MarketReflexivitySimulator, MarketNarrative


@pytest.fixture
def simulator():
    return MarketReflexivitySimulator()


@pytest.fixture
def bullish_narrative():
    return MarketNarrative(
        narrative_id="N-BULL",
        content="BTC to 100K",
        sentiment=0.9,
        spread_velocity=0.8,
        reach=1000,
        confidence=0.85,
        stage="emerging",
        belief_ratio=0.4,
        price_impact=0.06,
    )


@pytest.fixture
def bearish_narrative():
    return MarketNarrative(
        narrative_id="N-BEAR",
        content="Market crash imminent",
        sentiment=-0.85,
        spread_velocity=0.7,
        reach=800,
        confidence=0.7,
        stage="spreading",
        belief_ratio=0.5,
        price_impact=-0.04,
    )


# ── MarketNarrative Tests ─────────────────────────────────────────


class TestMarketNarrative:
    """Test MarketNarrative dataclass."""

    def test_creation_with_valid_data(self):
        n = MarketNarrative("N1", "test", 0.5, 0.6, 100, 0.7, "emerging", 0.3, 0.02)
        assert n.narrative_id == "N1"
        assert n.content == "test"
        assert n.sentiment == 0.5

    def test_sentiment_extremes(self):
        n_pos = MarketNarrative("N1", "test", 1.0, 0.5, 100, 0.5, "emerging", 0.3, 0.01)
        n_neg = MarketNarrative("N2", "test", -1.0, 0.5, 100, 0.5, "emerging", 0.3, -0.01)
        assert n_pos.sentiment == 1.0
        assert n_neg.sentiment == -1.0

    def test_all_stages(self):
        for stage in ["emerging", "spreading", "dominating", "peaking", "collapsing"]:
            n = MarketNarrative("N1", "test", 0.5, 0.5, 100, 0.5, stage, 0.3, 0.02)
            assert n.stage == stage


# ── Narrative Spread Tests ────────────────────────────────────────


class TestNarrativeSpread:
    """Test simulate_narrative_spread method."""

    def test_returns_dict_with_required_keys(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        assert isinstance(result, dict)
        required_keys = ["narrative_id", "network_size", "final_reach", "final_belief_ratio", "spread_history"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_final_reach_exceeds_initial(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        assert result["final_reach"] >= bullish_narrative.reach

    def test_spread_history_is_list(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        assert isinstance(result["spread_history"], list)
        assert len(result["spread_history"]) > 0

    def test_spread_history_has_tick_data(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        for entry in result["spread_history"]:
            assert "tick" in entry
            assert "stage" in entry
            assert "total_reach" in entry

    def test_bearish_narrative_spreads(self, simulator, bearish_narrative):
        result = simulator.simulate_narrative_spread(bearish_narrative)
        assert result["final_reach"] >= bearish_narrative.reach

    def test_custom_network_size(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative, network_size=5000)
        assert result["network_size"] == 5000

    def test_belief_ratio_bounded(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        assert 0.0 <= result["final_belief_ratio"] <= 1.0

    def test_simulation_ticks_positive(self, simulator, bullish_narrative):
        result = simulator.simulate_narrative_spread(bullish_narrative)
        assert result["simulation_ticks"] > 0


# ── Reflexivity Loop Tests ────────────────────────────────────────


class TestReflexivityLoop:
    """Test simulate_reflexivity_loop method."""

    def test_returns_required_keys(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.5, 0.7, 10)
        required = ["initial_price", "final_price", "total_return_pct", "market_state", "risk_level", "price_history"]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_price_history_length_matches_ticks(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.5, 0.7, 15)
        assert len(result["price_history"]) == 15

    def test_bullish_sends_price_up(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.9, 0.9, 20)
        assert result["final_price"] > 100.0

    def test_bearish_sends_price_down(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, -0.9, 0.8, 20)
        assert result["final_price"] < 100.0

    def test_neutral_sentiment_stable(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.0, 0.5, 10)
        assert abs(result["total_return_pct"]) < 50

    def test_high_confidence_amplifies(self, simulator):
        r_high = simulator.simulate_reflexivity_loop(100.0, 0.8, 0.95, 15)
        r_low = simulator.simulate_reflexivity_loop(100.0, 0.8, 0.2, 15)
        assert abs(r_high["total_return_pct"]) > abs(r_low["total_return_pct"])

    def test_market_state_bubble(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.95, 0.95, 30)
        assert result["market_state"] in ("bubble_forming", "normal_fluctuation")

    def test_market_state_panic(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, -0.95, 0.9, 30)
        assert result["market_state"] in ("panic_selling", "normal_fluctuation")

    def test_market_state_stable(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.0, 0.5, 5)
        assert result["market_state"] in ("stable", "normal_fluctuation")

    def test_belief_history_present(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.5, 0.7, 10)
        assert "belief_history" in result
        assert len(result["belief_history"]) == 10

    def test_reflexivity_factor_in_result(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.5, 0.7, 10)
        assert "reflexivity_factor" in result
        assert result["reflexivity_factor"] > 0

    def test_single_tick(self, simulator):
        result = simulator.simulate_reflexivity_loop(100.0, 0.5, 0.7, 1)
        assert len(result["price_history"]) == 1


# ── Manipulation Detection Tests ──────────────────────────────────


class TestManipulationDetection:
    """Test detect_manipulation_risk method."""

    def test_returns_required_keys(self, simulator, bullish_narrative):
        result = simulator.detect_manipulation_risk(bullish_narrative, 10000, 1.0)
        required = ["narrative_id", "risk_factors", "total_risk_score", "risk_level", "recommended_action"]
        for key in required:
            assert key in result

    def test_high_volume_anomaly_detected(self, simulator, bullish_narrative):
        result = simulator.detect_manipulation_risk(bullish_narrative, 50000, 5.0)
        assert result["total_risk_score"] > 0
        assert any(f["factor"] == "volume_spike" for f in result["risk_factors"])

    def test_coordinated_spread_detected(self, simulator):
        n = MarketNarrative("N1", "pump", 0.95, 0.85, 500, 0.8, "spreading", 0.5, 0.05)
        result = simulator.detect_manipulation_risk(n, 10000, 1.0)
        factors = [f["factor"] for f in result["risk_factors"]]
        assert "coordinated_spread" in factors

    def test_confidence_belief_gap_detected(self, simulator):
        n = MarketNarrative("N1", "test", 0.5, 0.5, 100, 0.95, "emerging", 0.1, 0.02)
        result = simulator.detect_manipulation_risk(n, 1000, 1.0)
        factors = [f["factor"] for f in result["risk_factors"]]
        assert "confidence_belief_gap" in factors

    def test_low_risk_for_normal_conditions(self, simulator):
        n = MarketNarrative("N1", "normal", 0.3, 0.3, 100, 0.5, "emerging", 0.5, 0.01)
        result = simulator.detect_manipulation_risk(n, 1000, 1.0)
        assert result["risk_level"] == "LOW"

    def test_risk_level_classification(self, simulator, bullish_narrative):
        result = simulator.detect_manipulation_risk(bullish_narrative, 50000, 5.0)
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_recommended_action_is_string(self, simulator, bullish_narrative):
        result = simulator.detect_manipulation_risk(bullish_narrative, 10000, 1.0)
        assert isinstance(result["recommended_action"], str)


# ── Helper Method Tests ───────────────────────────────────────────


class TestHelperMethods:
    """Test helper methods."""

    def test_to_dict(self, simulator, bullish_narrative):
        d = simulator.to_dict(bullish_narrative)
        assert d["narrative_id"] == "N-BULL"
        assert d["content"] == "BTC to 100K"
        assert "sentiment" in d
        assert "spread_velocity" in d

    def test_get_regulation_action_high_risk(self, simulator):
        action = simulator._get_regulation_action(0.8)
        assert "调查" in action or "监控" in action

    def test_get_regulation_action_medium_risk(self, simulator):
        action = simulator._get_regulation_action(0.5)
        assert "信息披露" in action or "约谈" in action

    def test_get_regulation_action_low_risk(self, simulator):
        action = simulator._get_regulation_action(0.2)
        assert "监控" in action or "不采取" in action
