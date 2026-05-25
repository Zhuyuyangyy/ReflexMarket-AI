"""
Market Regulation Module
Regulator Agent that can intervene in market to prevent bubbles, panic, or manipulation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class InterventionType(Enum):
    NARRATIVE_THROTTLE = "narrative_throttle"      # Suppress alarming narratives
    KOL_DOWNWEIGHT = "kol_downweight"              # Reduce influential KOL's impact
    TRADING_COOLDOWN = "trading_cooldown"          # Slow down trading activity
    RISK_WARNING = "risk_warning"                 # Issue public risk warnings
    MARGIN_ADJUSTMENT = "margin_adjustment"       # Increase margin requirements
    LIQUIDITY_INJECTION = "liquidity_injection"   # Inject liquidity to calm market


@dataclass
class InterventionResult:
    """Result of a regulatory intervention"""
    intervention_type: str
    cost: float           # Regulatory cost (resources, credibility)
    effectiveness: float  # 0-1, how well it worked
    market_response: Dict
    side_effects: List[str]


@dataclass
class InterventionStrategy:
    """A defined intervention strategy"""
    name: str
    interventions: List[InterventionType]
    threshold_bubble_risk: float    # Activate when bubble_risk > this
    threshold_panic_risk: float     # Activate when panic_risk > this
    intensity: float               # 0-1, how aggressive


class RegulatorAgent:
    """
    Market Regulator Agent
    
    Can observe market state and apply interventions to:
    - Prevent bubble formation
    - Stop panic spreading
    - Detect and suppress manipulation
    
    Interventions have costs and effectiveness metrics.
    """
    
    def __init__(self, budget: float = 100.0, credibility: float = 0.8):
        self.budget = budget
        self.credibility = credibility
        self.intervention_history: List[InterventionResult] = []
        self.active_interventions: Dict[str, float] = {}  # type -> remaining_effect
    
    def observe_market(self, market_state: Dict) -> Dict:
        """Observe market and assess risk levels"""
        bubble_risk = market_state.get("bubble_risk", 0)
        panic_risk = market_state.get("panic_risk", 0)
        manipulation_risk = market_state.get("manipulation_risk", 0)
        volatility = market_state.get("volatility", 0)
        
        return {
            "bubble_risk": round(bubble_risk, 4),
            "panic_risk": round(panic_risk, 4),
            "manipulation_risk": round(manipulation_risk, 4),
            "overall_risk": round(max(bubble_risk, panic_risk, manipulation_risk), 4),
            "recommendation": self._get_recommendation(bubble_risk, panic_risk, manipulation_risk),
            "budget_remaining": round(self.budget, 2),
            "credibility": round(self.credibility, 3)
        }
    
    def _get_recommendation(self, bubble_risk: float, panic_risk: float, manipulation_risk: float) -> str:
        if bubble_risk > 0.7:
            return "INTERVENE_BUBBLE"
        elif panic_risk > 0.6:
            return "INTERVENE_PANIC"
        elif manipulation_risk > 0.5:
            return "INTERVENE_MANIPULATION"
        elif bubble_risk > 0.4 or panic_risk > 0.4:
            return "WATCH_AND_PREPARE"
        else:
            return "NO_ACTION"
    
    def propose_intervention(self, market_state: Dict, strategy: InterventionStrategy = None) -> Dict:
        """Propose intervention based on market state"""
        if strategy is None:
            # Default: moderate intervention
            strategy = InterventionStrategy(
                name="moderate_response",
                interventions=[InterventionType.RISK_WARNING, InterventionType.KOL_DOWNWEIGHT],
                threshold_bubble_risk=0.5,
                threshold_panic_risk=0.4,
                intensity=0.5
            )
        
        bubble_risk = market_state.get("bubble_risk", 0)
        panic_risk = market_state.get("panic_risk", 0)
        
        # Check if intervention is warranted
        if bubble_risk < strategy.threshold_bubble_risk and panic_risk < strategy.threshold_panic_risk:
            return {"action": "no_intervention", "reason": "risk_below_threshold"}
        
        proposed = []
        total_cost = 0
        
        for intervention in strategy.interventions:
            cost = self._calculate_cost(intervention, strategy.intensity)
            if total_cost + cost <= self.budget:
                proposed.append({
                    "type": intervention.value,
                    "cost": round(cost, 2),
                    "expected_effectiveness": round(self._estimate_effectiveness(intervention, market_state), 3)
                })
                total_cost += cost
        
        return {
            "action": "intervene",
            "strategy": strategy.name,
            "intensity": strategy.intensity,
            "proposed_interventions": proposed,
            "total_cost": round(total_cost, 2),
            "budget_after": round(self.budget - total_cost, 2),
            "risk_targeted": "bubble" if bubble_risk >= panic_risk else "panic"
        }
    
    def apply_intervention(self, intervention_type: InterventionType, intensity: float = 0.5) -> InterventionResult:
        """Apply an intervention and return result"""
        cost = self._calculate_cost(intervention_type, intensity)
        
        if cost > self.budget:
            return InterventionResult(
                intervention_type=intervention_type.value,
                cost=0,
                effectiveness=0,
                market_response={"rejected": "insufficient_budget"},
                side_effects=["Budget insufficient"]
            )
        
        self.budget -= cost
        
        # Simulate effectiveness
        effectiveness = self._estimate_effectiveness(intervention_type, {"intensity": intensity})
        
        # Apply side effects
        side_effects = self._get_side_effects(intervention_type, intensity)
        
        # Credibility impact
        if effectiveness < 0.3 and intensity > 0.6:
            self.credibility = max(0.3, self.credibility - 0.1)
        
        result = InterventionResult(
            intervention_type=intervention_type.value,
            cost=round(cost, 3),
            effectiveness=round(effectiveness, 3),
            market_response=self._simulate_market_response(intervention_type, effectiveness),
            side_effects=side_effects
        )
        
        self.intervention_history.append(result)
        return result
    
    def _calculate_cost(self, intervention_type: InterventionType, intensity: float) -> float:
        """Calculate cost of intervention"""
        base_costs = {
            InterventionType.NARRATIVE_THROTTLE: 5.0,
            InterventionType.KOL_DOWNWEIGHT: 8.0,
            InterventionType.TRADING_COOLDOWN: 15.0,
            InterventionType.RISK_WARNING: 3.0,
            InterventionType.MARGIN_ADJUSTMENT: 12.0,
            InterventionType.LIQUIDITY_INJECTION: 20.0,
        }
        return base_costs.get(intervention_type, 5.0) * intensity
    
    def _estimate_effectiveness(self, intervention_type: InterventionType, market_state: Dict) -> float:
        """Estimate how effective an intervention will be"""
        base_effectiveness = {
            InterventionType.NARRATIVE_THROTTLE: 0.6,
            InterventionType.KOL_DOWNWEIGHT: 0.55,
            InterventionType.TRADING_COOLDOWN: 0.7,
            InterventionType.RISK_WARNING: 0.4,
            InterventionType.MARGIN_ADJUSTMENT: 0.65,
            InterventionType.LIQUIDITY_INJECTION: 0.75,
        }
        base = base_effectiveness.get(intervention_type, 0.5)
        intensity = market_state.get("intensity", 0.5)
        return min(1.0, base * intensity * self.credibility)
    
    def _get_side_effects(self, intervention_type: InterventionType, intensity: float) -> List[str]:
        """Identify side effects of intervention"""
        side_effects_map = {
            InterventionType.NARRATIVE_THROTTLE: ["Reduced market efficiency", "Information asymmetry"],
            InterventionType.KOL_DOWNWEIGHT: ["Reduced price discovery", "Market maker displacement"],
            InterventionType.TRADING_COOLDOWN: ["Liquidity reduction", "Spread widening"],
            InterventionType.RISK_WARNING: ["Investor hesitation", "Volume reduction"],
            InterventionType.MARGIN_ADJUSTMENT: ["Leverage reduction", "Forced liquidations"],
            InterventionType.LIQUIDITY_INJECTION: ["Inflation risk", "moral_hazard"],
        }
        base_effects = side_effects_map.get(intervention_type, [])
        return [e for e in base_effects if random.random() < intensity]
    
    def _simulate_market_response(self, intervention_type: InterventionType, effectiveness: float) -> Dict:
        """Simulate immediate market response to intervention"""
        price_impact = {
            InterventionType.NARRATIVE_THROTTLE: 0.02 * effectiveness,
            InterventionType.KOL_DOWNWEIGHT: -0.01 * effectiveness,
            InterventionType.TRADING_COOLDOWN: -0.03 * effectiveness,
            InterventionType.RISK_WARNING: -0.02 * effectiveness,
            InterventionType.MARGIN_ADJUSTMENT: -0.04 * effectiveness,
            InterventionType.LIQUIDITY_INJECTION: 0.05 * effectiveness,
        }
        
        volatility_change = {
            InterventionType.NARRATIVE_THROTTLE: -0.1 * effectiveness,
            InterventionType.KOL_DOWNWEIGHT: -0.15 * effectiveness,
            InterventionType.TRADING_COOLDOWN: -0.25 * effectiveness,
            InterventionType.RISK_WARNING: 0.05 * effectiveness,
            InterventionType.MARGIN_ADJUSTMENT: 0.1 * effectiveness,
            InterventionType.LIQUIDITY_INJECTION: -0.2 * effectiveness,
        }
        
        return {
            "price_change_pct": round(price_impact.get(intervention_type, 0), 4),
            "volatility_change": round(volatility_change.get(intervention_type, 0), 4),
            "volume_change_pct": round(-0.1 * effectiveness, 4),
        }
    
    def compare_strategies(self, market_state: Dict) -> Dict:
        """Compare different intervention strategies"""
        strategies = [
            InterventionStrategy("baseline", [], 0.9, 0.9, 0.0),
            InterventionStrategy("light_touch", [InterventionType.RISK_WARNING], 0.5, 0.4, 0.3),
            InterventionStrategy("moderate", [InterventionType.RISK_WARNING, InterventionType.KOL_DOWNWEIGHT], 0.4, 0.3, 0.6),
            InterventionStrategy("strict", [InterventionType.MARGIN_ADJUSTMENT, InterventionType.TRADING_COOLDOWN, InterventionType.NARRATIVE_THROTTLE], 0.3, 0.2, 0.9),
        ]
        
        results = []
        for strategy in strategies:
            proposed = self.propose_intervention(market_state, strategy)
            results.append({
                "strategy": strategy.name,
                "proposed": proposed,
                "risk_reduction_expected": round(strategy.intensity * 0.4, 3)
            })
        
        return {"strategy_comparison": results}
    
    def get_intervention_stats(self) -> Dict:
        """Get statistics about intervention history"""
        if not self.intervention_history:
            return {"total_interventions": 0, "avg_effectiveness": 0}
        
        return {
            "total_interventions": len(self.intervention_history),
            "avg_effectiveness": round(sum(r.effectiveness for r in self.intervention_history) / len(self.intervention_history), 3),
            "total_cost": round(sum(r.cost for r in self.intervention_history), 2),
            "budget_remaining": round(self.budget, 2),
            "credibility": round(self.credibility, 3),
            "by_type": {
                it.value: sum(1 for r in self.intervention_history if r.intervention_type == it.value)
                for it in InterventionType
            }
        }