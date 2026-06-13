"""
ReflexMarket-AI V0.5: RegulatorAgent
监管干预Agent - 异常叙事传播抑制

4个干预动作:
- narrative_throttle: 叙事限流（降低NarrativeAgent生成速率/强度）
- kol_downweight: KOL降权（降低高信任KOL的影响力）
- risk_warning: 风险提示（向市场发出风险信号）
- trading_cooldown: 交易冷却（减少散户短期交易频率）

接入 ManipulationRiskAgent 输出，风险阈值触发干预决策。
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum


class InterventionAction(Enum):
    NARRATIVE_THROTTLE = "narrative_throttle"
    KOL_DOWNWEIGHT = "kol_downweight"
    RISK_WARNING = "risk_warning"
    TRADING_COOLDOWN = "trading_cooldown"
    NO_ACTION = "no_action"


class InterventionIntensity(IntEnum):
    NONE = 0
    LIGHT = 1    # narrative_throttle + risk_warning
    MODERATE = 2 # + kol_downweight
    STRONG = 3   # + trading_cooldown


@dataclass
class InterventionEffect:
    """干预效果记录"""
    step: int
    action: InterventionAction
    intensity: InterventionIntensity
    risk_reduction: float = 0.0
    narrative_suppression: float = 0.0
    fomo_reduction: float = 0.0
    price_volatility_change: float = 0.0
    bubble_risk_delta: float = 0.0


@dataclass
class RegulatorState:
    """监管状态机"""
    active_interventions: List[InterventionAction] = field(default_factory=list)
    intervention_steps_remaining: Dict[str, int] = field(default_factory=dict)
    cooldown_active: bool = False
    warning_active: bool = False
    kol_penalty: float = 1.0  # KOL影响力惩罚系数
    narrative_cap: float = 1.0  # 叙事生成上限
    trading_slowdown: float = 0.0  # 交易频率降低


class InterventionPolicy:
    """
    干预策略引擎 - 根据风险等级选择干预强度

    Risk Level -> Intervention Intensity:
    - risk < 0.3: NONE
    - 0.3 <= risk < 0.5: LIGHT
    - 0.5 <= risk < 0.7: MODERATE
    - risk >= 0.7: STRONG
    """

    RISK_LIGHT_THRESHOLD = 0.3
    RISK_MODERATE_THRESHOLD = 0.5
    RISK_STRONG_THRESHOLD = 0.7

    @classmethod
    def select_intensity(cls, risk_score: float, market_state: Dict) -> InterventionIntensity:
        """根据风险评分和市场状态选择干预强度"""
        if risk_score < cls.RISK_LIGHT_THRESHOLD:
            return InterventionIntensity.NONE
        elif risk_score < cls.RISK_MODERATE_THRESHOLD:
            return InterventionIntensity.LIGHT
        elif risk_score < cls.RISK_STRONG_THRESHOLD:
            return InterventionIntensity.MODERATE
        else:
            return InterventionIntensity.STRONG

    @classmethod
    def get_actions_for_intensity(cls, intensity: InterventionIntensity) -> List[InterventionAction]:
        """获取对应强度的干预动作组合"""
        if intensity == InterventionIntensity.NONE:
            return [InterventionAction.NO_ACTION]
        elif intensity == InterventionIntensity.LIGHT:
            return [InterventionAction.NARRATIVE_THROTTLE, InterventionAction.RISK_WARNING]
        elif intensity == InterventionIntensity.MODERATE:
            return [
                InterventionAction.NARRATIVE_THROTTLE,
                InterventionAction.KOL_DOWNWEIGHT,
                InterventionAction.RISK_WARNING
            ]
        else:  # STRONG
            return [
                InterventionAction.NARRATIVE_THROTTLE,
                InterventionAction.KOL_DOWNWEIGHT,
                InterventionAction.RISK_WARNING,
                InterventionAction.TRADING_COOLDOWN
            ]


class CoolingMechanism:
    """
    交易冷却机制 - 模拟交易所临时提价、涨跌停板、交易限制等
    """
    BASE_COOLDOWN_STEPS = 5
    MAX_COOLDOWN_STEPS = 15

    @classmethod
    def compute_cooldown_duration(cls, risk_score: float, intensity: InterventionIntensity) -> int:
        """计算冷却持续步数"""
        base = int(cls.BASE_COOLDOWN_STEPS * risk_score)
        if intensity == InterventionIntensity.STRONG:
            base = int(base * 1.5)
        return min(base, cls.MAX_COOLDOWN_STEPS)

    @classmethod
    def apply_trading_slowdown(cls, state: RegulatorState, risk_score: float, duration: int) -> RegulatorState:
        """应用交易放缓效果"""
        state.cooldown_active = True
        state.trading_slowdown = min(risk_score * 0.8, 0.8)  # 最多降低80%交易频率
        state.intervention_steps_remaining[InterventionAction.TRADING_COOLDOWN.value] = duration
        return state


class InvestorProtection:
    """
    投资者保护机制 - 模拟风险提示、冷静期、风险教育等
    """
    WARNING_DECAY_STEPS = 8

    @classmethod
    def issue_risk_warning(cls, state: RegulatorState, risk_score: float) -> RegulatorState:
        """发出风险警告，影响投资者行为"""
        state.warning_active = True
        state.warning_steps_remaining = cls.WARNING_DECAY_STEPS
        state.investor_fear_factor = min(risk_score * 1.5, 1.0)
        return state

    @classmethod
    def apply_warning_decay(cls, state: RegulatorState) -> RegulatorState:
        """风险警告自然衰减"""
        if hasattr(state, 'warning_steps_remaining') and state.warning_steps_remaining > 0:
            state.warning_steps_remaining -= 1
            if state.warning_steps_remaining == 0:
                state.warning_active = False
                state.investor_fear_factor = 0.0
        return state


class RegulatorAgent:
    """
    监管Agent - 根据ManipulationRiskAgent的风险检测结果执行干预

    核心逻辑:
    1. 接收 risk_score 和市场状态
    2. InterventionPolicy 根据风险等级选择干预强度
    3. 执行对应干预动作，修改市场状态
    4. 记录干预效果
    5. 冷却后逐步退出干预
    """

    def __init__(self, name: str = "RegulatorAgent"):
        self.name = name
        self.state = RegulatorState()
        self.policy = InterventionPolicy()
        self.cooling = CoolingMechanism()
        self.investor_protection = InvestorProtection()
        self.intervention_history: List[InterventionEffect] = []
        self.current_intensity = InterventionIntensity.NONE

    def reset(self):
        """重置监管状态"""
        self.state = RegulatorState()
        self.current_intensity = InterventionIntensity.NONE

    def step(self, risk_score: float, market_state: Dict,
             manipulation_flags: Dict,
             narrative_agent_ref=None,
             kol_agents: List = None) -> Dict:
        """
        执行监管干预

        Args:
            risk_score: ManipulationRiskAgent输出的风险评分
            market_state: 市场状态（price, bubble_risk, retail_fomo, etc.）
            manipulation_flags: ManipulationRiskAgent的标志位
            narrative_agent_ref: NarrativeAgent引用（用于限流）
            kol_agents: KOL Agent列表（用于降权）

        Returns:
            intervention_report: 干预效果报告
        """
        # 1. 检查冷却状态
        self._check_cooldown_expiry()

        # 2. 投资者警告衰减
        self.state = self.investor_protection.apply_warning_decay(self.state)

        # 3. 根据风险评分选择干预强度
        new_intensity = self.policy.select_intensity(risk_score, market_state)

        # 4. 如果风险降低，尝试降级干预
        if new_intensity < self.current_intensity:
            self._escalate_or_deescalate(new_intensity)
            self.current_intensity = new_intensity

        # 5. 执行干预动作
        effects = []
        actions = self.policy.get_actions_for_intensity(new_intensity)

        for action in actions:
            if action == InterventionAction.NO_ACTION:
                continue
            effect = self._apply_action(action, risk_score, market_state)
            effects.append(effect)

        # 6. 更新KOL降权
        if self.state.kol_penalty < 1.0 and kol_agents:
            for kol in kol_agents:
                if hasattr(kol, 'influence_weight'):
                    kol.influence_weight *= self.state.kol_penalty

        # 7. 更新叙事限流
        if self.state.narrative_cap < 1.0 and narrative_agent_ref:
            if hasattr(narrative_agent_ref, 'generation_rate'):
                narrative_agent_ref.generation_rate *= self.state.narrative_cap

        # 8. 记录本步干预效果
        if effects:
            avg_effect = self._aggregate_effects(effects)
            avg_effect.step = market_state.get('step', 0)
            self.intervention_history.append(avg_effect)

        return {
            'intensity': new_intensity,
            'actions': [a.value for a in actions],
            'state_snapshot': {
                'kol_penalty': self.state.kol_penalty,
                'narrative_cap': self.state.narrative_cap,
                'trading_slowdown': self.state.trading_slowdown,
                'warning_active': self.state.warning_active,
                'cooldown_active': self.state.cooldown_active
            },
            'effects': [e.__dict__ for e in effects] if effects else []
        }

    def _apply_action(self, action: InterventionAction, risk_score: float,
                      market_state: Dict) -> InterventionEffect:
        """执行单个干预动作并计算效果"""
        effect = InterventionEffect(
            step=market_state.get('step', 0),
            action=action,
            intensity=self.current_intensity
        )

        if action == InterventionAction.NARRATIVE_THROTTLE:
            # 叙事限流：降低叙事生成速率和传播强度
            self.state.narrative_cap = max(1.0 - risk_score * 0.5, 0.3)
            effect.narrative_suppression = risk_score * 0.6

        elif action == InterventionAction.KOL_DOWNWEIGHT:
            # KOL降权：降低高信任KOL的影响力
            self.state.kol_penalty = max(1.0 - risk_score * 0.7, 0.2)
            effect.risk_reduction = risk_score * 0.4

        elif action == InterventionAction.RISK_WARNING:
            # 风险提示：发出市场风险警告
            self.state = self.investor_protection.issue_risk_warning(self.state, risk_score)
            effect.risk_reduction = risk_score * 0.25

        elif action == InterventionAction.TRADING_COOLDOWN:
            # 交易冷却：减少短期交易频率
            duration = self.cooling.compute_cooldown_duration(risk_score, self.current_intensity)
            self.state = self.cooling.apply_trading_slowdown(self.state, risk_score, duration)
            effect.risk_reduction = risk_score * 0.5
            effect.fomo_reduction = risk_score * 0.35

        return effect

    def _check_cooldown_expiry(self):
        """检查干预冷却是否过期"""
        expired_actions = []
        for action_str, steps in self.state.intervention_steps_remaining.items():
            if steps <= 0:
                expired_actions.append(action_str)

        for action_str in expired_actions:
            del self.state.intervention_steps_remaining[action_str]

            if action_str == InterventionAction.TRADING_COOLDOWN.value:
                self.state.cooldown_active = False
                self.state.trading_slowdown = 0.0
            elif action_str == InterventionAction.NARRATIVE_THROTTLE.value:
                self.state.narrative_cap = 1.0
            elif action_str == InterventionAction.KOL_DOWNWEIGHT.value:
                self.state.kol_penalty = 1.0

        # 步减所有干预持续时间
        for k in self.state.intervention_steps_remaining:
            self.state.intervention_steps_remaining[k] = max(0, self.state.intervention_steps_remaining[k] - 1)

    def _escalate_or_deescalate(self, new_intensity: InterventionIntensity):
        """调整干预强度"""
        if new_intensity > self.current_intensity:
            # 升级干预：新动作逐步加入
            pass
        elif new_intensity < self.current_intensity:
            # 降级干预：冷却旧动作
            pass

    def _aggregate_effects(self, effects: List[InterventionEffect]) -> InterventionEffect:
        """聚合多个动作的效果"""
        if not effects:
            return InterventionEffect(step=0, action=InterventionAction.NO_ACTION,
                                      intensity=InterventionIntensity.NONE)

        total_risk = sum(e.risk_reduction for e in effects)
        total_narr = sum(e.narrative_suppression for e in effects)
        total_fomo = sum(e.fomo_reduction for e in effects)

        return InterventionEffect(
            step=effects[0].step,
            action=InterventionAction.NO_ACTION,
            intensity=self.current_intensity,
            risk_reduction=total_risk / len(effects),
            narrative_suppression=total_narr / len(effects),
            fomo_reduction=total_fomo / len(effects)
        )

    def get_intervention_summary(self) -> Dict:
        """获取干预历史摘要"""
        if not self.intervention_history:
            return {'total_interventions': 0, 'avg_risk_reduction': 0.0}

        return {
            'total_interventions': len(self.intervention_history),
            'avg_risk_reduction': np.mean([e.risk_reduction for e in self.intervention_history]),
            'avg_narrative_suppression': np.mean([e.narrative_suppression for e in self.intervention_history]),
            'avg_fomo_reduction': np.mean([e.fomo_reduction for e in self.intervention_history]),
            'actions_taken': list(set(e.action.value for e in self.intervention_history))
        }