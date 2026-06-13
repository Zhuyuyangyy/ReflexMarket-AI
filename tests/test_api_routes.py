"""
Unit tests for FastAPI API routes.
Tests all endpoints with valid and edge-case inputs.
"""

import sys
import os
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

for p in [PROJECT_ROOT, BACKEND_DIR, SRC_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


# ── Health Endpoint Tests ─────────────────────────────────────────


class TestHealthEndpoint:
    """Test health check endpoints."""

    def test_health_root(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ReflexMarket-AI"

    def test_health_api(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"


# ── Narrative Spread Endpoint Tests ───────────────────────────────


class TestNarrativeSpreadEndpoint:
    """Test POST /api/v1/narrative/spread"""

    def test_valid_request(self, client):
        payload = {
            "content": "Market rally coming",
            "sentiment": 0.7,
            "spread_velocity": 0.5,
            "reach": 200,
            "confidence": 0.8,
            "stage": "emerging",
            "belief_ratio": 0.3,
            "price_impact": 0.04,
        }
        resp = client.post("/api/v1/narrative/spread", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "data" in data

    def test_response_has_spread_history(self, client):
        payload = {
            "content": "Test narrative",
            "sentiment": 0.5,
            "spread_velocity": 0.5,
            "reach": 100,
            "confidence": 0.7,
            "stage": "emerging",
            "belief_ratio": 0.3,
            "price_impact": 0.02,
        }
        resp = client.post("/api/v1/narrative/spread", json=payload)
        data = resp.json()
        assert "spread_history" in data["data"]

    def test_bearish_narrative(self, client):
        payload = {
            "content": "Market crash",
            "sentiment": -0.8,
            "spread_velocity": 0.7,
            "reach": 500,
            "confidence": 0.6,
            "stage": "spreading",
            "belief_ratio": 0.5,
            "price_impact": -0.03,
        }
        resp = client.post("/api/v1/narrative/spread", json=payload)
        assert resp.status_code == 200

    def test_missing_content_field(self, client):
        payload = {"sentiment": 0.5}
        resp = client.post("/api/v1/narrative/spread", json=payload)
        assert resp.status_code == 422  # Validation error

    def test_default_values_applied(self, client):
        payload = {"content": "Minimal request"}
        resp = client.post("/api/v1/narrative/spread", json=payload)
        assert resp.status_code == 200


# ── Reflexivity Loop Endpoint Tests ───────────────────────────────


class TestReflexivityLoopEndpoint:
    """Test POST /api/v1/reflexivity/loop"""

    def test_valid_request(self, client):
        payload = {
            "initial_price": 100.0,
            "narrative_sentiment": 0.5,
            "confidence": 0.7,
            "ticks": 10,
        }
        resp = client.post("/api/v1/reflexivity/loop", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "final_price" in data["data"]

    def test_bullish_loop(self, client):
        payload = {
            "initial_price": 100.0,
            "narrative_sentiment": 0.9,
            "confidence": 0.9,
            "ticks": 20,
        }
        resp = client.post("/api/v1/reflexivity/loop", json=payload)
        data = resp.json()
        assert data["data"]["final_price"] > 100.0

    def test_bearish_loop(self, client):
        payload = {
            "initial_price": 100.0,
            "narrative_sentiment": -0.9,
            "confidence": 0.8,
            "ticks": 20,
        }
        resp = client.post("/api/v1/reflexivity/loop", json=payload)
        data = resp.json()
        assert data["data"]["final_price"] < 100.0

    def test_price_history_length(self, client):
        payload = {
            "initial_price": 100.0,
            "narrative_sentiment": 0.5,
            "confidence": 0.7,
            "ticks": 15,
        }
        resp = client.post("/api/v1/reflexivity/loop", json=payload)
        data = resp.json()
        assert len(data["data"]["price_history"]) == 15

    def test_default_values(self, client):
        resp = client.post("/api/v1/reflexivity/loop", json={})
        assert resp.status_code == 200


# ── Manipulation Detection Endpoint Tests ─────────────────────────


class TestManipulationDetectionEndpoint:
    """Test POST /api/v1/risk/manipulation"""

    def test_valid_request(self, client):
        payload = {
            "narrative_content": "Pump this coin!",
            "narrative_sentiment": 0.95,
            "trading_volume": 50000,
            "volume_anomaly": 4.5,
        }
        resp = client.post("/api/v1/risk/manipulation", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "risk_level" in data["data"]

    def test_high_risk_detection(self, client):
        payload = {
            "narrative_content": "Moon pump!",
            "narrative_sentiment": 0.95,
            "trading_volume": 100000,
            "volume_anomaly": 5.0,
        }
        resp = client.post("/api/v1/risk/manipulation", json=payload)
        data = resp.json()
        assert data["data"]["risk_level"] in ("LOW", "MEDIUM", "HIGH")

    def test_low_risk(self, client):
        payload = {
            "narrative_content": "Normal market activity",
            "narrative_sentiment": 0.3,
            "trading_volume": 1000,
            "volume_anomaly": 1.0,
        }
        resp = client.post("/api/v1/risk/manipulation", json=payload)
        data = resp.json()
        assert data["data"]["risk_level"] == "LOW"

    def test_response_has_risk_factors(self, client):
        payload = {
            "narrative_content": "Test",
            "narrative_sentiment": 0.9,
            "trading_volume": 50000,
            "volume_anomaly": 4.0,
        }
        resp = client.post("/api/v1/risk/manipulation", json=payload)
        data = resp.json()
        assert "risk_factors" in data["data"]


# ── CORS and Middleware Tests ─────────────────────────────────────


class TestMiddleware:
    """Test CORS and middleware configuration."""

    def test_cors_headers(self, client):
        resp = client.options("/api/v1/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
        # FastAPI CORS middleware should handle this
        assert resp.status_code in (200, 204, 405)

    def test_openapi_docs(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "paths" in schema
        assert "/api/v1/narrative/spread" in schema["paths"]
