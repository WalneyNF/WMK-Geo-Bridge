# Relatório de testes — WMK Geo Bridge

Data: 06/11/2026
Responsável: Walney Moreira Klein — walneyk@hotmail.com

## Método obrigatório
Cada etapa tem ID, objetivo, preparação, comandos, resultados esperados, resultados observados, decisão e próxima etapa. Não avançar após falha não explicada. Não solicitar ao usuário verificações que podem ser automatizadas.

## T001 — Inicialização independente
**Objetivo:** validar que o novo repositório executa sem afetar a ponte antiga.

**Ambiente:** Windows; D:\Ferramentas\WMK-Geo-Bridge; Python 3; porta 8767 para o novo serviço; porta 8766 para laboratório anterior.

**Execução:**
- py -3 -m unittest discover -s tests -v
- WMK_BRIDGE_PORT=8767; py -3 src/bridge.py
- GET http://127.0.0.1:8767/health
- GET http://127.0.0.1:8767/api/v1/capabilities
- GET http://127.0.0.1:8767/api/v1/vehicles
- GET http://127.0.0.1:8766/health

**Resultado observado:**
- 4/4 testes unitários passaram.
- /health 200: service=wmk-geo-bridge, version=0.1.0.
- /api/v1/capabilities 200: traccarConfigured=false; writeEnabled=false.
- /api/v1/vehicles 503: esperado, autenticação ainda não configurada.
- Porta 8766 preservada: service=wmk-gps-bridge.

**Decisão:** APROVADO. Sem alterações na interface do WMK ou Traccar.

## T002 — Traccar autenticado (PENDENTE)
**Objetivo:** consultar /api/devices e /api/positions via Bridge e conferir normalização de coordenadas e velocidade.
**Pré-requisitos:** credencial de integração do Traccar configurada de modo seguro, sem registrar segredo em Git ou relatório.
**Critérios de aprovação:** HTTP 200; dispositivos autorizados; velocidade em km/h; sem vazamento de token; erros 401/403/502 tratados.
**Status:** NÃO EXECUTADO. Não interpretar como aprovado.

## T003 � Documenta��o OpenAPI e clientes (APROVADO PARCIALMENTE)
- GET /docs: HTTP 200 (HTML Swagger servido; renderiza��o externa da CDN n�o verificada).
- GET /docs/manual: HTTP 200 (manual HTML).
- GET /openapi.json: HTTP 200 (JSON sintaticamente v�lido).
- GET /health e /api/v1/capabilities: HTTP 200.
- GET /api/v1/vehicles: HTTP 503 esperado, credencial Traccar n�o configurada.
- Clientes Node.js, Python e PHP executados; os tr�s exibiram o diagn�stico e HTTP 503 esperado.
- 4/4 testes unit�rios passaram; sintaxe JS e PHP verificada.
- N�o foi realizado teste de autentica��o real do Traccar nem renderiza��o do Swagger em navegador.
