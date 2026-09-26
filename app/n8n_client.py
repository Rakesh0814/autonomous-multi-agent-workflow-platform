import requests
from .config import settings

def notify_n8n(payload: dict) -> bool:
    if not settings.notify_n8n or not settings.n8n_webhook_url:
        return False

    try:
        response = requests.post(
            settings.n8n_webhook_url,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return True
    except Exception as exc:
        print(f"[n8n] webhook failed: {exc}")
        return False
