"""MarketReflexivitySimulator — 金融反身性市场仿真引擎"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


@dataclass
class MarketNarrative:
    narrative_id: str
    content: str
    sentiment: float  # -1.0 to 1.0
    spread_velocity: float
    reach: int
    confidence: float
    stage: str  # emerging/spreading/dominating/peaking/collaing
    belief_ratio: float  # 0.0-1.0 of agents believing
    price_impact: float  # price change driver


class MarketReflexivitySimulator:
    """
    市场反身性仿真引擎

    核心能力：
    1. 市场叙事传播仿真（社交网络扩散模型）
    2. 价格-信心反馈回路（反身性核心机制）
    3. KOL/机构情绪共振检测
    4. 泡沫/恐慌/异常传播风险识别
    5. 监管干预效果评估

    关键机制：
    - 叙事扩散：SIR/IC传播模型
    - 反身性回路：价格上涨 → 信心上升 → 资金流入 → 价格继续上涨
    - 崩溃机制：信心崩塌 → 抛售 → 价格下跌 → 恐慌
    """

    def simulate_narrative_spread(self, narrative: MarketNarrative, network_size: int = 1000) -> Dict[str, Any]:
        """
        仿真叙事在市场中的传播

        传播机制：
        - emerging: 少数KOL开始提及
        - spreading: 社交网络快速扩散
        - dominating: 成为市场主导叙事
        - peaking: 传播达到饱和
        - collapsing: 被新叙事取代或信心崩塌
        """
        stages_transitions = {
            "emerging": {"next": "spreading", "duration_ticks": 5, "spread_rate": 0.15},
            "spreading": {"next": "dominating", "duration_ticks": 8, "spread_rate": 0.45},
            "dominating": {"next": "peaking", "duration_ticks": 6, "spread_rate": 0.30},
            "peaking": {"next": "collapsing", "duration_ticks": 4, "spread_rate": 0.10},
            "collapsing": {"next": None, "duration_ticks": 3, "spread_rate": 0.05},
        }

        current_stage = narrative.stage
        total_reach = narrative.reach
        tick = 0

        history = []
        for _ in range(20):
            if current_stage is None:
                break
            transition = stages_transitions.get(current_stage, stages_transitions["peaking"])
            spread_rate = transition["spread_rate"]

            new_reach = int(total_reach * spread_rate * (1 + narrative.sentiment * 0.5))
            total_reach += new_reach

            history.append({
                "tick": tick,
                "stage": current_stage,
                "total_reach": total_reach,
                "spread_rate": spread_rate,
                "belief_ratio": min(0.99, narrative.belief_ratio + random.uniform(0.01, 0.08)),
                "price_impact": narrative.price_impact * (1 + spread_rate) * narrative.sentiment,
            })

            if tick > 0 and tick % transition["duration_ticks"] == 0:
                current_stage = transition["next"]
            tick += 1

        final_stage = history[-1]["stage"] if history else "emerging"
        final_belief = history[-1]["belief_ratio"] if history else 0.0

        return {
            "narrative_id": narrative.narrative_id,
            "network_size": network_size,
            "final_reach": total_reach,
            "final_belief_ratio": round(final_belief, 3),
            "final_stage": final_stage,
            "spread_history": history,
            "simulation_ticks": len(history),
        }

    def simulate_reflexivity_loop(self, initial_price: float, narrative_sentiment: float, confidence: float, ticks: int = 10) -> Dict[str, Any]:
        """
        仿真价格-信心反身性反馈回路

        核心回路：
        P(t+1) = P(t) * (1 + sentiment * belief_ratio * reflexivity_factor)
        belief_ratio(t+1) = belief_ratio(t) + price_change * learning_rate

        关键参数：
        - sentiment: 叙事情绪（正面=1.0, 负面=-1.0）
        - confidence: 初始信心水平（0-1）
        - reflexivity_factor: 反身性强度系数
        """
        reflexivity_factor = 0.3 + confidence * 0.5
        price = initial_price
        belief_ratio = confidence
        price_history = []
        belief_history = []

        for t in range(ticks):
            price_change = price * narrative_sentiment * belief_ratio * reflexivity_factor
            price += price_change
            belief_ratio += price_change / price * 0.2 * narrative_sentiment
            belief_ratio = max(0.0, min(0.99, belief_ratio))

            price_history.append(round(price, 2))
            belief_history.append(round(belief_ratio, 3))

        final_return = (price - initial_price) / initial_price

        # 判断市场状态
        if final_return > 0.3:
            market_state = "bubble_forming"
            risk_level = "HIGH"
        elif final_return < -0.2:
            market_state = "panic_selling"
            risk_level = "CRITICAL"
        elif abs(final_return) < 0.1:
            market_state = "stable"
            risk_level = "LOW"
        else:
            market_state = "normal_fluctuation"
            risk_level = "MEDIUM"

        return {
            "initial_price": initial_price,
            "final_price": round(price, 2),
            "total_return_pct": round(final_return * 100, 2),
            "market_state": market_state,
            "risk_level": risk_level,
            "price_history": price_history,
            "belief_history": belief_history,
            "narrative_sentiment": narrative_sentiment,
            "confidence": confidence,
            "reflexivity_factor": reflexivity_factor,
        }

    def detect_manipulation_risk(self, narrative: MarketNarrative, trading_volume: float, volume_anomaly: float) -> Dict[str, Any]:
        """
        检测市场操纵风险

        操纵模式：
        1. 虚假信息拉抬（Pump & Dump）
        2. 轧空逼仓（Squeeze）
        3. 虚假成交（Wash Trading）
        4. 层压式推广（Pump Chain）
        """
        risk_factors = []

        if volume_anomaly > 3.0:
            risk_factors.append({"factor": "volume_spike", "score": min(1.0, volume_anomaly / 5), "description": "成交量异常激增，可能存在对敲或操纵"})

        if abs(narrative.sentiment) > 0.8 and narrative.spread_velocity > 0.7:
            risk_factors.append({"factor": "coordinated_spread", "score": 0.85, "description": "极端情绪+快速扩散，疑似协调行动"})

        if narrative.confidence > 0.9 and narrative.belief_ratio < 0.3:
            risk_factors.append({"factor": "confidence_belief_gap", "score": 0.78, "description": "高置信度但低信念比例，疑似信息不对称"})

        total_risk = sum(f["score"] for f in risk_factors) / len(risk_factors) if risk_factors else 0.0

        return {
            "narrative_id": narrative.narrative_id,
            "trading_volume": trading_volume,
            "volume_anomaly_ratio": volume_anomaly,
            "risk_factors": risk_factors,
            "total_risk_score": round(total_risk, 3),
            "risk_level": "HIGH" if total_risk > 0.7 else ("MEDIUM" if total_risk > 0.4 else "LOW"),
            "recommended_action": self._get_regulation_action(total_risk),
        }

    def _get_regulation_action(self, risk_score: float) -> str:
        if risk_score > 0.7:
            return "启动调查程序，密切监控相关账户交易行为，必要时暂停相关标的交易"
        elif risk_score > 0.4:
            return "加强信息披露要求，约谈相关市场参与者"
        return "持续监控，不采取干预行动"

    def to_dict(self, narrative: MarketNarrative) -> Dict[str, Any]:
        return {"narrative_id": narrative.narrative_id, "content": narrative.content, "sentiment": narrative.sentiment, "spread_velocity": narrative.spread_velocity, "reach": narrative.reach, "confidence": narrative.confidence, "stage": narrative.stage, "belief_ratio": narrative.belief_ratio, "price_impact": narrative.price_impact}