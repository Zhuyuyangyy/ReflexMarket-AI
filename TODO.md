# ReflexMarket-AI TODO

> Innovation Suggestions and Feature Backlog

---

## Market Sentiment Reflexivity Modeling

### S1. Adaptive Sentiment Regime Detection
**Priority:** P0 | **Effort:** 2 weeks | **Impact:** High

Implement a Hidden Markov Model (HMM) to detect latent sentiment regimes (euphoria, panic, accumulation, distribution) from the time series of narrative sentiment and price feedback signals.

**Technical Approach:**
- Use Baum-Welch algorithm to learn regime transition probabilities from simulation output
- Define 4-5 hidden states mapping to market psychology phases
- Integrate regime detection into the reflexivity loop as a meta-feedback signal

**Innovation Value:** Current system uses fixed thresholds for market state classification. HMM-based regime detection would enable the system to identify phase transitions before they fully manifest.

### S2. Cross-Asset Narrative Spillover Model
**Priority:** P1 | **Effort:** 3 weeks | **Impact:** High

Extend the single-asset model to multi-asset simulation where narratives can spill over across correlated markets.

**Technical Approach:**
- Define asset correlation matrix (e.g., BTC-ETH, stocks-bonds)
- Narrative propagation follows correlation-weighted paths
- Contagion coefficient determines cross-asset belief transfer rate

### S3. Narrative Memory and Decay
**Priority:** P1 | **Effort:** 1 week | **Impact:** Medium

Add temporal memory to narratives -- older narratives decay in influence unless reinforced by new events.

**Technical Approach:**
- Exponential decay: `influence(t) = influence(0) * exp(-lambda * t)`
- Reinforcement from correlated new narratives
- Memory window configurable per agent type

---

## Bubble Detection

### S4. Log-Periodic Power Law (LPPL) Bubble Detection
**Priority:** P0 | **Effort:** 2 weeks | **Impact:** High

Implement LPPL model for bubble detection based on Sornette's work on log-periodic oscillations preceding crashes.

**Technical Approach:**
- Fit `P(t) = A + B(tc - t)^m * [1 + C * cos(omega * log(tc - t) + phi)]` to price series
- Detect critical time `tc` and exponent `m`
- Flag bubble when `m < 1` and `tc` is within prediction horizon

**Innovation Value:** Combines LPPL with narrative analysis -- narrative saturation correlates with approaching `tc`.

### S5. Volatility Clustering and Regime Switching
**Priority:** P1 | **Effort:** 2 weeks | **Impact:** Medium

Implement GARCH-type volatility modeling within the simulation to capture volatility clustering effects.

### S6. Reflexivity Index (Multi-Factor Composite)
**Priority:** P0 | **Effort:** 1 week | **Impact:** High

Create a real-time Reflexivity Index combining:
1. Narrative velocity (spread rate)
2. Belief convergence (std deviation of beliefs)
3. Price momentum (rate of price change)
4. Volume anomaly (deviation from baseline)
5. Trust volatility (fluctuation in KOL trust scores)

Formula: `RI = w1*NV + w2*(1-BC) + w3*PM + w4*VA + w5*TV`

---

## Adaptive Trading Strategy

### S7. Regime-Aware Agent Trading Behavior
**Priority:** P1 | **Effort:** 3 weeks | **Impact:** High

Replace static trading behavior with regime-adaptive strategies where agents adjust their behavior based on detected market regime.

**Technical Approach:**
- Each agent has a strategy profile: {conservative, moderate, aggressive}
- Strategy selection depends on detected regime and agent risk tolerance
- Strategy switching has friction (delay, cost) to model real behavioral inertia

### S8. Feedback-Aware Portfolio Optimization
**Priority:** P2 | **Effort:** 4 weeks | **Impact:** High

Implement portfolio optimization that accounts for reflexivity effects -- traditional Markowitz assumes exogenous prices, but here prices are endogenous to agent behavior.

### S9. Multi-Agent Game Theory Module
**Priority:** P1 | **Effort:** 3 weeks | **Impact:** High

Implement incomplete information game theory for agent interactions:
- Bayesian Nash equilibrium for KOL strategy selection
- Mechanism design for regulatory intervention
- Evolutionary game theory for belief propagation dynamics

---

## Technical Debt and Infrastructure

### S10. Async Simulation Engine
**Priority:** P2 | **Effort:** 2 weeks | **Impact:** Medium

Refactor simulation engine to support async parallel execution of multiple scenarios.

### S11. Real-Time WebSocket Dashboard
**Priority:** P1 | **Effort:** 2 weeks | **Impact:** Medium

Replace polling-based dashboard with WebSocket streaming for real-time simulation visualization.

### S12. Configuration Management
**Priority:** P2 | **Effort:** 1 week | **Impact:** Low

Add YAML/JSON configuration file support for simulation parameters instead of hard-coded values.

### S13. Historical Data Calibration
**Priority:** P1 | **Effort:** 3 weeks | **Impact:** High

Add capability to calibrate simulation parameters against historical market data (e.g., 2021 BTC bubble, 2008 financial crisis).

---

## Research and Publication

### S14. Ablation Study Framework
**Priority:** P0 | **Effort:** 2 weeks | **Impact:** High

Systematic framework for measuring the contribution of each component (Narrative, KOL, Price Feedback, Regulation) to overall simulation dynamics.

### S15. Sensitivity Analysis Module
**Priority:** P1 | **Effort:** 1 week | **Impact:** Medium

Automated parameter sensitivity analysis to identify which parameters most influence simulation outcomes.

---

## Priority Summary

| Priority | Count | Items |
|---|---|---|
| P0 | 4 | S1, S4, S6, S14 |
| P1 | 7 | S2, S3, S5, S7, S9, S11, S13, S15 |
| P2 | 3 | S8, S10, S12 |
