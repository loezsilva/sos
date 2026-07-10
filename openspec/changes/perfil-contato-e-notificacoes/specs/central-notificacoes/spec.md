## ADDED Requirements

### Requirement: Indicador de notificações no navbar
O navbar SHALL exibir um ícone de sino com contador de notificações não lidas, atualizado em tempo real.

#### Scenario: Contador de não lidas
- **WHEN** o usuário tem buzinas ou respostas não lidas
- **THEN** o sino exibe um contador com a quantidade de itens não lidos

#### Scenario: Nova atividade em tempo real
- **WHEN** o usuário recebe uma buzina, resposta ou uma chamada é perdida com a aba aberta
- **THEN** o contador do sino incrementa sem reload via WebSocket

#### Scenario: Sem notificações
- **WHEN** não há itens não lidos
- **THEN** o sino não exibe contador

### Requirement: Lista de atividades recentes
Ao abrir a central, o usuário SHALL ver a lista de atividades recentes e os itens são marcados como lidos.

#### Scenario: Abrir a central
- **WHEN** o usuário toca no sino
- **THEN** abre um painel com as atividades recentes (buzinas recebidas, respostas recebidas e chamadas perdidas) em ordem cronológica decrescente
- **AND** cada item mostra o contato envolvido, o tipo de atividade e o horário

#### Scenario: Marcar como lidas
- **WHEN** o usuário abre a central
- **THEN** os itens não lidos passam a lidos
- **AND** o contador do sino zera

#### Scenario: Atalho para o contato
- **WHEN** o usuário toca em um item da central
- **THEN** é levado ao perfil do contato relacionado
