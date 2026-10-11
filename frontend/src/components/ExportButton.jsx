export default function ExportButton({ results }) {
  if (!results) return null;

  const exportJSON = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `parking-allocation-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportCSV = () => {
    let csv = 'Method,Vehicle,Space,Cost,Walking Distance\n';

    results.greedy.assignments.forEach(a => {
      csv += `Greedy,${a.vehicle_id},${a.space_id || 'unassigned'},${a.cost},${a.walking_distance}\n`;
    });

    results.optimal.assignments.forEach(a => {
      csv += `Optimal,${a.vehicle_id},${a.space_id || 'unassigned'},${a.cost},${a.walking_distance}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `parking-allocation-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
      <button className="secondary" onClick={exportJSON}>Export JSON</button>
      <button className="secondary" onClick={exportCSV}>Export CSV</button>
    </div>
  );
}
