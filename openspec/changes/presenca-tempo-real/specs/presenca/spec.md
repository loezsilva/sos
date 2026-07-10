## Purpose

Definir presença em tempo real: quem está com o app conectado aparece online para quem o tem no círculo, de forma simétrica e ao vivo.

## Requisitos ADICIONADOS

### Requirement: Presença baseada em conexão
O sistema SHALL considerar um usuário online quando existir pelo menos uma conexão WebSocket autenticada, e offline quando não houver nenhuma.

#### Scenario: Abrir o app
- **WHEN** o usuário autentica e o WebSocket conecta
- **THEN** o status efetivo passa a online (salvo se estiver explicitamente ocupado)
- **AND** quem o tem no círculo recebe atualização em tempo real

#### Scenario: Fechar todas as abas
- **WHEN** a última conexão WebSocket do usuário é encerrada
- **THEN** após o debounce configurado o status efetivo passa a offline
- **AND** quem o tem no círculo recebe atualização em tempo real

#### Scenario: Múltiplas abas
- **WHEN** o usuário tem duas abas abertas e fecha apenas uma
- **THEN** permanece online

### Requirement: Simetria no círculo
Quem possui o usuário como membro do círculo SHALL ver o mesmo status efetivo derivado da conexão, não um valor estático independente.

#### Scenario: Admin online, Alex no círculo
- **WHEN** admin está conectado e alex tem admin no círculo
- **THEN** alex vê admin como online nos cards, contadores e página de chamar
- **AND** o inverso vale se alex estiver conectado e admin o tiver no círculo

### Requirement: Atualização live na UI
A interface autenticada SHALL atualizar indicadores de presença sem recarregar a página ao receber o evento de presença.

#### Scenario: Contato fica online
- **WHEN** o cliente recebe `presenca_atualizada` com status online
- **THEN** o card correspondente muda o indicador e o rótulo
- **AND** o contador “X online” é recalculado quando aplicável

#### Scenario: Página de chamar
- **WHEN** o usuário está na página de chamar daquele contato e o status muda
- **THEN** o texto de status da página reflete a nova presença
- **AND** a possibilidade de buzinar segue a regra (offline não buzina)

### Requirement: Ocupado manual preservado
O status ocupado SHALL poder coexistir com conexão ativa e NÃO ser sobrescrito automaticamente para online no connect.

#### Scenario: Usuário ocupado conecta
- **WHEN** o usuário está marcado como ocupado e o WebSocket conecta
- **THEN** permanece ocupado para o círculo
- **AND** ao desconectar totalmente passa a offline
