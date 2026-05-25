"""
KOLNetwork Test Script
Quick test of kol_network.py with a simple scenario
"""
import json
import sys
sys.path.insert(0, 'src')
from social.kol_network import KOLNetwork, NetworkTopology, KOLAgent

def test_basic():
    print("=" * 50)
    print("KOLNetwork Basic Test")
    print("=" * 50)
    
    results = {}
    
    # Test 1: STAR topology
    print("\n[Test 1] STAR topology (n_agents=10)")
    net_star = KOLNetwork(topology=NetworkTopology.STAR, n_agents=10)
    stats_star = net_star.get_network_stats()
    results["star_stats"] = stats_star
    print(f"  Agents: {stats_star['total_agents']}, Hubs: {stats_star['hub_count']}")
    print(f"  Avg followers: {stats_star['avg_followers']}, Avg trust: {stats_star['avg_trust']}")
    
    # Test 2: DISTRIBUTED topology
    print("\n[Test 2] DISTRIBUTED topology (n_agents=15)")
    net_dist = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=15)
    stats_dist = net_dist.get_network_stats()
    results["distributed_stats"] = stats_dist
    print(f"  Agents: {stats_dist['total_agents']}, Hubs: {stats_dist['hub_count']}")
    print(f"  Avg followers: {stats_dist['avg_followers']}, Avg trust: {stats_dist['avg_trust']}")
    
    # Test 3: VIRAL topology
    print("\n[Test 3] VIRAL topology (n_agents=12)")
    net_viral = KOLNetwork(topology=NetworkTopology.VIRAL, n_agents=12)
    stats_viral = net_viral.get_network_stats()
    results["viral_stats"] = stats_viral
    print(f"  Agents: {stats_viral['total_agents']}, Avg trust: {stats_viral['avg_trust']}")
    
    # Test 4: Narrative propagation
    print("\n[Test 4] Narrative propagation (DISTRIBUTED, 3 rounds)")
    net_test = KOLNetwork(topology=NetworkTopology.DISTRIBUTED, n_agents=12)
    prop_result = net_test.propagate_narrative(
        narrative="BTC to $100K by end of year!",
        source_id=None,
        rounds=3
    )
    results["propagation"] = {
        "source": prop_result["source_name"],
        "reach_rate": prop_result["reach_rate"],
        "belief_mean": prop_result["belief_distribution"]["mean"],
        "convergence": prop_result["belief_distribution"]["convergence"]
    }
    print(f"  Source: {prop_result['source_name']}")
    print(f"  Reach rate: {prop_result['reach_rate']}, Reached: {prop_result['reached_agents']}/{prop_result['total_agents']}")
    print(f"  Belief mean: {prop_result['belief_distribution']['mean']}, Convergence: {prop_result['belief_distribution']['convergence']}")
    
    # Test 5: Belief distribution after propagation
    print("\n[Test 5] Belief distribution after propagation")
    belief = net_test.get_belief_distribution()
    results["belief"] = belief
    print(f"  Mean: {belief['mean']}, Median: {belief['median']}")
    print(f"  Bullish: {belief['bullish_pct']*100:.1f}%, Bearish: {belief['bearish_pct']*100:.1f}%, Neutral: {belief['neutral_pct']*100:.1f}%")
    
    # Test 6: Trust update from price
    print("\n[Test 6] Trust update after positive price change (+5%)")
    initial_trust = {a.agent_id: a.trust for a in net_test.agents.values()}
    net_test.update_trust_from_price(price_change=5.0)
    trust_changes = {a.agent_id: round(a.trust - initial_trust[a.agent_id], 4) for a in net_test.agents.values()}
    results["trust_updates"] = {
        "sample_changes": dict(list(trust_changes.items())[:3])
    }
    improved = sum(1 for c in trust_changes.values() if c > 0)
    print(f"  Trust improved: {improved}/{len(trust_changes)} agents")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)
    
    return results

if __name__ == "__main__":
    output = test_basic()
    print("\n[Summary JSON]")
    print(json.dumps(output, indent=2))