import { useState } from 'react';
import './VehicleQueue.css';

export default function VehicleQueue({ vehicles, setVehicles }) {
  const [vehicleType, setVehicleType] = useState('regular');
  const [urgency, setUrgency] = useState('normal');

  const addVehicle = () => {
    const newVehicle = {
      id: `V${vehicles.length + 1}`,
      vehicle_type: vehicleType,
      urgency: urgency,
    };
    setVehicles([...vehicles, newVehicle]);
  };

  const removeVehicle = (id) => {
    setVehicles(vehicles.filter(v => v.id !== id));
  };

  const addRandomVehicles = (count = 5) => {
    const types = ['regular', 'ev', 'accessible'];
    const urgencies = ['low', 'normal', 'high'];
    const weights = {
      types: [0.7, 0.2, 0.1],
      urgencies: [0.2, 0.6, 0.2],
    };

    const newVehicles = [];
    for (let i = 0; i < count; i++) {
      const typeRand = Math.random();
      const urgencyRand = Math.random();

      let type = 'regular';
      if (typeRand < weights.types[2]) type = 'accessible';
      else if (typeRand < weights.types[1] + weights.types[2]) type = 'ev';

      let urg = 'normal';
      if (urgencyRand < weights.urgencies[0]) urg = 'low';
      else if (urgencyRand > weights.urgencies[0] + weights.urgencies[1]) urg = 'high';

      newVehicles.push({
        id: `V${vehicles.length + newVehicles.length + 1}`,
        vehicle_type: type,
        urgency: urg,
      });
    }
    setVehicles([...vehicles, ...newVehicles]);
  };

  const clearAll = () => {
    setVehicles([]);
  };

  return (
    <div className="vehicle-queue">
      <div className="add-vehicle-form">
        <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)}>
          <option value="regular">Regular</option>
          <option value="ev">EV</option>
          <option value="accessible">Accessible</option>
        </select>
        <select value={urgency} onChange={(e) => setUrgency(e.target.value)}>
          <option value="low">Low Urgency</option>
          <option value="normal">Normal Urgency</option>
          <option value="high">High Urgency</option>
        </select>
        <button onClick={addVehicle}>Add Vehicle</button>
      </div>

      {vehicles.length > 0 && (
        <div className="vehicle-list">
          {vehicles.map(vehicle => (
            <div key={vehicle.id} className="vehicle-item">
              <div className="vehicle-info">
                <span className="vehicle-id">{vehicle.id}</span>
                <span>{vehicle.vehicle_type === 'ev' ? 'EV' : vehicle.vehicle_type === 'accessible' ? 'Accessible' : 'Regular'}</span>
                <span>({vehicle.urgency})</span>
              </div>
              <button className="secondary" onClick={() => removeVehicle(vehicle.id)}>Remove</button>
            </div>
          ))}
        </div>
      )}

      <div className="queue-controls">
        <button className="secondary" onClick={() => addRandomVehicles(5)}>Add 5 Random</button>
        {vehicles.length > 0 && (
          <button className="secondary" onClick={clearAll}>Clear All</button>
        )}
      </div>
    </div>
  );
}
