"""Pydantic models for parking allocation API."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SpaceType(str, Enum):
    """Type of parking space."""
    regular = "regular"
    ev_charging = "ev_charging"
    accessible = "accessible"


class SpaceState(str, Enum):
    """State of a parking space."""
    available = "available"
    occupied = "occupied"
    unavailable = "unavailable"


class VehicleType(str, Enum):
    """Type of vehicle."""
    regular = "regular"
    ev = "ev"
    accessible = "accessible"


class Urgency(str, Enum):
    """Urgency level for vehicle parking."""
    low = "low"
    normal = "normal"
    high = "high"


class ParkingSpace(BaseModel):
    """A parking space in the lot."""
    id: str
    space_type: SpaceType
    state: SpaceState
    row: int
    col: int


class Vehicle(BaseModel):
    """A vehicle requesting parking."""
    id: str
    vehicle_type: VehicleType
    urgency: Urgency


class AllocationRequest(BaseModel):
    """Request to allocate vehicles to parking spaces."""
    spaces: list[ParkingSpace]
    vehicles: list[Vehicle]
    entrance_row: int = Field(default=0, description="Row coordinate of parking lot entrance")
    entrance_col: int = Field(default=0, description="Column coordinate of parking lot entrance")


class Assignment(BaseModel):
    """Assignment of a vehicle to a parking space."""
    vehicle_id: str
    space_id: Optional[str] = None
    cost: float
    walking_distance: float


class AllocationResult(BaseModel):
    """Result of an allocation method."""
    assignments: list[Assignment]
    total_cost: float
    average_walking_distance: float
    num_unassigned: int
    utilization_percent: float


class AllocateResponse(BaseModel):
    """Response from /allocate endpoint."""
    greedy: AllocationResult
    optimal: AllocationResult
    cost_matrix: list[list[float]]
    vehicle_ids: list[str]
    space_ids: list[str]
    improvement_percent: float


class ExperimentRequest(BaseModel):
    """Request to run batch allocation experiment."""
    num_runs: int = Field(default=100, ge=1, le=1000)
    lot_size: int = Field(default=20, ge=4, le=50)
    num_vehicles: int = Field(default=8, ge=1, le=50)
    seed: int = Field(default=42)


class ExperimentResult(BaseModel):
    """Result of batch allocation experiment."""
    avg_greedy_cost: float
    avg_optimal_cost: float
    avg_improvement_percent: float
    improvements: list[float]
    greedy_costs: list[float]
    optimal_costs: list[float]
