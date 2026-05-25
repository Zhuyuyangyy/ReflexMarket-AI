"""
KOL Social Network Module
Simulates Key Opinion Leader (KOL) social network topology and narrative propagation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import math


class NetworkTopology(Enum):
    STAR = "star"          # One mega-KOL at center
    DISTRIBUTED = "distributed"  # Multiple mid-KOLs
    VIRAL = "viral"        # No central hub, peer-to-peer


@dataclass
class KOLAgent:
    """Key Opinion Leader Agent"""
    agent_id: str
    name: str
    followers: int
    trust: float          # 0-1
    influence_score: float  # 0-1
    topology_role: str     # "hub", "mid", "micro"
    belief_state: float = 0.5  # 0-1, 0.5=neutral
    narrative_count: int = 0
    
    def update_trust(self, price_change: float, accuracy: float = 0.6):
        """Update trust based on price prediction accuracy"""
        if price_change > 0:
            self.trust = min(1.0, self.trust + accuracy * 0.05)
        else:
            self.trust = max(0.1, self.trust - (1 - accuracy) * 0.08)
    
    def spread_narrative(self, narrative: str, audience: List['KOLAgent']) -> Dict:
        """Spread narrative to connected agents"""
        reach = int(self.followers * self.influence_score * 0.01)
        influenced = int(reach * self.trust * 0.3)
        self.narrative_count += 1
        return {
            "spreader_id": self.agent_id,
            "original_reach": reach,
            "influenced_count": influenced,
            "trust_leverage": round(self.trust * self.influence_score, 3)
        }


class KOLNetwork:
    """
    KOL Social Network Simulator
    
    Simulates how narratives spread through social networks based on:
    - Network topology (star, distributed, viral)
    - KOL trust and influence scores
    - Follower counts
    - Belief state convergence
    """
    
    def __init__(self, topology: NetworkTopology = NetworkTopology.DISTRIBUTED, n_agents: int = 20):
        self.topology = topology
        self.n_agents = n_agents
        self.agents: Dict[str, KOLAgent] = {}
        self.network_graph: Dict[str, List[str]] = {}
        self._build_network()
    
    def _build_network(self):
        """Build network based on topology"""
        if self.topology == NetworkTopology.STAR:
            self._build_star()
        elif self.topology == NetworkTopology.DISTRIBUTED:
            self._build_distributed()
        else:
            self._build_viral()
    
    def _build_star(self):
        """One mega-KOL at center, many micro-KOLs around"""
        hub = KOLAgent(
            agent_id="kol_hub_01",
            name="Mega KOL",
            followers=5000000,
            trust=0.85,
            influence_score=0.95,
            topology_role="hub"
        )
        self.agents[hub.agent_id] = hub
        self.network_graph[hub.agent_id] = []
        
        for i in range(self.n_agents - 1):
            mid = KOLAgent(
                agent_id=f"kol_mid_{i:02d}",
                name=f"Mid KOL {i}",
                followers=random.randint(10000, 500000),
                trust=random.uniform(0.5, 0.8),
                influence_score=random.uniform(0.4, 0.7),
                topology_role="mid"
            )
            self.agents[mid.agent_id] = mid
            self.network_graph[mid.agent_id] = [hub.agent_id]
            self.network_graph[hub.agent_id].append(mid.agent_id)
    
    def _build_distributed(self):
        """Multiple mid-KOLs with overlapping audiences"""
        mid_count = max(3, self.n_agents // 3)
        hubs = []
        for i in range(mid_count):
            hub = KOLAgent(
                agent_id=f"kol_hub_{i:02d}",
                name=f"Hub KOL {i}",
                followers=random.randint(100000, 2000000),
                trust=random.uniform(0.6, 0.9),
                influence_score=random.uniform(0.5, 0.8),
                topology_role="hub"
            )
            self.agents[hub.agent_id] = hub
            self.network_graph[hub.agent_id] = []
            hubs.append(hub)
        
        for i in range(self.n_agents - mid_count):
            micro = KOLAgent(
                agent_id=f"kol_micro_{i:02d}",
                name=f"Micro KOL {i}",
                followers=random.randint(1000, 50000),
                trust=random.uniform(0.3, 0.7),
                influence_score=random.uniform(0.2, 0.5),
                topology_role="micro"
            )
            self.agents[micro.agent_id] = micro
            # Connect to 1-3 random hubs
            connected_hubs = random.sample(hubs, min(random.randint(1, 3), len(hubs)))
            self.network_graph[micro.agent_id] = [h.agent_id for h in connected_hubs]
            for h in connected_hubs:
                self.network_graph[h.agent_id].append(micro.agent_id)
    
    def _build_viral(self):
        """No central hub, peer-to-peer mesh"""
        for i in range(self.n_agents):
            kol = KOLAgent(
                agent_id=f"kol_peer_{i:02d}",
                name=f"Peer KOL {i}",
                followers=random.randint(500, 100000),
                trust=random.uniform(0.3, 0.8),
                influence_score=random.uniform(0.2, 0.6),
                topology_role="mid"
            )
            self.agents[kol.agent_id] = kol
        
        # Random connections
        agent_ids = list(self.agents.keys())
        for aid in agent_ids:
            n_connections = random.randint(2, min(5, self.n_agents - 1))
            peers = random.sample([a for a in agent_ids if a != aid], n_connections)
            self.network_graph[aid] = peers
    
    def propagate_narrative(self, narrative: str, source_id: str = None, rounds: int = 3) -> Dict:
        """
        Propagate narrative through network
        
        Args:
            narrative: The narrative text to propagate
            source_id: Starting KOL agent_id (random if None)
            rounds: Number of propagation rounds
        
        Returns propagation report
        """
        if not self.agents:
            return {"error": "No agents in network"}
        
        # Select source
        if source_id is None:
            source = random.choice(list(self.agents.values()))
        else:
            source = self.agents.get(source_id, random.choice(list(self.agents.values())))
        
        propagation_log = []
        current_round_agents = [source]
        reached_agents = {source.agent_id}
        
        for round_num in range(rounds):
            next_round = []
            round_report = {
                "round": round_num + 1,
                "spreaders": [],
                "total_reach": 0,
                "avg_trust": 0
            }
            
            for agent in current_round_agents:
                # Get connected agents
                connected_ids = self.network_graph.get(agent.agent_id, [])
                unvisited = [cid for cid in connected_ids if cid not in reached_agents]
                
                for target_id in unvisited[:random.randint(1, max(1, len(unvisited)))]:
                    target = self.agents.get(target_id)
                    if not target:
                        continue
                    
                    # Narrative influence based on trust
                    influence = agent.trust * agent.influence_score
                    belief_shift = influence * random.uniform(0.05, 0.15)
                    
                    # Update target belief (move toward narrative sentiment)
                    target.belief_state = min(1.0, target.belief_state + belief_shift)
                    
                    spread_result = agent.spread_narrative(narrative, [target])
                    round_report["spreaders"].append({
                        "from": agent.agent_id,
                        "to": target_id,
                        "influence": round(influence, 3),
                        "belief_shift": round(belief_shift, 3),
                        "reach": spread_result["influenced_count"]
                    })
                    round_report["total_reach"] += spread_result["influenced_count"]
                    
                    if target_id not in reached_agents:
                        reached_agents.add(target_id)
                        next_round.append(target)
            
            if round_report["spreaders"]:
                round_report["avg_trust"] = round(
                    sum(s["influence"] for s in round_report["spreaders"]) / len(round_report["spreaders"]), 3
                )
                propagation_log.append(round_report)
            
            current_round_agents = next_round[:random.randint(1, max(1, len(next_round)))]
        
        # Compute belief distribution
        beliefs = [a.belief_state for a in self.agents.values()]
        belief_distribution = {
            "mean": round(sum(beliefs) / len(beliefs), 3),
            "std": round(math.sqrt(sum((b - sum(beliefs)/len(beliefs))**2 for b in beliefs) / len(beliefs)), 3),
            "convergence": round(1 - math.sqrt(sum((b - 0.7)**2 for b in beliefs) / len(beliefs)), 3)  # 0.7=bullish target
        }
        
        return {
            "source_id": source.agent_id,
            "source_name": source.name,
            "topology": self.topology.value,
            "total_agents": len(self.agents),
            "reached_agents": len(reached_agents),
            "reach_rate": round(len(reached_agents) / len(self.agents), 3),
            "rounds": rounds,
            "propagation_log": propagation_log,
            "belief_distribution": belief_distribution
        }
    
    def update_trust_from_price(self, price_change: float):
        """Update all KOL trust based on price prediction accuracy"""
        for agent in self.agents.values():
            # Each agent has some base prediction accuracy
            accuracy = agent.trust * 0.5 + random.uniform(0.1, 0.4)
            agent.update_trust(price_change, accuracy)
    
    def get_belief_distribution(self) -> Dict:
        """Get current belief distribution across network"""
        beliefs = [a.belief_state for a in self.agents.values()]
        return {
            "mean": round(sum(beliefs) / len(beliefs), 3),
            "median": round(sorted(beliefs)[len(beliefs)//2], 3),
            "bullish_pct": round(sum(1 for b in beliefs if b > 0.6) / len(beliefs), 3),
            "bearish_pct": round(sum(1 for b in beliefs if b < 0.4) / len(beliefs), 3),
            "neutral_pct": round(sum(1 for b in beliefs if 0.4 <= b <= 0.6) / len(beliefs), 3),
        }
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        return {
            "topology": self.topology.value,
            "total_agents": len(self.agents),
            "avg_followers": round(sum(a.followers for a in self.agents.values()) / len(self.agents)),
            "avg_trust": round(sum(a.trust for a in self.agents.values()) / len(self.agents), 3),
            "avg_influence": round(sum(a.influence_score for a in self.agents.values()) / len(self.agents), 3),
            "hub_count": sum(1 for a in self.agents.values() if a.topology_role == "hub"),
            "micro_count": sum(1 for a in self.agents.values() if a.topology_role == "micro"),
        }