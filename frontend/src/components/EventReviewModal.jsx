import React, { useState, useEffect } from 'react';
import { X, Play, Pause, AlertTriangle, ShieldCheck, CheckCircle2, FileText, ChevronRight, Activity, Info, Sparkles, Network, GitBranch } from 'lucide-react';
import { fetchEventRCA, submitReview } from '../services/api';

export default function EventReviewModal({
  event,
  onClose,
  onReviewSubmitted
}) {
  const [activeTab, setActiveTab] = useState('evidence'); // 'evidence' | 'rca'
  const [rcaData, setRcaData] = useState(null);
  const [loadingRca, setLoadingRca] = useState(false);
  const [notes, setNotes] = useState(event.supervisor_notes || '');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (activeTab === 'rca' && !rcaData) {
      setLoadingRca(true);
      fetchEventRCA(event.id)
        .then(data => setRcaData(data))
        .catch(() => {})
        .finally(() => setLoadingRca(false));
    }
  }, [activeTab, event.id, rcaData]);

  const handleAction = async (actionType) => {
    setSubmitting(true);
    try {
      await submitReview(event.id, actionType, notes, 'Supervisor');
      if (onReviewSubmitted) onReviewSubmitted(event.id, actionType, notes);
      onClose();
    } catch (e) {
      alert('Error updating review status: ' + e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const telemetry = event.kinematic_telemetry || {};
  const explain = event.explainability || {};
  const factors = explain.factors || [];
  const bayes = explain.bayesian_inference;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-4xl w-full shadow-2xl overflow-hidden my-8 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200">
              {event.id}
            </span>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                {event.behavior_name}
              </h3>
              <p className="text-xs text-slate-400">
                {event.bay_name} • {new Date(event.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="px-6 pt-3 border-b border-slate-800 flex items-center gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('evidence')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'evidence'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" /> CV Evidence & Kinematic Telemetry
          </button>
          <button
            onClick={() => setActiveTab('rca')}
            className={`pb-3 border-b-2 transition-all flex items-center gap-1.5 ${
              activeTab === 'rca'
                ? 'border-emerald-400 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" /> Automated 5-Why Root Cause Analysis (RCA)
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {activeTab === 'evidence' ? (
            <>
              {/* Media Preview & Kinematic KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {/* Visual Evidence Clip / Snapshot */}
                <div className="aspect-video bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 relative flex items-center justify-center">
                  <img
                    src={event.snapshot_url || '/api/media/snapshots/sample_drop.jpg'}
                    alt="Incident Snapshot"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = `/api/bays/${event.bay_id}/frame`;
                    }}
                  />
                  <div className="absolute top-2 left-2 bg-slate-950/85 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-semibold text-emerald-400 border border-slate-800">
                    CV Bounding Proof
                  </div>
                </div>

                {/* Kinematic Telemetry Metrics Grid */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Vertical Accel (ay)</span>
                    <span className="text-lg font-bold font-mono text-rose-400">
                      {telemetry.vertical_accel_mps2 || 0} m/s²
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Freefall &gt; 8.5 m/s²</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Drop Velocity</span>
                    <span className="text-lg font-bold font-mono text-amber-400">
                      {telemetry.drop_velocity_mps || 0} m/s
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Max downward velocity</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Kinetic Energy</span>
                    <span className="text-lg font-bold font-mono text-cyan-400">
                      {telemetry.kinetic_impact_energy_j || 0} Joules
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Impact shock energy</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Tilt / Overhang</span>
                    <span className="text-lg font-bold font-mono text-emerald-400">
                      {telemetry.pallet_overhang_pct || telemetry.tilt_angle_deg || 0}%
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-0.5">Stability index</span>
                  </div>
                </div>
              </div>

              {/* Explainability Breakdown Table */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-emerald-400" /> Explainable Risk Model Factor Attribution
                </h4>
                
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
                  <p className="text-xs text-slate-300 font-medium">
                    {explain.summary || 'Risk score synthesized from kinematic sensor evidence and cargo sensitivity profile.'}
                  </p>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                          <th className="pb-2">Factor Signature</th>
                          <th className="pb-2">Weight</th>
                          <th className="pb-2">Contribution</th>
                          <th className="pb-2">Verified Sensor Evidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {factors.map((f, i) => (
                          <tr key={i} className="text-slate-300">
                            <td className="py-2 font-medium text-white">{f.factor_name}</td>
                            <td className="py-2 font-mono text-slate-400">{(f.weight * 100).toFixed(0)}%</td>
                            <td className="py-2 font-mono text-emerald-400">+{f.contribution_pts} pts</td>
                            <td className="py-2 text-slate-400 text-[11px]">{f.evidence}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Module 5: Bayesian Belief Network Inference Card */}
              {bayes && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-950/40 to-slate-950 border border-indigo-500/40 space-y-3 shadow-lg">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-indigo-900/50 pb-2">
                    <div className="flex items-center gap-2">
                      <Network className="w-4 h-4 text-indigo-400" />
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 uppercase tracking-wider">
                        Module 5: Bayesian Belief Network
                      </span>
                      <span className="text-xs font-semibold text-white">Latent Internal Damage Inference</span>
                    </div>
                    <span className="text-xs font-mono text-indigo-300 font-bold bg-indigo-900/40 px-2 py-0.5 rounded border border-indigo-700/50">
                      P(SevereLoss | e) = {(bayes.p_severe_loss * 100).toFixed(1)}%
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Under sensor observation uncertainty, the internal state of sealed packaging is inferred via <strong>Bayes' Theorem</strong> across the CPT distribution conditioned on observed drop height, impact deceleration, and cargo fragility.
                  </p>

                  {/* Posterior Probability Bars */}
                  <div className="grid grid-cols-3 gap-2.5 text-center">
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">P(Intact | e)</span>
                      <span className="text-base font-bold font-mono text-emerald-400">
                        {(bayes.p_intact * 100).toFixed(1)}%
                      </span>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div className="bg-emerald-500 h-full rounded-full transition-all" style={{ width: `${bayes.p_intact * 100}%` }}></div>
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">P(Cosmetic | e)</span>
                      <span className="text-base font-bold font-mono text-amber-400">
                        {(bayes.p_cosmetic * 100).toFixed(1)}%
                      </span>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div className="bg-amber-500 h-full rounded-full transition-all" style={{ width: `${bayes.p_cosmetic * 100}%` }}></div>
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">P(Severe Loss | e)</span>
                      <span className="text-base font-bold font-mono text-rose-400">
                        {(bayes.p_severe_loss * 100).toFixed(1)}%
                      </span>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                        <div className="bg-rose-500 h-full rounded-full transition-all" style={{ width: `${bayes.p_severe_loss * 100}%` }}></div>
                      </div>
                    </div>
                  </div>

                  {/* Mathematical Derivation Steps */}
                  {bayes.mathematical_derivation && (
                    <div className="text-[11px] bg-slate-950/90 p-3 rounded-lg border border-slate-800/80 space-y-1 font-mono text-slate-300">
                      <div className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider flex items-center gap-1.5 mb-1">
                        <GitBranch className="w-3 h-3 text-indigo-400" /> Mathematical Derivation (Exact Bayes Inference):
                      </div>
                      {bayes.mathematical_derivation.map((step, idx) => (
                        <div key={idx} className="text-slate-400 pl-1 text-[10px]">• {step}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Proactive Prevention Recommendation */}
              <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-xs font-bold text-emerald-300">Recommended Operational Prevention Nudge</h5>
                  <p className="text-xs text-slate-300 mt-1">
                    {explain.prevention_recommendation || 'Reinforce standard loading guidelines.'}
                  </p>
                </div>
              </div>
            </>
          ) : (
            /* 5-Why Root Cause Analysis (RCA) Tab */
            <div className="space-y-4">
              {loadingRca ? (
                <div className="text-center py-12 text-slate-400 text-xs">
                  Generating automated 5-Why analysis from telemetry...
                </div>
              ) : rcaData ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wide">5-Why Incident Progression</h5>
                    <div className="space-y-1.5 text-xs text-slate-300 font-medium">
                      {rcaData.five_whys?.map((why, idx) => (
                        <div key={idx} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                          {why}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="p-3.5 rounded-xl bg-slate-950 border border-amber-500/30">
                      <span className="text-[10px] font-bold text-amber-400 uppercase block">Identified Root Cause</span>
                      <p className="text-slate-200 mt-1">{rcaData.root_cause}</p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-500/30">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase block">Preventive Corrective Action</span>
                      <p className="text-slate-200 mt-1">{rcaData.preventive_action}</p>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 italic">
                    {rcaData.responsible_ai_governance}
                  </p>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400 text-xs">
                  RCA data not available.
                </div>
              )}
            </div>
          )}

          {/* Supervisor Action & Review Notes */}
          <div className="pt-4 border-t border-slate-800 space-y-3">
            <label className="text-xs font-bold text-slate-300 block">
              Supervisor Operational Coaching & Audit Notes
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record coaching provided, dock adjustment, or reason for validation..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
            />

            <div className="flex flex-wrap items-center justify-end gap-2.5 pt-2">
              <button
                disabled={submitting}
                onClick={() => handleAction('False Positive')}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs transition-all"
              >
                Mark False Positive
              </button>

              <button
                disabled={submitting}
                onClick={() => handleAction('Coaching Logged')}
                className="px-4 py-2 rounded-xl bg-blue-600/90 hover:bg-blue-500 text-white font-semibold text-xs transition-all"
              >
                Log Coaching Completed
              </button>

              <button
                disabled={submitting}
                onClick={() => handleAction('Verified Damage Prevented')}
                className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-600/20 flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" /> Confirm Damage Prevented
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
