import React from 'react';
import { AlertCircle, FileText, Activity, Terminal, CheckCircle, Bookmark } from 'lucide-react';

export default function IncidentTimeline({ activeIncident, logs, traces, activeTimelineStep }) {
  const steps = [
    {
      title: '1. ALERT RECEIVED',
      desc: activeIncident 
        ? `Grafana contact point webhook fired for node '${activeIncident.node_id}'`
        : 'Awaiting alert webhook delivery via ngrok...',
      icon: AlertCircle,
      stepNum: 1,
    },
    {
      title: '2. LOKI INGESTION',
      desc: activeIncident
        ? `Ingested LogQL stream: {node="${activeIncident.node_id}"} |= "ERROR"`
        : 'Telemetry Loki logs index query pending...',
      icon: FileText,
      stepNum: 2,
    },
    {
      title: '3. TEMPO SEARCH',
      desc: activeIncident
        ? `Parsed traces: {resource.service.name="${activeIncident.node_id}"}`
        : 'Distributed TraceQL spans query pending...',
      icon: Activity,
      stepNum: 3,
    },
    {
      title: '4. GEMINI REASONING',
      desc: activeIncident
        ? `Generating technical root cause & remediation playbook...`
        : 'LLM root cause analysis engine idle...',
      icon: Terminal,
      stepNum: 4,
    },
    {
      title: '5. REMEDIATION PLAN',
      desc: activeIncident?.remediation_action
        ? `Remediation: ${activeIncident.remediation_action}`
        : 'Remediation script execution pending...',
      icon: CheckCircle,
      stepNum: 5,
    },
    {
      title: '6. POSTMORTEM ANNOTATED',
      desc: activeIncident?.resolved_at
        ? `Incident postmortem successfully posted back to Grafana Annotations API`
        : 'Grafana event timeline annotation pending...',
      icon: Bookmark,
      stepNum: 6,
    }
  ];

  return (
    <div className="glass-card p-6 h-full flex flex-col justify-between border border-white/5 bg-[#0a0b10] rounded-none">
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-sm uppercase tracking-wider font-extrabold text-gradient flex items-center gap-2">
              Incident Execution Loop
            </h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono mt-1">SRE Pipeline Orchestrator</p>
          </div>
          {activeIncident && (
            <span className={`px-2.5 py-1 text-[9px] font-mono font-bold rounded-none border flex items-center gap-1.5 ${
              activeIncident.resolved_at 
                ? 'bg-emerald-500/5 text-emerald-400 border-emerald-500/10'
                : 'bg-rose-500/5 text-rose-400 border-rose-500/10'
            }`}>
              <span className={`status-pulse ${activeIncident.resolved_at ? 'pulse-emerald' : 'pulse-rose animate-ping'}`}></span>
              {activeIncident.resolved_at ? 'RESOLVED' : 'INVESTIGATING'}
            </span>
          )}
        </div>

        <div className="timeline-stepper">
          {steps.map((step) => {
            const Icon = step.icon;
            const isCompleted = activeTimelineStep > step.stepNum || (activeIncident?.resolved_at && step.stepNum <= 6);
            const isActive = activeTimelineStep === step.stepNum;
            
            return (
              <div 
                key={step.stepNum} 
                className={`timeline-step ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
              >
                <div className="step-indicator rounded-none border font-mono">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-[11px] font-mono tracking-wide uppercase font-bold mb-1 flex items-center gap-2">
                    <span className={isCompleted ? 'text-emerald-500' : isActive ? 'text-sky-400 font-extrabold' : 'text-slate-500'}>
                      {step.title}
                    </span>
                    {isActive && (
                      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 status-pulse pulse-blue inline-block"></span>
                    )}
                  </h4>
                  <p className="text-[10px] text-slate-400 pr-4 leading-normal font-mono">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
