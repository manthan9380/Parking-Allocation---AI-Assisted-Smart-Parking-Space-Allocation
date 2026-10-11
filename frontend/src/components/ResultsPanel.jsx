import './ResultsPanel.css';

export default function ResultsPanel({ results }) {
  if (!results) return null;

  const { greedy, optimal, improvement_percent } = results;

  return (
    <div className="results-panel">
      <div className="improvement-banner">
        Optimal method improved cost by
        <span className="improvement-value">{improvement_percent.toFixed(2)}%</span>
        compared to greedy
      </div>

      <div className="results-comparison">
        <div className="result-card">
          <h4>Greedy (Baseline)</h4>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Total Cost:</span>
              <span className="metric-value">{greedy.total_cost.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Avg Walking Distance:</span>
              <span className="metric-value">{greedy.average_walking_distance.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Unassigned:</span>
              <span className="metric-value">{greedy.num_unassigned}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Utilization:</span>
              <span className="metric-value">{greedy.utilization_percent.toFixed(1)}%</span>
            </div>
          </div>

          <div className="assignments-table-wrapper">
            <table className="assignments-table">
              <thead>
                <tr>
                  <th>Vehicle</th>
                  <th>Space</th>
                  <th>Cost</th>
                  <th>Distance</th>
                </tr>
              </thead>
              <tbody>
                {greedy.assignments.map(a => (
                  <tr key={a.vehicle_id}>
                    <td>{a.vehicle_id}</td>
                    <td>{a.space_id || 'unassigned'}</td>
                    <td>{a.cost >= 1e6 ? '∞' : a.cost.toFixed(2)}</td>
                    <td>{a.walking_distance.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="result-card">
          <h4>Hungarian (Optimal)</h4>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Total Cost:</span>
              <span className="metric-value">{optimal.total_cost.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Avg Walking Distance:</span>
              <span className="metric-value">{optimal.average_walking_distance.toFixed(2)}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Unassigned:</span>
              <span className="metric-value">{optimal.num_unassigned}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Utilization:</span>
              <span className="metric-value">{optimal.utilization_percent.toFixed(1)}%</span>
            </div>
          </div>

          <div className="assignments-table-wrapper">
            <table className="assignments-table">
              <thead>
                <tr>
                  <th>Vehicle</th>
                  <th>Space</th>
                  <th>Cost</th>
                  <th>Distance</th>
                </tr>
              </thead>
              <tbody>
                {optimal.assignments.map(a => (
                  <tr key={a.vehicle_id}>
                    <td>{a.vehicle_id}</td>
                    <td>{a.space_id || 'unassigned'}</td>
                    <td>{a.cost >= 1e6 ? '∞' : a.cost.toFixed(2)}</td>
                    <td>{a.walking_distance.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
