"""Batch experiment runner for comparing greedy vs optimal allocation.

Generates random parking scenarios and evaluates both methods to measure
the improvement from mathematical optimization.
"""

import numpy as np
from .models import (
    Vehicle, ParkingSpace, VehicleType, SpaceType, SpaceState, Urgency,
    ExperimentResult
)
from .cost import build_cost_matrix
from .greedy import greedy_allocate
from .optimizer import hungarian_allocate, make_allocation_result


def generate_random_lot(
    rng: np.random.Generator,
    lot_size: int
) -> tuple[list[ParkingSpace], int, int]:
    """Generate a random parking lot with a grid layout.

    Distribution:
        - ~70% regular spaces
        - ~15% EV charging spaces
        - ~15% accessible spaces
        - ~20% of spaces are occupied

    Args:
        rng: Random number generator
        lot_size: Total number of spaces

    Returns:
        Tuple of (spaces list, entrance_row, entrance_col)
    """
    # Create a roughly square grid
    cols = int(np.ceil(np.sqrt(lot_size)))
    rows = int(np.ceil(lot_size / cols))

    spaces = []
    space_id = 0

    for row in range(rows):
        for col in range(cols):
            if space_id >= lot_size:
                break

            # Determine space type
            rand = rng.random()
            if rand < 0.70:
                space_type = SpaceType.regular
            elif rand < 0.85:
                space_type = SpaceType.ev_charging
            else:
                space_type = SpaceType.accessible

            # Determine state (80% available, 20% occupied)
            state = SpaceState.occupied if rng.random() < 0.20 else SpaceState.available

            spaces.append(ParkingSpace(
                id=f"S{space_id}",
                space_type=space_type,
                state=state,
                row=row,
                col=col
            ))
            space_id += 1

    # Entrance at (0, 0) for simplicity
    entrance_row, entrance_col = 0, 0

    return spaces, entrance_row, entrance_col


def generate_random_vehicles(
    rng: np.random.Generator,
    num_vehicles: int
) -> list[Vehicle]:
    """Generate random vehicles with varied types and urgencies.

    Distribution:
        - ~70% regular vehicles
        - ~20% EV vehicles
        - ~10% accessible vehicles
        - Urgency: 20% low, 60% normal, 20% high

    Args:
        rng: Random number generator
        num_vehicles: Number of vehicles to generate

    Returns:
        List of vehicles
    """
    vehicles = []

    for i in range(num_vehicles):
        # Determine vehicle type
        rand = rng.random()
        if rand < 0.70:
            vehicle_type = VehicleType.regular
        elif rand < 0.90:
            vehicle_type = VehicleType.ev
        else:
            vehicle_type = VehicleType.accessible

        # Determine urgency
        rand = rng.random()
        if rand < 0.20:
            urgency = Urgency.low
        elif rand < 0.80:
            urgency = Urgency.normal
        else:
            urgency = Urgency.high

        vehicles.append(Vehicle(
            id=f"V{i}",
            vehicle_type=vehicle_type,
            urgency=urgency
        ))

    return vehicles


def run_experiment(
    num_runs: int,
    lot_size: int,
    num_vehicles: int,
    seed: int
) -> ExperimentResult:
    """Run batch allocation experiment comparing greedy vs optimal methods.

    For each run:
        1. Generate a random parking lot and vehicle set
        2. Run greedy allocation
        3. Run optimal (Hungarian) allocation
        4. Record costs and improvement percentage

    Args:
        num_runs: Number of random scenarios to test
        lot_size: Number of parking spaces per scenario
        num_vehicles: Number of vehicles per scenario
        seed: Random seed for reproducibility

    Returns:
        ExperimentResult with aggregate statistics
    """
    rng = np.random.default_rng(seed)

    greedy_costs = []
    optimal_costs = []
    improvements = []

    for run_idx in range(num_runs):
        # Generate random scenario
        spaces, entrance_row, entrance_col = generate_random_lot(rng, lot_size)
        vehicles = generate_random_vehicles(rng, num_vehicles)

        # Build cost matrix
        cost_matrix = build_cost_matrix(vehicles, spaces, entrance_row, entrance_col)

        # Run greedy allocation
        greedy_assignments = greedy_allocate(vehicles, spaces, cost_matrix, entrance_row, entrance_col)
        greedy_result = make_allocation_result(greedy_assignments, lot_size)

        # Run optimal allocation
        optimal_assignments = hungarian_allocate(vehicles, spaces, cost_matrix, entrance_row, entrance_col)
        optimal_result = make_allocation_result(optimal_assignments, lot_size)

        # Record costs
        greedy_cost = greedy_result.total_cost
        optimal_cost = optimal_result.total_cost

        greedy_costs.append(greedy_cost)
        optimal_costs.append(optimal_cost)

        # Calculate improvement percentage
        if greedy_cost > 0:
            improvement = ((greedy_cost - optimal_cost) / greedy_cost) * 100.0
        else:
            improvement = 0.0

        improvements.append(improvement)

    # Compute aggregate metrics
    avg_greedy_cost = float(np.mean(greedy_costs))
    avg_optimal_cost = float(np.mean(optimal_costs))
    avg_improvement_percent = float(np.mean(improvements))

    return ExperimentResult(
        avg_greedy_cost=avg_greedy_cost,
        avg_optimal_cost=avg_optimal_cost,
        avg_improvement_percent=avg_improvement_percent,
        improvements=improvements,
        greedy_costs=greedy_costs,
        optimal_costs=optimal_costs
    )
