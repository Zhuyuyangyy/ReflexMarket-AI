"""ReflexMarket-AI - 金融反身性市场仿真系统主入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.api.routes import router

logger.remove()
logger.add(sys.stderr, format="<level>{time:HH:mm:ss}</level> | <level>{level}</level> | <level>{message}</level>", level="INFO")

app = FastAPI(
    title="ReflexMarket-AI",
    description="金融反身性市场仿真系统 — 叙事传播 × 价格-信心反馈 × 风险检测 × 监管干预",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ReflexMarket-AI",
        "framework": "OpenClaw + ASF-BGT + CrewAI + AgentShield V3",
        "version": "0.1.0",
        "disclaimer": "市场风险仿真 / 反身性建模 / 异常叙事传播检测 / 监管干预仿真 — 非真实市场预测",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020, log_level="info")