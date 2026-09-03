import React, { useState, useEffect } from 'react';
import { Cpu, Server, Radio, Shield, HelpCircle } from 'lucide-react';

export default function Header({ status }) {
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="px-8 py-5 flex justify-between items-center border-b border-white/5 bg-[#0b0c13]/80 backdrop-blur-md sticky top-0 z-50">
      {/* Brand logo & title */}
      <div className="flex items-center gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-slate-900 border border-white/10 flex items-center justify-center relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-tr from-sky-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <Cpu className="w-5 h-5 text-sky-400 relative z-10 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-extrabold uppercase tracking-wider text-gradient flex items-center gap-2">
            CineFlow <span className="text-sky-400 font-mono text-xs px-2 py-0.5 rounded bg-sky-500/10 border border-sky-500/20">IRM</span>
          </h1>
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-medium">
            Autonomous SRE Command Center • Grafana MCP Track
          </p>
        </div>
      </div>

      {/* Integration pulse dots & Status Indicators */}
      <div className="flex items-center gap-6">
        {/* Active Backend Connection Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-950/80 border border-white/5">
          <Radio className="w-3.5 h-3.5 text-sky-400 animate-pulse" />
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Backend: </span>
          <span className="text-[10px] font-mono text-sky-400 font-semibold">
            {import.meta.env.VITE_API_URL ? "Render Production" : "Local Engine"}
          </span>
        </div>

        {/* Live Status Indicators */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 status-pulse pulse-emerald"></span>
            <span>Loki: PUSH</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 status-pulse pulse-emerald"></span>
            <span>Tempo: TRACES</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className={`w-2 h-2 rounded-full ${
              status?.last_gemini_status === "LIVE" ? 'bg-emerald-500 status-pulse pulse-emerald' :
              status?.last_gemini_status === "FALLBACK MODE" ? 'bg-amber-500 status-pulse pulse-amber' :
              status?.gemini_api_configured ? 'bg-emerald-500 status-pulse pulse-emerald' : 'bg-rose-500 status-pulse pulse-rose'
            }`}></span>
            <span>
              Gemini: {
                status?.last_gemini_status === "LIVE" ? "LIVE" :
                status?.last_gemini_status === "FALLBACK MODE" ? "FALLBACK MODE" :
                status?.gemini_api_configured ? "READY" : "OFFLINE"
              }
            </span>
          </div>
        </div>

        {/* Local time */}
        <div className="text-xs font-mono font-semibold text-slate-400 px-3 py-1.5 rounded-lg bg-slate-950/50 border border-white/5 min-w-[90px] text-center">
          {time}
        </div>
      </div>
    </header>
  );
}
