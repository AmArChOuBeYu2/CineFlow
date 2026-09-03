import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from config import config
from render_farm_sim import simulator
from agents.irm_agent import gemini_sre_agent
from grafana_mcp.mcp_tools import grafana_mcp
from observability.metrics import metrics_mgr, CONTENT_TYPE_LATEST

app = FastAPI(
    title="CineFlow IRM Engine — Grafana Cloud IRM & SRE Agent",
    description="Grafana Track Submission for Agentic Cinema Hackathon",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FaultTriggerRequest(BaseModel):
    fault_type: str  # gpu_memory_leak, corrupt_texture_asset, runaway_agent_loop

@app.get("/health")
@app.get("/health/")
@app.get("/api/health")
@app.get("/api/health/")
def health_check(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return {
        "status": "healthy",
        "service": "CineFlow IRM Engine",
        "grafana_url": config.GRAFANA_URL,
        "demo_mode": config.DEMO_MODE,
        "gemini_api_configured": bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE")
    }

@app.get("/metrics")
@app.get("/metrics/")
@app.get("/api/metrics")
@app.get("/api/metrics/")
def get_metrics():
    """Prometheus metrics endpoint scrapable by Grafana Cloud Agent / Alloy."""
    data = metrics_mgr.get_prometheus_metrics()
    return Response(
        content=data,
        media_type=CONTENT_TYPE_LATEST,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    )

@app.get("/api/cluster-status")
@app.get("/api/cluster-status/")
def get_cluster_status(response: Response):
    """Get real-time render farm node matrix and active incidents."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    status = simulator.get_cluster_status()
    status["demo_mode"] = config.DEMO_MODE
    status["gemini_api_configured"] = bool(config.GEMINI_API_KEY and config.GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE")
    return status

@app.post("/api/trigger-fault")
@app.post("/api/trigger-fault/")
def trigger_fault(req: FaultTriggerRequest):
    """Trigger a simulated studio render farm or AI agent fault."""
    valid_faults = ["gpu_memory_leak", "corrupt_texture_asset", "runaway_agent_loop"]
    if req.fault_type not in valid_faults:
        raise HTTPException(status_code=400, detail=f"Invalid fault_type. Choose from {valid_faults}")
    
    result = simulator.trigger_fault(req.fault_type)
    
    # Step 1: Push real telemetry log line to Grafana Cloud Loki Push API
    incident = result.get("incident", {})
    if incident:
        if simulator.active_incident:
            simulator.active_incident["stage"] = "TRIGGERED"
        node_id = incident.get("node_id", "render-gpu-04")
        log_msg = result.get("logs", ["CUDA_ERROR_OUT_OF_MEMORY"])[-1]
        grafana_mcp.push_loki_log(node_id, log_msg, level="fatal")
        
    return result

@app.post("/webhook/grafana-alert")
async def handle_grafana_alert_webhook(request: Request):
    """
    Step 3: Official Grafana Alerting Webhook Endpoint.
    Accepts real HTTP POST alerts directly from Grafana Cloud Alerting rules.
    """
    try:
        payload = await request.json()
        print(f"\n[REAL GRAFANA WEBHOOK RECEIVED] Incoming alert status: {payload.get('status')}")
        
        alerts = payload.get("alerts", [])
        if not alerts:
            return {"status": "no_alerts_in_payload"}
            
        first_alert = alerts[0]
        labels = first_alert.get("labels", {})
        annotations = first_alert.get("annotations", {})
        
        incident_id = f"INC-{labels.get('alertname', 'GRAFANA-ALERT')}-{int(time.time() % 10000)}"
        node_id = labels.get("node", "render-gpu-04")
        summary = annotations.get("summary", annotations.get("description", "Grafana Alert Fired"))
        
        webhook_incident = {
            "incident_id": incident_id,
            "title": labels.get("alertname", "Grafana Cloud Firing Alert"),
            "severity": labels.get("severity", "CRITICAL"),
            "source": "Official Grafana Cloud Webhook",
            "timestamp": time.strftime("%H:%M:%S"),
            "node_id": node_id,
            "frame": labels.get("frame", 142),
            "summary": summary,
            "raw_grafana_payload": payload
        }
        
        # Set the active incident in the simulator so SRE actions and UI sync with it
        simulator.active_incident = webhook_incident
        
        # Automatically trigger Gemini SRE Agent investigation on real webhook alert
        sre_result = gemini_sre_agent.investigate_and_remediate(webhook_incident)
        return {"status": "processed_by_gemini_sre", "result": sre_result}
    except Exception as e:
        print(f"[WEBHOOK ERROR] Failed to parse Grafana webhook payload: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/run-sre-agent")
@app.post("/api/run-sre-agent/")
def run_sre_agent():
    """Execute Gemini SRE Agent to investigate incident via Grafana MCP and remediate."""
    active_incident = simulator.active_incident
    if not active_incident:
        raise HTTPException(status_code=400, detail="No active firing incident to investigate. Trigger a fault first.")
    
    result = gemini_sre_agent.investigate_and_remediate(active_incident)
    return result

@app.get("/api/incident-history")
@app.get("/api/incident-history/")
def get_incident_history(response: Response):
    """Get log history of resolved incidents and postmortems."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return simulator.incident_history

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
