# Integração opcional: GPS Tracker → Geo Bridge → Geo Intelligence

**Créditos WMK:** Walney Moreira Klein — walneyk@hotmail.com.

## Arquitetura

Cada produto funciona de maneira independente. O Tracker mantém seu próprio servidor e sua API; o Bridge disponibiliza endpoints HTTP; o Geo Intelligence mantém suas fontes geoespaciais. A conexão é opcional.

## Teste A — servidores sem autenticação

1. Inicie o Tracker e confira `http://127.0.0.1:8082/api/server`.
2. Inicie o Bridge: `$env:WMK_BRIDGE_PORT="8768"; py -3 src/bridge.py` (PowerShell, na pasta do Bridge).
3. Confira `http://127.0.0.1:8768/health` e `http://127.0.0.1:8768/api/v1/capabilities`.
4. Abra o Geo Intelligence no endereço exibido pelo Vite.

**Resultado observado em 06/11/2026:** os três serviços responderam HTTP 200. Sem credenciais, `GET /api/v1/vehicles` respondeu HTTP 503; `traccarConfigured` estava `false`. A API Traccar `/api/devices` e `/api/positions` retornou HTTP 401 sem autenticação, como esperado.

## Teste B — configurar credenciais somente em memória

Use uma **conta de laboratório com permissão mínima**, criada na interface do Tracker. Não coloque senha em arquivos do repositório ou comandos publicados. No PowerShell interativo, antes de iniciar uma nova instância do Bridge:

```powershell
$env:WMK_BRIDGE_PORT = "8769"
$env:WMK_TRACCAR_URL = "http://127.0.0.1:8082"
$env:WMK_TRACCAR_USER = Read-Host "Usuario Traccar"
$secure = Read-Host "Senha Traccar" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $env:WMK_TRACCAR_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
py -3 src/bridge.py
```

**Atenção:** variáveis de ambiente ainda ficam disponíveis para o processo e processos filhos. Para produção, adote um gerenciador de segredos; não use esse exemplo como solução de segurança de produção.

Em outro terminal, consulte `http://127.0.0.1:8769/api/v1/capabilities` e depois `http://127.0.0.1:8769/api/v1/vehicles`. Um HTTP 200 com `items` comprova a leitura autorizada; verifique os campos e horários. Um 401/403 indica problema de autorização; 503 indica fonte indisponível ou falha de integração.

## Teste C — adaptador Geo Intelligence

O adaptador `src/wmk/traccar/bridgeAdapter.js` consulta `/api/v1/vehicles` e normaliza a resposta. Por padrão, usa o Bridge local na porta 8768; para testar a instância autenticada, passe `base: 'http://127.0.0.1:8769'`. Ele não deve receber senhas do Tracker. O adaptador ainda precisa ser ligado à camada visual do mapa para exibir veículos.

## Segurança e privacidade

O endpoint `/api/v1/vehicles` da versão Bridge 0.1 **não implementa autenticação própria para leitura**; ele fica vinculado a `127.0.0.1`. **Não exponha o Bridge diretamente à internet.** Antes de disponibilizar uma API pública para terceiros, implemente autorização por cliente/dispositivo, TLS, limites de acesso e auditoria. Evite dados de localização reais nos testes.

## Critério de aprovação final

Só considerar a integração completa depois de comprovar: (1) Tracker recebe posição autorizada; (2) Bridge retorna a mesma posição autenticada; (3) Geo Intelligence exibe e atualiza a posição; (4) cada produto continua funcionando quando os outros dois estão desligados.
