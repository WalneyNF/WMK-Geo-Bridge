# Instalação, uso e testes — WMK Geo Bridge

**Regra WMK:** documentação para usuários, desenvolvedores e administradores, exemplos testados, funcionamento independente, API documentada e créditos Walney Moreira Klein — walneyk@hotmail.com. Respeitar licenças upstream.

## 1. Como baixar e instalar

Instale Python 3.10+; baixe o ZIP em https://github.com/WalneyNF/WMK-Geo-Bridge ou execute git clone com essa URL. Abra o terminal na pasta extraída e execute `py -3 src/bridge.py`. Por padrão o serviço usa 127.0.0.1:8766. Se a porta estiver ocupada, defina `WMK_BRIDGE_PORT` antes de iniciar. Teste `GET /health` e `GET /api/v1/capabilities`.

## 2. Como verificar se funciona

Execute `py -3 -m unittest discover -s tests -v`. Em 06/11/2026, quatro testes unitários passaram e a instância na porta 8768 respondeu HTTP 200. O endpoint POST /api/v1/positions não persiste dados; não o utilize como armazenamento de posições.

## 3. APIs e integração independente

Consulte `docs/openapi.json`, `docs/swagger.html` e exemplos em `examples/`. Configure autenticação do Traccar fora do Git. Não exponha localizações privadas sem autorização.

## 4. Segurança e manutenção

Não publique tokens, credenciais, IMEI nem coordenadas pessoais. Faça backup de dados e configurações antes de atualizar. Verifique `git status` e preserve alterações locais. Utilize HTTPS e autorização para serviços expostos à internet.

## 5. Créditos e redistribuição

Contribuições WMK: **Walney Moreira Klein — walneyk@hotmail.com**. Preserve avisos de copyright, licenças e arquivos NOTICE aplicáveis dos autores originais. Atribuições adicionais devem respeitar a licença efetiva de cada componente.
