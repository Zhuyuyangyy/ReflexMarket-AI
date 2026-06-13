# ReflexMarket-AI

> Narrative-Driven Financial Reflexivity Multi-Agent Simulation Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/ReflexMarket-AI/ReflexMarket-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/ReflexMarket-AI/ReflexMarket-AI/actions/workflows/ci.yml)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![Status: V1.0](https://img.shields.io/badge/status-V1.0-orange.svg)](#)

ReflexMarket-AI provides a REST API and interactive visualization layer for simulating financial reflexivity dynamics. It models how narratives propagate through social networks, influence investor beliefs and trading behavior, generate capital flows, and feed back into prices -- producing emergent market phenomena such as bubbles, panic cascades, and manipulation risks.

This is a market risk simulation and reflexivity modeling tool. It does not predict real market prices and is not a quantitative trading system.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [Testing](#testing)
- [Benchmark Suite](#benchmark-suite)
- [Research](#research)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

ReflexMarket-AI implements the Soros reflexivity feedback loop as a REST API service. The core simulation chain is:

```
Narrative --> Trust --> Belief --> Emotion --> Behavior --> Capital --> Price --> Feedback
                                                                   |
                                                         Risk Detection (V0.4)
                                                                   |
                                                         Governance (V0.5)
```

The system exposes three primary simulation endpoints:

1. **Narrative Spread Simulation**: Models how a narrative event propagates through a multi-tier KOL social network, shifting beliefs and generating trading signals.
2. **Reflexivity Loop Simulation**: Runs a closed-loop price-belief feedback simulation over multiple ticks.
3. **Manipulation Risk Detection**: Analyzes narrative and volume patterns for signs of coordinated pump-and-dump activity.

---

## Key Features

### Narrative Propagation Engine

Models narrative diffusion through a five-stage lifecycle: emerging -> spreading -> dominating -> peaking -> collapsing. Uses SIR/IC-inspired propagation dynamics with configurable spread velocity, reach, and confidence parameters.

### KOL Social Network

Three network topologies for modeling information diffusion:

| Topology | Structure | Use Case |
|---|---|---|
| STAR | Single super-KOL hub | Centralized media influence |
| DISTRIBUTED | Multiple mid-tier hubs | Multi-channel information spread |
| VIRAL | Decentralized peer-to-peer | Organic viral propagation |

### Price-Belief Reflexivity Loop

Implements the core feedback equation:

```
P(t+1) = P(t) * (1 + sentiment * belief * reflexivity_factor)
```

where sentiment and belief co-evolve through the narrative-causal chain, producing endogenous price dynamics.

### Manipulation Risk Detection

Multi-pattern detection for market manipulation:

- **Pump and Dump**: Abnormal volume spikes combined with extreme sentiment
- **Coordinated Spread**: Synchronized narrative propagation across KOL tiers
- **Information Asymmetry**: Unusual narrative concentration in specific network nodes

### Regulatory Intervention Simulation

Two regulatory agent implementations:

1. **Strategy-Comparison Regulator**: Evaluates intervention strategies with budget, reputation, and side-effect modeling.
2. **State-Machine Regulator**: Implements intervention logic with cooldown mechanisms and investor protection rules.

### Interactive Visualization Dashboard

A browser-based dashboard (Chart.js) for real-time simulation monitoring with configurable parameters and result visualization.

---

## Architecture

```
ReflexMarket-AI/
+-- backend/                       FastAPI application server
|   +-- app/
|       +-- main.py                API entry point (port 8020)
|       +-- api/routes.py          REST endpoint definitions
|       +-- agents/
|           +-- market_simulator.py  Core reflexivity simulation engine
|
+-- src/                           Simulation modules
|   +-- agents/
|   |   +-- regulator_agent.py     Strategy-comparison regulator
|   +-- social/
|   |   +-- kol_network.py         KOL social network (3 topologies)
|   +-- intervention/
|       +-- regulator_agent.py     State-machine intervention engine
|
+-- frontend/
|   +-- index.html                 Interactive visualization dashboard
|
+-- experiments/                   Benchmark and test scripts
|   +-- run_benchmark.py           5-scenario benchmark suite
|   +-- kol_test_script.py         KOL network validation
|
+-- tests/
|   +-- test_smoke.py              Integration smoke tests
|
+-- docs/
|   +-- INNOVATION.md              Technical innovation documentation
|   +-- API.md                     Detailed API documentation
|   +-- ARCHITECTURE.md            Architecture deep-dive
|
+-- Dockerfile                     Container image definition
+-- docker-compose.yml             Multi-service orchestration
+-- .github/workflows/ci.yml       CI/CD pipeline
```

### Core Simulation Flow

```
                   +-----------+
                   | Narrative |
                   | Injection |
                   +-----+-----+
                         |
                   +-----v-----+
                   |    KOL    |
                   |  Network  |
                   | Propagate |
                   +-----+-----+
                         |
                   +-----v-----+
                   |  Belief   |
                   |  Update   |
                   +-----+-----+
                         |
                   +-----v-----+
                   |  Emotion  |
                   |  Update   |
                   +-----+-----+
                         |
                   +-----v-----+       +----------------+
                   | Behavior  |------>| Risk Detection |
                   | Decision  |       | (Manipulation) |
                   +-----+-----+       +-------+--------+
                         |                     |
                   +-----v-----+       +------v---------+
                   |  Capital  |       |   Governance   |
                   |   Flow    |       | (Intervention) |
                   +-----+-----+       +----------------+
                         |
                   +-----v-----+
                   |   Price   |-------+
                   |  Update   |       |
                   +-----------+       |
                         ^             |
                         +---Feedback--+
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| API Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic v2 |
| Logging | Loguru |
| Numerical Computing | NumPy |
| Frontend | HTML + JavaScript + Chart.js |
| Testing | Pytest + Coverage |
| Linting | Ruff |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Quick Start

### Prerequisites

- Python 3.10 or later
- pip

### Installation

```bash
git clone <repo-url>
cd ReflexMarket-AI
pip install -r requirements.txt
```

### Start the Backend

```bash
# Option 1: Using the startup script
bash start.sh

# Option 2: Direct run
cd backend/app
python -m uvicorn main:app --host 0.0.0.0 --port 8020 --reload
```

Once started:
- API service: `http://localhost:8020`
- Swagger docs: `http://localhost:8020/docs`
- Health check: `http://localhost:8020/health`

### Open the Visualization Dashboard

Open `frontend/index.html` in a browser for the interactive simulation dashboard.

---

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t reflexmarket-ai .

# Run the container
docker run -p 8020:8020 reflexmarket-ai
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## API Reference

### Health Check

```
GET /health
GET /api/v1/health
```

Returns service status, version, and framework information.

### Narrative Spread Simulation

```
POST /api/v1/narrative/spread
```

**Request Body:**

| Field | Type | Description |
|---|---|---|
| content | string | Narrative text content |
| sentiment | float | Sentiment score (-1.0 to 1.0) |
| spread_velocity | float | Propagation speed (0.0 to 1.0) |
| reach | int | Number of agents reached |
| confidence | float | Narrative credibility (0.0 to 1.0) |
| stage | string | Lifecycle stage (emerging/spreading/dominating/peaking/collapsing) |
| belief_ratio | float | Fraction of agents adopting the narrative |
| price_impact | float | Expected price impact magnitude |

**Example:**

```bash
curl -X POST http://localhost:8020/api/v1/narrative/spread \
  -H "Content-Type: application/json" \
  -d '{
    "content": "BTC to the moon",
    "sentiment": 0.8,
    "spread_velocity": 0.6,
    "reach": 500,
    "confidence": 0.75,
    "stage": "emerging",
    "belief_ratio": 0.3,
    "price_impact": 0.05
  }'
```

### Reflexivity Loop Simulation

```
POST /api/v1/reflexivity/loop
```

**Request Body:**

| Field | Type | Description |
|---|---|---|
| initial_price | float | Starting price |
| narrative_sentiment | float | Narrative direction and strength |
| confidence | float | Initial confidence level |
| ticks | int | Number of simulation steps |

**Example:**

```bash
curl -X POST http://localhost:8020/api/v1/reflexivity/loop \
  -H "Content-Type: application/json" \
  -d '{
    "initial_price": 100.0,
    "narrative_sentiment": 0.8,
    "confidence": 0.7,
    "ticks": 20
  }'
```

### Manipulation Risk Detection

```
POST /api/v1/risk/manipulation
```

**Request Body:**

| Field | Type | Description |
|---|---|---|
| narrative_content | string | Narrative text to analyze |
| narrative_sentiment | float | Sentiment extremity |
| trading_volume | float | Observed trading volume |
| volume_anomaly | float | Volume deviation from baseline |

**Example:**

```bash
curl -X POST http://localhost:8020/api/v1/risk/manipulation \
  -H "Content-Type: application/json" \
  -d '{
    "narrative_content": "Pump this coin to the moon!",
    "narrative_sentiment": 0.95,
    "trading_volume": 50000,
    "volume_anomaly": 4.5
  }'
```

---

## Project Structure

```
ReflexMarket-AI/
+-- backend/
|   +-- app/
|       +-- main.py                     FastAPI entry point (port 8020)
|       +-- api/
|       |   +-- routes.py               API route definitions
|       |   +-- __init__.py
|       +-- agents/
|           +-- market_simulator.py      Core reflexivity simulation engine
|           +-- __init__.py
|
+-- src/
|   +-- agents/
|   |   +-- regulator_agent.py          Strategy-comparison regulator
|   +-- social/
|   |   +-- kol_network.py              KOL social network simulator
|   +-- intervention/
|       +-- regulator_agent.py          State-machine intervention engine
|       +-- __init__.py
|
+-- frontend/
|   +-- index.html                      Interactive visualization dashboard
|
+-- experiments/
|   +-- run_benchmark.py                5-scenario benchmark suite
|   +-- kol_test_script.py             KOL network test script
|
+-- tests/
|   +-- test_smoke.py                   Integration smoke tests
|   +-- test_market_simulator.py        Unit tests for market simulator
|   +-- test_kol_network.py             Unit tests for KOL network
|   +-- test_regulator_agents.py        Unit tests for regulator agents
|   +-- test_api_routes.py              Unit tests for API endpoints
|   +-- test_integration.py             End-to-end integration tests
|   +-- __init__.py
|
+-- docs/
|   +-- INNOVATION.md                   Innovation documentation
|   +-- API.md                          API documentation
|   +-- ARCHITECTURE.md                 Architecture documentation
|
+-- Dockerfile                          Container image definition
+-- docker-compose.yml                  Multi-service orchestration
+-- .github/workflows/ci.yml            CI/CD pipeline
+-- start.sh                            Startup script
+-- requirements.txt                    Python dependencies
+-- TODO.md                             Innovation suggestions
+-- INNOVATION_ROADMAP.md               Patent and research roadmap
+-- OPTIMIZATION_REPORT.md              Optimization report
+-- README.md
```

---

## Core Modules

### MarketReflexivitySimulator

The central simulation engine (`backend/app/agents/market_simulator.py`) implements three capabilities:

1. **Narrative Propagation**: SIR/IC-based five-stage diffusion model that tracks narrative lifecycle from emergence to collapse.
2. **Price-Belief Feedback**: Closed-loop equation where prices evolve based on the product of sentiment, belief, and a reflexivity factor.
3. **Manipulation Detection**: Pattern recognition for pump-and-dump, coordinated spread, and information asymmetry scenarios.

### KOLNetwork

The KOL social network (`src/social/kol_network.py`) supports three topology modes:

- **STAR**: Single dominant hub node with peripheral followers. Models centralized media influence.
- **DISTRIBUTED**: Multiple mid-tier hub nodes with overlapping follower sets. Models multi-channel information ecosystems.
- **VIRAL**: Decentralized peer-to-peer connections. Models organic viral spread through social platforms.

### RegulatorAgent (Two Implementations)

1. **Strategy-Comparison** (`src/agents/regulator_agent.py`): Evaluates multiple intervention strategies simultaneously, modeling budget constraints, reputation costs, and side effects. Selects the strategy with the best risk-adjusted outcome.

2. **State-Machine** (`src/intervention/regulator_agent.py`): Implements a stateful intervention cycle with cooldown periods, escalation thresholds, and investor protection mechanisms.

---

## Testing

### Run All Tests

```bash
pytest tests/ -v --cov=backend --cov=src --cov-report=term-missing
```

### Run Specific Test Suites

```bash
# Unit tests
pytest tests/test_market_simulator.py -v
pytest tests/test_kol_network.py -v
pytest tests/test_regulator_agents.py -v
pytest tests/test_api_routes.py -v

# Integration tests
pytest tests/test_integration.py -v

# Smoke tests
pytest tests/test_smoke.py -v
```

### Test Coverage

The test suite covers:

- Market simulator core logic (narrative spread, reflexivity loop, manipulation detection)
- KOL network topology construction and narrative propagation
- Regulator agent intervention strategies and state machines
- API endpoint request/response validation
- Cross-module integration pipeline

---

## Benchmark Suite

The benchmark suite (`experiments/run_benchmark.py`) runs five predefined scenarios to validate simulation behavior:

| Scenario | Description | Validation Criteria |
|---|---|---|
| Baseline | Normal market conditions, no narrative injection | Price stability, low reflexivity |
| Positive Narrative | Bullish narrative with moderate strength | Bubble formation, reflexivity increase |
| Negative Shock | Sudden negative event | Panic propagation, price decline |
| Coordinated KOL | Multiple KOLs amplify same narrative | Manipulation risk detection trigger |
| Regulatory Intervention | Regulator intervenes during bubble | Bubble dampening, regime change |

### Run Benchmarks

```bash
cd experiments
python run_benchmark.py
```

---

## Research

### Theoretical Foundation

ReflexMarket-AI operationalizes George Soros's theory of financial reflexivity, which posits that:

1. Participants' perceptions are inherently biased due to incomplete knowledge.
2. Biased perceptions influence market prices.
3. Distorted prices feed back into participants' perceptions and market fundamentals.
4. Self-reinforcing cycles create far-from-equilibrium dynamics (bubbles, crashes).

### Version History

| Version | Key Additions |
|---|---|
| V0.2 | Narrative engine + KOL network + price feedback + reflexivity monitor |
| V0.2-exp | Ablation experiments (Narrative/KOL/PriceFeedback contribution analysis) |
| V0.3 | Trust-weighted propagation, falsification-triggered trust collapse |
| V0.4 | ManipulationRiskAgent for abnormal narrative detection |
| V0.5 | RegulatorAgent for governance intervention simulation |
| V1.0 | Benchmark suite (50 scenarios) + SCI paper + patent submission |

### Key Innovation Points

1. **Narrative-Belief-Price Closed Loop**: First implementation treating narrative as an endogenous reflexivity variable.
2. **Three-Tier KOL Trust Network**: Heterogeneous trust propagation across Macro/Influencer/Micro layers.
3. **Manipulation Risk Score**: Multi-factor detection combining coordination, FOMO, and self-validation signals.
4. **Volatility-Based Bubble Risk**: Using realized volatility regime (not single-step price changes) for stable bubble detection.
5. **Quantified Regulatory Effectiveness**: Controlled experiments measuring intervention impact across light/moderate/strong levels.
6. **Reflexivity Index**: Five-factor weighted real-time composite metric for feedback-loop intensity.

---

## Roadmap

| Phase | Version | Status | Description |
|---|---|---|---|
| 0 | V0.2 | Complete | Narrative propagation + KOL network + price feedback |
| 1 | V0.3 | Complete | Trust-weighted propagation + falsification dynamics |
| 2 | V0.4 | Complete | Manipulation risk detection |
| 3 | V0.5 | Complete | Regulatory intervention simulation |
| 4 | V1.0 | Complete | Benchmark suite + SCI paper + patent |
| 5 | V1.1 | Planned | Real-time parameter tuning via dashboard |
| 6 | V2.0 | Planned | Multi-asset cross-market simulation |

See [INNOVATION_ROADMAP.md](INNOVATION_ROADMAP.md) for the detailed innovation and patent roadmap.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Disclaimer

This system is for academic research and market risk simulation purposes only. It does not constitute investment advice and does not predict real market prices. All simulations operate in controlled environments.
