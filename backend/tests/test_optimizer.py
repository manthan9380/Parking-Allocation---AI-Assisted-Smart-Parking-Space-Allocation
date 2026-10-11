"""Tests for Hungarian optimizer."""

import numpy as np
import pytest
from itertools import permutations
from app.optimizer import hungarian_allocate, make_allocation_result
from app.cost import build_cost_matrix, INFEASIBLE_COST
from app.models import (
    Vehicle, ParkingSpace, VehicleType, SpaceType, SpaceState, Urgency
)


def test_hungarian_on_worked_example():
    """Test Hungarian algorithm on the 3x3 worked example from notes.

    Cost matrix:
           S1  S2  S3
      V1 [  2   5   8 ]
      V2 [  3   2   6 ]
      V3 [  7   4   1 ]

    Optimal assignment: V1→S1 (2), V2→S2 (2), V3→S3 (1) = Total 5
    """
    # Create vehicles at entrance (0,0) with distances matching the matrix
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V2", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V3", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]

    # Create spaces at distances: S1=2, S2=5, S3=8 for V1, etc.
    # We need to construct a scenario where the cost matrix matches
    # Since cost = urgency_weight * distance, and normal urgency = 1.0,
    # we can directly use the cost values as distances
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0),
        ParkingSpace(id="S3", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0),
    ]

    # Manually construct the cost matrix from the example
    cost_matrix = np.array([
        [2.0, 5.0, 8.0],
        [3.0, 2.0, 6.0],
        [7.0, 4.0, 1.0]
    ])

    assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # Check that we get the optimal assignment
    assignment_dict = {a.vehicle_id: (a.space_id, a.cost) for a in assignments}

    # The optimal solution should have total cost = 5
    total_cost = sum(a.cost for a in assignments if a.space_id is not None)
    assert total_cost == 5.0, f"Expected total cost 5, got {total_cost}"

    # Verify the specific assignment (V1→S1, V2→S2, V3→S3)
    assert assignment_dict["V1"][1] == 2.0
    assert assignment_dict["V2"][1] == 2.0
    assert assignment_dict["V3"][1] == 1.0


def brute_force_assignment(cost_matrix: np.ndarray) -> float:
    """Compute optimal cost by trying all permutations (brute force).

    Only works for small square matrices (n ≤ 10).
    """
    n = cost_matrix.shape[0]
    min_cost = float('inf')

    for perm in permutations(range(n)):
        cost = sum(cost_matrix[i, j] for i, j in enumerate(perm))
        if cost < min_cost:
            min_cost = cost

    return min_cost


def test_hungarian_vs_brute_force_3x3():
    """Test Hungarian matches brute force on 3x3 matrices."""
    rng = np.random.default_rng(123)

    for trial in range(10):
        # Generate random 3x3 cost matrix
        cost_matrix = rng.uniform(1, 100, size=(3, 3))

        # Create dummy vehicles and spaces
        vehicles = [
            Vehicle(id=f"V{i}", vehicle_type=VehicleType.regular, urgency=Urgency.normal)
            for i in range(3)
        ]
        spaces = [
            ParkingSpace(id=f"S{i}", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0)
            for i in range(3)
        ]

        # Hungarian result
        assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)
        hungarian_cost = sum(a.cost for a in assignments if a.space_id is not None)

        # Brute force result
        brute_force_cost = brute_force_assignment(cost_matrix)

        assert abs(hungarian_cost - brute_force_cost) < 1e-9, \
            f"Trial {trial}: Hungarian {hungarian_cost} != Brute force {brute_force_cost}"


def test_hungarian_vs_brute_force_4x4():
    """Test Hungarian matches brute force on 4x4 matrices."""
    rng = np.random.default_rng(456)

    for trial in range(5):
        # Generate random 4x4 cost matrix
        cost_matrix = rng.uniform(1, 100, size=(4, 4))

        # Create dummy vehicles and spaces
        vehicles = [
            Vehicle(id=f"V{i}", vehicle_type=VehicleType.regular, urgency=Urgency.normal)
            for i in range(4)
        ]
        spaces = [
            ParkingSpace(id=f"S{i}", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0)
            for i in range(4)
        ]

        # Hungarian result
        assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)
        hungarian_cost = sum(a.cost for a in assignments if a.space_id is not None)

        # Brute force result
        brute_force_cost = brute_force_assignment(cost_matrix)

        assert abs(hungarian_cost - brute_force_cost) < 1e-9, \
            f"Trial {trial}: Hungarian {hungarian_cost} != Brute force {brute_force_cost}"


def test_hungarian_handles_rectangular_matrix():
    """Test Hungarian handles more spaces than vehicles (n < m)."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V2", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=2, col=0),
        ParkingSpace(id="S3", space_type=SpaceType.regular, state=SpaceState.available, row=3, col=0),
        ParkingSpace(id="S4", space_type=SpaceType.regular, state=SpaceState.available, row=4, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # Should assign both vehicles
    assert len(assignments) == 2
    assert all(a.space_id is not None for a in assignments)

    # Should choose the two closest spaces (S1 and S2)
    assigned_spaces = sorted([a.space_id for a in assignments])
    assert assigned_spaces == ["S1", "S2"]


def test_hungarian_all_infeasible_results_in_unassigned():
    """Test that all infeasible assignments result in unassigned vehicles."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.ev, urgency=Urgency.normal),
        Vehicle(id="V2", vehicle_type=VehicleType.accessible, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=2, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # Both vehicles should be unassigned (no compatible spaces)
    assert len(assignments) == 2
    assert all(a.space_id is None for a in assignments)
    assert all(a.cost >= INFEASIBLE_COST for a in assignments)


def test_make_allocation_result_computes_metrics():
    """Test that make_allocation_result computes correct summary metrics."""
    from app.models import Assignment

    assignments = [
        Assignment(vehicle_id="V1", space_id="S1", cost=10.0, walking_distance=5.0),
        Assignment(vehicle_id="V2", space_id="S2", cost=20.0, walking_distance=10.0),
        Assignment(vehicle_id="V3", space_id=None, cost=INFEASIBLE_COST, walking_distance=0.0),
    ]

    result = make_allocation_result(assignments, num_spaces=10)

    assert result.num_unassigned == 1
    assert result.total_cost == 30.0  # 10 + 20
    assert result.average_walking_distance == 7.5  # (5 + 10) / 2
    assert result.utilization_percent == 20.0  # 2 assigned / 10 spaces * 100
