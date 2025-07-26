import React from 'react';
import StockList from './StockList';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1 className="text-2xl font-bold mb-6">株式分析システム</h1>
      </header>
      <main className="p-4 max-w-4xl mx-auto">
        <StockList />
      </main>
    </div>
  );
}

export default App;
