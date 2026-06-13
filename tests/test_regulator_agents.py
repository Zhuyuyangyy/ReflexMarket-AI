"""
Unit tests for both RegulatorAgent implementations.
- src/agents/regulator_agent.py: State-machine regulator (step/reset/get_intervention_summary)
- src/intervention/regulator_agent.py: Strategy-comparison regulator (observe_market/propose_intervention/apply_intervention)
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


# ── Strategy-Comparison RegulatorAgent Tests ──────────────────────
# (src/intervention/regulator_agent.py)


class TestStrategyComparisonRegulator:
    """Test RegulatorAgent from src/intervention/regulator_agent.py."""

    @pytest.fixture
    def regulator(self):
        from intervention.regulator_agent import RegulatorAgent
        return RegulatorAgent(budget=100.0, credibility=0.8)

    def test_creation(self, regulator):
        assert regulator.budget == 100.0
        assert regulator.credibility == 0.8
        assert regulator.intervention_history == []

    def test_observe_market_low_risk(self, regulator):
        state = {"bubble_risk": 0.1, "panic_risk": 0.1, "manipulation_risk": 0.05, "volatility": 0.1}
        obs = regulator.observe_market(state)
        assert obs["recommendation"] == "NO_ACTION"
        assert obs["overall_risk"] < 0.5

    def test_observe_market_high_bubble(self, regulator):
        state = {"bubble_risk": 0.8, "panic_risk": 0.1, "manipulation_risk": 0.1}
        obs = regulator.observe_market(state)
        assert obs["recommendation"] == "INTERVENE_BUBBLE"

    def test_observe_market_high_panic(self, regulator):
        state = {"bubble_risk": 0.1, "panic_risk": 0.7, "manipulation_risk": 0.1}
        obs = regulator.observe_market(state)
        assert obs["recommendation"] == "INTERVENE_PANIC"

    def test_observe_market_high_manipulation(self, regulator):
        state = {"bubble_risk": 0.2, "panic_risk": 0.2, "manipulation_risk": 0.6}
        obs = regulator.observe_market(state)
        assert obs["recommendation"] == "INTERVENE_MANIPULATION"

    def test_observe_market_watch(self, regulator):
        state = {"bubble_risk": 0.45, "panic_risk": 0.3, "manipulation_risk": 0.1}
        obs = regulator.observe_market(state)
        assert obs["recommendation"] == "WATCH_AND_PREPARE"

    def test_propose_below_threshold(self, regulator):
        state = {"bubble_risk": 0.1, "panic_risk": 0.1}
        result = regulator.propose_intervention(state)
        assert result["action"] == "no_intervention"

    def test_propose_above_threshold(self, regulator):
        state = {"bubble_risk": 0.7, "panic_risk": 0.3}
        result = regulator.propose_intervention(state)
        assert result["action"] == "intervene"
        assert "proposed_interventions" in result
        assert len(result["proposed_interventions"]) > 0

    def test_propose_respects_budget(self, regulator):
        state = {"bubble_risk": 0.8, "panic_risk": 0.8}
        result = regulator.propose_intervention(state)
        assert result["total_cost"] <= regulator.budget

    def test_apply_intervention_deducts_budget(self, regulator):
        from intervention.regulator_agent import InterventionType
        initial = regulator.budget
        regulator.apply_intervention(InterventionType.RISK_WARNING, intensity=0.5)
        assert regulator.budget < initial

    def test_apply_intervention_returns_result(self, regulator):
        from intervention.regulator_agent import InterventionType
        result = regulator.apply_intervention(InterventionType.KOL_DOWNWEIGHT, intensity=0.5)
        assert result.intervention_type == "kol_downweight"
        assert result.cost > 0
        assert 0.0 <= result.effectiveness <= 1.0

    def test_apply_intervention_insufficient_budget(self):
        from intervention.regulator_agent import RegulatorAgent, InterventionType
        reg = RegulatorAgent(budget=0.01, credibility=0.8)
        result = reg.apply_intervention(InterventionType.LIQUIDITY_INJECTION, intensity=1.0)
        assert result.effectiveness == 0
        assert "rejected" in result.market_response or result.cost == 0

    def test_compare_strategies(self, regulator):
        state = {"bubble_risk": 0.6, "panic_risk": 0.4}
        result = regulator.compare_strategies(state)
        assert "strategy_comparison" in result
        assert len(result["strategy_comparison"]) == 4

    def test_intervention_stats_empty(self, regulator):
        stats = regulator.get_intervention_stats()
        assert stats["total_interventions"] == 0

    def test_intervention_stats_after_action(self, regulator):
        from intervention.regulator_agent import InterventionType
        regulator.apply_intervention(InterventionType.RISK_WARNING, intensity=0.5)
        stats = regulator.get_intervention_stats()
        assert stats["total_interventions"] == 1
        assert stats["avg_effectiveness"] > 0

    def test_credibility_impact(self):
        from intervention.regulator_agent import RegulatorAgent, InterventionType
        reg = RegulatorAgent(budget=100.0, credibility=0.8)
        reg.apply_intervention(InterventionType.LIQUIDITY_INJECTION, intensity=0.8)

    def test_all_intervention_types(self, regulator):
        from intervention.regulator_agent import InterventionType
        for itype in InterventionType:
            reg_fresh = regulator.__class__(budget=100.0, credibility=0.8)
            result = reg_fresh.apply_intervention(itype, intensity=0.5)
            assert result.intervention_type == itype.value


# ── State-Machine RegulatorAgent Tests ────────────────────────────
# (src/agents/regulator_agent.py)


class TestStateMachineRegulator:
    """Test RegulatorAgent from src/agents/regulator_agent.py."""

    @pytest.fixture
    def regulator(self):
        from agents.regulator_agent import RegulatorAgent
        return RegulatorAgent()

    def test_creation(self, regulator):
        assert regulator.name == "RegulatorAgent"
        assert regulator.intervention_history == []

    def test_reset(self, regulator):
        from agents.regulator_agent import InterventionIntensity
        regulator.step(risk_score=0.6, market_state={"step": 1}, manipulation_flags={})
        regulator.reset()
        assert regulator.current_intensity == InterventionIntensity.NONE

    def test_low_risk_no_action(self, regulator):
        result = regulator.step(risk_score=0.1, market_state={"step": 1}, manipulation_flags={})
        from agents.regulator_agent import InterventionIntensity
        assert result["intensity"] == InterventionIntensity.NONE

    def test_moderate_risk(self, regulator):
        result = regulator.step(risk_score=0.4, market_state={"step": 1}, manipulation_flags={})
        from agents.regulator_agent import InterventionIntensity
        assert result["intensity"] in (InterventionIntensity.LIGHT, InterventionIntensity.MODERATE)

    def test_high_risk_strong_intervention(self, regulator):
        result = regulator.step(risk_score=0.8, market_state={"step": 1}, manipulation_flags={})
        from agents.regulator_agent import InterventionIntensity
        assert result["intensity"] == InterventionIntensity.STRONG
        assert len(result["actions"]) > 1

    def test_result_has_actions(self, regulator):
        result = regulator.step(risk_score=0.5, market_state={"step": 1}, manipulation_flags={})
        assert "actions" in result
        assert isinstance(result["actions"], list)

    def test_result_has_state_snapshot(self, regulator):
        result = regulator.step(risk_score=0.5, market_state={"step": 1}, manipulation_flags={})
        assert "state_snapshot" in result
        snapshot = result["state_snapshot"]
        assert "kol_penalty" in snapshot
        assert "narrative_cap" in snapshot

    def test_intervention_summary(self, regulator):
        regulator.step(risk_score=0.6, market_state={"step": 1}, manipulation_flags={})
        summary = regulator.get_intervention_summary()
        assert "total_interventions" in summary


# ── InterventionPolicy Tests ──────────────────────────────────────


class TestInterventionPolicy:
    """Test InterventionPolicy class from agents.regulator_agent."""

    def test_none_intensity(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity
        result = InterventionPolicy.select_intensity(0.1, {})
        assert result == InterventionIntensity.NONE

    def test_light_intensity(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity
        result = InterventionPolicy.select_intensity(0.35, {})
        assert result == InterventionIntensity.LIGHT

    def test_moderate_intensity(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity
        result = InterventionPolicy.select_intensity(0.55, {})
        assert result == InterventionIntensity.MODERATE

    def test_strong_intensity(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity
        result = InterventionPolicy.select_intensity(0.8, {})
        assert result == InterventionIntensity.STRONG

    def test_actions_for_none(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity, InterventionAction
        actions = InterventionPolicy.get_actions_for_intensity(InterventionIntensity.NONE)
        assert actions == [InterventionAction.NO_ACTION]

    def test_actions_for_strong(self):
        from agents.regulator_agent import InterventionPolicy, InterventionIntensity
        actions = InterventionPolicy.get_actions_for_intensity(InterventionIntensity.STRONG)
        assert len(actions) == 4


# ── CoolingMechanism Tests ────────────────────────────────────────


class TestCoolingMechanism:
    """Test CoolingMechanism class from agents.regulator_agent."""

    def test_cooldown_duration_bounded(self):
        from agents.regulator_agent import CoolingMechanism, InterventionIntensity
        duration = CoolingMechanism.compute_cooldown_duration(0.8, InterventionIntensity.STRONG)
        assert 0 <= duration <= CoolingMechanism.MAX_COOLDOWN_STEPS

    def test_strong_multiplier(self):
        from agents.regulator_agent import CoolingMechanism, InterventionIntensity
        d_strong = CoolingMechanism.compute_cooldown_duration(0.8, InterventionIntensity.STRONG)
        d_light = CoolingMechanism.compute_cooldown_duration(0.8, InterventionIntensity.LIGHT)
        assert d_strong >= d_light


# ── InvestorProtection Tests ──────────────────────────────────────


class TestInvestorProtection:
    """Test InvestorProtection class from agents.regulator_agent."""

    def test_issue_warning(self):
        from agents.regulator_agent import InvestorProtection, RegulatorState
        state = RegulatorState()
        result = InvestorProtection.issue_risk_warning(state, 0.7)
        assert result.warning_active is True
        assert result.investor_fear_factor > 0

    def test_warning_decay(self):
        from agents.regulator_agent import InvestorProtection, RegulatorState
        state = RegulatorState()
        state = InvestorProtection.issue_risk_warning(state, 0.7)
        for _ in range(InvestorProtection.WARNING_DECAY_STEPS + 1):
            state = InvestorProtection.apply_warning_decay(state)
        assert state.warning_active is False
