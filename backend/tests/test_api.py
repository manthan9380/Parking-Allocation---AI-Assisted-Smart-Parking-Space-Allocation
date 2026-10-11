"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import (
    Vehicle, ParkingSpace, VehicleType, SpaceType, SpaceState, Urgency
)


client = TestClient(app)


def test_health_endpoint():
    """Test that health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_allocate_endpoint_returns_valid_response():
    """Test that /allocate endpoint returns valid allocation response."""
    request_data = {
        "vehicles": [
            {"id": "V1", "vehicle_type": "regular", "urgency": "normal"},
            {"id": "V2", "vehicle_type": "ev", "urgency": "high"},
        ],
        "spaces": [
            {"id": "S1", "space_type": "regular", "state": "available", "row": 1, "col": 0},
            {"id": "S2", "space_type": "ev_charging", "state": "available", "row": 2, "col": 0},
            {"id": "S3", "space_type": "regular", "state": "occupied", "row": 0, "col": 1},
        ],
        "entrance_row": 0,
        "entrance_col": 0
    }

    response = client.post("/allocate", json=request_data)

    assert response.status_code == 200

    data = response.json()

    # Check response structure
    assert "greedy" in data
    assert "optimal" in data
    assert "cost_matrix" in data
    assert "vehicle_ids" in data
    assert "space_ids" in data
    assert "improvement_percent" in data

    # Check greedy result structure
    assert "assignments" in data["greedy"]
    assert "total_cost" in data["greedy"]
    assert "average_walking_distance" in data["greedy"]
    assert "num_unassigned" in data["greedy"]
    assert "utilization_percent" in data["greedy"]

    # Check optimal result structure
    assert "assignments" in data["optimal"]
    assert "total_cost" in data["optimal"]
    assert "average_walking_distance" in data["optimal"]
    assert "num_unassigned" in data["optimal"]
    assert "utilization_percent" in data["optimal"]

    # Check that both methods assigned vehicles
    assert len(data["greedy"]["assignments"]) == 2
    assert len(data["optimal"]["assignments"]) == 2

    # Check cost matrix dimensions (2 vehicles x 3 spaces)
    assert len(data["cost_matrix"]) == 2
    assert len(data["cost_matrix"][0]) == 3

    # Verify vehicle and space IDs
    assert data["vehicle_ids"] == ["V1", "V2"]
    assert data["space_ids"] == ["S1", "S2", "S3"]

    # Optimal should never be worse than greedy
    assert data["optimal"]["total_cost"] <= data["greedy"]["total_cost"]


def test_allocate_endpoint_handles_all_spaces_occupied():
    """Test /allocate when all spaces are occupied."""
    request_data = {
        "vehicles": [
            {"id": "V1", "vehicle_type": "regular", "urgency": "normal"},
        ],
        "spaces": [
            {"id": "S1", "space_type": "regular", "state": "occupied", "row": 1, "col": 0},
            {"id": "S2", "space_type": "regular", "state": "occupied", "row": 2, "col": 0},
        ],
        "entrance_row": 0,
        "entrance_col": 0
    }

    response = client.post("/allocate", json=request_data)

    assert response.status_code == 200

    data = response.json()

    # Vehicle should be unassigned in both methods
    assert data["greedy"]["num_unassigned"] == 1
    assert data["optimal"]["num_unassigned"] == 1
    assert data["greedy"]["assignments"][0]["space_id"] is None
    assert data["optimal"]["assignments"][0]["space_id"] is None


def test_experiment_endpoint_returns_valid_response():
    """Test that /experiment endpoint returns valid experiment results."""
    request_data = {
        "num_runs": 10,
        "lot_size": 15,
        "num_vehicles": 5,
        "seed": 42
    }

    response = client.post("/experiment", json=request_data)

    assert response.status_code == 200

    data = response.json()

    # Check response structure
    assert "avg_greedy_cost" in data
    assert "avg_optimal_cost" in data
    assert "avg_improvement_percent" in data
    assert "improvements" in data
    assert "greedy_costs" in data
    assert "optimal_costs" in data

    # Check that arrays have correct length
    assert len(data["improvements"]) == 10
    assert len(data["greedy_costs"]) == 10
    assert len(data["optimal_costs"]) == 10

    # Optimal should be better or equal on average
    assert data["avg_optimal_cost"] <= data["avg_greedy_cost"]

    # Improvement should be non-negative
    assert data["avg_improvement_percent"] >= 0


def test_experiment_endpoint_with_defaults():
    """Test /experiment with default parameters."""
    response = client.post("/experiment", json={})

    assert response.status_code == 200

    data = response.json()

    # Should run 100 times by default
    assert len(data["improvements"]) == 100
    assert len(data["greedy_costs"]) == 100
    assert len(data["optimal_costs"]) == 100


def test_experiment_is_reproducible():
    """Test that experiment results are reproducible with same seed."""
    request_data = {
        "num_runs": 20,
        "lot_size": 20,
        "num_vehicles": 8,
        "seed": 999
    }

    response1 = client.post("/experiment", json=request_data)
    response2 = client.post("/experiment", json=request_data)

    data1 = response1.json()
    data2 = response2.json()

    # Results should be identical
    assert data1["avg_greedy_cost"] == data2["avg_greedy_cost"]
    assert data1["avg_optimal_cost"] == data2["avg_optimal_cost"]
    assert data1["improvements"] == data2["improvements"]
