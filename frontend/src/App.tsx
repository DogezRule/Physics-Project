import React, { useState } from 'react';
import Scene from './components/Scene';
import ControlPanel from './components/ControlPanel';
import TelemetryPanel from './components/TelemetryPanel';
import type { CalculationResponse } from './api';
import './App.css';

const App: React.FC = () => {
  const [result, setResult] = useState<CalculationResponse | null>(null);
  const [target, setTarget] = useState({ x: 10, y: 0, z: 0 });

  const handleCalculationResult = (data: CalculationResponse, newTarget: { x: number, y: number, z: number }) => {
    setResult(data);
    setTarget(newTarget);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', overflow: 'hidden', background: '#050510' }}>
      <Scene trajectory={result?.trajectory || []} target={target} />

      <ControlPanel onCalculationResult={handleCalculationResult} />

      <TelemetryPanel trajectory={result?.trajectory || []} lastResult={result} />
    </div>
  );
};

export default App;
