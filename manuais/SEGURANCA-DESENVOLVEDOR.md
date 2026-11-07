# WMK API Security Center — Manual do desenvolvedor

**Walney Moreira Klein — walneyk@hotmail.com**

## Arquitetura
- `src/security.py`: credenciais aleatórias geradas com `secrets`, SHA-256 dos tokens no SQLite, escopos, expiração, revogação, auditoria.
- `src/security_cli.py`: CLI administrativa local, sem endpoints públicos para gerar credenciais.
- `src/protected_bridge.py`: servidor HTTP protegido, isolado do `src/bridge.py` legado.
- `tests/test_security.py` e `tests/test_protected_http.py`: testes unitários e HTTP real em porta efêmera.

## Contrato
```http
GET /api/v1/vehicles
Authorization: Bearer wmk_...
```
Escopo: `gps:read`. Se a chave limita `devices`, a lista de veículos é filtrada após consultar Traccar. Não existe paginação nem filtragem por usuário do Traccar neste protótipo.

```http
POST /api/v1/positions
Authorization: Bearer wmk_...
Content-Type: application/json

{"id":"CAR-01","latitude":-22.28,"longitude":-42.53,"simulated":true}
```
Escopo: `gps:write`. O ID é validado contra a lista autorizada. Retorna `{"accepted":true,"persisted":false,...}`. **Não persiste nem encaminha ao Traccar.**

## Permissões
`gps:read`, `gps:write`, `gps:history`, `devices:manage`, `admin`. Somente read/write possuem endpoints protegidos nesta etapa. Os demais escopos são reservados, não representam funcionalidades prontas.

## Configuração
- `WMK_SECURE_PORT`: porta local (8772).
- `WMK_SECURITY_DB`: caminho do banco SQLite privado. Padrão `data/security.sqlite3`, excluído pelo Git.
- `WMK_RATE_LIMIT`: máximo de solicitações autorizadas por chave a cada 60 s, padrão 60.
- `WMK_TRACCAR_URL`, `WMK_TRACCAR_TOKEN` ou usuário/senha: conexão upstream já suportada pelo módulo legado.

## Segurança
- Segredo gerado por CSPRNG; armazenar somente hash no banco.
- Nunca incluir chaves no navegador ou app móvel.
- O banco SQLite contém metadados sensíveis; aplicar ACL de sistema de arquivos e backup criptografado.
- Rate limit é em memória e por processo; não serve para clusters nem protege contra ataques distribuídos.
- Auditoria local não tem retenção automática, anonimização de IP ou proteção antiviolação.
- Não há TLS nativo: loopback obrigatório. Para rede/produção, proxy HTTPS, autenticação de usuários, autorização multitenant, políticas de retenção e revisão de segurança.
- Não confundir CORS com autenticação. OPTIONS não habilita acesso cruzado no navegador.
- Não confundir HTTP 202 com persistência.
- Os endpoints públicos de saúde/capabilities não retornam posições.
- O Bridge legado permanece inalterado; migração requer decisão explícita para evitar interromper os consumidores atuais.

## Testes
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python -m py_compile src/security.py src/protected_bridge.py src/security_cli.py
```

Cobrir ainda: carga concorrente, rotação de chave, proteção de backups, indisponibilidade do Traccar, HTTPS e autenticação de usuários antes de produção.
