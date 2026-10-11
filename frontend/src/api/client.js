const API_BASE_URL = 'http://localhost:8000';

export async function allocate(spaces, vehicles, entranceRow = 0, entranceCol = 0) {
  const response = await fetch(`${API_BASE_URL}/allocate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      spaces,
      vehicles,
      entrance_row: entranceRow,
      entrance_col: entranceCol,
    }),
  });

  if (!response.ok) {
    throw new Error(`Allocation failed: ${response.statusText}`);
  }

  return response.json();
}

export async function runExperiment(numRuns = 100, lotSize = 20, numVehicles = 8, seed = 42) {
  const response = await fetch(`${API_BASE_URL}/experiment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      num_runs: numRuns,
      lot_size: lotSize,
      num_vehicles: numVehicles,
      seed,
    }),
  });

  if (!response.ok) {
    throw new Error(`Experiment failed: ${response.statusText}`);
  }

  return response.json();
}
