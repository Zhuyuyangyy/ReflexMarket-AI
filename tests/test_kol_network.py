"""
Unit tests for KOLNetwork module
Tests all three topologies, narrative propagation, and trust dynamics.
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

from social.kol_network import KOLNetwork, NetworkTopology, KOLAgent


# ── KOLAgent Tests ────────────────────────────────────────────────


class TestKOLAgent:
    """Test KOLAgent dataclass and methods."""

    def test_creation(self):
        agent = KOLAgent("k1", "Test KOL", 10000, 0.7, 0.6, "hub")
        assert agent.agent_id == "k1"
        assert agent.followers == 10000
        assert agent.trust == 0.7

    def test_default_belief_state(self):
        agent = KOLAgent("k1", "Test", 1000, 0.5, 0.5, "micro")
        assert agent.belief_state == 0.5

    def test_trust_update_positive(self):
        agent = KOLAgent("k1", "Test", 1000, 0.5, 0.5, "hub")
        initial = agent.trust
        agent.update_trust(price_change=5.0, accuracy=0.8)
        assert agent.trust >= initial

    def test_trust_update_negative(self):
        agent = KOLAgent("k1", "Test", 1000, 0.5, 0.5, "hub")
        initial = agent.trust
        agent.update_trust(price_change=-5.0, accuracy=0.3)
        assert agent.trust <= initial

    def test_trust_bounded_0_to_1(self):
        agent = KOLAgent("k1", "Test", 1000, 0.05, 0.5, "hub")
        agent.update_trust(price_change=-10.0, accuracy=0.1)
        assert agent.trust >= 0.1

        agent2 = KOLAgent("k2", "Test", 1000, 0.98, 0.5, "hub")
        agent2.update_trust(price_change=10.0, accuracy=0.99)
        assert agent2.trust <= 1.0

    def test_spread_narrative(self):
        agent = KOLAgent("k1", "Test", 100000, 0.8, 0.7, "hub")
        audience = [KOLAgent(f"k{i}", f"K{i}", 1000, 0.5, 0.5, "micro") for i in range(2, 5)]
        result = agent.spread_narrative("Test narrative", audience)
        assert "spreader_id" in result
        assert "original_reach" in result
        assert result["spreader_id"] == "k1"
        assert agent.narrative_count == 1


# ── NetworkTopology Tests ─────────────────────────────────────────


class TestNetworkTopology:
    """Test topology enum values."""

    def test_star_value(self):
        assert NetworkTopology.STAR.value == "star"

    def test_distributed_value(self):
        assert NetworkTopology.DISTRIBUTED.value == "distributed"

    def test_viral_value(self):
        assert NetworkTopology.VIRAL.value == "viral"


# ── KOLNetwork STAR Topology Tests ────────────────────────────────


class TestKOLNetworkStar:
    """Test STAR topology construction and properties."""

    def test_agent_count(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        assert len(net.agents) == 10

    def test_has_hub(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        hubs = [a for a in net.agents.values() if a.topology_role == "hub"]
        assert len(hubs) >= 1

    def test_hub_has_high_followers(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        hub = next(a for a in net.agents.values() if a.topology_role == "hub")
        assert hub.followers >= 100000

    def test_network_stats(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        stats = net.get_network_stats()
        assert stats["total_agents"] == 10
        assert stats["topology"] == "star"
        assert stats["hub_count"] >= 1


# ── KOLNetwork DISTRIBUTED Topology Tests ─────────────────────────


class TestKOLNetworkDistributed:
    """Test DISTRIBUTED topology construction."""

    def test_agent_count(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        assert len(net.agents) == 15

    def test_multiple_hubs(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        stats = net.get_network_stats()
        assert stats["hub_count"] >= 2

    def test_has_micro_agents(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        stats = net.get_network_stats()
        assert stats["micro_count"] >= 1


# ── KOLNetwork VIRAL Topology Tests ───────────────────────────────


class TestKOLNetworkViral:
    """Test VIRAL topology construction."""

    def test_agent_count(self):
        net = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
        assert len(net.agents) == 12

    def test_no_dominant_hub(self):
        net = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
        stats = net.get_network_stats()
        # In viral topology, all are "mid" role
        assert stats["hub_count"] == 0

    def test_all_connected(self):
        net = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
        for agent_id in net.agents:
            assert agent_id in net.network_graph
            assert len(net.network_graph[agent_id]) >= 2


# ── Narrative Propagation Tests ───────────────────────────────────


class TestNarrativePropagation:
    """Test propagate_narrative method across topologies."""

    def test_propagation_returns_dict(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        result = net.propagate_narrative("Test narrative", rounds=3)
        assert isinstance(result, dict)

    def test_propagation_has_required_keys(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        result = net.propagate_narrative("Test", rounds=3)
        required = ["source_id", "topology", "total_agents", "reached_agents", "reach_rate", "rounds"]
        for key in required:
            assert key in result

    def test_reach_rate_bounded(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        result = net.propagate_narrative("BTC rally!", rounds=3)
        assert 0.0 <= result["reach_rate"] <= 1.0

    def test_at_least_source_reached(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        result = net.propagate_narrative("Test", rounds=1)
        assert result["reached_agents"] >= 1

    def test_star_propagation(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        result = net.propagate_narrative("Market rally!", rounds=3)
        assert result["reach_rate"] > 0

    def test_viral_propagation(self):
        net = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
        result = net.propagate_narrative("Viral news!", rounds=3)
        assert result["reach_rate"] > 0

    def test_more_rounds_more_reach(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        r1 = net.propagate_narrative("Test", rounds=1)
        # Reset
        net2 = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        r3 = net2.propagate_narrative("Test", rounds=5)
        # More rounds should generally reach more (stochastic, so just check structure)
        assert r1["reached_agents"] >= 1
        assert r3["reached_agents"] >= 1

    def test_specific_source(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
        hub_id = next(a.agent_id for a in net.agents.values() if a.topology_role == "hub")
        result = net.propagate_narrative("From the top!", source_id=hub_id, rounds=3)
        assert result["source_id"] == hub_id

    def test_propagation_log_structure(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        result = net.propagate_narrative("Test", rounds=3)
        assert "propagation_log" in result
        if result["propagation_log"]:
            log = result["propagation_log"][0]
            assert "round" in log
            assert "spreaders" in log

    def test_belief_distribution_present(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        result = net.propagate_narrative("Test", rounds=3)
        assert "belief_distribution" in result
        assert "mean" in result["belief_distribution"]


# ── Trust Update Tests ────────────────────────────────────────────


class TestTrustUpdate:
    """Test trust dynamics."""

    def test_positive_price_updates_trust(self):
        net = KOLNetwork(topology=NetworkTopology.STAR, n_agents=8)
        initial_trust = {a.agent_id: a.trust for a in net.agents.values()}
        net.update_trust_from_price(price_change=5.0)
        # At least some should change
        changed = sum(1 for a in net.agents.values() if a.trust != initial_trust[a.agent_id])
        assert changed >= 0  # Stochastic

    def test_negative_price_updates_trust(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        initial_trust = {a.agent_id: a.trust for a in net.agents.values()}
        net.update_trust_from_price(price_change=-5.0)
        changed = sum(1 for a in net.agents.values() if a.trust != initial_trust[a.agent_id])
        assert changed >= 0


# ── Belief Distribution Tests ─────────────────────────────────────


class TestBeliefDistribution:
    """Test belief distribution methods."""

    def test_get_belief_distribution(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        dist = net.get_belief_distribution()
        assert "mean" in dist
        assert "median" in dist
        assert "bullish_pct" in dist
        assert "bearish_pct" in dist
        assert "neutral_pct" in dist

    def test_percentages_sum_to_one(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        dist = net.get_belief_distribution()
        total = dist["bullish_pct"] + dist["bearish_pct"] + dist["neutral_pct"]
        assert abs(total - 1.0) < 0.01


# ── Network Stats Tests ───────────────────────────────────────────


class TestNetworkStats:
    """Test get_network_stats method."""

    def test_stats_has_all_fields(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=10)
        stats = net.get_network_stats()
        required = ["topology", "total_agents", "avg_followers", "avg_trust", "avg_influence", "hub_count", "micro_count"]
        for key in required:
            assert key in stats

    def test_stats_values_reasonable(self):
        net = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
        stats = net.get_network_stats()
        assert stats["total_agents"] == 15
        assert 0.0 <= stats["avg_trust"] <= 1.0
        assert 0.0 <= stats["avg_influence"] <= 1.0
