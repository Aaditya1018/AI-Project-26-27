import React, { useState } from 'react';
import { PlayCircle, AlertTriangle, Box, ShieldAlert, Sparkles, Check, Flame } from 'lucide-react';
import { triggerSimulation } from '../services/api';

export default function SimulationControls({
  selectedBayId,
  onScenarioTriggered
}) {
  const [selectedCategory, setSelectedCategory] = useState('Electronics & Fragile');
  const [triggering, setTriggering] = useState(null);
  const [lastSuccess, setLastSuccess] = useState(null);

  const categories = [
    'Electronics & Fragile',
    'Glassware & Ceramics',
    'Heavy Industrial Goods',
    'Perishables & Cold Chain',
    'General Boxed Cargo'
  ];

  const behaviors = [
    { code: 'BEH_DROP', name: 'Product Dropped from Height', defaultTier: 'Critical', desc: 'Freefall kinetics ay ~ 9.8 m/s², height > 1.2m' },
    { code: 'BEH_DRAG', name: 'Floor Dragging Cartons', defaultTier: 'High', desc: 'Sustained ground friction abrasion > 4.0m' },
    { code: 'BEH_IMPROPER_STACK', name: 'Inverted Pyramid Stacking', defaultTier: 'Critical', desc: 'Heavy mass crate balanced atop small fragile base' },
    { code: 'BEH_PALLET_OVERHANG', name: 'Unsafe Pallet Overhang & Tilt', defaultTier: 'High', desc: 'Box overhang > 30% beyond pallet boundary' },
    { code: 'BEH_ROUGH_HANDLING', name: 'Rough Handling / Slamming', defaultTier: 'High', desc: 'Severe impact shock deceleration upon landing' },
    { code: 'BEH_TOSS_THROW', name: 'Carton Tossing / Throwing', defaultTier: 'Critical', desc: 'Parabolic airborne trajectory without hand contact' },
    { code: 'BEH_STEP_ON_CARGO', name: 'Stepping / Sitting on Cargo', defaultTier: 'Critical', desc: 'Personnel weight load directly atop cargo packaging' },
    { code: 'BEH_OVERSTACK', name: 'Over-Stacking Height Limit', defaultTier: 'Medium', desc: 'Exceeding 2.1m safe clearance threshold' },
    { code: 'BEH_ROLLING_TUMBLE', name: 'Rolling / Tumbling Cartons', defaultTier: 'Medium', desc: 'Cyclic corner flipping instead of lifted transfer' },
    { code: 'BEH_FORKLIFT_PINCH', name: 'Forklift / Pedestrian Hazard', defaultTier: 'Critical', desc: 'Moving forklift operating < 1.0m from dock worker' }
  ];

  const handleTrigger = async (beh) => {
    setTriggering(beh.code);
    try {
      const res = await triggerSimulation(selectedBayId, beh.code, selectedCategory);
      setLastSuccess(`Injected ${beh.name} into ${selectedBayId}`);
      if (onScenarioTriggered) onScenarioTriggered(res.event);
      setTimeout(() => setLastSuccess(null), 4000);
    } catch (e) {
      alert('Simulation trigger failed: ' + e.message);
    } finally {
      setTriggering(null);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <PlayCircle className="w-5 h-5 text-emerald-400" /> 10-Behavior Damage Taxonomy Simulator
          </h2>
          <p className="text-xs text-slate-400">
            Inject sequence-level actions into active bay video feeds to validate CV detection & risk scoring
          </p>
        </div>

        {/* Product Category Selector */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium">Cargo Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500 font-medium"
          >
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {lastSuccess && (
        <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/40 text-emerald-400 text-xs flex items-center gap-2 animate-in fade-in">
          <Check className="w-4 h-4" />
          <span>{lastSuccess} — Processed by Computer Vision & Alert Broadcast!</span>
        </div>
      )}

      {/* 10-Behavior Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {behaviors.map(beh => (
          <button
            key={beh.code}
            disabled={triggering === beh.code}
            onClick={() => handleTrigger(beh)}
            className="p-3 rounded-xl border bg-slate-950/70 border-slate-800 hover:border-emerald-500/60 hover:bg-slate-800/80 transition-all text-left flex flex-col justify-between group disabled:opacity-50"
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                  beh.defaultTier === 'Critical' ? 'bg-rose-500/20 text-rose-400' :
                  (beh.defaultTier === 'High' ? 'bg-amber-500/20 text-amber-400' : 'bg-yellow-500/20 text-yellow-400')
                }`}>
                  {beh.defaultTier}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">{beh.code.replace('BEH_', '')}</span>
              </div>
              <h4 className="text-xs font-semibold text-white group-hover:text-emerald-300 transition-colors">
                {beh.name}
              </h4>
              <p className="text-[10px] text-slate-400 mt-1 line-clamp-2">
                {beh.desc}
              </p>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400 group-hover:text-emerald-400">
              <span>{triggering === beh.code ? 'Simulating...' : 'Inject Event'}</span>
              <PlayCircle className="w-3.5 h-3.5" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
