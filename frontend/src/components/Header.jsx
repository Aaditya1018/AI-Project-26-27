import React from 'react';
import { ShieldCheck, Video, BellRing, BellOff, Users, Clock, Radio, Activity } from 'lucide-react';

export default function Header({
  activeRole,
  onSelectRole,
  soundEnabled,
  onToggleSound,
  isConnected,
  unreadAlertsCount
}) {
  const roles = ['Supervisor', 'Bay Lead', 'Auditor'];

  return (
    <header className="bg-slate-900/95 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand & Project Identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-cyan-400 p-0.5 shadow-lg shadow-emerald-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-emerald-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black tracking-tight text-white flex items-center gap-2">
                SafeStack <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">AI</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">Bharat Logistics OS</span>
              </h1>
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Radio className="w-3 h-3 animate-pulse" /> EDGE ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Damage-Free Warehouse Loading & Unloading Video Intelligence • Multi-Hub Fulfillment India (Bhiwandi & NCR)
            </p>
          </div>
        </div>

        {/* Controls, Sound & Role Switcher */}
        <div className="flex items-center gap-3">
          {/* Audio Chime Nudge Toggle */}
          <button
            onClick={onToggleSound}
            title={soundEnabled ? "Audio coaching alert enabled" : "Audio coaching alert muted"}
            className={`p-2 rounded-lg border transition-all text-xs font-medium flex items-center gap-1.5 ${
              soundEnabled
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {soundEnabled ? <BellRing className="w-4 h-4 text-emerald-400" /> : <BellOff className="w-4 h-4" />}
            <span className="hidden sm:inline">{soundEnabled ? 'Chime ON' : 'Muted'}</span>
          </button>

          {/* Connection Indicator */}
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-sm shadow-emerald-400' : 'bg-amber-400'}`} />
            <span className="text-slate-400 hidden sm:inline">{isConnected ? 'Sub-50ms WS' : 'Connecting...'}</span>
          </div>

          {/* Role-Based Access Control (RBAC) Switcher */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <span className="px-2 text-slate-400 flex items-center gap-1 font-semibold">
              <Users className="w-3.5 h-3.5" /> Role:
            </span>
            {roles.map(r => (
              <button
                key={r}
                onClick={() => onSelectRole(r)}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
                  activeRole === r
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

      </div>
    </header>
  );
}
