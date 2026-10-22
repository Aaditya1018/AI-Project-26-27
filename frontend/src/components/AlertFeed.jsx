import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, CheckCircle, Clock, ChevronRight, Filter } from 'lucide-react';

export default function AlertFeed({
  events,
  selectedEvent,
  onSelectEvent,
  activeFilter,
  onChangeFilter
}) {
  const tiers = ['All', 'Critical', 'High', 'Medium', 'Low'];

  const filteredEvents = events.filter(e => {
    if (activeFilter === 'All') return true;
    return e.risk_tier.toLowerCase() === activeFilter.toLowerCase();
  });

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'Critical':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40 critical-pulse font-bold';
      case 'High':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40 font-semibold';
      case 'Medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40 font-medium';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'Verified Damage Prevented') {
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    } else if (status === 'Coaching Logged') {
      return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    } else if (status === 'False Positive') {
      return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
    return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  };

  const formatTimeAgo = (isoString) => {
    try {
      const diffSec = Math.floor((new Date() - new Date(isoString)) / 1000);
      if (diffSec < 60) return `${Math.max(1, diffSec)}s ago`;
      if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
      return `${Math.floor(diffSec / 3600)}h ago`;
    } catch (e) {
      return 'Just now';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col h-full space-y-3.5">
      {/* Alert Feed Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" /> Real-Time Damage Risk Stream
          </h2>
          <p className="text-xs text-slate-400">
            Graded risk detections requiring proactive intervention
          </p>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
          {filteredEvents.length} events
        </span>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        {tiers.map(t => (
          <button
            key={t}
            onClick={() => onChangeFilter(t)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all shrink-0 ${
              activeFilter === t
                ? 'bg-slate-700 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Events Scrollable List */}
      <div className="space-y-2.5 overflow-y-auto max-h-[580px] pr-1">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            No incidents found matching this filter.
          </div>
        ) : (
          filteredEvents.map(event => (
            <div
              key={event.id}
              onClick={() => onSelectEvent(event)}
              className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                selectedEvent?.id === event.id
                  ? 'bg-slate-800 border-emerald-500/80 shadow-lg shadow-emerald-500/10'
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-slate-200">{event.id}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getTierBadge(event.risk_tier)}`}>
                    {event.risk_tier} ({event.risk_score})
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" /> {formatTimeAgo(event.timestamp)}
                </span>
              </div>

              <h4 className="text-xs font-semibold text-white tracking-wide mb-1">
                {event.behavior_name}
              </h4>

              <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400 mb-2">
                <span className="text-slate-300 font-medium">{event.bay_name.split('(')[0]}</span>
                <span>•</span>
                <span className="text-emerald-400">{event.product_category}</span>
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
                <span className={`text-[10px] px-2 py-0.5 rounded-md border ${getStatusBadge(event.status)}`}>
                  {event.status}
                </span>
                <span className="text-[11px] text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-0.5">
                  Inspect Evidence <ChevronRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
