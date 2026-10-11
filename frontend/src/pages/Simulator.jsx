import { useState } from 'react';
import './Simulator.css';
import ParkingGrid from '../components/ParkingGrid';
import VehicleQueue from '../components/VehicleQueue';
import ResultsPanel from '../components/ResultsPanel';
import CostMatrix from '../components/CostMatrix';
import ExportButton from '../components/ExportButton';
import { allocate } from '../api/client';

// Initialize default parking lot (20 spaces in 4x5 grid)
function createDefaultLot() {
  const spaces = [];
  const types = ['regular', 'regular', 'regular', 'regular', 'regular',
                 'regular', 'regular', 'regular', 'regular', 'regular',
                 'regular', 'regular', 'regular', 'ev_charging', 'ev_charging',
                 'ev_charging', 'accessible', 'accessible', 'regular', 'regular'];

  for (let i = 0; i < 20; i++) {
    const row = Math.floor(i / 5);
    const col = i % 5;
    spaces.push({
      id: `S${i + 1}`,
      space_type: types[i],
      state: 'available',
      row,
      col,
    });
  }
  return spaces;
}

export default function Simulator() {
  const [spaces, setSpaces] = useState(createDefaultLot());
  const [vehicles, setVehicles] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runAllocation = async () => {
    if (vehicles.length === 0) {
      setError('Please add at least one vehicle');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await allocate(spaces, vehicles, 0, 0);
      setResults(result);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const resetLot = () => {
    setSpaces(createDefaultLot());
    setVehicles([]);
    setResults(null);
    setError(null);
  };

  // Get assigned space IDs for highlighting
  const assignedSpaces = new Set();
  if (results) {
    results.optimal.assignments.forEach(a => {
      if (a.space_id) assignedSpaces.add(a.space_id);
    });
  }

  return (
    <div className="container">
      <div className="simulator-layout">
        <div className="simulator-main">
          <div className="card">
            <h2>Parking Lot (4×5 grid)</h2>
            <p style={{ fontSize: '12px', color: 'var(--accent)', marginBottom: '12px' }}>
              Click a space to cycle its state: Available → Occupied → Unavailable
            </p>
            <ParkingGrid
              spaces={spaces}
              setSpaces={setSpaces}
              cols={5}
              assignedSpaces={assignedSpaces}
            />
          </div>

          {results && (
            <>
              <div className="card">
                <ResultsPanel results={results} />
              </div>
              <div className="card">
                <CostMatrix
                  costMatrix={results.cost_matrix}
                  vehicleIds={results.vehicle_ids}
                  spaceIds={results.space_ids}
                />
                <ExportButton results={results} />
              </div>
            </>
          )}
        </div>

        <div className="simulator-sidebar">
          <div className="card">
            <h2>Vehicle Queue</h2>
            <VehicleQueue vehicles={vehicles} setVehicles={setVehicles} />

            <div className="action-buttons">
              <button onClick={runAllocation} disabled={loading || vehicles.length === 0}>
                {loading ? 'Running...' : 'Run Allocation'}
              </button>
              <button className="secondary" onClick={resetLot}>
                Reset All
              </button>
            </div>

            {error && (
              <div style={{
                marginTop: '12px',
                padding: '8px',
                background: 'var(--occupied)',
                border: '1px solid var(--border)',
                borderRadius: '2px',
                fontSize: '12px'
              }}>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
