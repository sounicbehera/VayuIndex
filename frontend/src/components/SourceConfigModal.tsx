import React, { useState, useEffect } from 'react';
import { X, SlidersHorizontal, Globe, Plane, Layers, Plus, Trash2 } from 'lucide-react';

interface SourceConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'corridors' | 'sources';
}

export default function SourceConfigModal({ isOpen, onClose, initialTab = 'corridors' }: SourceConfigModalProps) {
  const [activeTab, setActiveTab] = useState(initialTab);
  
  useEffect(() => {
    if (isOpen) {
      setActiveTab(initialTab);
    }
  }, [isOpen, initialTab]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-[#0b1329] border border-cyan-900/40 rounded-xl w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-cyan-900/40 bg-[#070d1d]">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5 text-cyan-400" />
            Configuration & Telemetry
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-800 bg-[#070d1d] px-6 overflow-x-auto">
          <button
            onClick={() => setActiveTab('corridors')}
            className={`px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
              activeTab === 'corridors' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-2"><Layers className="w-4 h-4" /> City-Pair Corridors & Weights</div>
          </button>
          <button
            onClick={() => setActiveTab('sources')}
            className={`px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
              activeTab === 'sources' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="flex items-center gap-2"><Globe className="w-4 h-4" /> Target Sources (Airlines & OTAs)</div>
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6 text-slate-300">
          {activeTab === 'corridors' && <CorridorsTab />}
          {activeTab === 'sources' && <SourcesTab />}
        </div>
      </div>
    </div>
  );
}

function CorridorsTab() {
  const [routes, setRoutes] = useState([
    { id: 'DEL-BOM', weight: '22.0%' },
    { id: 'DEL-BLR', weight: '14.5%' },
  ]);

  const removeRoute = (id: string) => {
    setRoutes(routes.filter(r => r.id !== id));
  };

  const addRoute = () => {
    if (!routes.find(r => r.id === 'BOM-BLR')) {
      setRoutes([...routes, { id: 'BOM-BLR', weight: '10.0%' }]);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-white">Active Domestic Trunk Corridors</h3>
        <div className="flex items-center gap-2 text-xs font-mono font-medium px-3 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Total Weight: 100.0%
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {routes.map(route => (
          <div key={route.id} className="flex items-center justify-between p-3 bg-slate-900 border border-slate-800 rounded-lg">
            <div className="flex items-center gap-3">
              <input type="checkbox" defaultChecked className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-slate-900" />
              <span className="font-mono text-white">{route.id}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-cyan-400 font-mono text-sm">{route.weight}</span>
              <button onClick={() => removeRoute(route.id)} className="text-slate-500 hover:text-rose-400 transition"><Trash2 className="w-4 h-4" /></button>
            </div>
          </div>
        ))}
      </div>
      <div className="pt-4 border-t border-slate-800">
        <button onClick={addRoute} className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300 font-medium transition">
          <Plus className="w-4 h-4" /> Add New Sector Pair
        </button>
      </div>
    </div>
  );
}

function SourcesTab() {
  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Plane className="w-5 h-5 text-sky-400" /> Target Airlines (5 Domestic Carriers)
        </h3>
        <div className="grid gap-3">
          {[
            { name: 'IndiGo (6E)', type: 'LCC', share: '62.4%' },
          ].map(airline => (
            <div key={airline.name} className="flex items-center justify-between p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <div>
                <div className="font-medium text-white">{airline.name}</div>
                <div className="text-xs text-slate-400">{airline.type} • {airline.share} Domestic Share</div>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Active
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5 text-indigo-400" /> Online Travel Aggregators (6 OTAs)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {['MakeMyTrip'].map(ota => (
            <div key={ota} className="flex flex-col gap-2 p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="font-medium text-white">{ota}</span>
                <span className="text-[10px] uppercase tracking-wider text-slate-500">Live API/Scrape</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono mt-1">
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Pulse OK
                </div>
                <span className="text-slate-400">~{Math.floor(Math.random() * 200 + 300)}ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
