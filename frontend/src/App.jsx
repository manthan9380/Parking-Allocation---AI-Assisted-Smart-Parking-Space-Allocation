import { useState } from 'react';
import './App.css';
import Simulator from './pages/Simulator';
import Experiment from './pages/Experiment';
import Method from './pages/Method';

function App() {
  const [currentPage, setCurrentPage] = useState('simulator');

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1 className="app-title">Parking Allocation</h1>
          <nav className="app-nav">
            <a
              href="#simulator"
              className={currentPage === 'simulator' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setCurrentPage('simulator'); }}
            >
              Simulator
            </a>
            <a
              href="#experiment"
              className={currentPage === 'experiment' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setCurrentPage('experiment'); }}
            >
              Experiment
            </a>
            <a
              href="#method"
              className={currentPage === 'method' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setCurrentPage('method'); }}
            >
              Method
            </a>
          </nav>
        </div>
      </header>

      <main>
        {currentPage === 'simulator' && <Simulator />}
        {currentPage === 'experiment' && <Experiment />}
        {currentPage === 'method' && <Method />}
      </main>
    </div>
  );
}

export default App;
