"""Hungarian algorithm (optimal) allocator for parking spaces.

Uses scipy.optimize.linear_sum_assignment to solve the assignment problem optimally.
This implements the Hungarian algorithm, which finds the minimum-cost perfect matching
in a bipartite graph (vehicles to spaces).
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from .models import Vehicle, ParkingSpace, Assignment, AllocationResult
from .cost import INFEASIBLE_COST, manhattan_distance


def hungarian_allocate(
    vehicles: list[Vehicle],
    spaces: list[ParkingSpace],
    cost_matrix: np.ndarray,
    entrance_row: int,
    entrance_col: int
) -> list[Assignment]:
    """Allocate vehicles to spaces using the Hungarian algorithm (optimal).

    Mathematical formulation:
        Minimize: sum_{i,j} c_ij * x_ij
        Subject to:
            sum_j x_ij <= 1  for all i  (each vehicle gets at most one space)
            sum_i x_ij <= 1  for all j  (each space gets at most one vehicle)
            x_ij in {0, 1}

    The scipy implementation handles rectangular matrices (n < m) natively.
    Any assignment with cost >= INFEASIBLE_COST is treated as unassigned.

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

    # Run Hungarian algorithm
    # Returns: row_ind (vehicle indices), col_ind (space indices) of optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Build assignment list
    assignments = []
    assigned_vehicles = set()

    for i, j in zip(row_ind, col_ind):
        vehicle = vehicles[i]
        space = spaces[j]
        cost = cost_matrix[i, j]

        if cost >= INFEASIBLE_COST:
            # Infeasible assignment - vehicle is unassigned
            assignments.append(Assignment(
                vehicle_id=vehicle.id,
                space_id=None,
                cost=cost,
                walking_distance=0.0
            ))
        else:
            # Feasible assignment
            walking_distance = manhattan_distance(
                space.row, space.col, entrance_row, entrance_col
            )

            assignments.append(Assignment(
                vehicle_id=vehicle.id,
                space_id=space.id,
                cost=cost,
                walking_distance=float(walking_distance)
            ))

        assigned_vehicles.add(i)

    # Handle any vehicles that weren't in the assignment (shouldn't happen with scipy, but be safe)
    for i in range(n_vehicles):
        if i not in assigned_vehicles:
            assignments.append(Assignment(
                vehicle_id=vehicles[i].id,
                space_id=None,
                cost=INFEASIBLE_COST,
                walking_distance=0.0
            ))

    return assignments


def make_allocation_result(
    assignments: list[Assignment],
    num_spaces: int
) -> AllocationResult:
    """Compute summary metrics from a list of assignments.

    Args:
        assignments: List of vehicle-to-space assignments
        num_spaces: Total number of spaces in the lot

    Returns:
        AllocationResult with computed metrics
    """
    num_assigned = sum(1 for a in assignments if a.space_id is not None)
    num_unassigned = len(assignments) - num_assigned

    total_cost = sum(a.cost for a in assignments if a.space_id is not None)

    if num_assigned > 0:
        total_walking_distance = sum(a.walking_distance for a in assignments if a.space_id is not None)
        average_walking_distance = total_walking_distance / num_assigned
        utilization_percent = (num_assigned / num_spaces) * 100.0
    else:
        average_walking_distance = 0.0
        utilization_percent = 0.0

    return AllocationResult(
        assignments=assignments,
        total_cost=total_cost,
        average_walking_distance=average_walking_distance,
        num_unassigned=num_unassigned,
        utilization_percent=utilization_percent
    )
