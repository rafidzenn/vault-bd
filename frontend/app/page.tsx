'use client';
import React, { useState } from 'react';
import { AlertCircle, TrendingUp, DollarSign } from 'lucide-react';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://rafidzenn-vault-bd-api.hf.space/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amounts: [120, 150, 135, 450, 140, 160] }) // Example data
      });
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Failed to fetch from HF:", err);
    }
    setLoading(false);
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans">
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Vault BD Dashboard</h1>
      
      <button 
        onClick={runAnalysis}
        className="mb-8 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
      >
        {loading ? 'Analyzing...' : 'Run Anomaly Check'}
      </button>

      {results && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 text-amber-600 mb-2">
              <AlertCircle size={20} />
              <span className="font-semibold">Anomalies</span>
            </div>
            <p className="text-2xl font-bold">{results.anomalies_detected.length} Found</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 text-blue-600 mb-2">
              <TrendingUp size={20} />
              <span className="font-semibold">Forecast</span>
            </div>
            <p className="text-2xl font-bold">${results.forecasted_next_month}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 text-green-600 mb-2">
              <DollarSign size={20} />
              <span className="font-semibold">Average Spend</span>
            </div>
            <p className="text-2xl font-bold">${results.average_spend}</p>
          </div>
        </div>
      )}
    </div>
  );
}
