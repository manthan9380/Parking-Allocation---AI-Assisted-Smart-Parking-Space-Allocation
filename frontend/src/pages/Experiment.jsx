import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Experiment.css';
import { runExperiment } from '../api/client';

export default function Experiment() {
  const [numRuns, setNumRuns] = useState(100);
  const [lotSize, setLotSize] = useState(20);
  const [numVehicles, setNumVehicles] = useState(8);
  const [seed, setSeed] = useState(42);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRunExperiment = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await runExperiment(numRuns, lotSize, numVehicles, seed);
      setResults(result);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const chartData = [
    {
      name: 'Average Cost',
      Greedy: results?.avg_greedy_cost || 0,
      Optimal: results?.avg_optimal_cost || 0,
    },
  ];

  // Distribution data for histogram
  const distributionData = results ?
    Array.from({ length: 10 }, (_, i) => {
      const min = i * 10;
      const max = (i + 1) * 10;
      const count = results.improvements.filter(imp => imp >= min && imp < max).length;
      return {
        range: `${min}-${max}%`,
        count,
      };
    }) : [];

  return (
    <div className="container experiment-page">
      <div className="card">
        <h2>Batch Experiment</h2>
        <p style={{ fontSize: '12px', color: 'var(--accent)', marginBottom: '16px' }}>
          Run multiple random scenarios to compare greedy vs optimal allocation
        </p>

        <div className="experiment-form">
          <div className="form-field">
            <label>Number of Runs</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={numRuns}
              onChange={(e) => setNumRuns(parseInt(e.target.value) || 1)}
            />
          </div>
          <div className="form-field">
            <label>Lot Size (spaces)</label>
            <input
              type="number"
              min="4"
              max="50"
              value={lotSize}
              onChange={(e) => setLotSize(parseInt(e.target.value) || 4)}
            />
          </div>
          <div className="form-field">
            <label>Vehicles per Run</label>
            <input
              type="number"
              min="1"
              max="50"
              value={numVehicles}
              onChange={(e) => setNumVehicles(parseInt(e.target.value) || 1)}
            />
          </div>
          <div className="form-field">
            <label>Random Seed</label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 0)}
            />
          </div>
        </div>

        <div className="experiment-actions">
          <button onClick={handleRunExperiment} disabled={loading}>
            {loading ? 'Running...' : 'Run Experiment'}
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

      {results && (
        <div className="experiment-results">
          <div className="summary-metrics">
            <div className="summary-card">
              <div className="label">Avg Greedy Cost</div>
              <div className="value">{results.avg_greedy_cost.toFixed(2)}</div>
            </div>
            <div className="summary-card">
              <div className="label">Avg Optimal Cost</div>
              <div className="value">{results.avg_optimal_cost.toFixed(2)}</div>
            </div>
            <div className="summary-card">
              <div className="label">Avg Improvement</div>
              <div className="value">{results.avg_improvement_percent.toFixed(2)}%</div>
            </div>
          </div>

          <div className="chart-container">
            <h3>Cost Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg)',
                    border: '1px solid var(--border)',
                    borderRadius: '2px',
                    fontSize: '12px'
                  }}
                />
                <Legend />
                <Bar dataKey="Greedy" fill="#ffb74d" />
                <Bar dataKey="Optimal" fill="#4caf50" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>Improvement Distribution ({numRuns} runs)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg)',
                    border: '1px solid var(--border)',
                    borderRadius: '2px',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" fill="var(--accent)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
