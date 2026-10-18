import React, { useEffect, useRef, useState } from 'react';
import { BarChart3, TrendingUp, DollarSign, ShieldCheck, CheckCircle2, AlertOctagon, Layers, ArrowUpRight, Calculator } from 'lucide-react';

export default function AnalyticsDashboard({ analytics }) {
  const lineChartRef = useRef(null);
  const doughnutChartRef = useRef(null);
  const bayChartRef = useRef(null);

  // Damage Prevention Financial ROI Calculator states
  const [dailyThroughput, setDailyThroughput] = useState(4800);
  const [avgUnitValueUsd, setAvgUnitValueUsd] = useState(140);
  const [baselineDamagePct, setBaselineDamagePct] = useState(1.6); // 1.6% without AI
  const [preventionRatePct, setPreventionRatePct] = useState(82);  // 82% prevented with SafeStack AI

  const damagedWithoutAiMonthly = Math.round(dailyThroughput * 30 * (baselineDamagePct / 100));
  const preventedMonthlyUnits = Math.round(damagedWithoutAiMonthly * (preventionRatePct / 100));
  const monthlySavingsUsd = preventedMonthlyUnits * avgUnitValueUsd;
  const annualSavingsUsd = monthlySavingsUsd * 12;

  // Initialize or update Chart.js instances if window.Chart is loaded
  useEffect(() => {
    if (typeof window === 'undefined' || !window.Chart) return;
    const Chart = window.Chart;

    let lineChart, doughnutChart, bayChart;

    // 1. Shift Hourly Trend Chart
    if (lineChartRef.current && analytics?.hourly_trends) {
      const ctx = lineChartRef.current.getContext('2d');
      lineChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: analytics.hourly_trends.map(t => t.hour),
          datasets: [
            {
              label: 'Risk Index (0-100)',
              data: analytics.hourly_trends.map(t => t.risk_index),
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              tension: 0.35,
              fill: true,
              pointBackgroundColor: '#10b981',
              borderWidth: 2.5
            },
            {
              label: 'Incidents Count',
              data: analytics.hourly_trends.map(t => t.incidents),
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              tension: 0.3,
              borderWidth: 2,
              borderDash: [5, 5]
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8', font: { size: 11 } } }
          },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8' } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8' } }
          }
        }
      });
    }

    // 2. Behavior Taxonomy Distribution Chart
    if (doughnutChartRef.current && analytics?.behavior_distribution) {
      const ctx = doughnutChartRef.current.getContext('2d');
      doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: analytics.behavior_distribution.slice(0, 6).map(b => b.behavior),
          datasets: [{
            data: analytics.behavior_distribution.slice(0, 6).map(b => b.count),
            backgroundColor: [
              '#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'
            ],
            borderWidth: 2,
            borderColor: '#0f172a'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 10 } } }
          }
        }
      });
    }

    // 3. Loading Bay Comparison Chart
    if (bayChartRef.current && analytics?.bay_comparison) {
      const ctx = bayChartRef.current.getContext('2d');
      bayChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: analytics.bay_comparison.map(b => b.bay_id),
          datasets: [
            {
              label: 'Avg Risk Score',
              data: analytics.bay_comparison.map(b => b.average_risk_score),
              backgroundColor: 'rgba(239, 68, 68, 0.75)',
              borderRadius: 6
            },
            {
              label: 'Total Incidents',
              data: analytics.bay_comparison.map(b => b.total_incidents),
              backgroundColor: 'rgba(16, 185, 129, 0.75)',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8', font: { size: 11 } } }
          },
          scales: {
            x: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8' } },
            y: { grid: { color: 'rgba(51, 65, 85, 0.3)' }, ticks: { color: '#94a3b8' } }
          }
        }
      });
    }

    return () => {
      if (lineChart) lineChart.destroy();
      if (doughnutChart) doughnutChart.destroy();
      if (bayChart) bayChart.destroy();
    };
  }, [analytics]);

  return (
    <div className="space-y-6">
      {/* Executive KPI Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold mb-2">
            <span>Total Tracked Incidents</span>
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white font-mono">{analytics?.total_events || 0}</div>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1 font-medium">
            <TrendingUp className="w-3 h-3" /> 100% Computer-Vision Grounded
          </p>
        </div>

        <div className="bg-slate-900 border border-emerald-500/40 rounded-2xl p-4 shadow-lg bg-gradient-to-b from-emerald-950/20 to-slate-900">
          <div className="flex items-center justify-between text-emerald-400 text-xs font-semibold mb-2">
            <span>Verified Damages Prevented</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono">
            {analytics?.damage_prevented_count || 0} Units
          </div>
          <p className="text-[11px] text-emerald-300 mt-1">
            Proactive Real-Time Coaching Nudges
          </p>
        </div>

        <div className="bg-slate-900 border border-rose-500/40 rounded-2xl p-4 shadow-lg bg-gradient-to-b from-rose-950/20 to-slate-900">
          <div className="flex items-center justify-between text-rose-400 text-xs font-semibold mb-2">
            <span>Critical Severity Alerts</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-black text-rose-400 font-mono">
            {analytics?.critical_events || 0}
          </div>
          <p className="text-[11px] text-rose-300 mt-1">
            Immediate Supervisor Review Required
          </p>
        </div>

        <div className="bg-slate-900 border border-teal-500/40 rounded-2xl p-4 shadow-lg bg-gradient-to-b from-teal-950/20 to-slate-900">
          <div className="flex items-center justify-between text-teal-400 text-xs font-semibold mb-2">
            <span>Est. Value Preserved</span>
            <DollarSign className="w-4 h-4 text-teal-400" />
          </div>
          <div className="text-2xl font-black text-teal-300 font-mono">
            ${(analytics?.prevented_value_est_usd || 0).toLocaleString()}
          </div>
          <p className="text-[11px] text-teal-400 mt-1">
            Avoided Claims & Freight Chargebacks
          </p>
        </div>
      </div>

      {/* Chart.js Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Hourly Trend Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-400" /> Hourly Shift Risk & Incident Timeline (Chart.js)
            </h3>
            <span className="text-[10px] text-slate-400">Past 8 Hours</span>
          </div>
          <div className="h-64 relative">
            <canvas ref={lineChartRef} />
          </div>
        </div>

        {/* Behavior Taxonomy Distribution Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" /> 10-Behavior Taxonomy Distribution (Chart.js)
            </h3>
            <span className="text-[10px] text-slate-400">Sequence Action Share</span>
          </div>
          <div className="h-64 relative">
            <canvas ref={doughnutChartRef} />
          </div>
        </div>
      </div>

      {/* Loading Bay Comparison & ROI Calculator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Bay Comparison */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-400" /> Loading Bay Operational Risk Index (Chart.js)
            </h3>
            <span className="text-[10px] text-slate-400">Bay 1 to Bay 4</span>
          </div>
          <div className="h-60 relative">
            <canvas ref={bayChartRef} />
          </div>
        </div>

        {/* Interactive Damage Prevention ROI Calculator */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Calculator className="w-4 h-4 text-emerald-400" /> Damage Prevention ROI & Impact Calculator
            </h3>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Interactive
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-slate-400 font-medium block mb-1">Daily Cartons Scanned</label>
              <input
                type="number"
                value={dailyThroughput}
                onChange={(e) => setDailyThroughput(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-white font-mono"
              />
            </div>
            <div>
              <label className="text-slate-400 font-medium block mb-1">Avg Product Value ($)</label>
              <input
                type="number"
                value={avgUnitValueUsd}
                onChange={(e) => setAvgUnitValueUsd(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-white font-mono"
              />
            </div>
            <div>
              <label className="text-slate-400 font-medium block mb-1">Baseline Damage Rate (%)</label>
              <input
                type="number"
                step="0.1"
                value={baselineDamagePct}
                onChange={(e) => setBaselineDamagePct(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-white font-mono"
              />
            </div>
            <div>
              <label className="text-slate-400 font-medium block mb-1">AI Prevention Rate (%)</label>
              <input
                type="number"
                value={preventionRatePct}
                onChange={(e) => setPreventionRatePct(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-white font-mono"
              />
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950 border border-emerald-500/30 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 block font-medium">Projected Annual Net Savings</span>
              <span className="text-xl font-black text-emerald-400 font-mono">
                ${annualSavingsUsd.toLocaleString()} / year
              </span>
            </div>
            <div className="text-right text-[11px] text-slate-400">
              <span className="block font-semibold text-slate-200">{preventedMonthlyUnits.toLocaleString()} Cartons / mo</span>
              <span>Damage claims eliminated</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
