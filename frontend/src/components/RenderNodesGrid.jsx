import React from 'react';
import { Server, Cpu, HardDrive, Terminal } from 'lucide-react';

export default function RenderNodesGrid({ clusterStatus }) {
  const nodes = clusterStatus?.nodes || [];

  const getStatusBadge = (status) => {
    switch (status) {
      case 'HEALTHY':
        return { 
          label: 'HEALTHY', 
          bg: 'bg-emerald-500/5 text-emerald-400 border-emerald-500/20',
          pulse: 'pulse-emerald',
          shadow: 'shadow-emerald-500/2'
        };
      case 'CRITICAL_FAIL':
        return { 
          label: 'CUDA CRASH', 
          bg: 'bg-rose-500/5 text-rose-400 border-rose-500/20',
          pulse: 'pulse-rose',
          shadow: 'shadow-rose-500/5'
        };
      case 'STALLED':
        return { 
          label: 'I/O STALL', 
          bg: 'bg-amber-500/5 text-amber-400 border-amber-500/20',
          pulse: 'pulse-amber',
          shadow: 'shadow-amber-500/5'
        };
      case 'RUNAWAY_LOOP':
        return { 
          label: 'LOOP TIMEOUT', 
          bg: 'bg-purple-500/5 text-purple-400 border-purple-500/20',
          pulse: 'pulse-rose',
          shadow: 'shadow-purple-500/5'
        };
      default:
        return { 
          label: status, 
          bg: 'bg-slate-500/5 text-slate-400 border-slate-500/20',
          pulse: 'pulse-blue',
          shadow: 'shadow-slate-500/2'
        };
    }
  };

  return (
    <div className="glass-card p-6 border border-white/5 bg-[#0a0b10] rounded-none">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-sm uppercase tracking-wider font-extrabold text-gradient flex items-center gap-2">
            <Server className="w-4 h-4 text-slate-400" /> Render Cluster Matrix
          </h2>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono mt-1">Telemetry Nodes Blade Enclosure</p>
        </div>
        <div>
          <span className={`text-[10px] font-mono font-bold px-2.5 py-1 border rounded-none ${
            nodes.length > 0
              ? 'text-emerald-400 bg-emerald-500/5 border-emerald-500/10'
              : 'text-amber-400 bg-amber-500/5 border-amber-500/10'
          }`}>
            {nodes.length > 0
              ? `HEALTHY: ${clusterStatus?.healthy_nodes || 0}/${clusterStatus?.total_nodes || 0}`
              : 'CONNECTING...'}
          </span>
        </div>
      </div>

      {nodes.length === 0 ? (
        <div className="text-center py-8 text-slate-500 text-xs font-mono uppercase tracking-wider border border-white/5 bg-slate-950/20">
          Connecting to Render Farm Telemetry Backend...
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {nodes.map((node) => {
          const badge = getStatusBadge(node.status);
          const vramPercent = Math.min(100, Math.round((node.gpu_memory_mb / 24000) * 100));
          const isStalled = node.status !== 'HEALTHY';

          return (
            <div 
              key={node.id} 
              className={`bg-slate-950/40 rounded-none border border-white/5 p-4 flex flex-col justify-between hover:border-white/15 transition-all duration-300 relative ${badge.shadow} ${isStalled ? 'border-l-2 border-l-rose-500' : ''}`}
            >
              {/* Scanline active glow */}
              {isStalled && (
                <div className="absolute top-0 right-0 w-1.5 h-1.5 bg-rose-500 rounded-full status-pulse pulse-rose m-2"></div>
              )}

              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-black text-slate-300 font-mono tracking-tight">{node.id}</span>
                  <span className={`px-2 py-0.5 text-[9px] font-mono font-semibold rounded-none border flex items-center gap-1.5 ${badge.bg}`}>
                    {!isStalled && <span className={`status-pulse ${badge.pulse}`}></span>}
                    {badge.label}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 font-mono tracking-tight">{node.name}</p>
              </div>

              {/* Resource Bars */}
              <div className="my-3 space-y-2">
                {/* VRAM Bar */}
                <div>
                  <div className="flex justify-between text-[9px] font-mono text-slate-500 mb-0.5">
                    <span>VRAM LOAD</span>
                    <span className="text-slate-400 font-semibold">{node.gpu_memory_mb} MB ({vramPercent}%)</span>
                  </div>
                  <div className="w-full h-1 bg-[#12131b] rounded-none overflow-hidden border border-white/5">
                    <div 
                      className={`h-full transition-all duration-500 ease-out ${
                        vramPercent > 90 
                          ? 'bg-rose-600' 
                          : vramPercent > 70 
                          ? 'bg-amber-600' 
                          : 'bg-emerald-600'
                      }`}
                      style={{ width: `${vramPercent}%` }}
                    ></div>
                  </div>
                </div>

                {/* CPU Bar */}
                <div>
                  <div className="flex justify-between text-[9px] font-mono text-slate-500 mb-0.5">
                    <span>CPU LOAD</span>
                    <span className="text-slate-400 font-semibold">{node.cpu_percent}%</span>
                  </div>
                  <div className="w-full h-1 bg-[#12131b] rounded-none overflow-hidden border border-white/5">
                    <div 
                      className={`h-full transition-all duration-500 ease-out ${
                        node.cpu_percent > 90 
                          ? 'bg-rose-600' 
                          : node.cpu_percent > 70 
                          ? 'bg-amber-600' 
                          : 'bg-emerald-600'
                      }`}
                      style={{ width: `${node.cpu_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="flex justify-between text-[9px] text-slate-500 border-t border-white/5 pt-2 mt-1 font-mono">
                <span>RACK SLOT: A-{node.id.slice(-2)}</span>
                <span>FRAME: <span className="text-slate-300 font-semibold">{node.current_frame}</span></span>
              </div>
            </div>
          );
        })}
      </div>
      )}
    </div>
  );
}
