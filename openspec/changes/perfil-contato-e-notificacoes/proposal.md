## Por quê

Hoje clicar no card de um contato leva direto à tela de chamar, sem contexto sobre o relacionamento (chamadas anteriores, status recente). Além disso, respostas e buzinas perdidas somem assim que o overlay fecha — não há onde reencontrá-las. Falta um ponto central para o usuário revisar o que aconteceu e um acesso rápido a atividades recentes no topo da interface.

## O que muda

- Card do círculo passa a abrir uma **página de perfil do contato** (avatar, status ao vivo, histórico de chamadas com aquela pessoa e o botão BUZZ com o mesmo comportamento de segurar 2s). A ação de chamar passa a viver dentro do perfil.
- Nova **central de notificações** no navbar (ícone de sino) com contador de não lidas, listando buzinas recebidas, respostas e chamadas perdidas recentes; abrir a central marca como lidas.
- **Histórico de chamadas** completo (recebidas e enviadas) com status (atendida, perdida, recusada, respondida, cancelada) e horário — consumido tanto pelo perfil (filtrado por contato) quanto por uma visão geral.
- Buzinas passam a persistir e ser consultáveis (leitura), reaproveitando o modelo `Buzina` já existente.

## Capacidades

### Novas capacidades

- `perfil-contato`: página dedicada por contato com status ao vivo, histórico de chamadas com ele e ação de buzinar (segurar 2s) integrada.
- `central-notificacoes`: indicador no navbar com contador de não lidas e lista de atividades recentes (buzinas recebidas, respostas, perdidas), atualizada em tempo real via WebSocket.

### Capacidades modificadas

- `buzz`: o requisito "Histórico de chamados" passa a especificar histórico bidirecional (enviadas + recebidas) com status e horário, além de leitura/marcação de não lidas para alimentar a central de notificações.

## Impacto

- **Models** (`apps/dashboard/models.py`): campo de leitura na `Buzina` (ex.: `lida_em`) e QuerySet/métodos para histórico por contato e contagem de não lidas.
- **Views/URLs** (`apps/dashboard/`): `PerfilContatoView` (rota `circulos/<membro_id>/`), endpoint de notificações e marcação de lidas; card passa a linkar para o perfil e o botão de chamar migra para dentro dele.
- **Templates**: novo `dashboard/perfil_contato.html`; ajuste em `partials/card_membro.html` (link) e `partials/nav.html` (sino + dropdown); parcial de item de histórico e de notificação.
- **WebSocket** (`consumers.py`/`presenca.py`): eventos existentes (`buzina_recebida`, `resposta_recebida`, `buzina_encerrada`) passam a alimentar o contador da central em tempo real.
- **Frontend** (`static/js/buzz.js`): abrir/fechar dropdown de notificações, atualizar contador ao vivo, marcar como lidas.
- **UX tátil**: perfil reutiliza o botão BUZZ (segurar 2s, anel de progresso) já padronizado.
