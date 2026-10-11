"""Greedy baseline allocator for parking spaces.

This implements a simple first-come, nearest-available heuristic:
- Process vehicles in order
- For each vehicle, assign it to the available space with lowest cost
- Mark assigned spaces as taken
"""

import numpy as np
from .models import Vehicle, ParkingSpace, Assignment
from .cost import INFEASIBLE_COST, manhattan_distance


def greedy_allocate(
    vehicles: list[Vehicle],
    spaces: list[ParkingSpace],
    cost_matrix: np.ndarray,
    entrance_row: int,
    entrance_col: int
) -> list[Assignment]:
    """Allocate vehicles to spaces using a greedy nearest-available strategy.

    Algorithm:
        For each vehicle in order:
            1. Find the available space with minimum cost
            2. If cost < INFEASIBLE_COST, assign vehicle to that space
            3. Mark space as taken
            4. Otherwise, leave vehicle unassigned

    Args:
        vehicles: List of vehicles to assign
        spaces: List of parking spaces
        cost_matrix: Pre-computed cost matrix (n_vehicles x n_spaces)
        entrance_row: Row coordinate of entrance (for distance calculation)
        entrance_col: Column coordinate of entrance

    Returns:
        List of Assignment objects, one per vehicle
    """
    n_vehicles = len(vehicles)
    n_spaces = len(spaces)

    # Track which spaces are still available
    available = np.ones(n_spaces, dtype=bool)

    assignments = []

    for i in range(n_vehicles):
        vehicle = vehicles[i]

        # Get costs for this vehicle to all available spaces
        costs = cost_matrix[i].copy()
        costs[~available] = INFEASIBLE_COST  # Mark taken spaces as infeasible

        # Find the space with minimum cost
        j = np.argmin(costs)
        min_cost = costs[j]

        if min_cost >= INFEASIBLE_COST:
            # No feasible space available
            assignments.append(Assignment(
                vehicle_id=vehicle.id,
                space_id=None,
                cost=min_cost,
                walking_distance=0.0
            ))
        else:
            # Assign vehicle to this space
            space = spaces[j]
            walking_distance = manhattan_distance(
                space.row, space.col, entrance_row, entrance_col
            )

            assignments.append(Assignment(
                vehicle_id=vehicle.id,
                space_id=space.id,
                cost=min_cost,
                walking_distance=float(walking_distance)
            ))

            # Mark space as taken
            available[j] = False

    return assignments
