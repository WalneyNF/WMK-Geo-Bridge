# Curso prático WMK: GPS Tracker, Geo Bridge e Geo Intelligence
**Edição de laboratório — 06/11/2026**  
**Autor das contribuições WMK:** Walney Moreira Klein — walneyk@hotmail.com  
**Objetivo:** aprender a instalar, diagnosticar, testar e integrar os três projetos sem comprometer o funcionamento independente de cada um.

## Módulo 1 — O que é cada programa?

**WMK GPS Tracker:** fork do Traccar. Recebe posições por protocolos GPS, guarda dispositivos/posições e fornece API HTTP autenticada. Interface/API: `http://127.0.0.1:8082`. Porta de entrada GPS depende do protocolo; OsmAnd costuma usar 5055.

**WMK Geo Bridge:** servidor Python independente, com documentação e API REST. No laboratório, roda em `http://127.0.0.1:8768`. Normaliza os dados do Tracker para JSON, mas precisa de credenciais autorizadas para ler dispositivos. Não grava posições recebidas pelo endpoint POST nesta versão.

**WMK Geo Intelligence:** aplicação web de visualização geoespacial. No laboratório, abre em `http://127.0.0.1:4173`. O laboratório separado `/geo-bridge-lab.html` permite consultar a API Bridge e ver veículos numa tabela e gráfico esquemático. **Ainda não é a integração com o mapa 3D principal.**

Os três produtos podem funcionar separadamente. Integrá-los é opcional.

## Módulo 2 — Entender a arquitetura

```text
[GPS / Celular] -- protocolo GPS --> [GPS Tracker :5055 ou outra porta]
                                          |
                                    API REST :8082
                                          |
                                 autenticação do Tracker
                                          |
                                    [Geo Bridge :8768]
                                          |
                                    JSON /api/v1/vehicles
                                          |
                           [Geo Intelligence :4173]
                           /geo-bridge-lab.html
```

**Importante:** a porta 8082 é a API/interface do Tracker, não a porta padrão de recepção de dados GPS. O laboratório e o mapa 3D principal são componentes distintos.

## Módulo 3 — Primeiro teste: serviços respondem?

Abra o PowerShell e execute:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8082/api/server'
Invoke-RestMethod 'http://127.0.0.1:8768/health'
Invoke-RestMethod 'http://127.0.0.1:8768/api/v1/capabilities'
```

Resultado observado no laboratório em 06/11/2026:
- Tracker: HTTP 200;
- Bridge health: HTTP 200, versão 0.1.0;
- Bridge capabilities: HTTP 200, `traccarConfigured: false`;
- Bridge vehicles: HTTP 503.

O HTTP 200 de `/health` prova que o Bridge responde; **não** prova que ele consegue ler o Tracker.

## Módulo 4 — O que significa HTTP 503?

`GET /api/v1/vehicles` chama internamente o Tracker para obter `/api/devices` e `/api/positions`.

Na versão 0.1 do Bridge:
- **503** com `{"error":"traccar_auth_not_configured"}`: nenhuma credencial foi fornecida ao processo Bridge.
- **502** com `{"error":"traccar_unavailable_or_invalid_response"}`: a fonte não respondeu corretamente, incluindo falhas HTTP do Tracker.
- **200** com `items: []`: a consulta funcionou, mas não retornou dispositivos.
- **200** com `items` preenchido: a consulta funcionou; valide também se os dados estão corretos.
- **401** na API do Tracker sem login: esperado, porque os dados são privados.

O 503 observado foi confirmado por `traccarConfigured: false`; **não significa** que o Tracker ou o mapa estejam quebrados.

## Módulo 5 — Preparar uma conta autorizada

1. Abra `http://127.0.0.1:8082/`.
2. Entre com uma conta existente de laboratório; se não houver conta, configure uma por meio dos procedimentos oficiais do Tracker. Não use credenciais padrão presumidas.
3. Cadastre um dispositivo fictício, sem localização real de terceiros, e confirme que aparece na interface.
4. Prefira conta com permissões mínimas para leitura de dispositivos e posições.
5. Nunca cole senha ou token no GitHub, no README, em prints ou neste chat.

## Módulo 6 — Iniciar um Bridge autenticado (PowerShell)

**Não altere a instância atual na porta 8768.** Abra outro PowerShell, entre na pasta `D:\Ferramentas\WMK-Geo-Bridge` e execute:

```powershell
Set-Location 'D:\Ferramentas\WMK-Geo-Bridge'
$env:WMK_BRIDGE_PORT = '8769'
$env:WMK_TRACCAR_URL = 'http://127.0.0.1:8082'
$env:WMK_TRACCAR_USER = Read-Host 'Usuário Traccar'
$senha = Read-Host 'Senha Traccar' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($senha)
try {
    $env:WMK_TRACCAR_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
py -3 src/bridge.py
```

O processo permanece aberto enquanto o Bridge estiver executando. **Atenção:** variáveis de ambiente são convenientes para laboratório, mas não são um cofre de segredos; processos com permissões adequadas podem acessá-las. Não exponha o Bridge à rede pública. Ao encerrar a sessão, remova as variáveis ou feche o terminal.

Em outro PowerShell, teste:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8769/health'
Invoke-RestMethod 'http://127.0.0.1:8769/api/v1/capabilities'
Invoke-RestMethod 'http://127.0.0.1:8769/api/v1/vehicles'
```

O campo `traccarConfigured` deve ser `true`. Isso indica somente que credenciais foram fornecidas; não prova que são válidas. O teste de veículos deve retornar HTTP 200 com JSON para confirmar a leitura autorizada.

## Módulo 7 — Testar na interface WMK

1. Abra `http://127.0.0.1:4173/geo-bridge-lab.html`.
2. No campo **Endereço do Bridge**, digite `http://127.0.0.1:8769` se estiver usando a nova instância autenticada.
3. Clique em **Verificar API**.
4. Clique em **Atualizar veículos**.
5. Confira nome, latitude, longitude, velocidade e horário.
6. Marque **Atualizar a cada 10 s** para testar a atualização automática.

**Atenção:** o Bridge 0.1 permite CORS apenas das origens `http://127.0.0.1:4173` e `http://localhost:4173`. Se o Vite usar outra porta, o navegador poderá bloquear a consulta por CORS, mesmo quando a API responde no PowerShell. Esse cenário exige configurar a origem permitida no Bridge, não desativar a segurança do navegador.

## Módulo 8 — Entender a resposta JSON

Exemplo didático fictício (não é dado coletado do servidor):

```json
{
  "schemaVersion": "1.0",
  "source": "traccar",
  "count": 1,
  "items": [
    {
      "id": "12",
      "deviceId": 12,
      "name": "Veiculo de teste",
      "source": "traccar",
      "simulated": null,
      "position": {
        "latitude": -22.28,
        "longitude": -42.53,
        "speedKmh": 18.52,
        "heading": 90,
        "timestamp": "2026-11-06T12:00:00Z",
        "valid": true
      }
    }
  ]
}
```

**schemaVersion:** versão do contrato JSON. **items:** lista de veículos. **position:** última posição ou `null`. **speedKmh:** velocidade convertida de nós (unidade do Traccar) para quilômetros por hora. **timestamp:** instante da medição, normalmente UTC. O adaptador JavaScript transforma cada item em dados fáceis de mostrar na interface.

## Módulo 9 — Exercícios

1. Desligue somente o Bridge e observe: o Tracker continua respondendo? Isso comprova independência.
2. Ligue o Bridge sem credenciais e explique por que `/health` retorna 200, mas `/vehicles` retorna 503.
3. Consulte `/capabilities` e identifique o valor de `traccarConfigured`.
4. Crie um dispositivo fictício autorizado e observe a diferença entre dispositivo cadastrado e dispositivo com posição.
5. Verifique se a posição exibida na tabela é a mesma retornada pelo JSON.
6. Interrompa o Tracker e verifique se o Bridge informa falha de fonte, sem travar a interface.
7. Comprove que a interface Geo Intelligence principal continua abrindo sem Bridge.

## Módulo 10 — Critérios para considerar tudo funcionando

- Tracker acessível, usuário autenticado e dispositivo de teste cadastrado.
- Posição de teste realmente recebida pelo Tracker.
- Bridge autenticado retornando o mesmo dispositivo e posição.
- Laboratório web exibindo posição e atualizações.
- Testes automatizados e compilação aprovados.
- Cada produto testado isoladamente, com os demais desligados.
- Para declarar integração **com o mapa 3D principal**, ainda é necessário conectar e testar uma camada visual de veículos; o laboratório separado não substitui esse passo.

## Referências locais

- Tracker: `manuais/17-integracao-celular-gps.md`.
- Bridge: `docs/openapi.json`, `docs/swagger.html` e `manuais/INTEGRACAO-TRACCAR-GEO.md`.
- Geo Intelligence: `geo-bridge-lab.html`, `src/wmk/traccar/bridgeAdapter.js`.

**Licenças:** preserve a licença e os créditos dos autores originais, além das atribuições das contribuições WMK.
