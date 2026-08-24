# 🚨 CineFlow IRM — Autonomous Render Farm & AI Infrastructure Incident Response Manager

> **Devpost Hackathon Submission**: Agentic Cinema: The Blockbuster Hackathon  
> **Partner Studio Track**: **Grafana Track** ($15,000 Track Pool: $7,500 1st Place)  
> **License**: Apache 2.0 License

**CineFlow IRM** is an autonomous SRE & Technical Director Agent powered by **Google Gemini** and the **Grafana Cloud MCP Server**. It monitors film render farms (Maya/Houdini/Nuke render nodes) and multi-agent AI pipelines for operational bottlenecks—including GPU memory leaks, silent frame corruption, asset load stalls, and runaway agent loops. 

When Grafana triggers an alert, the Gemini Agent automatically investigates Loki logs, analyzes Tempo trace spans via Grafana MCP tools, executes remediation actions (killing worker processes, quarantining bad assets, re-queuing frames), and posts an automated Incident Postmortem.

---

## 🌟 Key Features

1. **Grafana Cloud MCP Server Integration**:
   - Uses official Grafana Cloud MCP tools (`query_loki_logs`, `get_tempo_trace`, `search_dashboards`, `resolve_incident`, `post_postmortem`).
2. **Render Farm & AI Agent Telemetry Simulator**:
   - Simulates Maya/Houdini/Nuke GPU render nodes and multi-agent AI workers.
   - Fault Type A: **GPU VRAM Leak & CUDA Overflow** on `render-gpu-04` at Frame 0142.
   - Fault Type B: **Corrupt 0-Byte Texture File I/O Lock** on `render-gpu-02`.
   - Fault Type C: **Runaway AI Agent Loop** (Execution stalled >18s with token burn spike).
3. **Gemini Agentic Root Cause Analysis**:
   - Correlates firing alerts with Loki logs & Tempo trace spans to pinpoint exact root cause.
4. **Autonomous Remediation & Executive Postmortem**:
   - Executes SRE fixes (process isolation, asset quarantine, frame re-allocation) and generates a Markdown Incident Postmortem report (showing up to 87% MTTR reduction).

---

## 🏗️ System Architecture

```
  ┌───────────────────────────────────────────────────────────────────────┐
  |                       Studio Telemetry Sources                        |
  |  - Render Farm Workers (Maya/Houdini/Nuke GPU/CPU & frame logs)       |
  |  - Multi-Agent AI Workflows (LLM latency, token burn, tool errors)    |
  └───────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼ (OpenTelemetry / Prometheus / Loki)
  ┌───────────────────────────────────────────────────────────────────────┐
  |                          Grafana LGTM Stack                           |
  |   - Loki (Logs) | Mimir (Metrics) | Tempo (Traces) | IRM (Alerts)     |
  └───────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼ (Grafana IRM MCP Integration)
  ┌───────────────────────────────────────────────────────────────────────┐
  |               Gemini SRE & Technical Director Agent                   |
  |  - Step 1: Ingests firing alert payload via Grafana IRM MCP           |
  |  - Step 2: Queries Tempo traces & Loki logs for root cause analysis   |
  |  - Step 3: Decides remediation action (kill process, re-queue frame)  |
  |  - Step 4: Executes fixes & posts automated Markdown Postmortem       |
  └───────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼ (Autonomous Remediation & Dashboard)
  ┌───────────────────────────────────────────────────────────────────────┐
  |                  Studio Command Dashboard & Postmortem                |
  └───────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Setup Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows
pip install -r requirements.txt
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` to launch the **CineFlow IRM Command Dashboard**!

---

## 📄 License
This project is licensed under the [Apache 2.0 License](LICENSE).
