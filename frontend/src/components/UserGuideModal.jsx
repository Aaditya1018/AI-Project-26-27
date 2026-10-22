import React, { useState } from 'react';
import { 
  BookOpen, 
  PlayCircle, 
  Film, 
  BarChart3, 
  ShieldCheck, 
  MessageSquare, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight,
  Eye,
  IndianRupee,
  Layers,
  Sparkles,
  HelpCircle,
  FileCheck2,
  Cpu,
  Video,
  Activity,
  Flame,
  Truck,
  PackageCheck,
  FileText
} from 'lucide-react';

export default function UserGuideModal({ isOpen, onClose, onNavigateTab }) {
  const [activeStep, setActiveStep] = useState(0);

  if (!isOpen) return null;

  const steps = [
    {
      id: 'quickstart',
      title: '1. Platform Overview & Architecture',
      badge: 'Getting Started',
      icon: BookOpen,
      content: (
        <div className="space-y-4">
          <p className="text-sm text-slate-300 leading-relaxed">
            Welcome to <strong className="text-emerald-400">SafeStack AI</strong> — India’s frontline video intelligence and damage-free warehouse loading operating system designed for high-throughput fulfillment centers (Bhiwandi, Bilaspur-Gurugram, Hoskote-Bengaluru, Sriperumbudur-Chennai).
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5" /> 1. Edge Live Cameras
              </span>
              <p className="text-xs text-slate-400">
                Monitors loading bays in real time with continuous carton multi-frame tracking and stability kinematics.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> 2. 10 Damage Scenarios
              </span>
              <p className="text-xs text-slate-400">
                Automated detection of carton drops, floor drags, pyramid over-stacks, rough slams, and forklift pinch hazards.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <span className="text-xs font-bold text-teal-400 flex items-center gap-1.5">
                <IndianRupee className="w-3.5 h-3.5" /> 3. Indian Rupee ROI
              </span>
              <p className="text-xs text-slate-400">
                Live metrics calculating prevented freight write-offs and claim chargebacks in Lakhs & Crores (₹ INR).
              </p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/20 text-xs text-slate-300 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span><strong>Privacy Guaranteed:</strong> Worker faces are blurred or converted into ergonomic silhouettes at the camera edge with zero facial biometric storage.</span>
          </div>
        </div>
      )
    },
    {
      id: 'simulation',
      title: '2. How to Run Simulation & Test Behaviors',
      badge: 'Core Feature',
      icon: PlayCircle,
      content: (
        <div className="space-y-3.5 text-xs text-slate-300">
          <p className="leading-relaxed">
            SafeStack AI includes a live scenario generator to test computer vision models and alert logic against edge-case warehouse handling:
          </p>
          <div className="space-y-2.5">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-3">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold shrink-0">1</div>
              <div>
                <strong className="text-white block font-semibold mb-0.5">Select a Target Bay</strong>
                Click on any of the 4 loading bays (<span className="text-emerald-400 font-mono">BAY-01 Heavy Cargo</span>, <span className="text-emerald-400 font-mono">BAY-02 Electronics</span>, <span className="text-emerald-400 font-mono">BAY-03 Express</span>, <span className="text-emerald-400 font-mono">BAY-04 Cold Chain</span>).
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-3">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold shrink-0">2</div>
              <div>
                <strong className="text-white block font-semibold mb-0.5">Choose Cargo Sensitivity Profile</strong>
                Select the product category (<em>Electronics & Fragile</em>, <em>Glassware</em>, <em>Heavy Industrial</em>, <em>Perishables FMCG</em>). The risk algorithm scales dynamically based on cargo tolerance.
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-start gap-3">
              <div className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold shrink-0">3</div>
              <div>
                <strong className="text-white block font-semibold mb-0.5">Click any Scenario Card to Inject</strong>
                Choose <strong>"Product Dropped from Height"</strong>, <strong>"Unsafe Pallet Overhang & Tilt"</strong>, or <strong>"Inverted Pyramid Stacking"</strong>. The event immediately broadcasts across WebSocket, updates the live feed, and chimes an audio coaching alert!
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'video_injection',
      title: '3. Testing Custom Warehouse Videos',
      badge: 'Real CCTV Video',
      icon: Film,
      content: (
        <div className="space-y-3.5 text-xs text-slate-300">
          <p className="leading-relaxed">
            Have actual warehouse CCTV recordings (MP4, AVI, MOV)? SafeStack AI allows loading real footage directly into the inspection pipeline:
          </p>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
                <Video className="w-4 h-4" />
              </div>
              <div>
                <strong className="text-white block font-semibold">Mode A: Stream Live into Bay</strong>
                <p className="text-slate-400 mt-0.5">
                  Replaces the synthetic loading feed of your chosen bay with your actual video clip. The detector continuously tracks moving cartons, persons, and forklifts with real-time bounding boxes.
                </p>
              </div>
            </div>

            <div className="border-t border-slate-800/80 pt-2 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 shrink-0">
                <Activity className="w-4 h-4" />
              </div>
              <div>
                <strong className="text-white block font-semibold">Mode B: Full Offline Scan</strong>
                <p className="text-slate-400 mt-0.5">
                  Executes a rapid offline scan across every single video frame, tabulating carton detections, bounding proofs, and logging potential mishandling events into the incident database.
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'review_and_roi',
      title: '4. Evidence Audit & Rupee (₹) Savings',
      badge: 'Finance & Governance',
      icon: IndianRupee,
      content: (
        <div className="space-y-3.5 text-xs text-slate-300">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <h5 className="font-bold text-white flex items-center gap-1.5">
                <FileCheck2 className="w-4 h-4 text-emerald-400" /> Human-in-the-Loop & 5-Why RCA
              </h5>
              <p className="text-slate-400 leading-relaxed">
                Click any event in the <strong>Alert Stream</strong> to open the audit dialog. Inspect kinematic telemetry (<span className="text-rose-400 font-mono">ay</span> acceleration, velocity, impact Joules) and auto-generated 5-Why root cause analysis.
              </p>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <h5 className="font-bold text-white flex items-center gap-1.5">
                <IndianRupee className="w-4 h-4 text-teal-400" /> ₹ Indian Rupee ROI Calculator
              </h5>
              <p className="text-slate-400 leading-relaxed">
                In <strong>Shift Analytics</strong>, adjust daily carton throughput and average cargo unit price in ₹ INR to calculate annual projected damage write-offs saved across Indian fulfillment centers.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-300">Need immediate answers? Open <strong>SafeStack Copilot</strong> to query bay incidents in natural language.</span>
            </div>
          </div>
        </div>
      )
    }
  ];

  const current = steps[activeStep];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full shadow-2xl overflow-hidden my-6">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                User Guide & Operation Manual
              </h3>
              <p className="text-xs text-slate-400">SafeStack AI — Enterprise Warehouse Logistics India</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all font-semibold"
          >
            Close ✕
          </button>
        </div>

        {/* Step Navigation Pill Bar */}
        <div className="px-6 pt-3 pb-2 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto text-xs">
          {steps.map((s, idx) => (
            <button
              key={s.id}
              onClick={() => setActiveStep(idx)}
              className={`px-3 py-1.5 rounded-xl font-medium transition-all shrink-0 flex items-center gap-1.5 ${
                activeStep === idx
                  ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-600/30'
                  : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              <s.icon className="w-3.5 h-3.5" />
              <span>{s.title.split('.')[1] || s.title}</span>
            </button>
          ))}
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-5">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <current.icon className="w-4 h-4 text-emerald-400" />
              {current.title}
            </h4>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {current.badge}
            </span>
          </div>

          {current.content}
        </div>

        {/* Footer controls */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/70 flex items-center justify-between text-xs">
          <button
            disabled={activeStep === 0}
            onClick={() => setActiveStep(prev => Math.max(0, prev - 1))}
            className="px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 transition-all"
          >
            ← Previous
          </button>

          <div className="flex items-center gap-1.5">
            {steps.map((_, i) => (
              <span
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  activeStep === i ? 'w-5 bg-emerald-400' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>

          {activeStep < steps.length - 1 ? (
            <button
              onClick={() => setActiveStep(prev => Math.min(steps.length - 1, prev + 1))}
              className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition-all flex items-center gap-1 shadow-sm"
            >
              Next Step <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              onClick={() => {
                onClose();
                onNavigateTab && onNavigateTab('live');
              }}
              className="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all flex items-center gap-1 shadow-sm shadow-emerald-600/30"
            >
              Start Using Platform <CheckCircle2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
