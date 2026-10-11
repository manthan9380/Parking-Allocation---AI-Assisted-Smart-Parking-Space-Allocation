# Parking Allocation - AI-Assisted Smart Parking Space Allocation

A web application that demonstrates mathematical optimization for parking space allocation using the Hungarian algorithm (linear sum assignment).

## Project Structure

```
cmai/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI routes
│   │   ├── models.py         # Pydantic data models
│   │   ├── cost.py           # Cost matrix construction
│   │   ├── greedy.py         # Greedy baseline allocator
│   │   ├── optimizer.py      # Hungarian algorithm (optimal)
│   │   └── experiment.py     # Batch experiment runner
│   ├── tests/
│   │   ├── test_cost.py      # Cost matrix tests
│   │   ├── test_greedy.py    # Greedy allocator tests
│   │   ├── test_optimizer.py # Hungarian algorithm tests
│   │   └── test_api.py       # API integration tests
│   └── requirements.txt
└── frontend/          # React + Vite frontend
    ├── src/
    │   ├── api/client.js         # API client
    │   ├── components/           # Reusable components
    │   ├── pages/                # Simulator, Experiment, Method
    │   ├── App.jsx               # Main app with navigation
    │   └── index.css             # Global styles
    └── package.json
```

## Mathematical Model

### Objective Function
Minimize the total weighted cost:

```
minimize: Σ(i,j) c_ij * x_ij
```

where:
- `x_ij = 1` if vehicle `i` is assigned to space `j`, else `0`
- `c_ij` is the cost of assigning vehicle `i` to space `j`

### Cost Function

```
c_ij = urgency_weight(i) * manhattan_distance(space_j, entrance) + penalties
```

**Urgency Weights:**
- High urgency: 2.0 (distance costs more → optimizer assigns closer spaces)
- Normal urgency: 1.0 (baseline)
- Low urgency: 0.5 (distance costs less → optimizer tolerates farther spaces)

**Type Compatibility (Hard Constraints):**
- EV vehicles → only EV charging spaces (else INFEASIBLE_COST = 10⁶)
- Accessible vehicles → only accessible spaces (else INFEASIBLE_COST)
- Regular vehicles → regular or EV spaces (accessible spaces = INFEASIBLE_COST)
- Regular vehicles using EV chargers get +5 preference penalty (to leave chargers for EVs)

### Constraints
1. Each vehicle gets at most one space: `Σ_j x_ij ≤ 1` for all `i`
2. Each space is assigned to at most one vehicle: `Σ_i x_ij ≤ 1` for all `j`
3. Occupied/unavailable spaces are excluded (encoded as INFEASIBLE_COST)
4. Type compatibility constraints (encoded as INFEASIBLE_COST)

### Methods Compared

**Greedy (Baseline):**
- First-come, nearest-available heuristic
- Process vehicles in order, assign each to the closest compatible available space
- Simple but suboptimal

**Hungarian Algorithm (Optimal):**
- Uses `scipy.optimize.linear_sum_assignment`
- Finds the globally optimal assignment that minimizes total cost
- Handles rectangular matrices (more spaces than vehicles)

## Setup

### Backend

1. **Create Python 3.12 virtual environment:**
   ```bash
   cd backend
   uv venv --python 3.12 .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```
   
   All 25 tests should pass.

### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Build (optional):**
   ```bash
   npm run build
   ```

## Running the Application

You need to run both the backend and frontend servers.

### Start Backend Server

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Start Frontend Development Server

In a separate terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

Open your browser and navigate to `http://localhost:5173` to use the application.

## API Endpoints

### `GET /health`
Health check endpoint.

### `POST /allocate`
Allocate vehicles to parking spaces using both greedy and optimal methods.

**Request:**
```json
{
  "vehicles": [
    {"id": "V1", "vehicle_type": "regular", "urgency": "high"},
    {"id": "V2", "vehicle_type": "ev", "urgency": "normal"}
  ],
  "spaces": [
    {"id": "S1", "space_type": "regular", "state": "available", "row": 1, "col": 0},
    {"id": "S2", "space_type": "ev_charging", "state": "available", "row": 2, "col": 0}
  ],
  "entrance_row": 0,
  "entrance_col": 0
}
```

**Response:**
```json
{
  "greedy": {
    "assignments": [...],
    "total_cost": 25.0,
    "average_walking_distance": 3.5,
    "num_unassigned": 0,
    "utilization_percent": 10.0
  },
  "optimal": {
    "assignments": [...],
    "total_cost": 20.0,
    "average_walking_distance": 3.0,
    "num_unassigned": 0,
    "utilization_percent": 10.0
  },
  "cost_matrix": [[2.0, 1e6], [1e6, 4.0]],
  "vehicle_ids": ["V1", "V2"],
  "space_ids": ["S1", "S2"],
  "improvement_percent": 20.0
}
```

### `POST /experiment`
Run batch experiment with random scenarios.

**Request:**
```json
{
  "num_runs": 100,
  "lot_size": 20,
  "num_vehicles": 8,
  "seed": 42
}
```

**Response:**
```json
{
  "avg_greedy_cost": 45.2,
  "avg_optimal_cost": 38.7,
  "avg_improvement_percent": 14.4,
  "improvements": [12.5, 15.3, ...],
  "greedy_costs": [50.0, 48.2, ...],
  "optimal_costs": [43.8, 40.8, ...]
}
```

## Algorithm Details

### Hungarian Algorithm
The Hungarian algorithm (also known as the Kuhn-Munkres algorithm) solves the assignment problem in polynomial time O(n³). It finds the minimum-cost perfect matching in a bipartite graph.

**Why it's optimal:**
- Explores all possible assignments systematically
- Uses dual variables and alternating paths to iteratively improve the solution
- Guarantees global optimum for the linear assignment problem

**Worked Example (3×3):**

Cost matrix:
```
       S1  S2  S3
  V1 [  2   5   8 ]
  V2 [  3   2   6 ]
  V3 [  7   4   1 ]
```

Optimal assignment: V1→S1 (2) + V2→S2 (2) + V3→S3 (1) = **Total: 5**

### Random Number Generation
All random scenario generation uses `numpy.random.default_rng(seed)` for reproducibility. The same seed always produces the same sequence of scenarios, making experiments repeatable.

## Testing

The test suite covers:
- **Cost matrix construction:** dimensions, urgency weights, type compatibility, Manhattan distance
- **Greedy allocator:** nearest-available logic, constraint handling, never beats optimal
- **Hungarian optimizer:** worked example, brute-force verification (3×3, 4×4), rectangular matrices
- **API integration:** endpoint responses, edge cases, reproducibility

Run all tests:
```bash
cd backend
python3 -m pytest tests/ -v
```

Run specific test file:
```bash
python3 -m pytest tests/test_optimizer.py -v
```

## License
University assignment project.
