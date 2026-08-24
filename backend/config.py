import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "magnetic-clone-472606-e7")
    
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "https://quirkyviper1507.grafana.net")
    GRAFANA_SERVICE_ACCOUNT_TOKEN: str = os.getenv("GRAFANA_SERVICE_ACCOUNT_TOKEN", "")
    GRAFANA_OTLP_ENDPOINT: str = os.getenv("GRAFANA_OTLP_ENDPOINT", "")
    GRAFANA_INSTANCE_ID: str = os.getenv("GRAFANA_INSTANCE_ID", "")
    GRAFANA_LOKI_PUSH_USER: str = os.getenv("GRAFANA_LOKI_PUSH_USER", "")
    GRAFANA_LOKI_ACCESS_POLICY_TOKEN: str = os.getenv("GRAFANA_LOKI_ACCESS_POLICY_TOKEN", "")
    
    # Mode Toggle: Set DEMO_MODE=false in .env for 100% real live Grafana Cloud HTTP requests
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    # Official Google GenAI SDK Supported Model Names for this API Key
    GEMINI_MODEL: str = "gemini-flash-latest"
    GEMINI_FLASH_MODEL: str = "gemini-flash-latest"
    IMAGEN_MODEL: str = "imagen-3.0-generate-002"

config = Config()
