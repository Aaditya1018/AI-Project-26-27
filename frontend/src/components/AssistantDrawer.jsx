import React, { useState } from 'react';
import { MessageSquare, Send, Sparkles, ShieldCheck, CornerDownLeft, ExternalLink, Bot, User } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function AssistantDrawer({ isOpen, onClose, onSelectEventById }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "👋 Hello! I am the **SafeStack AI Supervisor Assistant**. Ask me any operational or risk query about loading bay activities, dropping incidents, pallet stability, or forklift clearance. All answers are strictly grounded in computer-vision evidence.",
      citations: [],
      provider: 'SafeStack Evidence-Grounded Engine'
    }
  ]);
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    "Which bay had the most drop incidents?",
    "Why was event EVT-1001 flagged as Critical?",
    "Provide a shift summary and high-risk behaviors",
    "Forklift and pedestrian clearance audit"
  ];

  const handleSend = async (textToSend) => {
    const q = textToSend || query;
    if (!q.trim() || loading) return;

    const userMsg = { sender: 'user', text: q };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await sendChatMessage(q);
      const assistantMsg = {
        sender: 'assistant',
        text: res.answer,
        citations: res.citations || [],
        provider: res.provider_used || 'Grounded Engine'
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: "⚠️ Unable to connect to the operational telemetry service: " + e.message,
          citations: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              SafeStack AI Assistant <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            </h3>
            <p className="text-[11px] text-emerald-400 font-medium">
              Zero-Fabrication Grounded in CV Telemetry
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
        >
          ✕
        </button>
      </div>

      {/* Quick Suggestion Pills */}
      <div className="p-3 bg-slate-950/40 border-b border-slate-800/80 overflow-x-auto flex items-center gap-2">
        {quickPrompts.map((p, i) => (
          <button
            key={i}
            onClick={() => handleSend(p)}
            className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium whitespace-nowrap border border-slate-700/60 transition-all shrink-0"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`p-3.5 rounded-2xl max-w-[90%] space-y-2 ${
                m.sender === 'user'
                  ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-600/10'
                  : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none shadow-md'
              }`}
            >
              <div className="whitespace-pre-line leading-relaxed font-sans">
                {m.text}
              </div>

              {/* Citations Pills */}
              {m.citations && m.citations.length > 0 && (
                <div className="pt-2 border-t border-slate-800/80 mt-2 space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">
                    Telemetry Citations
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {m.citations.map((c, ci) => (
                      <button
                        key={ci}
                        onClick={() => onSelectEventById && onSelectEventById(c.event_id)}
                        className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-slate-700 flex items-center gap-1 font-mono transition-all"
                      >
                        {c.event_id} ({c.risk_tier}) <ExternalLink className="w-2.5 h-2.5" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {m.provider && (
              <span className="text-[9px] text-slate-400 mt-1 px-1">
                Verified via {m.provider}
              </span>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs italic p-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            Querying computer-vision event store...
          </div>
        )}
      </div>

      {/* Input Field */}
      <div className="p-3.5 border-t border-slate-800 bg-slate-950 flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about bay incidents, risk, or root causes..."
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !query.trim()}
          className="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white transition-all shadow-md shadow-emerald-600/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
