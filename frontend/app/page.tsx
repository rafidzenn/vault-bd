'use client';
import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, DollarSign, PieChart } from 'lucide-react';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [categories, setCategories] = useState<any[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Get Anomaly/Forecast logic
      const resAnalyze = await fetch('https://rafidzenn-vault-bd-api.hf.space/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amounts: [120, 150, 135, 450, 140, 160] })
      });
      const dataAnalyze = await resAnalyze.json();
      setResults(dataAnalyze);

      // 2. Get Real MongoDB Category Aggregates
      const resMeta = await fetch('https://rafidzenn-vault-bd-api.hf.space/analytics');
      const dataMeta = await resMeta.json();
      setCategories(dataMeta.category_summaries);
    } catch (err) {
      console.error("Fetch error:", err);
    }
    setLoading(false);
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen font-sans text-slate-900">
      <h1 className="text-3xl font-bold mb-8">Vault BD Dashboard</h1>
      
      <button 
        onClick={fetchData}
        className="mb-8 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition shadow-md"
      >
        {loading ? 'Fetching Live Data...' : 'Sync with MongoDB'}
      </button>

      {results && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 text-amber-600 mb-2 font-semibold">
              <AlertCircle size={20} /> Anomalies
            </div>
            <p className="text-3xl font-bold">{results.anomalies_detected.length}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center gap-2 text-blue-600 mb-2 font-semibold">
              <TrendingUp size={20} /> Forecast
            </div>
            <p className="text-3xl font-bold">${results.forecasted_next_month}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 text-green-700">
             <div className="flex items-center gap-2 mb-2 font-semibold text-green-600">
              <DollarSign size={20} /> DB Status
            </div>
            <p className="text-lg font-medium">{results.database}</p>
          </div>
        </div>
      )}

      {categories.length > 0 && (
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-2 text-slate-700 mb-6 font-bold text-xl">
            <PieChart size={24} /> Category Distribution (Live from Atlas)
          </div>
          <div className="space-y-4">
            {categories.map((item: any) => (
              <div key={item._id} className="flex items-center justify-between border-b pb-2">
                <span className="capitalize text-slate-600 font-medium">{item._id}</span>
                <span className="bg-slate-100 px-3 py-1 rounded-full text-sm font-bold">{item.count} items</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
