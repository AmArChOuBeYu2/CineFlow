import time
import json
import traceback
from typing import Dict, Any, List
from google import genai
from config import config
from grafana_mcp.mcp_tools import grafana_mcp
from observability.metrics import metrics_mgr
from render_farm_sim import simulator

class GeminiSREAgent:
    """
    Autonomous SRE & Technical Director Agent powered by Gemini Flash (gemini-flash-latest).
    Executes live API calls to Google GenAI for dynamic SRE reasoning,
    invokes Grafana Cloud MCP tools over HTTP, and posts automated Incident Postmortems.
    Includes 3x retry handling with backoff for HTTP 429 rate limits & 503 server demand spikes.
    """
    def __init__(self):
        self.name = "GeminiSREAgent"
        if config.GEMINI_API_KEY and config.GEMINI_API_KEY != "PASTE_YOUR_GEMINI_API_KEY_HERE":
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        else:
            self.client = None

    def investigate_and_remediate(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        incident_id = incident.get("incident_id", "INC-9999")
        node_id = incident.get("node_id", "render-gpu-04")
        summary = incident.get("summary", "Render farm alert fired")

        print(f"\n[Gemini SRE Agent] Initiating incident investigation for {incident_id} ({node_id})...")

        # Step 1: Query Grafana Cloud MCP Tools
        if simulator.active_incident: simulator.active_incident["stage"] = "LOKI"
        loki_logs = grafana_mcp.query_loki_logs(f'{{node="{node_id}"}} |= "ERROR"')
        if simulator.active_incident: simulator.active_incident["stage"] = "TEMPO"
        tempo_traces = grafana_mcp.get_tempo_trace(node_id)

        # Step 2: Build Live Prompt for Gemini Flash Model
        prompt = f"""
        You are an expert Hollywood Studio Technical Director and Site Reliability Engineer (SRE).
        An incident has fired in Grafana IRM for render resource '{node_id}'.

        INCIDENT PAYLOAD:
        - Incident ID: {incident_id}
        - Severity: {incident.get('severity', 'HIGH')}
        - Summary: {summary}

        FETCHED GRAFANA LOKI LOGS:
        {json.dumps(loki_logs, indent=2)}

        FETCHED GRAFANA TEMPO TRACES:
        {json.dumps(tempo_traces, indent=2)}

        Perform root cause analysis and respond strictly as a valid JSON object with the following schema:
        {{
            "root_cause": "Detailed 1-sentence technical root cause explaining why this node failed",
            "action_taken": "Specific SRE remediation action executed (e.g. process termination, asset quarantine, frame re-allocation)",
            "reasoning_steps": [
                "1. Step 1 reasoning...",
                "2. Step 2 reasoning...",
                "3. Step 3 reasoning...",
                "4. Step 4 reasoning...",
                "5. Step 5 reasoning..."
            ],
            "postmortem_markdown": "# 🚨 Grafana IRM Postmortem\\n\\n### Executive Summary\\n..."
        }}
        Do not wrap output in ```json markdown block if possible.
        """

        result_data = None
        raw_llm_response = None

        # Step 3: Execute LIVE Gemini API Call with backoff retry on 429 / 503
        if simulator.active_incident: simulator.active_incident["stage"] = "GEMINI"
        if self.client:
            for attempt in range(1, 4):
                try:
                    print(f"[REAL GEMINI LLM CALL] Attempt {attempt}/3: Sending prompt to Google GenAI endpoint (model: {config.GEMINI_FLASH_MODEL})...")
                    response = self.client.models.generate_content(
                        model=config.GEMINI_FLASH_MODEL,
                        contents=prompt
                    )
                    raw_llm_response = response.text.strip()
                    print(f"[RAW GEMINI LLM RESPONSE BODY]\n{raw_llm_response[:300]}...\n")

                    # Parse JSON output from Gemini
                    clean_text = raw_llm_response
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.startswith("```"):
                        clean_text = clean_text[3:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]

                    result_data = json.loads(clean_text.strip())
                    print("[REAL GEMINI LLM SUCCESS] Gemini Flash generated 100% dynamic live reasoning & postmortem!")
                    
                    # Record metrics
                    metrics_mgr.record_agent_task(self.name, "success")
                    simulator.last_gemini_status = "LIVE"
                    usage = getattr(response, 'usage_metadata', None)
                    in_tokens = getattr(usage, 'prompt_token_count', 120) if usage else 120
                    out_tokens = getattr(usage, 'candidates_token_count', 250) if usage else 250
                    metrics_mgr.record_token_usage(config.GEMINI_FLASH_MODEL, in_tokens, out_tokens)
                    break
                except Exception as e:
                    print(f"[LLM NOTICE ATTEMPT {attempt}] Exception: {e}")
                    if attempt < 3:
                        time.sleep(2.5 * attempt)
                    else:
                        print(f"[LLM EXCEPTION TRACEBACK]\n{traceback.format_exc()}")

        # Fallback dynamic generator if key is missing or all attempts failed
        if not result_data:
            print("[MOCKED FALLBACK] Gemini SRE Agent using local dynamic reasoning engine.")
            result_data = self._generate_dynamic_sre_reasoning(incident, loki_logs, tempo_traces)
            metrics_mgr.record_agent_task(self.name, "fallback")
            simulator.last_gemini_status = "FALLBACK MODE"

        duration = round(time.time() - start_time, 2)

        # Step 4: Execute SRE Fix in Simulator & Grafana IRM
        if simulator.active_incident: simulator.active_incident["stage"] = "REMEDIATE"
        action_taken = result_data.get("action_taken", f"Restarted worker process on {node_id}")
        grafana_mcp.resolve_incident(incident_id, action_taken)

        # Step 5: Post Postmortem back to Grafana IRM & Grafana Annotations API
        if simulator.active_incident: simulator.active_incident["stage"] = "POSTMORTEM"
        postmortem_md = result_data.get("postmortem_markdown", "# Postmortem")
        grafana_mcp.post_postmortem(incident_id, postmortem_md)

        return {
            "incident_id": incident_id,
            "node_id": node_id,
            "root_cause": result_data.get("root_cause", "CUDA VRAM Memory Overflow"),
            "action_taken": action_taken,
            "reasoning_steps": result_data.get("reasoning_steps", []),
            "postmortem_markdown": postmortem_md,
            "resolution_time_seconds": duration,
            "is_live_gemini_llm": bool(self.client and raw_llm_response is not None),
            "raw_llm_response_snippet": raw_llm_response[:200] if raw_llm_response else None
        }

    def _generate_dynamic_sre_reasoning(self, incident: Dict[str, Any], logs: List[str], traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        node_id = incident.get("node_id", "render-gpu-04")
        summary = incident.get("summary", "")

        if "CUDA" in str(logs) or "VRAM" in summary:
            root_cause = f"CUDA Out-Of-Memory allocation overflow on node {node_id} (VRAM allocation exceeded 24GB ceiling)."
            action_taken = f"Terminated crashed Arnold process pid=18402 on {node_id}, cleared VRAM cache, and re-allocated Frame 142 to render-gpu-01."
        elif "Texture" in str(logs) or "0-Byte" in summary:
            root_cause = f"File I/O lock stall caused by zero-byte corrupt EXR asset on node {node_id}."
            action_taken = f"Quarantined corrupt asset '/assets/env_wall_diffuse.exr', cleared texture cache, and re-triggered Houdini bake."
        else:
            root_cause = f"Runaway multi-agent LLM tool execution loop exceeding 18,500ms latency ceiling on node {node_id}."
            action_taken = f"Issued SIGTERM signal to worker {node_id}, reset recursion depth to 5, and resumed task queue."

        postmortem = f"""# 🚨 Grafana IRM Postmortem: {incident.get('incident_id', 'INC-9999')}

**Target Resource**: `{node_id}` | **Severity**: `{incident.get('severity', 'HIGH')}`

### 🔍 Executive Root Cause Summary
{root_cause}

### 📋 Investigation Timeline & Grafana MCP Trace
* **Alert Ingested**: Ingested payload from Grafana OnCall/Mimir.
* **Loki Logs Queried**: Executed `query_loki_logs()` -> Found error: `{logs[-1] if logs else 'None'}`.
* **Tempo Traces Queried**: Executed `get_tempo_trace()` -> Found span bottleneck in `{traces[0].get('span', 'RenderPipeline') if traces else 'Pipeline'}`.
* **Action Executed**: `{action_taken}`.
"""

        return {
            "root_cause": root_cause,
            "action_taken": action_taken,
            "reasoning_steps": [
                f"1. Ingested Grafana IRM alert payload for {node_id}.",
                f"2. Invoked Grafana MCP tool query_loki_logs() -> Found {len(logs)} error logs.",
                f"3. Invoked Grafana MCP tool get_tempo_trace() -> Pinpointed span bottleneck.",
                f"4. Diagnosed Root Cause: {root_cause}",
                f"5. Executed SRE Remediation: {action_taken}"
            ],
            "postmortem_markdown": postmortem
        }

gemini_sre_agent = GeminiSREAgent()
