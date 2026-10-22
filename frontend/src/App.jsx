import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import LiveBaysGrid from './components/LiveBaysGrid';
import AlertFeed from './components/AlertFeed';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SimulationControls from './components/SimulationControls';
import VideoInjector from './components/VideoInjector';
import EventReviewModal from './components/EventReviewModal';
import AssistantDrawer from './components/AssistantDrawer';
import UserGuideModal from './components/UserGuideModal';
import { fetchBays, fetchEvents, fetchAnalytics } from './services/api';
import { SafeStackAlertSocket } from './services/websocket';
import { Video, BarChart3, PlayCircle, MessageSquare, ShieldCheck, FileCheck2, Film, BookOpen, HelpCircle, Sparkles, CheckCircle2, ArrowRight, Layers } from 'lucide-react';

export default function App() {
  const [bays, setBays] = useState([]);
  const [events, setEvents] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedBayId, setSelectedBayId] = useState('BAY-01');
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  // Navigation & View Mode
  const [activeTab, setActiveTab] = useState('live'); // 'live' | 'analytics' | 'simulate' | 'governance' | 'instructions'
  const [privacyMode, setPrivacyMode] = useState('blur'); // 'blur' | 'silhouettes' | 'none'
  const [activeRole, setActiveRole] = useState('Supervisor'); // 'Supervisor' | 'Bay Lead' | 'Auditor'
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [activeFilter, setActiveFilter] = useState('All');

  // Synthesize Web Audio Chime for alerts
  const playAlertChime = (riskTier) => {
    if (!soundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = riskTier === 'Critical' ? 'sawtooth' : 'sine';
      osc.frequency.setValueAtTime(riskTier === 'Critical' ? 660 : 440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(riskTier === 'Critical' ? 880 : 550, ctx.currentTime + 0.15);

      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.35);
    } catch (e) {
      // Audio autoplay policy fallback
    }
  };

  // Initial Data Load
  const loadData = async () => {
    try {
      const [baysData, eventsData, analyticsData] = await Promise.all([
        fetchBays(),
        fetchEvents(),
        fetchAnalytics()
      ]);
      setBays(baysData || []);
      setEvents(eventsData || []);
      setAnalytics(analyticsData || null);
      if (baysData && baysData.length > 0 && !selectedBayId) {
        setSelectedBayId(baysData[0].bay_id);
      }
    } catch (e) {
      console.error('Failed to load initial data:', e);
    }
  };

  useEffect(() => {
    loadData();

    // Setup WebSocket
    const socket = new SafeStackAlertSocket((newAlert) => {
      setEvents(prev => [newAlert, ...prev]);
      playAlertChime(newAlert.risk_tier);
      // Refresh analytics
      fetchAnalytics().then(setAnalytics).catch(() => {});
      fetchBays().then(setBays).catch(() => {});
    });

    socket.connect();
    setIsConnected(true);

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleReviewSubmitted = (eventId, action, notes) => {
    setEvents(prev => prev.map(e => {
      if (e.id === eventId) {
        return {
          ...e,
          status: action,
          supervisor_notes: notes,
          reviewed_by: activeRole
        };
      }
      return e;
    }));
    fetchAnalytics().then(setAnalytics).catch(() => {});
  };

  const handleSelectEventById = (eventId) => {
    const ev = events.find(e => e.id === eventId);
    if (ev) {
      setSelectedEvent(ev);
      setIsAssistantOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* App Header */}
      <Header
        activeRole={activeRole}
        onSelectRole={setActiveRole}
        soundEnabled={soundEnabled}
        onToggleSound={() => setSoundEnabled(!soundEnabled)}
        isConnected={isConnected}
        unreadAlertsCount={events.filter(e => e.status === 'Pending Review').length}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 space-y-6">
        
        {/* Navigation Tabs Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setActiveTab('live')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'live'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Video className="w-4 h-4" /> Live Feeds & Alert Stream
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'analytics'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <BarChart3 className="w-4 h-4" /> Shift Analytics (Chart.js)
            </button>

            <button
              onClick={() => setActiveTab('simulate')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'simulate'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <PlayCircle className="w-4 h-4" /> 10-Behavior Simulator
            </button>

            <button
              onClick={() => setActiveTab('inject')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'inject'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Film className="w-4 h-4" /> Inject Video
            </button>

            <button
              onClick={() => setActiveTab('governance')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'governance'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <ShieldCheck className="w-4 h-4" /> Responsible AI & Privacy Shield
            </button>

            <button
              onClick={() => setActiveTab('instructions')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeTab === 'instructions'
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-4 h-4 text-amber-400" /> User Guide & Instructions
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsGuideOpen(true)}
              className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 flex items-center gap-1.5 transition-all shadow-sm"
              title="Open Quick Interactive Guide"
            >
              <HelpCircle className="w-4 h-4 text-amber-400" />
              <span className="hidden sm:inline">Quick Guide</span>
            </button>

            <button
              onClick={() => setIsAssistantOpen(true)}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-bold text-xs shadow-md shadow-emerald-500/20 flex items-center gap-2 transition-all"
            >
              <MessageSquare className="w-4 h-4" /> Ask SafeStack Copilot
            </button>
          </div>
        </div>

        {/* Tab 1: Live Loading Bays & Alert Stream */}
        {activeTab === 'live' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <LiveBaysGrid
                bays={bays}
                selectedBayId={selectedBayId}
                onSelectBay={setSelectedBayId}
                privacyMode={privacyMode}
                onChangePrivacyMode={setPrivacyMode}
                onQuickSimulate={(bayId, beh) => {
                  import('./services/api').then(m => {
                    m.triggerSimulation(bayId, beh, 'Electronics & Fragile').then(loadData);
                  });
                }}
              />
              <VideoInjector
                selectedBayId={selectedBayId}
                onVideoInjected={() => {
                  loadData();
                }}
              />
              <SimulationControls
                selectedBayId={selectedBayId}
                onScenarioTriggered={(newEvent) => {
                  setEvents(prev => [newEvent, ...prev]);
                  playAlertChime(newEvent.risk_tier);
                  fetchAnalytics().then(setAnalytics).catch(() => {});
                }}
              />
            </div>

            <div className="lg:col-span-4">
              <AlertFeed
                events={events}
                selectedEvent={selectedEvent}
                onSelectEvent={setSelectedEvent}
                activeFilter={activeFilter}
                onChangeFilter={setActiveFilter}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Shift Analytics & Chart.js */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard analytics={analytics} />
        )}

        {/* Tab 3: 10-Behavior Simulator Standalone */}
        {activeTab === 'simulate' && (
          <div className="space-y-6">
            <SimulationControls
              selectedBayId={selectedBayId}
              onScenarioTriggered={(newEvent) => {
                setEvents(prev => [newEvent, ...prev]);
                playAlertChime(newEvent.risk_tier);
                fetchAnalytics().then(setAnalytics).catch(() => {});
              }}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <LiveBaysGrid
                bays={bays}
                selectedBayId={selectedBayId}
                onSelectBay={setSelectedBayId}
                privacyMode={privacyMode}
                onChangePrivacyMode={setPrivacyMode}
                onQuickSimulate={(bayId, beh) => {
                  import('./services/api').then(m => {
                    m.triggerSimulation(bayId, beh, 'Electronics & Fragile').then(loadData);
                  });
                }}
              />
              <AlertFeed
                events={events}
                selectedEvent={selectedEvent}
                onSelectEvent={setSelectedEvent}
                activeFilter={activeFilter}
                onChangeFilter={setActiveFilter}
              />
            </div>
          </div>
        )}

        {/* Tab: Dedicated Custom Video Injection View */}
        {activeTab === 'inject' && (
          <div className="space-y-6">
            <VideoInjector
              selectedBayId={selectedBayId}
              onVideoInjected={() => {
                loadData();
              }}
            />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-8">
                <LiveBaysGrid
                  bays={bays}
                  selectedBayId={selectedBayId}
                  onSelectBay={setSelectedBayId}
                  privacyMode={privacyMode}
                  onChangePrivacyMode={setPrivacyMode}
                  onQuickSimulate={(bayId, beh) => {
                    import('./services/api').then(m => {
                      m.triggerSimulation(bayId, beh, 'Electronics & Fragile').then(loadData);
                    });
                  }}
                />
              </div>
              <div className="lg:col-span-4">
                <AlertFeed
                  events={events}
                  selectedEvent={selectedEvent}
                  onSelectEvent={setSelectedEvent}
                  activeFilter={activeFilter}
                  onChangeFilter={setActiveFilter}
                />
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Responsible AI & Privacy Shield */}
        {activeTab === 'governance' && (
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-emerald-400" /> Responsible AI Safeguards & Labor Protection Architecture
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Ensuring warehouse surveillance transforms into a supportive coaching partner rather than punitive employee tracking
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide block">1. Edge Privacy Shield</span>
                <p className="text-xs text-slate-300">
                  Workers' faces are anonymized via Gaussian blurring at the edge, or replaced with non-identifiable ergonomic silhouettes. No facial recognition or biometric profiles are ever stored.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-cyan-400 uppercase tracking-wide block">2. Non-Punitive Culture</span>
                <p className="text-xs text-slate-300">
                  SafeStack AI audits handling kinematics (acceleration, center-of-gravity, tilt) and equipment bottlenecks. Incidents are flagged for coaching and dock safety redesign, not disciplinary action.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wide block">3. Human-in-the-Loop</span>
                <p className="text-xs text-slate-300">
                  High and Critical risk alerts must be validated by a designated warehouse supervisor. Every alert includes transparent factor attribution and 5-Why root cause analysis.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-emerald-500/30 flex items-center justify-between text-xs">
              <div>
                <span className="font-bold text-emerald-400 block">GDPR & OSHA Compliance Status</span>
                <span className="text-slate-300">Article 25 Data Minimisation Verified • Zero Facial Biometric Retention</span>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                AUDITED & COMPLIANT
              </span>
            </div>
          </div>
        )}

        {/* Tab 5: User Guide & Operational Instructions */}
        {activeTab === 'instructions' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      Standard Operating Procedure (SOP)
                    </span>
                    <span className="text-xs text-slate-400 font-medium">• Multi-Hub Hub Logistics Operations</span>
                  </div>
                  <h2 className="text-xl font-black text-white flex items-center gap-2">
                    <BookOpen className="w-6 h-6 text-emerald-400" /> SafeStack AI User Manual & Operational Instructions
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Complete visual handbook for warehouse managers, dock supervisors, bay leads, and quality assurance auditors.
                  </p>
                </div>

                <button
                  onClick={() => setIsGuideOpen(true)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md shadow-emerald-600/30 flex items-center gap-2 self-start md:self-auto transition-all"
                >
                  <Sparkles className="w-4 h-4" /> Launch Interactive Walkthrough
                </button>
              </div>

              {/* 4 Step Workflow Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="w-7 h-7 rounded-xl bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center">1</div>
                  <h4 className="text-xs font-bold text-white">Live Loading Bay Audit</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Select any of the 4 active loading bays (Bays 01 to 04). Check real-time video frames, package kinematic impulse, and face anonymization/silhouette shields.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="w-7 h-7 rounded-xl bg-amber-500/20 text-amber-400 font-bold text-xs flex items-center justify-center">2</div>
                  <h4 className="text-xs font-bold text-white">Inject Damage Scenarios</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Test how the pipeline detects drops, crushes, rough throws, or floor dragging. The system calculates impact Joules and acceleration in sub-50 milliseconds.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="w-7 h-7 rounded-xl bg-blue-500/20 text-blue-400 font-bold text-xs flex items-center justify-center">3</div>
                  <h4 className="text-xs font-bold text-white">Review & 5-Why RCA</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Click any incident card from the Alert Feed to inspect high-speed freeze frame evidence, sensor physics breakdown, and automated 5-Why root cause analysis.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="w-7 h-7 rounded-xl bg-teal-500/20 text-teal-400 font-bold text-xs flex items-center justify-center">4</div>
                  <h4 className="text-xs font-bold text-white">Track Savings in ₹ (Rupees)</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Navigate to Shift Analytics to observe historical risk indexes and use the Indian Rupee ROI calculator to determine monthly and annual damage write-offs saved.
                  </p>
                </div>
              </div>
            </div>

            {/* Detailed Instructions Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Card 1: 10 Damage Behaviors Reference */}
              <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-400" /> 10-Behavior Taxonomy Reference Chart
                </h3>
                <p className="text-xs text-slate-400">
                  Standard handling failure modes recognized across Indian logistics networks (Flipkart, Amazon India, Delhivery, BlueDart hubs):
                </p>
                <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1 text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">1. Freefall Drop (BEH_DROP)</strong>
                      <span className="text-slate-400 text-[11px]">Vertical acceleration &gt; 8.5 m/s², height &gt; 1.2m</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">Critical</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">2. Inverted Pyramid (BEH_IMPROPER_STACK)</strong>
                      <span className="text-slate-400 text-[11px]">Heavy mass carton placed over fragile or smaller lower carton</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">Critical</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">3. Unsafe Pallet Overhang (BEH_PALLET_OVERHANG)</strong>
                      <span className="text-slate-400 text-[11px]">Carton base protrudes &gt; 30% beyond wooden pallet perimeter</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">High</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">4. Carton Throwing / Tossing (BEH_TOSS_THROW)</strong>
                      <span className="text-slate-400 text-[11px]">Parabolic flight trajectory without two-point continuous grip</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">Critical</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">5. Floor Dragging Cartons (BEH_DRAG)</strong>
                      <span className="text-slate-400 text-[11px]">Abrasion drag over 4.0 meters on concrete dock floor</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">High</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                    <div>
                      <strong className="text-white block font-medium">6. Forklift Pinch Hazard (BEH_FORKLIFT_PINCH)</strong>
                      <span className="text-slate-400 text-[11px]">Moving forklift within 1.0m pedestrian exclusion boundary</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">Critical</span>
                  </div>
                </div>
              </div>

              {/* Card 2: Supervisor Guidelines & Best Practices */}
              <div className="bg-slate-900 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-teal-400" /> Operational Roles & Guidelines
                </h3>
                <p className="text-xs text-slate-400">
                  Role-Based Action Protocols for SafeStack AI users:
                </p>
                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <span className="font-bold text-emerald-400 block">Supervisor Role</span>
                    <p className="text-slate-400 leading-relaxed">
                      Responsible for approving or rejecting Critical incident alerts. Add corrective coaching notes and verify whether damages were prevented before signing off.
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <span className="font-bold text-cyan-400 block">Bay Lead Role</span>
                    <p className="text-slate-400 leading-relaxed">
                      Monitors the live camera feeds, listens to audio coaching chimes, and conducts quick verbal nudges to dock loaders if boxes tilt or overhang excessive margins.
                    </p>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                    <span className="font-bold text-amber-400 block">Auditor / Safety Officer</span>
                    <p className="text-slate-400 leading-relaxed">
                      Reviews aggregate shift trends in Chart.js, calculates month-end cost savings in ₹ Rupees, and verifies zero worker facial data retention for labor audits.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Human-in-the-Loop Review Modal */}
      {selectedEvent && (
        <EventReviewModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onReviewSubmitted={handleReviewSubmitted}
        />
      )}

      {/* User Guide & Walkthrough Modal */}
      <UserGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
        onNavigateTab={(tab) => setActiveTab(tab)}
      />

      {/* Conversational AI Assistant Drawer */}
      <AssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
        onSelectEventById={handleSelectEventById}
      />
    </div>
  );
}
