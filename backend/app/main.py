"""FastAPI application for parking allocation optimization."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    AllocationRequest, AllocateResponse, ExperimentRequest, ExperimentResult
)
from .cost import build_cost_matrix
from .greedy import greedy_allocate
from .optimizer import hungarian_allocate, make_allocation_result
from .experiment import run_experiment


app = FastAPI(
    title="Parking Allocation API",
    description="AI-Assisted Smart Parking Space Allocation Using Mathematical Optimization",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/allocate", response_model=AllocateResponse)
async def allocate(request: AllocationRequest):
    """Allocate vehicles to parking spaces using greedy and optimal methods.

    Returns comparison of both methods with cost matrix and metrics.
    """
    # Build cost matrix
    cost_matrix = build_cost_matrix(
        request.vehicles,
        request.spaces,
        request.entrance_row,
        request.entrance_col
    )

    # Run greedy allocation
    greedy_assignments = greedy_allocate(
        request.vehicles,
        request.spaces,
        cost_matrix,
        request.entrance_row,
        request.entrance_col
    )
    greedy_result = make_allocation_result(greedy_assignments, len(request.spaces))

    # Run optimal (Hungarian) allocation
    optimal_assignments = hungarian_allocate(
        request.vehicles,
        request.spaces,
        cost_matrix,
        request.entrance_row,
        request.entrance_col
    )
    optimal_result = make_allocation_result(optimal_assignments, len(request.spaces))

    # Calculate improvement percentage
    if greedy_result.total_cost > 0:
        improvement_percent = (
            (greedy_result.total_cost - optimal_result.total_cost) / greedy_result.total_cost
        ) * 100.0
    else:
        improvement_percent = 0.0

    # Prepare response
    vehicle_ids = [v.id for v in request.vehicles]
    space_ids = [s.id for s in request.spaces]
    cost_matrix_list = cost_matrix.tolist()

    return AllocateResponse(
        greedy=greedy_result,
        optimal=optimal_result,
        cost_matrix=cost_matrix_list,
        vehicle_ids=vehicle_ids,
        space_ids=space_ids,
        improvement_percent=improvement_percent
    )


@app.post("/experiment", response_model=ExperimentResult)
async def experiment(request: ExperimentRequest):
    """Run batch allocation experiment comparing greedy vs optimal methods.

    Generates random scenarios and returns aggregate statistics.
    """
    result = run_experiment(
        num_runs=request.num_runs,
        lot_size=request.lot_size,
        num_vehicles=request.num_vehicles,
        seed=request.seed
    )

    return result
