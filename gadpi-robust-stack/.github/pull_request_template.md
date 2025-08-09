## Checklist de Robustez
- [ ] OpenAPI atualizado e cliente FE regenerado (`npm run gen:api`) — anexar diff
- [ ] BE: unit + snapshot de contrato (`tests/__snapshots__`)
- [ ] Schemathesis verde (link do job)
- [ ] FE: stories criadas/atualizadas + diffs visuais aprovados (Chromatic/Loki)
- [ ] E2E crítico passou (quando habilitado)
- [ ] Feature flag e plano de rollback documentados
- [ ] Changelog / migração (/v1 → /v2, se houver quebra)