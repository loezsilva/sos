## MODIFIED Requirements

### Requirement: Histórico de chamados
O usuário SHALL consultar o histórico bidirecional de chamadas (enviadas e recebidas), com status e horário, e o sistema SHALL rastrear quais atividades ainda não foram lidas para alimentar a central de notificações.

#### Scenario: Ver histórico
- **WHEN** o usuário acessa o histórico
- **THEN** vê lista cronológica decrescente de buzinas recebidas e enviadas com timestamp e status (atendida, perdida, recusada, respondida, cancelada)

#### Scenario: Histórico por contato
- **WHEN** o usuário abre o perfil de um contato
- **THEN** vê apenas as chamadas trocadas com aquele contato, indicando direção (enviada/recebida), status e horário

#### Scenario: Marcar atividades como lidas
- **WHEN** o usuário abre a central de notificações
- **THEN** as buzinas recebidas e respostas ainda não lidas passam a lidas
- **AND** deixam de contar para o indicador de não lidas
