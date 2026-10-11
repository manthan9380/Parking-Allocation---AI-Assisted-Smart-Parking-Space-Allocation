import { useState } from 'react';
import './ParkingGrid.css';

export default function ParkingGrid({ spaces, setSpaces, cols = 5, assignedSpaces = new Set() }) {
  const cycleState = (spaceId) => {
    setSpaces(spaces.map(space => {
      if (space.id === spaceId) {
        const states = ['available', 'occupied', 'unavailable'];
        const currentIndex = states.indexOf(space.state);
        const nextState = states[(currentIndex + 1) % states.length];
        return { ...space, state: nextState };
      }
      return space;
    }));
  };

  const gridStyle = {
    gridTemplateColumns: `repeat(${cols}, 1fr)`,
  };

  return (
    <div>
      <div className="parking-grid" style={gridStyle}>
        {spaces.map(space => {
          const isAssigned = assignedSpaces.has(space.id);
          const className = `parking-space ${isAssigned ? 'assigned' : space.state}`;

          return (
            <div
              key={space.id}
              className={className}
              onClick={() => cycleState(space.id)}
              title={`${space.id}: ${space.space_type} (${space.state})`}
            >
              <span className="space-id">{space.id}</span>
              <span className="space-type">
                {space.space_type === 'ev_charging' ? 'EV' :
                 space.space_type === 'accessible' ? 'ACC' : 'REG'}
              </span>
            </div>
          );
        })}
      </div>

      <div className="grid-legend">
        <div className="legend-item">
          <div className="legend-box" style={{ background: 'var(--available)' }}></div>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <div className="legend-box" style={{ background: 'var(--occupied)' }}></div>
          <span>Occupied</span>
        </div>
        <div className="legend-item">
          <div className="legend-box" style={{ background: 'var(--unavailable)' }}></div>
          <span>Unavailable</span>
        </div>
        <div className="legend-item">
          <div className="legend-box" style={{ background: 'var(--assigned)', borderWidth: '2px', borderColor: 'var(--accent)' }}></div>
          <span>Newly Assigned</span>
        </div>
      </div>
    </div>
  );
}
