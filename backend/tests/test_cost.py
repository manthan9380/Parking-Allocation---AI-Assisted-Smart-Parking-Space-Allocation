"""Tests for cost matrix construction."""

import numpy as np
import pytest
from app.cost import (
    build_cost_matrix, manhattan_distance, INFEASIBLE_COST, URGENCY_WEIGHTS
)
from app.models import (
    Vehicle, ParkingSpace, VehicleType, SpaceType, SpaceState, Urgency
)


def test_manhattan_distance():
    """Test Manhattan distance calculation."""
    assert manhattan_distance(0, 0, 0, 0) == 0
    assert manhattan_distance(0, 0, 3, 4) == 7
    assert manhattan_distance(2, 3, 5, 1) == 5
    assert manhattan_distance(1, 1, 4, 5) == 7


def test_cost_matrix_dimensions():
    """Test cost matrix has correct shape."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V2", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.available, row=0, col=1),
        ParkingSpace(id="S3", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    assert cost_matrix.shape == (2, 3)


def test_occupied_spaces_get_infeasible_cost():
    """Test that occupied/unavailable spaces receive INFEASIBLE_COST."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.occupied, row=0, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.regular, state=SpaceState.unavailable, row=0, col=1),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    assert cost_matrix[0, 0] == INFEASIBLE_COST
    assert cost_matrix[0, 1] == INFEASIBLE_COST


def test_ev_vehicle_requires_ev_space():
    """Test that EV vehicles can only use EV charging spaces."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.ev, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.ev_charging, state=SpaceState.available, row=2, col=0),
        ParkingSpace(id="S3", space_type=SpaceType.accessible, state=SpaceState.available, row=3, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    # Regular and accessible spaces should be infeasible for EV
    assert cost_matrix[0, 0] == INFEASIBLE_COST  # regular
    assert cost_matrix[0, 2] == INFEASIBLE_COST  # accessible

    # EV charging space should have finite cost
    assert cost_matrix[0, 1] < INFEASIBLE_COST
    assert cost_matrix[0, 1] == URGENCY_WEIGHTS[Urgency.normal] * 2  # distance = 2


def test_accessible_vehicle_requires_accessible_space():
    """Test that accessible vehicles can only use accessible spaces."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.accessible, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.ev_charging, state=SpaceState.available, row=2, col=0),
        ParkingSpace(id="S3", space_type=SpaceType.accessible, state=SpaceState.available, row=3, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    # Regular and EV spaces should be infeasible for accessible vehicle
    assert cost_matrix[0, 0] == INFEASIBLE_COST  # regular
    assert cost_matrix[0, 1] == INFEASIBLE_COST  # EV

    # Accessible space should have finite cost
    assert cost_matrix[0, 2] < INFEASIBLE_COST
    assert cost_matrix[0, 2] == URGENCY_WEIGHTS[Urgency.normal] * 3  # distance = 3


def test_regular_vehicle_cannot_use_accessible_space():
    """Test that regular vehicles cannot use accessible spaces."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=1, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.accessible, state=SpaceState.available, row=2, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    # Regular space should be feasible
    assert cost_matrix[0, 0] < INFEASIBLE_COST

    # Accessible space should be infeasible
    assert cost_matrix[0, 1] == INFEASIBLE_COST


def test_urgency_weights_affect_costs():
    """Test that urgency weights correctly scale distance costs."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.low),
        Vehicle(id="V2", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
        Vehicle(id="V3", vehicle_type=VehicleType.regular, urgency=Urgency.high),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=2, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    distance = 2  # Manhattan distance from (0,0) to (2,0)

    # Check that costs are scaled by urgency weights
    assert cost_matrix[0, 0] == URGENCY_WEIGHTS[Urgency.low] * distance      # 0.5 * 2 = 1.0
    assert cost_matrix[1, 0] == URGENCY_WEIGHTS[Urgency.normal] * distance   # 1.0 * 2 = 2.0
    assert cost_matrix[2, 0] == URGENCY_WEIGHTS[Urgency.high] * distance     # 2.0 * 2 = 4.0

    # High urgency should have highest cost (optimizer will assign closer spaces)
    assert cost_matrix[2, 0] > cost_matrix[1, 0] > cost_matrix[0, 0]


def test_regular_vehicle_ev_charger_preference_penalty():
    """Test that regular vehicles get a small penalty for using EV chargers."""
    vehicles = [
        Vehicle(id="V1", vehicle_type=VehicleType.regular, urgency=Urgency.normal),
    ]
    spaces = [
        ParkingSpace(id="S1", space_type=SpaceType.regular, state=SpaceState.available, row=2, col=0),
        ParkingSpace(id="S2", space_type=SpaceType.ev_charging, state=SpaceState.available, row=2, col=0),
    ]

    cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row=0, entrance_col=0)

    distance = 2
    base_cost = URGENCY_WEIGHTS[Urgency.normal] * distance

    # Regular space should have base cost
    assert cost_matrix[0, 0] == base_cost

    # EV charger should have base cost + 5 penalty
    assert cost_matrix[0, 1] == base_cost + 5.0

    # Both should be feasible (< INFEASIBLE_COST)
    assert cost_matrix[0, 0] < INFEASIBLE_COST
    assert cost_matrix[0, 1] < INFEASIBLE_COST
