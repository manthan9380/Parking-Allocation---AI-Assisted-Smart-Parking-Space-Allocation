"""Cost matrix construction for parking allocation.

Mathematical formulation:
    Minimize: sum_{i,j} c_ij * x_ij
    where x_ij = 1 if vehicle i is assigned to space j, else 0

    Cost function:
    c_ij = urgency_weight(i) * distance(j) + penalties

    Constraints (encoded as high cost):
    - Occupied/unavailable spaces: cost = INFEASIBLE_COST
    - EV vehicle requires EV charging space
    - Accessible vehicle requires accessible space
    - Regular/EV vehicles cannot use accessible spaces
"""

import numpy as np
from .models import Vehicle, ParkingSpace, SpaceState, VehicleType, SpaceType, Urgency


# Named constant for infeasible assignments
INFEASIBLE_COST = 1e6

# Urgency weights: higher weight = higher distance penalty = optimizer pushes vehicle closer
# The optimizer MINIMIZES cost, so urgent vehicles get higher weights to make distant spaces costly
URGENCY_WEIGHTS = {
    Urgency.high: 2.0,    # High urgency: distance costs 2x, optimizer prefers closer spaces
    Urgency.normal: 1.0,  # Normal urgency: baseline distance cost
    Urgency.low: 0.5,     # Low urgency: distance costs 0.5x, optimizer tolerates farther spaces
}


def manhattan_distance(row1: int, col1: int, row2: int, col2: int) -> int:
    """Calculate Manhattan distance between two points on the grid.

    Args:
        row1, col1: First point (e.g., parking space)
        row2, col2: Second point (e.g., entrance)

    Returns:
        Manhattan distance (sum of absolute differences)
    """
    return abs(row1 - row2) + abs(col1 - col2)


def build_cost_matrix(
    vehicles: list[Vehicle],
    spaces: list[ParkingSpace],
    entrance_row: int,
    entrance_col: int
) -> np.ndarray:
    """Build the cost matrix C where C[i,j] is the cost of assigning vehicle i to space j.

    Mathematical model:
        c_ij = w_urgency(i) * d_manhattan(space_j, entrance) + penalty(i, j)

        where penalty(i, j) is:
        - INFEASIBLE_COST if space is occupied/unavailable
        - INFEASIBLE_COST if vehicle type incompatible with space type
        - Small preference penalty (+5) if regular vehicle uses EV charger

    Type compatibility rules:
        - EV vehicle → only EV charging spaces (else INFEASIBLE)
        - Accessible vehicle → only accessible spaces (else INFEASIBLE)
        - Regular vehicle → regular or EV spaces (accessible is INFEASIBLE)
        - Regular on EV charger gets +5 penalty to leave chargers for EVs when possible

    Args:
        vehicles: List of vehicles requesting parking
        spaces: List of parking spaces in the lot
        entrance_row: Row coordinate of the entrance
        entrance_col: Column coordinate of the entrance

    Returns:
        Cost matrix of shape (n_vehicles, n_spaces)
    """
    n_vehicles = len(vehicles)
    n_spaces = len(spaces)
    cost_matrix = np.zeros((n_vehicles, n_spaces))

    for i, vehicle in enumerate(vehicles):
        for j, space in enumerate(spaces):
            # Start with infeasible cost, then check constraints
            cost = INFEASIBLE_COST

            # Check if space is unavailable
            if space.state in [SpaceState.occupied, SpaceState.unavailable]:
                cost = INFEASIBLE_COST

            # Check type compatibility
            elif vehicle.vehicle_type == VehicleType.ev:
                # EV vehicles require EV charging spaces
                if space.space_type == SpaceType.ev_charging:
                    distance = manhattan_distance(space.row, space.col, entrance_row, entrance_col)
                    cost = URGENCY_WEIGHTS[vehicle.urgency] * distance
                else:
                    cost = INFEASIBLE_COST

            elif vehicle.vehicle_type == VehicleType.accessible:
                # Accessible vehicles require accessible spaces
                if space.space_type == SpaceType.accessible:
                    distance = manhattan_distance(space.row, space.col, entrance_row, entrance_col)
                    cost = URGENCY_WEIGHTS[vehicle.urgency] * distance
                else:
                    cost = INFEASIBLE_COST

            elif vehicle.vehicle_type == VehicleType.regular:
                # Regular vehicles can use regular or EV spaces, but NOT accessible
                if space.space_type == SpaceType.accessible:
                    cost = INFEASIBLE_COST
                elif space.space_type == SpaceType.regular:
                    distance = manhattan_distance(space.row, space.col, entrance_row, entrance_col)
                    cost = URGENCY_WEIGHTS[vehicle.urgency] * distance
                elif space.space_type == SpaceType.ev_charging:
                    # Regular vehicle can use EV charger but with preference penalty
                    distance = manhattan_distance(space.row, space.col, entrance_row, entrance_col)
                    cost = URGENCY_WEIGHTS[vehicle.urgency] * distance + 5.0

            cost_matrix[i, j] = cost

    return cost_matrix
