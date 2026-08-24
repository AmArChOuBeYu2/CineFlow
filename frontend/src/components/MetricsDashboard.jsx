import React, { useState, useEffect } from 'react';
import { Cpu, Zap, Link, Clock, RefreshCw } from 'lucide-react';

export default function MetricsDashboard({ metrics, incidentCount, mttrSeconds }) {
  const [lastPolled, setLastPolled] = useState('');

  useEffect(() => {
    setLastPolled(new Date().toLocaleTimeString());
  }, [metrics, incidentCount, mttrSeconds]);

  const formatMttr = (sec) => {
    if (!sec || isNaN(sec)) return '0.0s';
    return `${parseFloat(sec).toFixed(1)}s`;
  };

  const liveCount = Math.max(0, metrics.task_executions - metrics.fallback_count);

  return (
    <div className="flex flex-col gap-2 mb-6">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {/* Metric Card 1: MTTR */}
        <div className="glass-card p-5 flex items-center justify-between border border-white/5 bg-[#0a0b10] rounded-none">
          <div>
            <span className="text-[10px] uppercase tracking-wider font-mono text-slate-500 block mb-1">MTTR (MEAN TIME TO RESOLUTION)</span>
            <h3 className="text-xl font-bold font-mono text-slate-100">
              {formatMttr(mttrSeconds)}
            </h3>
          </div>
          <div className="w-9 h-9 rounded-none bg-sky-500/5 flex items-center justify-center text-sky-400 border border-sky-500/10">
            <Clock className="w-4.5 h-4.5" />
          </div>
        </div>

        {/* Metric Card 2: Total Incidents */}
        <div className="glass-card p-5 flex items-center justify-between border border-white/5 bg-[#0a0b10] rounded-none">
          <div>
            <span className="text-[10px] uppercase tracking-wider font-mono text-slate-500 block mb-1">WEBHOOKS RECEIVED</span>
            <h3 className="text-xl font-bold font-mono text-slate-100">
              {incidentCount || 0}
            </h3>
          </div>
          <div className="w-9 h-9 rounded-none bg-purple-500/5 flex items-center justify-center text-purple-400 border border-purple-500/10">
            <Zap className="w-4.5 h-4.5" />
          </div>
        </div>

        {/* Metric Card 3: LLM Calls & Quotas */}
        <div className="glass-card p-5 flex items-center justify-between border border-white/5 bg-[#0a0b10] rounded-none">
          <div>
            <span className="text-[10px] uppercase tracking-wider font-mono text-slate-500 block mb-1">AGENT ENGINE PIPELINE</span>
            <h3 className="text-[10px] font-bold font-mono text-slate-300 mt-1 flex flex-col gap-0.5">
              {metrics.task_executions > 0 ? (
                <>
                  <span className="text-slate-100 font-extrabold text-sm">{metrics.task_executions} PROCESS RUNS</span>
                  <span className="text-slate-500">
                    LIVE: <span className="text-emerald-400">{liveCount}</span> | FALLBACK: <span className="text-amber-500">{metrics.fallback_count}</span>
                  </span>
                </>
              ) : (
                <span className="text-slate-500 font-normal uppercase">SYSTEM IN standby</span>
              )}
            </h3>
          </div>
          <div className="w-9 h-9 rounded-none bg-amber-500/5 flex items-center justify-center text-amber-400 border border-amber-500/10">
            <Cpu className="w-4.5 h-4.5" />
          </div>
        </div>

        {/* Metric Card 4: Grafana Annotations Integration */}
        <div className="glass-card p-5 flex items-center justify-between border border-white/5 bg-[#0a0b10] rounded-none">
          <div>
            <span className="text-[10px] uppercase tracking-wider font-mono text-slate-500 block mb-1">GRAFANA MCP telemetry</span>
            <h3 className="text-[11px] font-bold font-mono text-emerald-400 mt-1 flex items-center gap-1.5 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 status-pulse pulse-emerald"></span>
              DATA FEED OK
            </h3>
          </div>
          <div className="w-9 h-9 rounded-none bg-emerald-500/5 flex items-center justify-center text-emerald-400 border border-emerald-500/10">
            <Link className="w-4.5 h-4.5" />
          </div>
        </div>
      </div>

      {/* Live Polling Info Bar */}
      <div className="flex justify-end items-center gap-1.5 px-3 py-1 bg-slate-950/30 border border-white/5 text-[9px] font-mono text-slate-500 uppercase rounded-none">
        <RefreshCw className="w-3 h-3 text-slate-600 animate-spin" />
        <span>Live Polling Active • Last telemetry update: {lastPolled}</span>
      </div>
    </div>
  );
}
