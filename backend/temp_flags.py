import os

class Flags:
    def __init__(self):
        self.client = None

    def is_enabled(self, name: str, context: dict | None = None) -> bool:
        return os.getenv(f"FLAG_{name.upper()}", "false").lower() == "true"
