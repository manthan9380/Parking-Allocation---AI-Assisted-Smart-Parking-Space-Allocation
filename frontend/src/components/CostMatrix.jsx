import { useState } from 'react';
import './CostMatrix.css';

export default function CostMatrix({ costMatrix, vehicleIds, spaceIds }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!costMatrix || !vehicleIds || !spaceIds) return null;

  return (
    <div className="cost-matrix">
      <div className="collapsible-header" onClick={() => setIsOpen(!isOpen)}>
        <h3>Cost Matrix</h3>
        <span>{isOpen ? '▼' : '▶'}</span>
      </div>

      {isOpen && (
        <div className="matrix-table-wrapper">
          <table className="matrix-table">
            <thead>
              <tr>
                <th></th>
                {spaceIds.map(sid => (
                  <th key={sid}>{sid}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {costMatrix.map((row, i) => (
                <tr key={vehicleIds[i]}>
                  <th>{vehicleIds[i]}</th>
                  {row.map((cost, j) => (
                    <td key={j} className={cost >= 1e6 ? 'infeasible' : ''}>
                      {cost >= 1e6 ? '∞' : cost.toFixed(1)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
