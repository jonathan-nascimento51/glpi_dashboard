#!/usr/bin/env python3
# Script para atualizar validate_system.py
import re
from pathlib import Path

validate_file = Path("scripts/validation/validate_system.py")
with open(validate_file, "r", encoding="utf-8") as f:
    content = f.read()

# Substituir importações
content = content.replace(
    "from app.services.glpi_service import GLPIService",
    "from backend.app.services.glpi_service import GLPIService"
)
content = content.replace(
    "from app.core.config import active_config", 
    "from backend.app.core.config import active_config"
)

with open(validate_file, "w", encoding="utf-8") as f:
    f.write(content)

print(" validate_system.py atualizado")
