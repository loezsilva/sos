## ADDED Requirements

### Requirement: Página de perfil do contato
O usuário SHALL acessar uma página de perfil ao clicar em um card do círculo, exibindo o contato, seu status ao vivo e o histórico de chamadas com ele, com a ação de buzinar integrada.

#### Scenario: Abrir perfil pelo card
- **WHEN** o usuário clica em um card de contato em `/circulos/`
- **THEN** é redirecionado para `/circulos/<membro_id>/`
- **AND** vê avatar, nome e status atual (online, ocupado, offline) do contato

#### Scenario: Botão de buzinar no perfil
- **WHEN** o usuário mantém pressionado o botão BUZZ do perfil por 2 segundos
- **THEN** uma buzina é enviada ao contato
- **AND** o botão exibe o anel de progresso durante o pressionar e feedback tátil ao disparar

#### Scenario: Contato offline no perfil
- **WHEN** o contato está offline
- **THEN** o botão BUZZ fica desabilitado
- **AND** o perfil informa que o contato está indisponível para buzina

#### Scenario: Status atualiza ao vivo
- **WHEN** o status de presença do contato muda enquanto o perfil está aberto
- **THEN** o indicador de status e o estado do botão BUZZ atualizam sem reload

### Requirement: Histórico de chamadas por contato
O perfil SHALL listar as chamadas trocadas com aquele contato, mais recentes primeiro, com direção, status e horário.

#### Scenario: Ver histórico do contato
- **WHEN** o usuário abre o perfil de um contato
- **THEN** vê a lista de buzinas trocadas com ele em ordem cronológica decrescente
- **AND** cada item mostra se foi enviada ou recebida, o status (atendida, perdida, recusada, respondida, cancelada) e o horário

#### Scenario: Perfil sem histórico
- **WHEN** não há chamadas registradas com o contato
- **THEN** o perfil exibe um estado vazio informando que ainda não houve chamadas
