# PADRÃO OBRIGATÓRIO DE DOCUMENTAÇÃO WMK

**Aplicação:** WMK GPS Tracker, WMK Geo Bridge, WMK Geo Intelligence e futuros projetos WMK.  
**Responsável pelas contribuições WMK:** Walney Moreira Klein — walneyk@hotmail.com.

## Princípios

1. **Independência:** cada produto e cada API devem poder ser usados isoladamente quando sua função principal permitir. Integrações com outros projetos WMK são opcionais e claramente identificadas.
2. **Documentação em português (Brasil):** instruções separadas para usuário comum, desenvolvedor e administrador.
3. **Do zero até funcionar:** informar onde baixar, pré-requisitos, instalação, configuração, primeira execução, exemplos reais, atualização, backup, desinstalação e solução de problemas. Incluir caminhos e comandos Windows quando aplicáveis; cobrir Linux/Docker quando suportados e testados.
4. **APIs utilizáveis por terceiros:** documentar base URL, versão, autenticação, autorização, parâmetros, esquemas JSON, códigos HTTP, limites, exemplos copiáveis e cuidados com dados pessoais.
5. **Integração móvel:** mostrar como um app Android/iOS autorizado pode enviar GPS sem depender da instalação dos outros produtos. Distinguir protocolo existente, adaptador proposto e recurso testado.
6. **Testes antes de anunciar:** registrar ambiente, comando, resultado esperado/observado, status e data. Não confundir documentação publicada com nova versão funcional compilada.
7. **Licenciamento e créditos:** preservar os avisos e direitos dos autores upstream. Atribuir claramente as contribuições WMK a **Walney Moreira Klein — walneyk@hotmail.com**. Orientar redistribuidores a manter os avisos de copyright, licença e NOTICE aplicáveis; não afirmar obrigações de marca ou atribuição além do que a licença realmente permite.
8. **Segurança:** não publicar senhas, tokens, IMEI ou dados reais de localização. Orientar consentimento, HTTPS, autenticação e proteção de dados.
9. **Manutenção:** documentação acompanha cada mudança funcional; exemplos e links devem ser testados.
10. **Navegação:** README deve direcionar à central `manuais/` e à documentação de API.

## Entregáveis mínimos

- `README.md` em pt-BR.
- `manuais/index.html` com navegação.
- Guias de usuário, desenvolvedor e administrador.
- Guia de instalação e configuração passo a passo.
- Referência de API (OpenAPI quando aplicável) e exemplos de consumo.
- Guia de integração móvel quando o produto fornecer recursos para apps.
- `manuais/TESTES-WMK.md` ou relatório equivalente.
- `ATRIBUICOES-E-LICENCAS.md` explicando origem, contribuições e obrigações de redistribuição.

## Controle de qualidade

A publicação só é considerada concluída após validar os arquivos, os links e os procedimentos documentados no ambiente correspondente. Procedimentos não testados devem ser marcados como **pendentes de validação**.
