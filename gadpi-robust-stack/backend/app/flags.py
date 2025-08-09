import os
from unleash_client import UnleashClient

class Flags:
    def __init__(self):
        url = os.getenv("UNLEASH_URL")
        app_name = os.getenv("UNLEASH_APP_NAME", "gadpi-backend")
        instance_id = os.getenv("UNLEASH_INSTANCE_ID", "local")
        self.client = None
        if url:
            self.client = UnleashClient(url=url, app_name=app_name, instance_id=instance_id)
            self.client.initialize_client()

    def is_enabled(self, name: str, context: dict | None = None) -> bool:
        if not self.client:
            return os.getenv(f"FLAG_{name.upper()}", "false").lower() == "true"
        return self.client.is_enabled(name, context or {})