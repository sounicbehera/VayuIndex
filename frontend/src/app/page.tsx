'use client';

import React, { useEffect, useState } from 'react';
import { 
  Plane, 
  ShieldCheck, 
  Layers, 
  RefreshCw,
  Download,
  SlidersHorizontal,
  Globe
} from 'lucide-react';
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ComposedChart,
  BarChart,
  Bar,
  Legend,
  AreaChart,
  Area,
  LineChart,
  Line
} from 'recharts';
import { 
  fetchLatestIndex, 
  fetchElasticity, 
  fetchRoutes, 
  fetchBenchmark,
  IndexRecord, 
  ElasticityMetric, 
  RouteBreakdown,
  BenchmarkPoint
} from '@/lib/api';
import SourceConfigModal from '@/components/SourceConfigModal';
import ProofOfDocumentModal from '@/components/ProofOfDocumentModal';

export default function Dashboard() {
  const [latestIndex, setLatestIndex] = useState<IndexRecord | null>(null);
  const [elasticityData, setElasticityData] = useState<ElasticityMetric[]>([]);
  const [routesData, setRoutesData] = useState<RouteBreakdown[]>([]);
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [isSourceModalOpen, setIsSourceModalOpen] = useState(false);
  const [sourceModalTab, setSourceModalTab] = useState<'corridors' | 'sources'>('corridors');
  const [isProofModalOpen, setIsProofModalOpen] = useState(false);

  const openSourceModal = (tab: 'corridors' | 'sources') => {
    setSourceModalTab(tab);
    setIsSourceModalOpen(true);
  };

  const openProofModal = () => {
    setIsProofModalOpen(true);
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [indexRes, elastRes, routeRes, benchRes] = await Promise.all([
        fetchLatestIndex().catch(() => null),
        fetchElasticity().catch(() => []),
        fetchRoutes().catch(() => []),
        fetchBenchmark().catch(() => []),
      ]);
      setLatestIndex(indexRes);
      setElasticityData(elastRes);
      setRoutesData(routeRes);
      setBenchmarkData(benchRes);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <SourceConfigModal 
        isOpen={isSourceModalOpen} 
        onClose={() => setIsSourceModalOpen(false)} 
        initialTab={sourceModalTab} 
      />
      <ProofOfDocumentModal 
        isOpen={isProofModalOpen}
        onClose={() => setIsProofModalOpen(false)}
      />

      {/* Streamlined Action Header */}
      <header className="flex flex-col lg:flex-row lg:items-center justify-between border-b border-slate-800 pb-6 mb-8 gap-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-lg text-sky-400">
              <Plane className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                vayuIndex (6E-Proxy Baseline) <span className="text-xs bg-sky-500/20 text-sky-400 border border-sky-500/30 px-2 py-0.5 rounded font-mono">APIx Engine v1.0</span>
              </h1>
              <p className="text-xs text-slate-400 mt-1">High-Frequency Econometric Airfare Price Index for Retail CPI Augmentation (MoSPI / RBI)</p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button 
            onClick={openProofModal}
            className="flex items-center gap-2 text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-2 rounded-md font-medium transition"
          >
            <ShieldCheck className="w-4 h-4" /> Proof of Document
          </button>
          
          <button 
            onClick={() => openSourceModal('corridors')}
            className="flex items-center gap-2 text-xs bg-[#0b1329] hover:bg-slate-800 text-cyan-400 border border-cyan-900/40 px-3 py-2 rounded-md font-medium transition"
          >
            <SlidersHorizontal className="w-4 h-4" /> Configure City-Pairs
          </button>
          
          <button 
            onClick={() => openSourceModal('sources')}
            className="flex items-center gap-2 text-xs bg-[#0b1329] hover:bg-slate-800 text-cyan-400 border border-cyan-900/40 px-3 py-2 rounded-md font-medium transition"
          >
            <Globe className="w-4 h-4" /> Sources (5 Airlines / 6 OTAs)
          </button>

          <div className="h-6 w-px bg-slate-700 mx-1 hidden sm:block"></div>
          
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/export/mospi-report.csv`}
            download="vayuIndex_MoSPI_CPI_SubClass58_Report.csv"
            className="flex items-center gap-1.5 text-xs bg-sky-600 hover:bg-sky-500 text-white font-medium px-3 py-2 rounded-md transition border border-sky-400/30"
          >
            <Download className="w-4 h-4" /> Export MoSPI CSV
          </a>
          
          <button 
            onClick={loadDashboardData} 
            className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-md border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>
      </header>

      {/* 30-Day Historical Time Series Benchmark Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">30-Day Time-Series: vayuIndex (6E-Proxy Baseline) vs Official MoSPI CPI Sub-Class 58</h2>
            <p className="text-xs text-slate-400">Comparing real-time high-frequency price discovery with official lagged monthly publications (r = 0.6881)</p>
          </div>
        </div>
        <div className="h-80 w-full min-h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={benchmarkData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="index_date" stroke="#64748b" fontSize={11} tickFormatter={(str) => str.slice(5)} />
              <YAxis stroke="#64748b" fontSize={11} domain={['dataMin - 5', 'dataMax + 5']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line type="monotone" dataKey="apix_value" name="High-Freq vayuIndex (6E-Proxy Baseline)" stroke="#38bdf8" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="mospi_proxy_value" name="Official MoSPI CPI (Lagged)" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Lead-Time Elasticity Curve */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Lead-Time Elasticity Curve (ΔP / ΔT)</h2>
              <p className="text-xs text-slate-400">Deconstructing Base Fare surge pricing vs statutory airport taxes</p>
            </div>
          </div>
          <div className="h-72 w-full min-h-[288px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={elasticityData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="advance_window" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} tickFormatter={(val) => `₹${val}`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val: any) => [`₹${val}`, '']}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Area type="monotone" dataKey="avg_total_fare" name="Avg Total Fare (₹)" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorTotal)" />
                <Area type="monotone" dataKey="avg_base_fare" name="Base Fare (₹)" stroke="#6366f1" fillOpacity={1} fill="url(#colorBase)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* DGCA Sector Passenger Volume Weights */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Corridor Pricing vs DGCA Weights</h2>
              <p className="text-xs text-slate-400">Sector-specific average fare and institutional index weighting</p>
            </div>
          </div>
          <div className="h-72 w-full min-h-[288px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={routesData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="route_id" stroke="#64748b" fontSize={12} />
                <YAxis yAxisId="left" stroke="#64748b" fontSize={12} tickFormatter={(val) => `₹${val}`} />
                <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={12} tickFormatter={(val) => `${(Number(val) * 100).toFixed(0)}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val: any, name: any) => {
                    if (name === 'Avg Fare (₹)') return [`₹${Number(val).toFixed(2)}`, name];
                    if (name === 'DGCA Passenger Weight (%)') return [`${(Number(val) * 100).toFixed(2)}%`, name];
                    return [val, name];
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar yAxisId="left" dataKey="avg_total_fare" name="Avg Fare (₹)" fill="#0284c7" radius={[4, 4, 0, 0]} />
                <Line yAxisId="right" type="monotone" dataKey="dgca_passenger_weight" name="DGCA Passenger Weight (%)" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Corridor Breakdown Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-x-auto">
        <h2 className="text-base font-semibold text-white mb-1">Domestic Corridor Matrix & Econometric Attributes</h2>
        <p className="text-xs text-slate-400 mb-4">Real-time quotes breakdown across high-density metro routes</p>
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
            <tr>
              <th className="px-4 py-3">Route ID</th>
              <th className="px-4 py-3">Origin / Destination</th>
              <th className="px-4 py-3">DGCA Weight (w_i)</th>
              <th className="px-4 py-3">Sample Quotes</th>
              <th className="px-4 py-3">Min Fare</th>
              <th className="px-4 py-3">Max Fare</th>
              <th className="px-4 py-3">Avg Market Fare</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {routesData.map((route) => (
              <tr key={route.route_id} className="hover:bg-slate-800/40">
                <td className="px-4 py-3 font-bold text-sky-400">{route.route_id}</td>
                <td className="px-4 py-3 text-slate-300">{route.origin_city} → {route.destination_city}</td>
                <td className="px-4 py-3 text-amber-400">{(Number(route.dgca_passenger_weight) * 100).toFixed(1)}%</td>
                <td className="px-4 py-3 text-slate-300">{route.quote_count}</td>
                <td className="px-4 py-3 text-emerald-400">₹{Number(route.min_fare).toFixed(2)}</td>
                <td className="px-4 py-3 text-rose-400">₹{Number(route.max_fare).toFixed(2)}</td>
                <td className="px-4 py-3 font-bold text-white">₹{Number(route.avg_total_fare).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}