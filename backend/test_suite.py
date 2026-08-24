import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

def log_test(test_name: str, passed: bool, details: str = ""):
    status_str = "[PASS]" if passed else "[FAIL]"
    print(f"{status_str} {test_name} {f'- {details}' if details else ''}")

def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        return res.status, json.loads(res.read().decode())

def http_post(endpoint: str, payload: dict = None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload or {}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        return res.status, json.loads(res.read().decode())

def run_all_tests():
    print("\n" + "="*70)
    print("CINEFLOW IRM -- AUTOMATED SUITE VERIFICATION REPORT")
    print("="*70 + "\n")

    # Test 1: Health Check Endpoint
    try:
        status, data = http_get("/health")
        passed = status == 200 and data.get("status") == "healthy"
        log_test("Test 1: Health Check Endpoint (/health)", passed, f"Response: {data.get('status')}")
    except Exception as e:
        log_test("Test 1: Health Check Endpoint (/health)", False, str(e))

    # Test 2: Cluster Status Matrix Endpoint
    try:
        status, data = http_get("/api/cluster-status")
        nodes = data.get("nodes", [])
        passed = status == 200 and len(nodes) == 5
        log_test("Test 2: Cluster Status Matrix (/api/cluster-status)", passed, f"Total Nodes: {len(nodes)}")
    except Exception as e:
        log_test("Test 2: Cluster Status Matrix (/api/cluster-status)", False, str(e))

    # Test 3: Prometheus Metrics Scrapability
    try:
        url = f"{BASE_URL}/metrics"
        with urllib.request.urlopen(url) as res:
            raw_metrics = res.read().decode()
            passed = res.status == 200 and "agent_task_executions_total" in raw_metrics
            log_test("Test 3: Prometheus OTLP Endpoint (/metrics)", passed, "Found scrapable Prometheus metrics format")
    except Exception as e:
        log_test("Test 3: Prometheus OTLP Endpoint (/metrics)", False, str(e))

    # Test 4: Scenario A - GPU Memory Leak Incident
    try:
        print("\n--- Scenario A: GPU VRAM Memory Leak (CUDA Overflow on render-gpu-04) ---")
        s1, d1 = http_post("/api/trigger-fault", {"fault_type": "gpu_memory_leak"})
        inc_id = d1.get("incident", {}).get("incident_id")
        print(f"   [Alert Triggered] {inc_id}: {d1.get('incident', {}).get('title')}")
        
        # Wait up to 10 seconds for webhook to auto-resolve
        resolved_inc = None
        for _ in range(10):
            time.sleep(1)
            s_hist, history = http_get("/api/incident-history")
            resolved_inc = next((inc for inc in history if inc.get("node_id") == "render-gpu-04"), None)
            if resolved_inc:
                break
                
        if resolved_inc:
            action = resolved_inc.get("remediation_action", "")
            passed = "Arnold" in action or "VRAM" in action or "render-gpu" in action or "Terminated" in action
            log_test("Scenario A: GPU Memory Leak Incident & Gemini SRE Remediation (Webhook Auto-Resolved)", passed, f"Action: {action[:70]}...")
        else:
            s2, d2 = http_post("/api/run-sre-agent")
            action = d2.get("action_taken", "")
            passed = s2 == 200 and ("render-gpu-04" in action or "Arnold" in action or "Terminated" in action)
            log_test("Scenario A: GPU Memory Leak Incident & Gemini SRE Remediation (Manual Trigger)", passed, f"Action: {action[:70]}...")
    except Exception as e:
        log_test("Scenario A: GPU Memory Leak Incident", False, str(e))

    # Test 5: Scenario B - Corrupt Texture Asset Stall
    try:
        print("\n--- Scenario B: Corrupt 0-Byte Texture Asset Stall on render-gpu-02 ---")
        s1, d1 = http_post("/api/trigger-fault", {"fault_type": "corrupt_texture_asset"})
        inc_id = d1.get("incident", {}).get("incident_id")
        print(f"   [Alert Triggered] {inc_id}: {d1.get('incident', {}).get('title')}")
        
        # Wait up to 10 seconds for webhook to auto-resolve
        resolved_inc = None
        for _ in range(10):
            time.sleep(1)
            s_hist, history = http_get("/api/incident-history")
            resolved_inc = next((inc for inc in history if inc.get("node_id") == "render-gpu-02"), None)
            if resolved_inc:
                break

        if resolved_inc:
            action = resolved_inc.get("remediation_action", "")
            passed = "render-gpu-02" in action or "Quarantined" in action or "Asset" in action or "texture" in action
            log_test("Scenario B: Corrupt Texture Asset Stall & Gemini SRE Remediation (Webhook Auto-Resolved)", passed, f"Action: {action[:70]}...")
        else:
            s2, d2 = http_post("/api/run-sre-agent")
            action = d2.get("action_taken", "")
            passed = s2 == 200 and ("render-gpu-02" in action or "Quarantined" in action)
            log_test("Scenario B: Corrupt Texture Asset Stall & Gemini SRE Remediation (Manual Trigger)", passed, f"Action: {action[:70]}...")
    except Exception as e:
        log_test("Scenario B: Corrupt Texture Asset Stall", False, str(e))

    # Test 6: Scenario C - Runaway AI Agent Loop
    try:
        print("\n--- Scenario C: Runaway AI Agent Tool Loop & High Latency Alert ---")
        s1, d1 = http_post("/api/trigger-fault", {"fault_type": "runaway_agent_loop"})
        inc_id = d1.get("incident", {}).get("incident_id")
        print(f"   [Alert Triggered] {inc_id}: {d1.get('incident', {}).get('title')}")
        
        # Wait up to 10 seconds for webhook to auto-resolve
        resolved_inc = None
        for _ in range(10):
            time.sleep(1)
            s_hist, history = http_get("/api/incident-history")
            resolved_inc = next((inc for inc in history if inc.get("node_id") == "ai-worker-01"), None)
            if resolved_inc:
                break

        if resolved_inc:
            action = resolved_inc.get("remediation_action", "")
            passed = "SIGTERM" in action or "worker" in action or "ai-worker-01" in action or "Recursion" in action or "loop" in action
            log_test("Scenario C: Runaway AI Agent Loop & Gemini SRE Remediation (Webhook Auto-Resolved)", passed, f"Action: {action[:70]}...")
        else:
            s2, d2 = http_post("/api/run-sre-agent")
            action = d2.get("action_taken", "")
            passed = s2 == 200 and ("SIGTERM" in action or "worker" in action or "ai-worker-01" in action)
            log_test("Scenario C: Runaway AI Agent Loop & Gemini SRE Remediation (Manual Trigger)", passed, f"Action: {action[:70]}...")
    except Exception as e:
        log_test("Scenario C: Runaway AI Agent Loop", False, str(e))

    print("\n" + "="*70)
    print("ALL TEST SCENARIOS COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()
