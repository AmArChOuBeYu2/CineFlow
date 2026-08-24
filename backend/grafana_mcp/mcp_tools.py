import time
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List
from config import config
from render_farm_sim import simulator

class GrafanaMCPClient:
    """
    Wraps the official Grafana Cloud MCP Server & REST APIs.
    Supports real HTTP PUSH (Loki / Annotations / Telemetry) & REAL HTTP QUERY (Loki LogQL / Tempo).
    Includes explicit DEMO_MODE toggle for offline fallback.
    """
    def __init__(self):
        self.grafana_url = config.GRAFANA_URL or "https://quirkyviper1507.grafana.net"
        self.token = config.GRAFANA_SERVICE_ACCOUNT_TOKEN
        self.demo_mode = config.DEMO_MODE

    def is_real_mode(self) -> bool:
        return bool(self.token and self.token != "PASTE_YOUR_GRAFANA_SERVICE_ACCOUNT_TOKEN_HERE" and not self.demo_mode)

    def push_loki_log(self, node_id: str, log_message: str, level: str = "error") -> bool:
        """Step 1: Pushes a real log line to Grafana Cloud Loki Push API over HTTP."""
        if not self.is_real_mode():
            print(f"[DEMO MODE] Skipped real Loki push for node '{node_id}'. Local log recorded.")
            return False

        # If Loki Basic Auth credentials are provided, use direct Basic Auth to logs-prod-028.grafana.net
        if config.GRAFANA_LOKI_PUSH_USER and config.GRAFANA_LOKI_ACCESS_POLICY_TOKEN:
            try:
                import base64
                url = "https://logs-prod-028.grafana.net/loki/api/v1/push"
                auth_str = f"{config.GRAFANA_LOKI_PUSH_USER}:{config.GRAFANA_LOKI_ACCESS_POLICY_TOKEN}"
                auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
                
                nanos = str(int(time.time() * 1e9))
                payload = {
                    "streams": [
                        {
                            "stream": {
                                "job": "render-farm",
                                "node": node_id,
                                "level": level
                            },
                            "values": [
                                [nanos, log_message]
                            ]
                        }
                    ]
                }
                data = json.dumps(payload).encode('utf-8')
                headers = {
                    "Authorization": f"Basic {auth_b64}",
                    "Content-Type": "application/json",
                    "X-Scope-OrgID": config.GRAFANA_LOKI_PUSH_USER
                }
                req = urllib.request.Request(url, data=data, headers=headers)
                print(f"[REAL LOKI PUSH] POST {url} (Direct Basic Auth) | Node: {node_id}")
                with urllib.request.urlopen(req, timeout=5) as res:
                    print(f"[REAL LOKI RESPONSE] Direct push returned HTTP {res.status}")
                    return res.status in (200, 204)
            except Exception as e:
                print(f"[LOKI DIRECT PUSH ERROR] {e}")
                return False

        try:
            url = f"{self.grafana_url}/loki/api/v1/push"
            nanos = str(int(time.time() * 1e9))
            payload = {
                "streams": [
                    {
                        "stream": {
                            "job": "render-farm",
                            "node": node_id,
                            "level": level
                        },
                        "values": [
                            [nanos, log_message]
                        ]
                    }
                ]
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })
            print(f"[REAL HTTP PUSH] POST {url} | Label node={node_id}")
            with urllib.request.urlopen(req, timeout=5) as res:
                print(f"[REAL HTTP RESPONSE] Grafana Loki Push returned HTTP {res.status}")
                return res.status in (200, 204)
        except Exception as e:
            print(f"[NETWORK NOTICE] Loki Push API notice: {e}")
            return False

    def post_grafana_annotation(self, incident_id: str, title: str, text_content: str, node_id: str) -> Dict[str, Any]:
        """Step 5: Posts a real annotation back to Grafana Cloud Annotations API."""
        if not self.is_real_mode():
            print(f"[DEMO MODE] Skipped real Grafana annotation POST for incident '{incident_id}'.")
            return {"status": "demo_mode_local_rendered", "annotation_id": int(time.time() % 10000)}

        try:
            url = f"{self.grafana_url}/api/annotations"
            payload = {
                "text": f"### 🚨 Grafana IRM Postmortem ({incident_id})\n\n{text_content}",
                "tags": ["render-farm", "incident-postmortem", node_id],
                "time": int(time.time() * 1000)
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })
            print(f"[REAL HTTP POST] POST {url} | Tag: {node_id}")
            with urllib.request.urlopen(req, timeout=5) as res:
                result = json.loads(res.read().decode())
                print(f"[REAL HTTP RESPONSE] Posted annotation ID #{result.get('id')} to Grafana Cloud UI!")
                return {"status": "posted_to_grafana_cloud", "annotation_id": result.get("id")}
        except Exception as e:
            print(f"[NETWORK NOTICE] Grafana Annotations API notice: {e}")
            return {"status": "local_fallback", "error": str(e)}

    def query_loki_logs(self, query: str, limit: int = 10) -> List[str]:
        """Grafana MCP Tool: Queries Loki LogQL logs over real HTTP proxy."""
        if self.is_real_mode():
            try:
                # Use verified proxy URL for Loki queries in Grafana Cloud
                url = f"{self.grafana_url}/api/datasources/proxy/uid/grafanacloud-logs/loki/api/v1/query_range?query={urllib.parse.quote(query)}&limit={limit}"
                print(f"[REAL HTTP QUERY] GET {url}")
                req = urllib.request.Request(url, headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/json"
                })
                with urllib.request.urlopen(req, timeout=5) as res:
                    data = json.loads(res.read().decode())
                    results = data.get("data", {}).get("result", [])
                    if results:
                        logs = []
                        for stream in results:
                            for val in stream.get("values", []):
                                logs.append(val[1])
                        print(f"[REAL HTTP RESPONSE] Live Loki returned {len(logs)} real log lines from Grafana Cloud!")
                        return logs
            except Exception as e:
                print(f"[NETWORK NOTICE] Grafana Cloud Loki HTTP notice: {e}")

        print(f"[SIMULATED LOGS] query_loki_logs('{query}') -> Returning active incident logs.")
        return simulator.loki_logs_db if simulator.loki_logs_db else [f"{time.strftime('%H:%M:%S')} [INFO] Log query OK."]

    def get_tempo_trace(self, service_name: str) -> List[Dict[str, Any]]:
        """Grafana MCP Tool: Retrieves Tempo trace spans over real HTTP proxy."""
        if self.is_real_mode():
            try:
                # Use verified proxy URL for Tempo queries in Grafana Cloud
                url = f"{self.grafana_url}/api/datasources/proxy/uid/grafanacloud-traces/api/search?q={urllib.parse.quote(f'{{resource.service.name=\"{service_name}\"}}')}&limit=5"
                print(f"[REAL HTTP QUERY] GET {url}")
                req = urllib.request.Request(url, headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/json"
                })
                with urllib.request.urlopen(req, timeout=5) as res:
                    data = json.loads(res.read().decode())
                    traces = data.get("traces", [])
                    if traces:
                        print(f"[REAL HTTP RESPONSE] Live Tempo returned {len(traces)} trace spans from Grafana Cloud!")
                        return traces
            except Exception as e:
                print(f"[NETWORK NOTICE] Grafana Cloud Tempo HTTP notice: {e}")

        print(f"[SIMULATED TRACES] get_tempo_trace('{service_name}') -> Returning active trace spans.")
        return simulator.tempo_traces_db if simulator.tempo_traces_db else [{"span": "RenderPipeline", "duration_ms": 120}]

    def resolve_incident(self, incident_id: str, action_taken: str) -> Dict[str, Any]:
        """Grafana MCP Tool: Marks an incident as resolved."""
        print(f"[SRE ACTION] resolve_incident('{incident_id}', action='{action_taken}').")
        node_id = simulator.active_incident.get("node_id", "render-gpu-04") if simulator.active_incident else "render-gpu-04"
        return simulator.execute_remediation(node_id, action_taken)

    def post_postmortem(self, incident_id: str, markdown_content: str) -> Dict[str, Any]:
        """Grafana MCP Tool: Posts postmortem to Grafana Annotations & IRM."""
        node_id = simulator.active_incident.get("node_id", "render-gpu-04") if simulator.active_incident else "render-gpu-04"
        res = self.post_grafana_annotation(incident_id, "Incident Postmortem", markdown_content, node_id)
        if res and res.get("annotation_id"):
            ann_id = res.get("annotation_id")
            for inc in simulator.incident_history:
                if inc.get("incident_id") == incident_id:
                    inc["annotation_id"] = ann_id
                    inc["postmortem_markdown"] = markdown_content
                    break
        return res

grafana_mcp = GrafanaMCPClient()
