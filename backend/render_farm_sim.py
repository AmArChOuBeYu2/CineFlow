import time
import random
from typing import Dict, Any, List

class RenderFarmSimulator:
    """
    Simulates a studio render farm (Maya / Houdini / Nuke render nodes)
    and multi-agent AI infrastructure workers.
    Includes telemetry generation (Loki logs, Tempo traces, Prometheus metrics).
    """
    def __init__(self):
        self.nodes = [
            {"id": "render-gpu-01", "name": "Maya GPU Worker 01", "status": "HEALTHY", "cpu_percent": 42, "gpu_memory_mb": 4200, "current_frame": 140, "total_frames": 250},
            {"id": "render-gpu-02", "name": "Houdini FX Worker 02", "status": "HEALTHY", "cpu_percent": 68, "gpu_memory_mb": 7800, "current_frame": 88, "total_frames": 200},
            {"id": "render-gpu-03", "name": "Nuke Comp Worker 03", "status": "HEALTHY", "cpu_percent": 35, "gpu_memory_mb": 3100, "current_frame": 210, "total_frames": 300},
            {"id": "render-gpu-04", "name": "Arnold Render Worker 04", "status": "HEALTHY", "cpu_percent": 55, "gpu_memory_mb": 5400, "current_frame": 142, "total_frames": 250},
            {"id": "ai-worker-01", "name": "Gemini Multimodal Agent Worker", "status": "HEALTHY", "cpu_percent": 25, "gpu_memory_mb": 2100, "current_frame": "N/A", "total_frames": "N/A"}
        ]
        self.active_incident = None
        self.incident_history = []
        self.loki_logs_db = []
        self.tempo_traces_db = []
        self.last_gemini_status = "READY"

    def get_cluster_status(self) -> Dict[str, Any]:
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "nodes": self.nodes,
            "active_incident": self.active_incident,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len([n for n in self.nodes if n["status"] == "HEALTHY"]),
            "firing_alerts": 1 if self.active_incident else 0,
            "last_gemini_status": self.last_gemini_status
        }

    def trigger_fault(self, fault_type: str) -> Dict[str, Any]:
        timestamp = time.strftime("%H:%M:%S")
        
        if fault_type == "gpu_memory_leak":
            target_node = next(n for n in self.nodes if n["id"] == "render-gpu-04")
            target_node["status"] = "CRITICAL_FAIL"
            target_node["gpu_memory_mb"] = 24576  # Out of VRAM
            target_node["cpu_percent"] = 99
            
            random_pid = random.randint(10200, 29900)
            random_frame = random.randint(110, 450)
            target_node["current_frame"] = random_frame

            self.active_incident = {
                "incident_id": f"INC-{random.randint(1000, 9999)}",
                "title": f"GPU Memory Overflow & CUDA Crash on render-gpu-04",
                "severity": "CRITICAL",
                "source": "Grafana Mimir / OnCall Alert",
                "timestamp": timestamp,
                "node_id": "render-gpu-04",
                "frame": random_frame,
                "summary": f"Worker node render-gpu-04 failed at Frame {random_frame:04d} due to CUDA VRAM allocation overflow (24.5 GB / 24 GB)."
            }

            self.loki_logs_db = [
                f"{timestamp}.102 [INFO] render-gpu-04: Loading scene asset '/prod/shots/sq04/sh{random.randint(10, 99)}/char_rig.usd'...",
                f"{timestamp}.340 [WARN] render-gpu-04: CUDA Memory allocation approaching 92% ceiling.",
                f"{timestamp}.890 [ERROR] render-gpu-04: CUDA_ERROR_OUT_OF_MEMORY: Failed to allocate 4.2GB texture buffer at Frame {random_frame:04d}.",
                f"{timestamp}.912 [FATAL] render-gpu-04: Process ArnoldRenderWorker pid={random_pid} terminated unexpectedly with signal 11 (SIGSEGV)."
            ]

            self.tempo_traces_db = [
                {"span": "ArnoldRenderPipeline::FrameRender", "duration_ms": 14200, "status": "ERROR", "node": "render-gpu-04"},
                {"span": "USDAssetResolver::LoadTextures", "duration_ms": 11800, "status": "CRASH", "error_code": "VRAM_OVERFLOW"},
            ]

        elif fault_type == "corrupt_texture_asset":
            target_node = next(n for n in self.nodes if n["id"] == "render-gpu-02")
            target_node["status"] = "STALLED"
            target_node["cpu_percent"] = 10

            self.active_incident = {
                "incident_id": f"INC-{random.randint(1000, 9999)}",
                "title": "Zero-Byte Texture Asset Read Stall on render-gpu-02",
                "severity": "WARNING",
                "source": "Grafana Loki LogQL Alert",
                "timestamp": timestamp,
                "node_id": "render-gpu-02",
                "frame": 88,
                "summary": "Houdini worker render-gpu-02 stalled at Frame 88 waiting for corrupted 0-byte texture file '/assets/env_wall_diffuse.exr'."
            }

            self.loki_logs_db = [
                f"{timestamp}.005 [INFO] render-gpu-02: Initializing frame 88 geometry bake.",
                f"{timestamp}.120 [WARN] render-gpu-02: File I/O bottleneck detected reading '/assets/env_wall_diffuse.exr'.",
                f"{timestamp}.450 [ERROR] render-gpu-02: TextureIOException: File size is 0 bytes (corrupt write). Thread locked waiting on FileSystem lock."
            ]

            self.tempo_traces_db = [
                {"span": "HoudiniFX::TextureBake", "duration_ms": 45000, "status": "STALLED", "node": "render-gpu-02"}
            ]

        elif fault_type == "runaway_agent_loop":
            target_node = next(n for n in self.nodes if n["id"] == "ai-worker-01")
            target_node["status"] = "RUNAWAY_LOOP"
            target_node["cpu_percent"] = 95

            self.active_incident = {
                "incident_id": f"INC-{random.randint(1000, 9999)}",
                "title": "Runaway Multi-Agent Tool Loop & High Latency Alert",
                "severity": "HIGH",
                "source": "Grafana AI Observability / Tempo Span Alert",
                "timestamp": timestamp,
                "node_id": "ai-worker-01",
                "frame": "N/A",
                "summary": "Gemini AI Agent worker entering infinite recursion loop on tool invocation `search_asset_db()`. Token burn spiking (>14,000 tokens/min)."
            }

            self.loki_logs_db = [
                f"{timestamp}.010 [INFO] ai-worker-01: Agent task initiated: 'Verify shot continuity for sq04_sh12'.",
                f"{timestamp}.230 [WARN] ai-worker-01: Tool 'search_asset_db' invoked 18 times in 10 seconds with identical parameters.",
                f"{timestamp}.890 [ERROR] ai-worker-01: AgentRecursionLimitExceeded: Tool execution loop detected. Latency exceeds 18,500ms."
            ]

            self.tempo_traces_db = [
                {"span": "GeminiAgent::ExecuteToolLoop", "duration_ms": 18500, "status": "TIMEOUT", "node": "ai-worker-01"}
            ]

        return {
            "status": "incident_triggered",
            "incident": self.active_incident,
            "logs": self.loki_logs_db,
            "traces": self.tempo_traces_db
        }

    def execute_remediation(self, node_id: str, action: str) -> Dict[str, Any]:
        """Executes SRE remediation action to resolve the incident."""
        target_node = next((n for n in self.nodes if n["id"] == node_id), None)
        if target_node:
            target_node["status"] = "HEALTHY"
            target_node["cpu_percent"] = random.randint(30, 50)
            target_node["gpu_memory_mb"] = random.randint(3000, 5000)
            if isinstance(target_node["current_frame"], int):
                target_node["current_frame"] += 1

        resolved_incident = self.active_incident
        self.active_incident = None

        if resolved_incident:
            resolved_incident["resolved_at"] = time.strftime("%H:%M:%S")
            resolved_incident["remediation_action"] = action
            self.incident_history.append(resolved_incident)

        return {
            "status": "resolved",
            "node_id": node_id,
            "action_taken": action,
            "resolved_incident": resolved_incident
        }

simulator = RenderFarmSimulator()
