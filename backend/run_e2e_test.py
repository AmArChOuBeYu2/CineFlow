import urllib.request
import json
import time
import sys

# Get fault type from command line or default to gpu_memory_leak
fault_type = sys.argv[1] if len(sys.argv) > 1 else "gpu_memory_leak"

history_url = "http://localhost:8000/api/incident-history"
trigger_url = "http://localhost:8000/api/trigger-fault"

# 1. Get initial history length
print("Checking initial incident history...")
try:
    req_hist = urllib.request.Request(history_url)
    with urllib.request.urlopen(req_hist) as res:
        initial_history = json.loads(res.read().decode())
        initial_count = len(initial_history)
        print(f"Initial resolved incident count: {initial_count}")
except Exception as e:
    print("Error fetching initial history:", e)
    exit(1)

# 2. Trigger fault
payload = {"fault_type": fault_type}
print(f"\nTriggering fault: '{fault_type}'...")
req = urllib.request.Request(trigger_url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as res:
        print("Trigger Response Status:", res.status)
        print("Trigger Response:", json.loads(res.read().decode()))
except Exception as e:
    print("Error triggering fault:", e)
    exit(1)

# 3. Poll for new entry in history matching target node
expected_node_map = {
    "gpu_memory_leak": "render-gpu-04",
    "corrupt_texture_asset": "render-gpu-02",
    "runaway_agent_loop": "ai-worker-01"
}
expected_node_id = expected_node_map.get(fault_type, "render-gpu-04")

print(f"\nWaiting for Grafana to detect the log line, fire the alert on node '{expected_node_id}', and trigger the webhook...")
print("Polling incident history for new resolution entries...")

for i in range(30):  # Poll for up to 300 seconds to ensure Grafana alert evaluation cycle
    time.sleep(10)
    print(f"Checking history (Attempt {i+1}/30)...")
    try:
        with urllib.request.urlopen(urllib.request.Request(history_url)) as res:
            history = json.loads(res.read().decode())
            new_entries = history[initial_count:]
            matching_entry = next((entry for entry in new_entries if entry.get("node_id") == expected_node_id), None)
            if matching_entry:
                print(f"\nSUCCESS! New firing alert for {expected_node_id} processed and resolved by SRE agent!")
                print("Latest resolved incident in history:")
                print(json.dumps(matching_entry, indent=2))
                break
    except Exception as e:
         print("Error checking history:", e)
else:
    print(f"\nTimeout: Fault '{fault_type}' did not result in a new resolved incident within 200 seconds.")
    exit(1)

# 4. Check metrics
print("\nFetching /metrics to verify Prometheus counters are updated...")
metrics_url = "http://localhost:8000/metrics"
try:
    with urllib.request.urlopen(urllib.request.Request(metrics_url)) as res:
        metrics_data = res.read().decode()
        print("--- Prometheus Metrics Output ---")
        for line in metrics_data.splitlines():
            if "agent_task_executions_total" in line or "gemini_token_count_total" in line:
                print(line)
        print("---------------------------------")
except Exception as e:
    print("Error fetching metrics:", e)
