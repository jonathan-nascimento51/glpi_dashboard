# Dockerfile para o serviço de mapeamento GLPI
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de configuração do projeto
COPY pyproject.toml ./
COPY tools/glpi_mapping/pyproject.toml ./tools/glpi_mapping/

# Instala dependências Python
RUN pip install --no-cache-dir -e ./tools/glpi_mapping/

# Copia código fonte
COPY tools/ ./tools/

# Cria diretórios necessários
RUN mkdir -p /app/lookups /app/logs /var/log

# Copia arquivo de cron
COPY tools/glpi_mapping/crontab /etc/cron.d/glpi-mapping

# Define permissões do cron
RUN chmod 0644 /etc/cron.d/glpi-mapping && \
    crontab /etc/cron.d/glpi-mapping

# Cria script de entrada
RUN echo '#!/bin/bash\n\
echo "Iniciando serviço de mapeamento GLPI..."\n\
echo "Configuração do cron:"\n\
crontab -l\n\
echo "Iniciando cron daemon..."\n\
cron\n\
echo "Executando mapeamento inicial..."\n\
python -m glpi_mapping dump --out /app/lookups || echo "Falha no mapeamento inicial"\n\
echo "Monitorando logs..."\n\
touch /var/log/cron.log\n\
tail -f /var/log/cron.log' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Variáveis de ambiente padrão
ENV MAPPING_OUTPUT_DIR=/app/lookups
ENV MAPPING_LOG_LEVEL=INFO
ENV PYTHONPATH=/app

# Expõe porta para health check (opcional)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m glpi_mapping test-connection || exit 1

# Comando padrão
CMD ["/app/entrypoint.sh"]