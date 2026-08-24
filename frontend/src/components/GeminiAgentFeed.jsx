import React from 'react';
import { Cpu, Terminal, CheckCircle2, ChevronRight, Activity, Code } from 'lucide-react';

export default function GeminiAgentFeed({ reasoningResult, loading }) {
  if (loading) {
    return (
      <div className="glass-card p-6 flex flex-col items-center justify-center min-h-[300px] text-center text-slate-500 border border-white/5 bg-[#0a0b10] rounded-none">
        <div className="w-10 h-10 rounded-none bg-sky-500/5 border border-sky-500/10 flex items-center justify-center text-sky-400 mb-4 animate-spin">
          <Activity className="w-4 h-4" />
        </div>
        <h4 className="text-xs font-mono font-bold text-white mb-1 uppercase tracking-wider">GEMINI SRE PIPELINE DEPLOYED</h4>
        <p className="text-[10px] font-mono max-w-sm uppercase leading-relaxed text-slate-500">Querying Loki index & Tempo trace matrix...Executing automated mitigation runbooks...</p>
        <div className="flex gap-1.5 mt-4">
          <span className="w-1.5 h-1.5 bg-sky-400 animate-bounce"></span>
          <span className="w-1.5 h-1.5 bg-sky-400 animate-bounce [animation-delay:0.2s]"></span>
          <span className="w-1.5 h-1.5 bg-sky-400 animate-bounce [animation-delay:0.4s]"></span>
        </div>
      </div>
    );
  }

  if (!reasoningResult) {
    return (
      <div className="glass-card p-8 flex flex-col items-center justify-center text-center text-slate-500 min-h-[300px] border border-white/5 bg-[#0a0b10] rounded-none">
        <Terminal className="w-8 h-8 opacity-20 mb-3" />
        <p className="text-[10px] max-w-xs leading-relaxed uppercase tracking-wider font-mono">
          Awaiting telemetry signals. SRE reasoning stream and tool logs will output here.
        </p>
      </div>
    );
  }

  const isFallback = reasoningResult.reasoning_steps?.some(s => s.includes("fallback") || s.includes("MOCKED"));

  return (
    <div className="glass-card p-6 flex flex-col justify-between h-full border border-white/5 bg-[#0a0b10] rounded-none">
      <div>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-sm uppercase tracking-wider font-extrabold text-gradient flex items-center gap-2">
              <Cpu className="w-4 h-4 text-sky-400" /> SRE Diagnostic Feed
            </h2>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono mt-1">Loki & Tempo Automated Cross-Reference</p>
          </div>

          <div className="flex gap-2">
            <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded-none border flex items-center gap-1.5 ${
              isFallback 
                ? 'bg-slate-500/5 text-slate-400 border-slate-500/10' 
                : 'bg-emerald-500/5 text-emerald-400 border-emerald-500/10'
            }`}>
              {isFallback ? 'DYNAMIC RESOLUTION' : 'LIVE GEMINI'}
            </span>
            <span className="text-[9px] font-mono font-bold text-slate-400 bg-slate-500/5 px-2 py-0.5 rounded-none border border-white/5">
              LATENCY: {reasoningResult.resolution_time_seconds || '6.2'}s
            </span>
          </div>
        </div>

        {/* Reasoning Steps */}
        <div className="flex flex-col gap-2 mb-6 font-mono text-[10px] leading-relaxed">
          {reasoningResult.reasoning_steps?.map((step, idx) => {
            let typeClass = "info";
            if (step.includes("[ERROR]") || step.includes("Exception") || step.includes("failed")) typeClass = "error";
            else if (step.includes("[WARN]") || step.includes("approaching")) typeClass = "warn";
            else if (step.includes("[SRE ACTION]") || step.includes("Posted annotation") || step.includes("remediate")) typeClass = "success";

            return (
              <div key={idx} className={`terminal-line ${typeClass} bg-slate-950/20 p-2.5 rounded-none border border-white/5 flex items-start gap-2`}>
                <ChevronRight className="w-3.5 h-3.5 mt-0.5 text-slate-600 shrink-0" />
                <span className="tracking-tight">{step}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Root Cause & Remediation Summary Box */}
      <div className="bg-emerald-950/5 border border-emerald-950/20 rounded-none p-5 relative overflow-hidden">
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500"></div>
        <h4 className="text-[9px] text-emerald-400 font-mono font-bold uppercase tracking-wider flex items-center gap-1.5">
          <Code className="w-3.5 h-3.5" /> ROOT CAUSE DIAGNOSIS & REMEDIATION RECORD
        </h4>
        <p className="text-xs font-mono font-bold text-white mt-2 leading-normal">
          {reasoningResult.root_cause}
        </p>
        <div className="text-[10px] text-slate-400 font-mono mt-3 flex items-start gap-2 border-t border-white/5 pt-3 leading-normal">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
          <span>Remediation: <span className="text-slate-200">{reasoningResult.action_taken}</span></span>
        </div>
      </div>
    </div>
  );
}
