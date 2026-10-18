import React, { useState } from 'react';
import { Video, ShieldAlert, Eye, EyeOff, UserCheck, Maximize2, AlertTriangle, Box, Users } from 'lucide-react';

export default function LiveBaysGrid({
  bays,
  selectedBayId,
  onSelectBay,
  privacyMode,
  onChangePrivacyMode,
  onQuickSimulate
}) {
  const [fullscreenBay, setFullscreenBay] = useState(null);

  const activeBay = bays.find(b => b.bay_id === selectedBayId) || bays[0] || {
    bay_id: 'BAY-01',
    bay_name: 'Bay-01 (Inbound Cargo)',
    current_risk_level: 'Low',
    active_workers: 2,
    active_packages: 18
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'Critical': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case 'High': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'Medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    }
  };

  const getStreamUrl = (bayId) => {
    const isPrivacy = privacyMode !== 'none';
    const isSilhouettes = privacyMode === 'silhouettes';
    return `/api/bays/${bayId}/stream?privacy=${isPrivacy}&silhouettes=${isSilhouettes}`;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
      {/* Grid Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Video className="w-5 h-5 text-emerald-400" /> Live Loading Bay Intelligence Feeds
          </h2>
          <p className="text-xs text-slate-400">
            Real-time multi-frame tracking, kinematics calculation, and edge privacy safeguards
          </p>
        </div>

        {/* Responsible AI Privacy Shield Mode Selector */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
          <span className="px-2 text-slate-400 flex items-center gap-1 font-semibold">
            <UserCheck className="w-3.5 h-3.5 text-emerald-400" /> Privacy Shield:
          </span>
          <button
            onClick={() => onChangePrivacyMode('blur')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              privacyMode === 'blur'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Face Blur
          </button>
          <button
            onClick={() => onChangePrivacyMode('silhouettes')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              privacyMode === 'silhouettes'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Silhouette Avatar
          </button>
          <button
            onClick={() => onChangePrivacyMode('none')}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              privacyMode === 'none'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Raw CCTV
          </button>
        </div>
      </div>

      {/* Loading Bay Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {bays.map(bay => (
          <button
            key={bay.bay_id}
            onClick={() => onSelectBay(bay.bay_id)}
            className={`p-3 rounded-xl border text-left transition-all relative overflow-hidden ${
              selectedBayId === bay.bay_id
                ? 'bg-slate-800/90 border-emerald-500/60 shadow-md shadow-emerald-500/10'
                : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold text-white tracking-wide">{bay.bay_id}</span>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getTierColor(bay.current_risk_level)}`}>
                {bay.current_risk_level}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 truncate">{bay.bay_name.split('(')[1]?.replace(')', '') || bay.bay_name}</p>
            <div className="flex items-center gap-3 mt-2 text-[10px] text-slate-400">
              <span className="flex items-center gap-1"><Users className="w-3 h-3 text-slate-400" /> {bay.active_workers} workers</span>
              <span className="flex items-center gap-1"><Box className="w-3 h-3 text-slate-400" /> {bay.active_packages} pkgs</span>
            </div>
          </button>
        ))}
      </div>

      {/* Main Active Camera Viewport */}
      <div className="relative aspect-video w-full bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center">
        {/* Stream image */}
        <img
          src={getStreamUrl(activeBay.bay_id)}
          alt={`Live Feed of ${activeBay.bay_name}`}
          className="w-full h-full object-cover"
          onError={(e) => {
            // Graceful fallback to static snapshot if multipart stream disconnects temporarily
            e.target.onerror = null;
            e.target.src = `/api/bays/${activeBay.bay_id}/frame?privacy=${privacyMode !== 'none'}&silhouettes=${privacyMode === 'silhouettes'}`;
          }}
        />

        {/* Live HUD Telemetry Overlay */}
        <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            LIVE CAM 1080p
          </div>
          <span className="text-slate-600">|</span>
          <span className="text-slate-300 font-medium">{activeBay.bay_name}</span>
        </div>

        {/* Privacy Shield Watermark */}
        <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-800 flex items-center gap-1.5 text-xs">
          <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-300 font-medium">
            {privacyMode === 'silhouettes' ? 'Silhouette Avatar Shield Active' : (privacyMode === 'blur' ? 'Face Masking Active' : 'Unmasked Audit Mode')}
          </span>
        </div>

        {/* Bottom Kinematic Telemetry HUD */}
        <div className="absolute bottom-3 inset-x-3 bg-slate-950/85 backdrop-blur-md px-4 py-2 rounded-xl border border-slate-800 flex flex-wrap items-center justify-between text-xs gap-3">
          <div className="flex items-center gap-4 text-slate-300">
            <div>
              <span className="text-slate-400 text-[10px] block">INSPECTION STATUS</span>
              <span className="font-semibold text-emerald-400 flex items-center gap-1">
                Sequence Action Recognizer: Running
              </span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] block">ESTIMATED DROP IMPULSE</span>
              <span className="font-mono font-medium text-slate-200">a_y &lt; 1.2 m/s² (Nominal)</span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] block">PALLET OVERHANG</span>
              <span className="font-mono font-medium text-slate-200">0.0% within boundary</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onQuickSimulate(activeBay.bay_id, 'BEH_DROP')}
              className="px-3 py-1.5 rounded-lg bg-rose-600/90 hover:bg-rose-500 text-white font-medium text-xs transition-all flex items-center gap-1 shadow-sm"
            >
              <AlertTriangle className="w-3.5 h-3.5" /> Test Drop Event
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
