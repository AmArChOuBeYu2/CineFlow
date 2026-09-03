import urllib.request
import json
import os

from config import config

def get_ngrok_url():
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "https":
                    return t.get("public_url")
            if tunnels:
                return tunnels[0].get("public_url")
    except Exception as e:
        print(f"[ERROR] Could not connect to local ngrok API (http://127.0.0.1:4040): {e}")
        return None

def update_grafana_contact_point(ngrok_url):
    target_webhook_url = f"{ngrok_url}/webhook/grafana-alert"
    print(f"\nTarget Webhook URL: {target_webhook_url}")
    
    headers = {
        "Authorization": f"Bearer {config.GRAFANA_SERVICE_ACCOUNT_TOKEN}",
        "Content-Type": "application/json"
    }

    # Fetch existing contact points
    list_url = f"{config.GRAFANA_URL}/api/v1/provisioning/contact-points"
    req_list = urllib.request.Request(list_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req_list) as res:
            contact_points = json.loads(res.read().decode())
            
        target_cp = None
        for cp in contact_points:
            if cp.get("name") == "cineflow-webhook" and "ngrok" in cp.get("settings", {}).get("url", ""):
                target_cp = cp
                break
                
        if not target_cp:
            target_cp = next((cp for cp in contact_points if cp.get("name") == "cineflow-webhook"), None)

        if target_cp:
            uid = target_cp["uid"]
            update_url = f"{config.GRAFANA_URL}/api/v1/provisioning/contact-points/{uid}"
            payload = {
                "uid": uid,
                "name": "cineflow-webhook",
                "type": "webhook",
                "settings": {
                    "httpMethod": "POST",
                    "url": target_webhook_url
                },
                "disableResolveMessage": False
            }
            req_put = urllib.request.Request(update_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="PUT")
            with urllib.request.urlopen(req_put) as res:
                print(f"SUCCESS: Updated Grafana Contact Point '{uid}' to: {target_webhook_url}")
        else:
            payload = {
                "name": "cineflow-webhook",
                "type": "webhook",
                "settings": {
                    "httpMethod": "POST",
                    "url": target_webhook_url
                },
                "disableResolveMessage": False
            }
            req_post = urllib.request.Request(list_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req_post) as res:
                print(f"SUCCESS: Created new Grafana Contact Point to: {target_webhook_url}")
    except Exception as e:
        print(f"[ERROR] Failed to update Grafana contact point: {e}")

if __name__ == "__main__":
    print("=======================================================")
    print("CineFlow IRM — Grafana Alerting Contact Point Setup")
    print("=======================================================")
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"Detected Active Ngrok Tunnel: {ngrok_url}")
        update_grafana_contact_point(ngrok_url)
    else:
        print("Please start ngrok first (`ngrok http 8000`) and run this script again.")
