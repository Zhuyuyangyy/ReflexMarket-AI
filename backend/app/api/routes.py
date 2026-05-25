"""API Routes for ReflexMarket-AI"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List
from app.agents.market_simulator import MarketReflexivitySimulator, MarketNarrative

router = APIRouter(prefix="/api/v1", tags=["ReflexMarket-AI"])

simulator = MarketReflexivitySimulator()


class NarrativeSpreadRequest(BaseModel):
    content: str = Field(..., description="叙事内容")
    sentiment: float = Field(default=0.5, description="叙事情绪 -1.0~1.0")
    spread_velocity: float = Field(default=0.5, description="传播速度 0.0~1.0")
    reach: int = Field(default=100, description="初始触达人数")
    confidence: float = Field(default=0.7, description="置信度 0.0~1.0")
    stage: str = Field(default="emerging", description="阶段: emerging/spreading/dominating/peaking/collapsing")
    belief_ratio: float = Field(default=0.3, description="信念比例 0.0~1.0")
    price_impact: float = Field(default=0.02, description="价格影响系数")


class ReflexivityLoopRequest(BaseModel):
    initial_price: float = Field(default=100.0, description="初始价格")
    narrative_sentiment: float = Field(default=0.5, description="叙事情绪 -1.0~1.0")
    confidence: float = Field(default=0.7, description="初始信心水平 0.0~1.0")
    ticks: int = Field(default=10, description="仿真步数")


class ManipulationDetectRequest(BaseModel):
    narrative_content: str
    narrative_sentiment: float
    trading_volume: float
    volume_anomaly: float


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "ReflexMarket-AI", "version": "0.1.0"}


@router.post("/narrative/spread")
async def simulate_spread(req: NarrativeSpreadRequest):
    narrative = MarketNarrative(
        narrative_id=f"NARR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        content=req.content,
        sentiment=req.sentiment,
        spread_velocity=req.spread_velocity,
        reach=req.reach,
        confidence=req.confidence,
        stage=req.stage,
        belief_ratio=req.belief_ratio,
        price_impact=req.price_impact,
    )
    result = simulator.simulate_narrative_spread(narrative)
    return {"status": "success", "data": result}


@router.post("/reflexivity/loop")
async def simulate_reflexivity(req: ReflexivityLoopRequest):
    result = simulator.simulate_reflexivity_loop(
        initial_price=req.initial_price,
        narrative_sentiment=req.narrative_sentiment,
        confidence=req.confidence,
        ticks=req.ticks,
    )
    return {"status": "success", "data": result}


@router.post("/risk/manipulation")
async def detect_manipulation(req: ManipulationDetectRequest):
    narrative = MarketNarrative(
        narrative_id=f"NARR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        content=req.narrative_content,
        sentiment=req.narrative_sentiment,
        spread_velocity=0.5,
        reach=0,
        confidence=0.8,
        stage="spreading",
        belief_ratio=0.5,
        price_impact=0.05,
    )
    result = simulator.detect_manipulation_risk(narrative, req.trading_volume, req.volume_anomaly)
    return {"status": "success", "data": result}