import { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import './Method.css';

function Latex({ children, display = false }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      katex.render(children, containerRef.current, {
        displayMode: display,
        throwOnError: false,
      });
    }
  }, [children, display]);

  return <span ref={containerRef}></span>;
}

export default function Method() {
  return (
    <div className="container method-page">
      <div className="card">
        <h2>Mathematical Formulation</h2>

        <div className="method-section">
          <h3>Objective Function</h3>
          <div className="formula-block">
            <Latex display>{String.raw`\text{minimize} \quad \sum_{i=1}^{n} \sum_{j=1}^{m} c_{ij} \cdot x_{ij}`}</Latex>
          </div>
          <p style={{ fontSize: '13px', marginTop: '8px' }}>
            where <Latex>{String.raw`x_{ij} = 1`}</Latex> if vehicle <Latex>{String.raw`i`}</Latex> is assigned to space <Latex>{String.raw`j`}</Latex>, else <Latex>{String.raw`x_{ij} = 0`}</Latex>
          </p>
        </div>

        <div className="method-section">
          <h3>Cost Function</h3>
          <div className="formula-block">
            <Latex display>{String.raw`c_{ij} = w_{\text{urgency}}(i) \cdot d_{\text{Manhattan}}(j, \text{entrance}) + \text{penalties}(i, j)`}</Latex>
          </div>

          <div className="cost-function-details">
            <p><strong>Urgency Weights:</strong></p>
            <ul style={{ marginLeft: '20px', marginTop: '6px' }}>
              <li>High urgency: <code>w = 2.0</code> (distance costs more → optimizer assigns closer spaces)</li>
              <li>Normal urgency: <code>w = 1.0</code> (baseline)</li>
              <li>Low urgency: <code>w = 0.5</code> (distance costs less → optimizer tolerates farther spaces)</li>
            </ul>

            <p style={{ marginTop: '12px' }}><strong>Type Compatibility Penalties:</strong></p>
            <ul style={{ marginLeft: '20px', marginTop: '6px' }}>
              <li>EV vehicle → only EV charging spaces (else <Latex>{String.raw`10^6`}</Latex>)</li>
              <li>Accessible vehicle → only accessible spaces (else <Latex>{String.raw`10^6`}</Latex>)</li>
              <li>Regular vehicle → regular or EV spaces (accessible = <Latex>{String.raw`10^6`}</Latex>)</li>
              <li>Regular vehicle on EV charger: <code>+5</code> preference penalty</li>
            </ul>
          </div>
        </div>

        <div className="method-section">
          <h3>Constraints</h3>
          <ul className="constraint-list">
            <li>
              <div className="formula-block">
                <Latex display>{String.raw`\sum_{j=1}^{m} x_{ij} \leq 1 \quad \forall i`}</Latex>
              </div>
              <p style={{ fontSize: '12px', marginTop: '4px' }}>Each vehicle gets at most one space</p>
            </li>
            <li>
              <div className="formula-block">
                <Latex display>{String.raw`\sum_{i=1}^{n} x_{ij} \leq 1 \quad \forall j`}</Latex>
              </div>
              <p style={{ fontSize: '12px', marginTop: '4px' }}>Each space is assigned to at most one vehicle</p>
            </li>
            <li>
              <div className="formula-block">
                <Latex display>{String.raw`x_{ij} \in \{0, 1\}`}</Latex>
              </div>
              <p style={{ fontSize: '12px', marginTop: '4px' }}>Binary decision variables</p>
            </li>
          </ul>
        </div>

        <div className="method-section">
          <h3>Worked Example (3×3)</h3>

          <div className="worked-example">
            <h4>Cost Matrix</h4>
            <div className="example-matrix">
              <table>
                <thead>
                  <tr>
                    <th></th>
                    <th>S1</th>
                    <th>S2</th>
                    <th>S3</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th>V1</th>
                    <td>2</td>
                    <td>5</td>
                    <td>8</td>
                  </tr>
                  <tr>
                    <th>V2</th>
                    <td>3</td>
                    <td>2</td>
                    <td>6</td>
                  </tr>
                  <tr>
                    <th>V3</th>
                    <td>7</td>
                    <td>4</td>
                    <td>1</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="example-solution">
              <h4>Optimal Assignment (Hungarian Algorithm)</h4>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', marginTop: '8px' }}>
                <div>V1 → S1 (cost = 2)</div>
                <div>V2 → S2 (cost = 2)</div>
                <div>V3 → S3 (cost = 1)</div>
                <div style={{ marginTop: '12px', fontWeight: '600', fontSize: '14px' }}>
                  Total Cost = 5
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="method-section">
          <h3>Algorithm</h3>
          <p style={{ fontSize: '13px', lineHeight: '1.6' }}>
            The Hungarian algorithm (also known as the Kuhn-Munkres algorithm) solves the assignment problem
            in polynomial time O(n³). It finds the minimum-cost perfect matching in a bipartite graph by:
          </p>
          <ol style={{ marginLeft: '20px', marginTop: '8px', fontSize: '13px', lineHeight: '1.8' }}>
            <li>Starting with dual variables for each row and column</li>
            <li>Finding an initial matching using the reduced cost matrix</li>
            <li>Iteratively improving the matching using alternating paths</li>
            <li>Guaranteeing the global optimum upon termination</li>
          </ol>
          <p style={{ fontSize: '13px', lineHeight: '1.6', marginTop: '12px' }}>
            This implementation uses <code>scipy.optimize.linear_sum_assignment</code>, which handles
            rectangular matrices (more spaces than vehicles) natively.
          </p>
        </div>
      </div>
    </div>
  );
}
