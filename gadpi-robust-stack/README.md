# GADPI Robust Stack — Kit Consolidado (COM ARQUIVOS)

Inclui:
1) **Higiene & Disciplina** — pre-commit, lint/typecheck strict, .env.example, Makefile.
2) **Max Robustez** — contrato-first (orval), adapters Zod, MSW, Storybook, snapshots & Schemathesis, CI com gates.
3) **Observability & Flags** — Sentry (FE/BE), OpenTelemetry (BE), Unleash (flags FE/BE).

## Como começar
### Backend
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```
### Frontend
```bash
cd frontend
npm i
npm run gen:api
npm run build-storybook
```
### CI
- `.github/workflows/ci.yml` incluído. Adicione secrets conforme comentários.

### Flags/Obs
- Sentry DSNs, OTEL collector e Unleash Proxy/Server via .env.

Se preferir, envio também um **script de recriação** para colar no seu projeto.