import React, { useState } from 'react';
import { History, ExternalLink, ChevronDown, ChevronUp, FileText, Activity } from 'lucide-react';

export default function IncidentHistory({ history, onSelectIncident }) {
  const [expandedRows, setExpandedRows] = useState({});

  const toggleRow = (id, inc, e) => {
    // Avoid toggling when clicking links
    if (e.target.closest('a')) return;
    
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
    
    if (onSelectIncident) {
      onSelectIncident(inc);
    }
  };

  const getSeverityAccent = (sev) => {
    const s = String(sev).toLowerCase();
    if (s === 'critical') return 'border-l-2 border-l-rose-600';
    if (s === 'high' || s === 'warning') return 'border-l-2 border-l-amber-500';
    return 'border-l-2 border-l-sky-500';
  };

  const getSeverityBadge = (sev) => {
    const s = String(sev).toLowerCase();
    if (s === 'critical') {
      return 'bg-rose-500/5 text-rose-400 border border-rose-500/20';
    }
    if (s === 'high' || s === 'warning') {
      return 'bg-amber-500/5 text-amber-400 border border-amber-500/20';
    }
    return 'bg-sky-500/5 text-sky-400 border border-sky-500/20';
  };

  // Inline basic markdown renderer
  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    let insideCodeBlock = false;
    let codeContent = [];

    return lines.map((line, idx) => {
      if (line.trim().startsWith('```')) {
        if (insideCodeBlock) {
          insideCodeBlock = false;
          const renderedCode = (
            <pre key={`code-${idx}`} className="bg-slate-950/80 border border-white/5 rounded-none p-3 font-mono text-[10px] text-slate-400 my-2 overflow-x-auto leading-normal">
              <code>{codeContent.join('\n')}</code>
            </pre>
          );
          codeContent = [];
          return renderedCode;
        } else {
          insideCodeBlock = true;
          return null;
        }
      }

      if (insideCodeBlock) {
        codeContent.push(line);
        return null;
      }

      if (line.startsWith('# ')) {
        return <h1 key={idx} className="text-xs uppercase tracking-wider font-extrabold text-white mb-2 mt-3 border-b border-white/5 pb-1 font-mono">{line.substring(2)}</h1>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={idx} className="text-[11px] font-mono uppercase tracking-wide font-extrabold text-slate-300 mb-1 mt-3 flex items-center gap-1.5">{line.substring(3)}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-[10px] font-mono uppercase font-bold text-slate-400 mb-1 mt-2">{line.substring(4)}</h3>;
      }

      if (line.startsWith('> ')) {
        return (
          <blockquote key={idx} className="border-l-2 border-sky-400 bg-sky-500/5 p-2 my-2 text-[10px] text-slate-300 font-mono italic leading-relaxed">
            {line.substring(2)}
          </blockquote>
        );
      }

      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return (
          <li key={idx} className="text-[10px] text-slate-400 ml-3 mb-1 list-disc leading-relaxed font-mono">
            {line.trim().substring(2)}
          </li>
        );
      }

      if (line.trim() === '') {
        return <div key={idx} className="h-1"></div>;
      }

      const parts = line.split(/(`[^`]+`)/g);
      const parsedLine = parts.map((part, pidx) => {
        if (part.startsWith('`') && part.endsWith('`')) {
          return <code key={pidx} className="bg-slate-900 text-sky-400 px-1.5 py-0.5 rounded-none text-[9px] font-mono border border-white/5">{part.slice(1, -1)}</code>;
        }
        return part;
      });

      return <p key={idx} className="text-[10px] text-slate-400 mb-1 leading-relaxed font-mono">{parsedLine}</p>;
    });
  };

  return (
    <div className="glass-card p-6 border border-white/5 bg-[#0a0b10] rounded-none">
      <div className="flex items-center gap-2 mb-6">
        <History className="w-4 h-4 text-slate-400" />
        <div>
          <h3 className="text-sm uppercase tracking-wider font-extrabold text-gradient">Incident History & Resolutions</h3>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono mt-1">Archived incident mitigation database</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        {history.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs font-mono uppercase tracking-wider">
            No incidents logged in this session yet. Inject a fault module to begin.
          </div>
        ) : (
          <table className="w-full text-left border-collapse font-mono">
            <thead>
              <tr className="border-b border-white/5 text-slate-500 text-[10px] font-bold uppercase tracking-wider">
                <th className="pb-3 pr-4 pl-2">Incident ID</th>
                <th className="pb-3 pr-4">Severity</th>
                <th className="pb-3 pr-4">Target Node</th>
                <th className="pb-3 pr-4">Remediation Action</th>
                <th className="pb-3 pr-2 text-right">Resolved At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-[11px]">
              {history.map((inc) => {
                const isExpanded = !!expandedRows[inc.incident_id];
                const postmortemText = inc.postmortem_markdown || 
                  `# Incident Postmortem: ${inc.incident_id}\n\n## Summary\n- **Incident Title:** ${inc.title}\n- **Target Node:** \`${inc.node_id}\`\n- **Impact:** ${inc.severity} severity.\n\n## Remediation\n> ${inc.remediation_action}`;
                
                return (
                  <React.Fragment key={inc.incident_id}>
                    <tr 
                      className={`hover:bg-white/[0.01] cursor-pointer transition ${getSeverityAccent(inc.severity)}`}
                      onClick={(e) => toggleRow(inc.incident_id, inc, e)}
                    >
                      <td className="py-3 pr-4 pl-2 font-bold text-sky-400 flex items-center gap-1.5">
                        {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-slate-500" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-500" />}
                        {inc.incident_id}
                      </td>
                      <td className="py-3 pr-4">
                        <span className={`px-2 py-0.5 text-[9px] font-bold uppercase ${getSeverityBadge(inc.severity)}`}>
                          {inc.severity}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-slate-300">{inc.node_id}</td>
                      <td className="py-3 pr-4 text-slate-400 truncate max-w-xs">{inc.remediation_action}</td>
                      <td className="py-3 pr-2 text-right text-slate-500">{inc.resolved_at}</td>
                    </tr>
                    
                    {isExpanded && (
                      <tr className="bg-slate-950/20">
                        <td colSpan={5} className="p-4 pl-8 border-l border-white/5">
                          <div className="flex flex-col gap-4">
                            {/* Deep Links / Actions Bar */}
                            <div className="flex items-center gap-4 text-[10px] border-b border-white/5 pb-2.5">
                              {inc.annotation_id ? (
                                <a 
                                  href={`https://quirkyviper1507.grafana.net/api/annotations/${inc.annotation_id}`} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1 text-sky-400 hover:text-sky-300 font-bold uppercase transition"
                                >
                                  <ExternalLink className="w-3.5 h-3.5" />
                                  View Annotation ID #{inc.annotation_id} in Grafana Cloud
                                </a>
                              ) : (
                                <span className="text-slate-500 uppercase">No active Grafana Cloud Annotation registered</span>
                              )}
                              
                              <span className="text-slate-600">|</span>
                              
                              <span className="text-slate-400">
                                NODE: <span className="text-slate-200 font-bold">{inc.node_id}</span>
                              </span>
                              <span className="text-slate-600">|</span>
                              <span className="text-slate-400">
                                TIMESTAMP: <span className="text-slate-200">{inc.timestamp}</span>
                              </span>
                            </div>

                            {/* Markdown render wrapper */}
                            <div className="postmortem-container max-w-4xl bg-slate-950/40 p-4 border border-white/5 rounded-none">
                              {renderMarkdown(postmortemText)}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
