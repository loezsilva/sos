## Por quê

Hoje o card de contato em `/circulos/` buzina direto via JavaScript, sem uma tela dedicada. O fluxo ideal é abrir uma página de chamada (estilo `chamada_sainte`) onde o usuário vê o contato, personaliza a mensagem e só então dispara a buzina — alinhado ao PRD e à referência visual da imagem 2.

## O que muda

- Card de membro em `circulos.html` vira link clicável para `/circulos/<membro_id>/chamar/`
- Nova página `chamar_contato.html` com layout da chamada sainte: avatar, nome, botão BUZZ redondo central
- Seção de personalização abaixo do botão: mensagem curta (até 80 caracteres)
- Campos de som e vibração aparecem como UI desabilitada/placeholder (implementação futura)
- Ao buzinar, reutiliza overlay `chamada_sainte` existente para aguardar resposta
- Botão bolt no card deixa de buzinar inline — apenas o card inteiro navega (bolt pode ser removido ou virar indicador visual)

## Capacidades

### Novas capacidades

_Nenhuma — a página de chamar é extensão do fluxo de círculo._

### Capacidades modificadas

- `buzz`: adiciona requisito de página dedicada para chamar contato do círculo com mensagem curta opcional

## Impacto

- `templates/dashboard/chamar_contato.html` — novo template
- `templates/partials/card_membro.html` — card clicável com link
- `apps/dashboard/views.py` — `PaginaChamarContatoView`
- `apps/dashboard/urls.py` — rota `circulos/<uuid:membro_id>/chamar/`
- `apps/dashboard/models.py` — campo opcional `mensagem` em `Buzina` (ou em envio)
- `static/js/buzz.js` — enviar mensagem junto com buzina
- Sem impacto em WebSocket (payload pode incluir mensagem depois)
- Som/vibração: apenas UI placeholder nesta mudança
