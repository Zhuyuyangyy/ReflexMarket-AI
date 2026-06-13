#!/bin/bash
# ReflexMarket-AI 启动脚本
# 金融反身性市场仿真系统 - FastAPI后端

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  ReflexMarket-AI - 金融反身性市场仿真"
echo "  叙事传播 × 价格-信心反馈 × 风险检测"
echo "=============================================="
echo

# 虚拟环境
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

pip install -q fastapi uvicorn loguru pydantic python-dotenv 2>/dev/null

echo "[启动] 服务运行于 http://localhost:8020"
echo "[启动] API文档: http://localhost:8020/docs"
cd "$SCRIPT_DIR/backend/app"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8020 --reload