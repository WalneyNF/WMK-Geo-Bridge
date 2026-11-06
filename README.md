# WMK Geo Bridge

**Ponte modular de integração GPS e geoespacial — documentação em português brasileiro.**

**Autor:** Walney Moreira Klein — walneyk@hotmail.com

O **WMK Geo Bridge** é um terceiro projeto independente, projetado para conectar servidores de rastreamento GPS, como o **Traccar**, ao **WMK Geo Intelligence** e a outras aplicações. Os projetos podem funcionar separadamente.

> **Estado atual: versão experimental 0.1.0.** API REST local funcional, adaptador Traccar em desenvolvimento, endpoint de recepção experimental sem persistência. Não use em produção ou para publicar localizações privadas.

## O que existe hoje

- API HTTP JSON com biblioteca padrão do Python, sem dependências externas.
- `GET /health`: estado do serviço.
- `GET /api/v1/capabilities`: recursos e estado de configuração.
- `GET /api/v1/vehicles`: consulta dispositivos e posições do Traccar, **quando credenciais válidas estiverem configuradas**.
- `POST /api/v1/positions`: recebe e valida posição externa, **sem persistir**, desativado por padrão.
- CORS limitado a origens locais do WMK; escuta apenas `127.0.0.1`.
- Documentação HTML em `docs/index.html`, exemplos e testes automatizados.

## Começar em 3 passos

Requisitos: **Python 3.10+**, Traccar opcional para testes de disponibilidade.

```powershell
git clone https://github.com/WalneyNF/WMK-Geo-Bridge.git
cd WMK-Geo-Bridge
py -3 src/bridge.py
```

Abra [http://127.0.0.1:8766/health](http://127.0.0.1:8766/health).

Para consultar o Traccar, abra **outro PowerShell**, configure credenciais válidas e inicie a ponte **nesse mesmo terminal**:

```powershell
$env:WMK_TRACCAR_URL = "http://127.0.0.1:8082"
$env:WMK_TRACCAR_TOKEN = "SEU_TOKEN_AQUI"
py -3 src/bridge.py
```

Não inclua tokens em arquivos públicos, commits, exemplos reais ou código de navegador.

## Contrato JSON

```json
{
  "schemaVersion": "1.0",
  "source": "traccar",
  "items": [
    {
      "id": "1",
      "deviceId": 1,
      "name": "Veículo exemplo",
      "source": "traccar",
      "simulated": null,
      "position": {
        "latitude": -22.28,
        "longitude": -42.53,
        "speedKmh": 42.0,
        "heading": 90,
        "timestamp": "2026-11-06T12:00:00Z",
        "valid": true
      }
    }
  ],
  "count": 1,
  "timestamp": "2026-11-06T12:00:01Z"
}
```

**Exemplo ilustrativo**, não uma posição real. Velocidades do Traccar são convertidas de nós para km/h. `simulated: null` significa origem não verificada, e não necessariamente veículo real.

## Estrutura

```text
WMK-Geo-Bridge/
├── src/bridge.py          # Servidor HTTP e adaptador Traccar
├── tests/test_bridge.py   # Testes unitários
├── examples/cliente.py    # Cliente independente
├── docs/index.html        # Manual navegável em português
├── scripts/iniciar.bat    # Inicialização Windows
├── .gitignore
└── README.md
```

## Testes

```powershell
py -3 -m unittest discover -s tests -v
```

## Integrações futuras

- Conexão ao Cesium no WMK Geo Intelligence como camada GPS opcional.
- WebSocket/SSE, cache, reconexão, histórico, geocercas e eventos.
- Adaptadores para outros provedores, sem dependência exclusiva do Traccar.
- OpenAPI formal, autenticação de produção, armazenamento e controle de acesso.

## Segurança e licença

A API atual foi projetada para **laboratório local**. Não exponha a porta 8766 na internet. A chave de escrita não protege os endpoints de leitura. Para produção será necessário autenticar todas as rotas sensíveis, autorizar por usuário/dispositivo e usar HTTPS.

**Licença:** ainda em avaliação; não há concessão expressa de licença de redistribuição até a publicação de um arquivo LICENSE. O código deste projeto é independente dos forks Traccar e WMK; respeite as licenças dos projetos originais.

## Documentação

Abra `docs/index.html` no navegador para consultar instalação, arquitetura, APIs, exemplos, segurança e roteiro de desenvolvimento.

**Créditos:** Walney Moreira Klein — walneyk@hotmail.com.
