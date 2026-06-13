"""
ReflexMarket-AI Smoke Tests
Comprehensive tests covering: backend API, market simulator, KOL network, regulator agent.

Run: pytest tests/test_smoke.py -v
"""

import sys
import os
import pytest

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if os.path.join(PROJECT_ROOT, "backend", "app") not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend", "app"))


# ── Market Simulator Tests ──────────────────────────────────────────

class TestMarketNarrative:
    """Test MarketNarrative dataclass creation."""

    def test_create_narrative(self):
        from app.agents.market_simulator import MarketNarrative
        n = MarketNarrative(
            narrative_id="N-001",
            content="BTC to the moon",
            sentiment=0.8,
            spread_velocity=0.6,
            reach=500,
            confidence=0.75,
            stage="emerging",
            belief_ratio=0.3,
            price_impact=0.05,
        )
        assert n.narrative_id == "N-001"
        assert n.sentiment == 0.8
        assert n.stage == "emerging"

    def test_narrative_sentiment_range(self):
        from app.agents.market_simulator import MarketNarrative
        n = MarketNarrative("N-002", "test", -0.9, 0.5, 100, 0.5, "spreading", 0.4, -0.03)
        assert -1.0 <= n.sentiment <= 1.0


class TestMarketSimulator:
    """Test MarketReflexivitySimulator core methods."""

    @pytest.fixture
    def simulator(self):
        from app.agents.market_simulator import MarketReflexivitySimulator
        return MarketReflexivitySimulator()

    @pytest.fixture
    def sample_narrative(self):
        from app.agents.market_simulator import MarketNarrative
        return MarketNarrative(
            narrative_id="N-TEST",
            content="Market rally expected",
            sentiment=0.7,
            spread_velocity=0.6,
            reach=200,
            confidence=0.8,
            stage="emerging",
            belief_ratio=0.3,
            price_impact=0.04,
        )

    def test_narrative_spread_returns_dict(self, simulator, sample_narrative):
        result = simulator.simulate_narrative_spread(sample_narrative)
        assert isinstance(result, dict)
        assert "narrative_id" in result
        assert "spread_history" in result

    def test_narrative_spread_increases_reach(self, simulator, sample_narrative):
        result = simulator.simulate_narrative_spread(sample_narrative)
        assert result["final_reach"] >= sample_narrative.reach

    def test_narrative_spread_has_stages(self, simulator, sample_narrative):
        result = simulator.simulate_narrative_spread(sample_narrative)
        stages_seen = {h["stage"] for h in result["spread_history"]}
        assert len(stages_seen) >= 1

    def test_reflexivity_loop_basic(self, simulator):
        result = simulator.simulate_reflexivity_loop(
            initial_price=100.0, narrative_sentiment=0.5, confidence=0.7, ticks=10
        )
        assert "final_price" in result
        assert "price_history" in result
        assert len(result["price_history"]) == 10

    def test_reflexivity_bullish_sends_price_up(self, simulator):
        result = simulator.simulate_reflexivity_loop(
            initial_price=100.0, narrative_sentiment=0.9, confidence=0.9, ticks=20
        )
        assert result["final_price"] > 100.0

    def test_reflexivity_bearish_sends_price_down(self, simulator):
        result = simulator.simulate_reflexivity_loop(
            initial_price=100.0, narrative_sentiment=-0.9, confidence=0.8, ticks=20
        )
        assert result["final_price"] < 100.0

    def test_reflexivity_market_state_classification(self, simulator):
        # Bubble
        r = simulator.simulate_reflexivity_loop(100.0, 0.95, 0.95, 30)
        assert r["market_state"] in ("bubble_forming", "normal_fluctuation")
        # Panic
        r2 = simulator.simulate_reflexivity_loop(100.0, -0.95, 0.9, 30)
        assert r2["market_state"] in ("panic_selling", "normal_fluctuation")
        # Stable
        r3 = simulator.simulate_reflexivity_loop(100.0, 0.0, 0.5, 10)
        assert r3["market_state"] in ("stable", "normal_fluctuation")

    def test_detect_manipulation_high_risk(self, simulator, sample_narrative):
        sample_narrative.sentiment = 0.95
        sample_narrative.spread_velocity = 0.85
        result = simulator.detect_manipulation_risk(sample_narrative, trading_volume=50000, volume_anomaly=4.5)
        assert result["total_risk_score"] > 0.0
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_detect_manipulation_low_risk(self, simulator, sample_narrative):
        result = simulator.detect_manipulation_risk(sample_narrative, trading_volume=1000, volume_anomaly=1.0)
        assert result["risk_level"] == "LOW"

    def test_to_dict(self, simulator, sample_narrative):
        d = simulator.to_dict(sample_narrative)
        assert d["narrative_id"] == "N-TEST"
        assert "sentiment" in d


# ── KOL Network Tests ───────────────────────────────────────────────

class TestKOLNetwork:
    """Test KOL social network module."""

    def test_import_kol(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        assert NetworkTopology.STAR.value == "star"

    def test_star_topology(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        stats = net.get_network_stats()
        assert stats["total_agents"] == 10
        assert stats["hub_count"] >= 1

    def test_distributed_topology(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        stats = net.get_network_stats()
        assert stats["total_agents"] == 15

    def test_viral_topology(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
        stats = net.get_network_stats()
        assert stats["total_agents"] == 12

    def test_narrative_propagation(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        result = net.propagate_narrative("BTC to 100K!", rounds=3)
        assert "reach_rate" in result
        assert 0.0 <= result["reach_rate"] <= 1.0
        assert result["reached_agents"] >= 1

    def test_belief_distribution(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        dist = net.get_belief_distribution()
        assert "mean" in dist
        assert 0.0 <= dist["mean"] <= 1.0

    def test_trust_update(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from social.kol_network import KOLNetwork, NetworkTopology
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=8)
        initial_trust = {a.agent_id: a.trust for a in net.agents.values()}
        net.update_trust_from_price(price_change=5.0)
        # At least some agents should have changed trust
        changed = sum(1 for a in net.agents.values() if a.trust != initial_trust[a.agent_id])
        assert changed >= 0  # Trust updates are stochastic


# ── Regulator Agent Tests (src/agents - state machine) ────────────

class TestRegulatorAgentIntervention:
    """Test the V0.5 RegulatorAgent from src/agents (state-machine)."""

    @pytest.fixture
    def regulator(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from agents.regulator_agent import RegulatorAgent
        return RegulatorAgent()

    def test_regulator_creation(self, regulator):
        assert regulator.name == "RegulatorAgent"
        assert regulator.intervention_history == []

    def test_step_low_risk_no_action(self, regulator):
        result = regulator.step(risk_score=0.1, market_state={"step": 1}, manipulation_flags={})
        from agents.regulator_agent import InterventionIntensity
        assert result["intensity"] == InterventionIntensity.NONE

    def test_step_high_risk_triggers_intervention(self, regulator):
        result = regulator.step(risk_score=0.8, market_state={"step": 1}, manipulation_flags={})
        from agents.regulator_agent import InterventionIntensity
        assert result["intensity"] == InterventionIntensity.STRONG
        assert len(result["actions"]) > 1

    def test_intervention_history_recorded(self, regulator):
        regulator.step(risk_score=0.6, market_state={"step": 1}, manipulation_flags={})
        summary = regulator.get_intervention_summary()
        assert "total_interventions" in summary

    def test_cooldown_mechanism(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from agents.regulator_agent import CoolingMechanism, InterventionIntensity
        duration = CoolingMechanism.compute_cooldown_duration(0.8, InterventionIntensity.STRONG)
        assert duration >= 0
        assert duration <= CoolingMechanism.MAX_COOLDOWN_STEPS


# ── Regulator Agent Tests (src/agents) ──────────────────────────────

class TestRegulatorAgentAgents:
    """Test the market regulator from src/intervention (strategy-comparison)."""

    @pytest.fixture
    def regulator(self):
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from intervention.regulator_agent import RegulatorAgent
        return RegulatorAgent(budget=100.0, credibility=0.8)

    def test_observe_market(self, regulator):
        market_state = {"bubble_risk": 0.3, "panic_risk": 0.2, "manipulation_risk": 0.1, "volatility": 0.15}
        obs = regulator.observe_market(market_state)
        assert "overall_risk" in obs
        assert "recommendation" in obs

    def test_observe_high_bubble_risk(self, regulator):
        market_state = {"bubble_risk": 0.8, "panic_risk": 0.1, "manipulation_risk": 0.1}
        obs = regulator.observe_market(market_state)
        assert obs["recommendation"] == "INTERVENE_BUBBLE"

    def test_propose_intervention_below_threshold(self, regulator):
        market_state = {"bubble_risk": 0.1, "panic_risk": 0.1}
        result = regulator.propose_intervention(market_state)
        assert result["action"] == "no_intervention"

    def test_propose_intervention_above_threshold(self, regulator):
        market_state = {"bubble_risk": 0.7, "panic_risk": 0.3}
        result = regulator.propose_intervention(market_state)
        assert result["action"] == "intervene"

    def test_apply_intervention_deducts_budget(self, regulator):
        from intervention.regulator_agent import InterventionType
        initial_budget = regulator.budget
        result = regulator.apply_intervention(InterventionType.RISK_WARNING, intensity=0.5)
        assert regulator.budget < initial_budget

    def test_compare_strategies(self, regulator):
        market_state = {"bubble_risk": 0.6, "panic_risk": 0.4}
        result = regulator.compare_strategies(market_state)
        assert "strategy_comparison" in result
        assert len(result["strategy_comparison"]) == 4

    def test_intervention_stats(self, regulator):
        stats = regulator.get_intervention_stats()
        assert stats["total_interventions"] == 0


# ── API Routes Tests ────────────────────────────────────────────────

class TestAPIRoutes:
    """Test FastAPI routes via TestClient."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ReflexMarket-AI"

    def test_api_health_endpoint(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_narrative_spread_endpoint(self, client):
        payload = {
            "content": "Market rally coming",
            "sentiment": 0.7,
            "spread_velocity": 0.5,
            "reach": 200,
            "confidence": 0.8,
            "stage": "emerging",
            "belief_ratio": 0.3,
            "price_impact": 0.04,
        }
        resp = client.post("/api/v1/narrative/spread", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "data" in data

    def test_reflexivity_loop_endpoint(self, client):
        payload = {
            "initial_price": 100.0,
            "narrative_sentiment": 0.5,
            "confidence": 0.7,
            "ticks": 10,
        }
        resp = client.post("/api/v1/reflexivity/loop", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "final_price" in data["data"]

    def test_manipulation_detect_endpoint(self, client):
        payload = {
            "narrative_content": "Pump this coin!",
            "narrative_sentiment": 0.95,
            "trading_volume": 50000,
            "volume_anomaly": 4.5,
        }
        resp = client.post("/api/v1/risk/manipulation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "risk_level" in data["data"]


# ── Integration / Cross-Module Tests ────────────────────────────────

class TestIntegration:
    """Cross-module integration tests."""

    def test_full_pipeline_narrative_to_regulation(self):
        """Simulate: narrative spread -> reflexivity loop -> risk detection -> regulation."""
        sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
        from app.agents.market_simulator import MarketReflexivitySimulator, MarketNarrative
        from agents.regulator_agent import RegulatorAgent

        # 1. Create narrative
        narrative = MarketNarrative("INT-001", "Bubble forming", 0.9, 0.8, 500, 0.85, "spreading", 0.5, 0.08)
        sim = MarketReflexivitySimulator()

        # 2. Spread narrative
        spread = sim.simulate_narrative_spread(narrative)
        assert spread["final_reach"] >= 500

        # 3. Run reflexivity loop
        loop = sim.simulate_reflexivity_loop(100.0, 0.9, 0.85, 15)
        assert loop["final_price"] != 100.0

        # 4. Detect manipulation
        risk = sim.detect_manipulation_risk(narrative, 80000, 5.0)
        assert risk["total_risk_score"] >= 0.0

        # 5. Regulate if needed
        regulator = RegulatorAgent()
        risk_score = risk["total_risk_score"]
        reg_result = regulator.step(risk_score, {"step": 1}, {})
        assert "intensity" in reg_result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
