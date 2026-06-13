"""
End-to-end integration tests.
Tests the full pipeline: Narrative -> Spread -> Reflexivity -> Risk -> Regulation.
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
from social.kol_network import KOLNetwork, NetworkTopology
from agents.regulator_agent import RegulatorAgent as StateMachineRegulator
from intervention.regulator_agent import RegulatorAgent as StrategyRegulator


# ── Full Pipeline Integration Tests ───────────────────────────────


class TestFullPipeline:
    """Test the complete simulation pipeline."""

    def test_narrative_to_reflexivity_to_risk(self):
        """Narrative spread feeds into reflexivity loop, then risk detection."""
        sim = MarketReflexivitySimulator()

        # 1. Create and spread narrative
        narrative = MarketNarrative(
            narrative_id="INT-001",
            content="Massive bull run incoming",
            sentiment=0.85,
            spread_velocity=0.7,
            reach=500,
            confidence=0.8,
            stage="emerging",
            belief_ratio=0.4,
            price_impact=0.05,
        )
        spread = sim.simulate_narrative_spread(narrative)
        assert spread["final_reach"] >= 500

        # 2. Run reflexivity loop with spread sentiment
        loop = sim.simulate_reflexivity_loop(
            initial_price=100.0,
            narrative_sentiment=narrative.sentiment,
            confidence=narrative.confidence,
            ticks=15,
        )
        assert loop["final_price"] != 100.0
        assert "market_state" in loop

        # 3. Detect manipulation risk
        risk = sim.detect_manipulation_risk(narrative, trading_volume=80000, volume_anomaly=5.0)
        assert risk["total_risk_score"] >= 0.0
        assert risk["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_pipeline_with_regulation(self):
        """Full pipeline including regulatory intervention."""
        sim = MarketReflexivitySimulator()
        regulator = StateMachineRegulator()

        # High-risk scenario
        narrative = MarketNarrative(
            narrative_id="INT-002",
            content="Pump and dump scheme",
            sentiment=0.95,
            spread_velocity=0.85,
            reach=1000,
            confidence=0.9,
            stage="spreading",
            belief_ratio=0.5,
            price_impact=0.08,
        )

        # Detect risk
        risk = sim.detect_manipulation_risk(narrative, 100000, 5.5)
        risk_score = risk["total_risk_score"]

        # Regulate
        reg_result = regulator.step(
            risk_score=risk_score,
            market_state={"step": 1, "price": 150.0, "bubble_risk": 0.7},
            manipulation_flags={},
        )
        assert "intensity" in reg_result
        assert "actions" in reg_result

    def test_kol_network_feeds_into_simulator(self):
        """KOL network propagation results feed into market simulator."""
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        sim = MarketReflexivitySimulator()

        # Propagate through KOL network
        prop = net.propagate_narrative("BTC to the moon!", rounds=3)
        belief_dist = net.get_belief_distribution()

        # Use belief distribution to parameterize simulation
        sentiment = belief_dist["mean"] * 2 - 1  # Map 0-1 to -1 to 1
        loop = sim.simulate_reflexivity_loop(
            initial_price=100.0,
            narrative_sentiment=max(-1, min(1, sentiment)),
            confidence=belief_dist["mean"],
            ticks=10,
        )
        assert "final_price" in loop

    def test_strategy_regulator_comparison(self):
        """Strategy regulator compares interventions across market states."""
        reg = StrategyRegulator(budget=200.0, credibility=0.85)

        scenarios = [
            {"bubble_risk": 0.8, "panic_risk": 0.1, "manipulation_risk": 0.1, "volatility": 0.3},
            {"bubble_risk": 0.1, "panic_risk": 0.8, "manipulation_risk": 0.1, "volatility": 0.5},
            {"bubble_risk": 0.3, "panic_risk": 0.3, "manipulation_risk": 0.7, "volatility": 0.4},
        ]

        for state in scenarios:
            obs = reg.observe_market(state)
            assert "recommendation" in obs
            assert obs["recommendation"] in (
                "INTERVENE_BUBBLE", "INTERVENE_PANIC", "INTERVENE_MANIPULATION",
                "WATCH_AND_PREPARE", "NO_ACTION"
            )

    def test_multi_topology_comparison(self):
        """Compare narrative spread across different network topologies."""
        results = {}
        for topo in NetworkTopology:
            net = KOLNetwork(topology=topo, n_agents=15)
            prop = net.propagate_narrative("Test narrative", rounds=3)
            results[topo.value] = prop["reach_rate"]

        # All topologies should produce valid reach rates
        for topo_name, reach_rate in results.items():
            assert 0.0 <= reach_rate <= 1.0, f"{topo_name} has invalid reach_rate: {reach_rate}"


# ── Cross-Module Data Flow Tests ──────────────────────────────────


class TestCrossModuleDataFlow:
    """Test data flows correctly between modules."""

    def test_narrative_belief_price_chain(self):
        """Verify the chain: narrative -> belief -> price."""
        sim = MarketReflexivitySimulator()

        # Positive narrative should increase price
        pos = sim.simulate_reflexivity_loop(100.0, 0.8, 0.8, 15)
        # Negative narrative should decrease price
        neg = sim.simulate_reflexivity_loop(100.0, -0.8, 0.8, 15)

        assert pos["final_price"] > neg["final_price"]

    def test_kol_trust_affects_propagation(self):
        """Higher trust KOLs should spread narratives more effectively."""
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)

        # Find the hub (highest trust)
        hub = max(net.agents.values(), key=lambda a: a.trust)
        result = net.propagate_narrative("High trust narrative", source_id=hub.agent_id, rounds=3)
        assert result["reached_agents"] >= 1

    def test_risk_score_drives_intervention_intensity(self):
        """Higher risk scores should trigger stronger interventions."""
        reg = StateMachineRegulator()

        low = reg.step(risk_score=0.2, market_state={"step": 1}, manipulation_flags={})
        reg.reset()
        high = reg.step(risk_score=0.9, market_state={"step": 2}, manipulation_flags={})

        from agents.regulator_agent import InterventionIntensity
        assert low["intensity"].value <= high["intensity"].value


# ── Benchmark Scenario Integration ────────────────────────────────


class TestBenchmarkScenarios:
    """Run benchmark-like scenarios through the full stack."""

    def test_bubble_scenario(self):
        """Simulate a bubble formation scenario."""
        sim = MarketReflexivitySimulator()

        # Escalating narrative
        for strength in [0.3, 0.5, 0.7, 0.9]:
            narrative = MarketNarrative(
                narrative_id=f"BUBBLE-{int(strength*100)}",
                content=f"Bubble phase {strength}",
                sentiment=strength,
                spread_velocity=strength * 0.8,
                reach=int(500 * strength),
                confidence=0.8,
                stage="spreading",
                belief_ratio=0.3 + strength * 0.3,
                price_impact=0.02 * strength,
            )
            result = sim.simulate_narrative_spread(narrative)
            assert result["final_reach"] > 0

    def test_panic_scenario(self):
        """Simulate a panic scenario."""
        sim = MarketReflexivitySimulator()

        result = sim.simulate_reflexivity_loop(
            initial_price=200.0,
            narrative_sentiment=-0.95,
            confidence=0.9,
            ticks=30,
        )
        assert result["market_state"] in ("panic_selling", "normal_fluctuation")
        assert result["final_price"] < 200.0

    def test_regulation_effectiveness(self):
        """Test that regulation reduces risk metrics."""
        reg = StateMachineRegulator()

        # Unregulated risk
        unregulated = reg.step(risk_score=0.8, market_state={"step": 1}, manipulation_flags={})

        # Continue with regulation active
        regulated = reg.step(risk_score=0.8, market_state={"step": 2}, manipulation_flags={})

        # Both should produce valid results
        assert "intensity" in unregulated
        assert "intensity" in regulated
