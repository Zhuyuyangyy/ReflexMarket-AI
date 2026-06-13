# ReflexMarket-AI API Documentation

## Base URL

```
http://localhost:8020
```

## Authentication

No authentication required. All endpoints are publicly accessible.

---

## Endpoints

### Health Check

#### `GET /health`

Returns service health status.

**Response:**

```json
{
  "status": "healthy",
  "service": "ReflexMarket-AI",
  "framework": "OpenClaw + ASF-BGT + CrewAI + AgentShield V3",
  "version": "0.1.0",
  "disclaimer": "..."
}
```

#### `GET /api/v1/health`

Same as above, under the versioned API prefix.

---

### Narrative Spread Simulation

#### `POST /api/v1/narrative/spread`

Simulates how a narrative propagates through the social network.

**Request Body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| content | string | Yes | - | Narrative text content |
| sentiment | float | No | 0.5 | Sentiment score (-1.0 to 1.0) |
| spread_velocity | float | No | 0.5 | Propagation speed (0.0 to 1.0) |
| reach | int | No | 100 | Initial agent reach count |
| confidence | float | No | 0.7 | Narrative credibility (0.0 to 1.0) |
| stage | string | No | "emerging" | Lifecycle stage |
| belief_ratio | float | No | 0.3 | Fraction of agents adopting narrative |
| price_impact | float | No | 0.02 | Expected price impact coefficient |

**Lifecycle Stages:**
- `emerging` - Initial appearance, limited reach
- `spreading` - Rapid diffusion through network
- `dominating` - Becomes market-dominant narrative
- `peaking` - Saturation point reached
- `collapsing` - Being replaced or losing credibility

**Response:**

```json
{
  "status": "success",
  "data": {
    "narrative_id": "NARR-20260529120000",
    "network_size": 1000,
    "final_reach": 2450,
    "final_belief_ratio": 0.65,
    "final_stage": "spreading",
    "spread_history": [...],
    "simulation_ticks": 20
  }
}
```

---

### Reflexivity Loop Simulation

#### `POST /api/v1/reflexivity/loop`

Runs a closed-loop price-belief feedback simulation.

**Request Body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| initial_price | float | No | 100.0 | Starting price |
| narrative_sentiment | float | No | 0.5 | Narrative direction (-1.0 to 1.0) |
| confidence | float | No | 0.7 | Initial confidence level (0.0 to 1.0) |
| ticks | int | No | 10 | Number of simulation steps |

**Core Equation:**

```
P(t+1) = P(t) * (1 + sentiment * belief * reflexivity_factor)
belief(t+1) = belief(t) + (price_change / price) * 0.2 * sentiment
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "initial_price": 100.0,
    "final_price": 145.32,
    "total_return_pct": 45.32,
    "market_state": "bubble_forming",
    "risk_level": "HIGH",
    "price_history": [100.5, 101.2, ...],
    "belief_history": [0.7, 0.72, ...],
    "narrative_sentiment": 0.9,
    "confidence": 0.85,
    "reflexivity_factor": 0.725
  }
}
```

**Market States:**
- `bubble_forming` - Return > 30%
- `panic_selling` - Return < -20%
- `stable` - |Return| < 10%
- `normal_fluctuation` - Other

---

### Manipulation Risk Detection

#### `POST /api/v1/risk/manipulation`

Analyzes narrative and volume patterns for manipulation risk.

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| narrative_content | string | Yes | Narrative text to analyze |
| narrative_sentiment | float | Yes | Sentiment extremity |
| trading_volume | float | Yes | Observed trading volume |
| volume_anomaly | float | Yes | Volume deviation multiplier |

**Risk Factors Detected:**
- `volume_spike` - Volume anomaly > 3.0x
- `coordinated_spread` - Extreme sentiment + fast spread
- `confidence_belief_gap` - High confidence but low belief ratio

**Response:**

```json
{
  "status": "success",
  "data": {
    "narrative_id": "NARR-...",
    "trading_volume": 50000,
    "volume_anomaly_ratio": 4.5,
    "risk_factors": [
      {
        "factor": "volume_spike",
        "score": 0.9,
        "description": "..."
      }
    ],
    "total_risk_score": 0.85,
    "risk_level": "HIGH",
    "recommended_action": "..."
  }
}
```

**Risk Levels:**
- `HIGH` - Score > 0.7
- `MEDIUM` - Score > 0.4
- `LOW` - Score <= 0.4

---

## Error Responses

All endpoints return standard FastAPI validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
