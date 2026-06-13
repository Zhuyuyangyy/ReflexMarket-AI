"""
Pytest configuration and shared fixtures for ReflexMarket-AI tests.
"""

import sys
import os
import pytest

# Ensure project paths are available
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "backend"),
    os.path.join(PROJECT_ROOT, "src"),
]:
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def sample_narrative_data():
    """Shared narrative data for tests."""
    return {
        "narrative_id": "N-FIXTURE",
        "content": "Test narrative for fixtures",
        "sentiment": 0.6,
        "spread_velocity": 0.5,
        "reach": 300,
        "confidence": 0.7,
        "stage": "emerging",
        "belief_ratio": 0.35,
        "price_impact": 0.03,
    }


@pytest.fixture
def sample_market_state():
    """Shared market state for regulator tests."""
    return {
        "bubble_risk": 0.5,
        "panic_risk": 0.3,
        "manipulation_risk": 0.2,
        "volatility": 0.25,
    }
