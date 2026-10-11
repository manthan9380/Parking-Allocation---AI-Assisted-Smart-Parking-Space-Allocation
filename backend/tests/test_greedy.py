"""Tests for greedy allocator."""

import numpy as np
import pytest
from app.greedy import greedy_allocate
from app.cost import build_cost_matrix, INFEASIBLE_COST
from app.models import (
    Vehicle, ParkingSpace, VehicleType, SpaceType, SpaceState, Urgency
)
from app.optimizer import hungarian_allocate, make_allocation_result
from app.experiment import generate_random_lot, generate_random_vehicles


def test_greedy_assigns_nearest_available():
    """Test that greedy assigns vehicles to nearest available spaces."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=5, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S3", space_type=SpaceType.regular, state=SpaceState.available, row=3, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # Should assign to S2 (closest at distance 1)
    assert len(assignments) == 1
    assert assignments[0].vehicle_id == "V1"
    assert assignments[0].space_id == "S2"
    assert assignments[0].walking_distance == 1.0


def test_greedy_marks_vehicle_unassigned_when_no_compatible_space():
    """Test that greedy leaves vehicle unassigned when no compatible space exists."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.ev, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.accessible, state=SpaceState.available, row=2, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # EV vehicle should be unassigned (no EV charging spaces)
    assert len(assignments) == 1
    assert assignments[0].vehicle_id == "V1"
    assert assignments[0].space_id is None
    assert assignments[0].cost >= INFEASIBLE_COST


def test_greedy_respects_occupied_spaces():
    """Test that greedy doesn't assign occupied spaces."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.occupied, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=3, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # Should skip S1 (occupied) and assign to S2
    assert assignments[0].space_id == "S2"


def test_greedy_processes_first_come_first_served():
    """Test that greedy processes vehicles in order."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V2", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)
    assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row=0, entrance_col=0)

    # V1 gets the only space, V2 is unassigned
    assert assignments[0].vehicle_id == "V1"
    assert assignments[0].space_id == "S1"

    assert assignments[1].vehicle_id == "V2"
    assert assignments[1].space_id is None


def test_greedy_never_beats_optimal():
    """Test that greedy never produces lower cost than optimal over 50 random scenarios."""
    rng = np.random.default_rng(42)

    for run_idx in range(50):
        # Generate random scenario
        lot_size = 20
        num_vehicles = 8

        spaces, entrance_row, entrance_col = generate_random_lot(rng, lot_size)
        vehicles = generate_random_vehicles(rng, num_vehicles)

        # Build cost matrix
        cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row, entrance_col)

        # Run both methods
        greedy_assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row, entrance_col)
        optimal_assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row, entrance_col)

        greedy_result = make_allocation_result(greedy_assignments, lot_size)
        optimal_result = make_allocation_result(optimal_assignments, lot_size)

        # Optimal should never exceed greedy cost
        assert optimal_result.total_cost <= greedy_result.total_cost, \
            f"Run {run_idx}: Optimal cost {optimal_result.total_cost} > Greedy cost {greedy_result.total_cost}"
