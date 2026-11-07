# WMK API Security Center — Manual do usuário

**Walney Moreira Klein — walneyk@hotmail.com**

## O que está protegido?
A nova API **experimental protegida** funciona em uma porta separada (padrão 8772). A consulta de veículos e o recebimento de posições exigem um token Bearer com permissões. Os servidores antigos nas portas 8766/8768 **não passam a ficar protegidos automaticamente**. Não publique essas portas na internet.

## 1. Inicializar sem instalar nada
No PowerShell, dentro de `D:\Ferramentas\WMK-Geo-Bridge`:

```powershell
python src/protected_bridge.py
```

Abra `http://127.0.0.1:8772/health`. Deve retornar status ok. O servidor aceita somente conexões do próprio computador.

## 2. Criar uma chave para leitura
Em outro terminal:

```powershell
python src/security_cli.py create --name "Aplicativo de consulta" --scopes gps:read --devices CAR-01 --days 30
```

A saída mostra a chave **uma única vez**. Guarde-a em gerenciador de segredos. Não cole em páginas web, repositórios, mensagens ou aplicativos distribuídos. O ID gerado serve para revogação.

## 3. Testar o acesso
No PowerShell, insira a chave de forma privada:

```powershell
$token = Read-Host 'Cole sua chave privada'
Invoke-RestMethod 'http://127.0.0.1:8772/api/v1/vehicles' -Headers @{ Authorization = "Bearer $token" }
```

Se o Traccar não estiver configurado, uma chave válida poderá resultar em HTTP 503; isso é diferente de falha de autenticação.

## 4. Criar uma chave para envio
```powershell
python src/security_cli.py create --name "Gateway de teste" --scopes gps:write --devices CAR-01 --days 7
```

Envie apenas posições fictícias de um dispositivo permitido. O endpoint protegido `POST /api/v1/positions` responde HTTP 202 com `persisted:false`: **não grava posições** nessa versão.

## 5. Revogar, listar e auditar
```powershell
python src/security_cli.py list
python src/security_cli.py revoke ID_DA_CHAVE
python src/security_cli.py audit
```

A listagem não mostra as chaves completas. Uma chave revogada deixa de autorizar imediatamente.

## 6. Mensagens
- HTTP 401: falta token.
- HTTP 403: token inválido, expirado, revogado ou sem permissão; dispositivo fora da lista também é bloqueado.
- HTTP 429: limite por chave excedido.
- HTTP 400: coordenadas ou JSON inválidos.
- HTTP 503: Traccar ainda sem credenciais.
- HTTP 502: falha na consulta ao Traccar.

## Limites atuais
Ainda não existe painel gráfico de administração, login de usuários, integração de produção com Traccar, TLS nativo ou persistência das posições recebidas. Use HTTPS via proxy reverso confiável em produção, com controle de usuários e dispositivos. O acesso é somente local até essas medidas serem implementadas e verificadas.
