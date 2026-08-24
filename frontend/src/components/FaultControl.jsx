import React from 'react';
import { ShieldCheck, Play, Flame, ShieldAlert, Cpu, Hammer } from 'lucide-react';

export default function FaultControl({ onTriggerFault, onRunSreAgent, activeIncident, loading }) {
  const isDisabled = activeIncident !== null || loading;

  return (
    <div className="glass-card p-6 flex flex-col gap-6 border border-white/5 bg-[#0a0b10] rounded-none">
      <div>
        <h2 className="text-sm uppercase tracking-wider font-extrabold text-gradient flex items-center gap-2">
          <Flame className="w-4 h-4 text-amber-500" /> Fault Injection Modules
        </h2>
        <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono mt-1">
          Trigger simulated bottlenecks & failures
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <button 
          className={`group border border-rose-950/40 bg-rose-950/5 rounded-none p-4 text-left transition-all flex flex-col justify-between ${
            isDisabled ? 'opacity-40 cursor-not-allowed' : 'hover:bg-rose-950/10 hover:border-rose-500/20'
          }`}
          onClick={() => !isDisabled && onTriggerFault('gpu_memory_leak')}
          disabled={isDisabled}
        >
          <div>
            <strong className="text-xs font-bold text-rose-400 font-mono tracking-tight block mb-1">🔴 GPU VRAM Leak</strong>
            <span className="text-[10px] text-slate-500 block leading-tight font-mono">CUDA Overflow on render-gpu-04</span>
          </div>
          <span className="text-[9px] uppercase tracking-wider font-mono text-rose-400/50 mt-4 flex items-center gap-1">
            {isDisabled ? 'LOCKED' : 'INJECT FAULT'} <Play className="w-2 h-2" />
          </span>
        </button>

        <button 
          className={`group border border-amber-950/40 bg-amber-950/5 rounded-none p-4 text-left transition-all flex flex-col justify-between ${
            isDisabled ? 'opacity-40 cursor-not-allowed' : 'hover:bg-amber-950/10 hover:border-amber-500/20'
          }`}
          onClick={() => !isDisabled && onTriggerFault('corrupt_texture_asset')}
          disabled={isDisabled}
        >
          <div>
            <strong className="text-xs font-bold text-amber-400 font-mono tracking-tight block mb-1">🟠 Asset Stall</strong>
            <span className="text-[10px] text-slate-500 block leading-tight font-mono">0-Byte EXR on render-gpu-02</span>
          </div>
          <span className="text-[9px] uppercase tracking-wider font-mono text-amber-400/50 mt-4 flex items-center gap-1">
            {isDisabled ? 'LOCKED' : 'INJECT FAULT'} <Play className="w-2 h-2" />
          </span>
        </button>

        <button 
          className={`group border border-purple-950/40 bg-purple-950/5 rounded-none p-4 text-left transition-all flex flex-col justify-between ${
            isDisabled ? 'opacity-40 cursor-not-allowed' : 'hover:bg-purple-950/10 hover:border-purple-500/20'
          }`}
          onClick={() => !isDisabled && onTriggerFault('runaway_agent_loop')}
          disabled={isDisabled}
        >
          <div>
            <strong className="text-xs font-bold text-purple-400 font-mono tracking-tight block mb-1">🟣 Runaway Loop</strong>
            <span className="text-[10px] text-slate-500 block leading-tight font-mono">LLM recursion on ai-worker-01</span>
          </div>
          <span className="text-[9px] uppercase tracking-wider font-mono text-purple-400/50 mt-4 flex items-center gap-1">
            {isDisabled ? 'LOCKED' : 'INJECT FAULT'} <Play className="w-2 h-2" />
          </span>
        </button>
      </div>

      {activeIncident ? (
        <div className="bg-rose-950/10 border border-rose-900/30 rounded-none p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-rose-500 animate-pulse"></div>
          <div>
            <span className="text-[9px] text-rose-400 font-mono font-black uppercase tracking-wider block">
              ⚠️ ACTIVE INCIDENT IN PROGRESS — NODE: {activeIncident.node_id}
            </span>
            <h4 className="text-xs font-bold text-white mt-1 font-mono tracking-tight">{activeIncident.title}</h4>
            <p className="text-[11px] text-slate-400 mt-1 max-w-xl font-mono">{activeIncident.summary}</p>
          </div>

          <button 
            className="px-4 py-2 text-xs font-bold font-mono tracking-wider bg-rose-600 hover:bg-rose-700 active:scale-98 text-white rounded-none transition flex items-center gap-2 self-end sm:self-auto shadow-md"
            onClick={onRunSreAgent}
            disabled={loading}
          >
            <Hammer className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'REMEDIATION IN PROGRESS...' : 'DEPLOY SRE AGENT'}
          </button>
        </div>
      ) : (
        <div className="bg-emerald-950/5 border border-emerald-950/20 rounded-none p-4 text-[10px] uppercase font-mono tracking-wider text-emerald-400 flex items-center gap-2.5">
          <ShieldAlert className="w-4 h-4 text-emerald-400" />
          <span>Matrix Operating Normally. Select a module to inject fault logs.</span>
        </div>
      )}
    </div>
  );
}
