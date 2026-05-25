# ReflexMarket-AI

> 叙事驱动的金融反身性多智能体仿真框架

## 核心定位

- **不是量化交易系统** → 市场风险仿真 / 反身性建模 / 异常叙事传播检测 / 监管干预仿真
- **不声称有真实市场预测能力** → 可控仿真环境下的反身性机制建模，非真实市场价格预测

## 版本路线

```
V0.2 ✅ Narrative + KOL + Price Feedback + Reflexivity（泡沫/恐慌/反转）
V0.2-exp ✅ 消融实验（Narrative/KOL/PriceFeedback 三机制贡献度）
V0.3 ✅ Trust Bootstrapping（信任加权传播，证伪触发信任崩塌）
V0.4 ✅ ManipulationRiskAgent（异常叙事传播风险识别）
V0.5 🔜 RegulatorAgent / 监管干预仿真
V1.0 🔜 Benchmark(50条) + SCI论文 + 专利提交
```

## 架构

```
Narrative → Trust → Belief → Emotion → Behavior → Capital → Price → Feedback
                                                              ↓
                                                    Risk Detection (V0.4)
                                                              ↓
                                                    Governance (V0.5)
```

## 防坑口径

- 任何新功能必须能回答：它是否增强"叙事→信任→行为→资金→反馈→治理"这条链路？
- 不包装成金融预测/量化交易系统
- 技术成熟度：可控仿真环境，非真实市场

## 关键文件

- `src/agents/market_cognition_agent.py` — 市场认知Agent
- `src/agents/narrative_agent.py` — 叙事生成Agent
- `src/agents/kl_social_agent.py` — KOL社交影响Agent
- `src/agents/trust_agent.py` — 信任计算Agent
- `src/agents/emotion_agent.py` — 情绪演化Agent
- `src/agents/behavior_agent.py` — 行为决策Agent
- `src/agents/capital_agent.py` — 资金流Agent
- `src/agents/price_feedback_agent.py` — 价格反馈Agent
- `src/agents/reflexivity_monitor.py` — 反身性监控
- `src/agents/manipulation_risk_agent.py` — V0.4 异常风险检测
- `src/agents/regulator_agent.py` — V0.5 监管干预
- `demos/demo_*.py` — 各版本验证Demo
- `docs/demo_evidence_v0.2/` — V0.2证据包
- `docs/demo_evidence_v0.3/` — V0.3证据包
- `docs/demo_evidence_v0.4/` — V0.4证据包
- `docs/demo_evidence_v0.5/` — V0.5证据包