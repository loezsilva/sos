## MODIFIED Requirements

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira e identifica corretamente a origem autenticada ou pública.

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina de uma pessoa conectada
- **THEN** a tela de alerta ocupa 100% da viewport com som e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente autenticado recebe a resposta em tempo real
- **AND** a tela de alerta é encerrada

#### Scenario: Receber cutucão público anônimo
- **WHEN** o usuário recebe um cutucão por seu link público de um visitante anônimo
- **THEN** a tela de alerta exibe o nickname como nome informado pelo visitante
- **AND** identifica explicitamente que a origem é o link público
- **AND** oferece as mesmas respostas rápidas do fluxo normal

#### Scenario: Receber cutucão público autenticado
- **WHEN** o usuário recebe um cutucão por seu link público de uma conta autenticada
- **THEN** a tela de alerta exibe a identidade da conta
- **AND** identifica explicitamente que a origem é o link público
- **AND** oferece as mesmas respostas rápidas do fluxo normal

#### Scenario: Resposta a cutucão público
- **WHEN** o destinatário responde um cutucão público com "Já vou", "Tô ocupado", "Ligo em 5 min" ou recusa
- **THEN** o visitante autorizado recebe o desfecho
- **AND** a tela de alerta do destinatário é encerrada
