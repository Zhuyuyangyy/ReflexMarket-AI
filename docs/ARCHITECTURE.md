# ReflexMarket-AI Architecture Documentation

## System Overview

ReflexMarket-AI is a multi-agent simulation framework that models financial market reflexivity -- the feedback loop between market participants' beliefs and market prices.

---

## Core Architecture

```
                    +-------------------+
                    |   FastAPI Server  |
                    |   (port 8020)     |
                    +--------+----------+
                             |
                    +--------v----------+
                    |   API Routes      |
                    |   (routes.py)     |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     | Narrative  |  | Reflexivity |  | Manipulation|
     | Spread     |  | Loop        |  | Detection   |
     +--------+---+  +------+------+  +----+--------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v----------+
                    | MarketReflexivity |
                    | Simulator        |
                    +--------+----------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     | KOLNetwork |  | Regulator   |  | Regulator   |
     | (3 topos)  |  | (Strategy)  |  | (State-Mach)|
     +------------+  +-------------+  +-------------+
```

---

## Module Descriptions

### 1. MarketReflexivitySimulator

**File:** `backend/app/agents/market_simulator.py`

The central simulation engine implementing three core capabilities:

#### 1.1 Narrative Propagation

Models narrative diffusion through a five-stage lifecycle using SIR/IC-inspired dynamics:

```
emerging -> spreading -> dominating -> peaking -> collapsing
```

Each stage has:
- `duration_ticks` - How long the stage lasts
- `spread_rate` - Fraction of new agents reached per tick

The propagation formula:

```
new_reach = total_reach * spread_rate * (1 + sentiment * 0.5)
```

#### 1.2 Price-Belief Feedback Loop

The core reflexivity equation:

```
reflexivity_factor = 0.3 + confidence * 0.5
P(t+1) = P(t) + P(t) * sentiment * belief * reflexivity_factor
belief(t+1) = belief(t) + (price_change / P(t)) * 0.2 * sentiment
```

This produces emergent dynamics:
- Positive sentiment + high belief = bubble formation
- Negative sentiment + collapsing belief = panic selling
- Neutral sentiment + stable belief = market equilibrium

#### 1.3 Manipulation Risk Detection

Multi-factor pattern recognition:

| Factor | Trigger | Score |
|---|---|---|
| Volume Spike | volume_anomaly > 3.0 | min(1.0, anomaly/5) |
| Coordinated Spread | sentiment > 0.8 AND spread_velocity > 0.7 | 0.85 |
| Confidence-Belief Gap | confidence > 0.9 AND belief_ratio < 0.3 | 0.78 |

### 2. KOLNetwork

**File:** `src/social/kol_network.py`

Models information diffusion through social networks with three topology modes:

#### STAR Topology
- One mega-KOL hub (5M followers, 0.85 trust)
- Multiple mid-tier KOLs connected to hub
- Models centralized media influence (e.g., Elon Musk effect)

#### DISTRIBUTED Topology
- Multiple hub KOLs (100K-2M followers)
- Micro-KOLs connected to 1-3 hubs
- Models multi-channel information ecosystems

#### VIRAL Topology
- All peer KOLs (500-100K followers)
- Random connections (2-5 per node)
- Models organic viral spread

#### Propagation Algorithm

```
for each round:
    for each active spreader:
        get unvisited connected agents
        for each target:
            influence = spreader.trust * spreader.influence_score
            belief_shift = influence * random(0.05, 0.15)
            target.belief_state += belief_shift
```

### 3. RegulatorAgent (Strategy-Comparison)

**File:** `src/agents/regulator_agent.py`

Evaluates multiple intervention strategies with budget and credibility constraints:

- **Intervention Types:** narrative_throttle, kol_downweight, trading_cooldown, risk_warning, margin_adjustment, liquidity_injection
- **Strategies:** baseline, light_touch, moderate, strict
- **Constraints:** budget consumption, credibility impact, side effects

### 4. RegulatorAgent (State-Machine)

**File:** `src/intervention/regulator_agent.py`

Implements stateful intervention with risk-based escalation:

```
Risk Score -> Intensity:
  < 0.3  -> NONE
  < 0.5  -> LIGHT   (narrative_throttle + risk_warning)
  < 0.7  -> MODERATE (+ kol_downweight)
  >= 0.7 -> STRONG   (+ trading_cooldown)
```

Features:
- Cooldown mechanisms for each intervention
- Investor protection (warning decay)
- KOL penalty and narrative cap enforcement

---

## Data Flow

### Narrative Spread Flow

```
Client Request
  -> NarrativeSpreadRequest (Pydantic validation)
  -> MarketNarrative dataclass creation
  -> simulate_narrative_spread()
     -> Stage transition logic
     -> Reach calculation
     -> Belief ratio update
  -> Response with spread_history
```

### Reflexivity Loop Flow

```
Client Request
  -> ReflexivityLoopRequest
  -> simulate_reflexivity_loop()
     -> For each tick:
        -> Price change = price * sentiment * belief * reflexivity_factor
        -> Belief update based on price change
        -> Record history
  -> Market state classification
  -> Response
```

---

## Design Principles

1. **Separation of Concerns:** Each module handles one aspect of the simulation
2. **Composability:** Modules can be combined in different configurations
3. **Testability:** Each module has independent unit tests
4. **Extensibility:** New topologies, intervention types, or risk factors can be added
5. **Reproducibility:** Deterministic given a random seed (stochastic elements are isolated)

---

## Performance Characteristics

| Operation | Time Complexity | Typical Latency |
|---|---|---|
| Narrative Spread | O(n * rounds) | < 50ms |
| Reflexivity Loop | O(ticks) | < 10ms |
| Manipulation Detection | O(1) | < 5ms |
| KOL Network Build | O(n) | < 20ms |
| KOL Propagation | O(n * rounds) | < 100ms |
