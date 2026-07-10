## MODIFIED Requirements

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira quando o app está em primeiro plano, e uma notificação do sistema operacional quando o app está em segundo plano ou fechado (com permissão de push ativa).

#### Scenario: Receber buzina com app em primeiro plano
- **WHEN** o usuário recebe uma buzina e a aba está visível
- **THEN** a tela de alerta ocupa 100% da viewport com som e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida

#### Scenario: Receber buzina com app em segundo plano
- **WHEN** o usuário recebe uma buzina, possui push ativo e a aba não está visível
- **THEN** o sistema exibe notificação do SO com identificação do remetente
- **AND** ao abrir o app pela notificação o alerta fullscreen é apresentado se a buzina ainda estiver pendente

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente recebe a resposta em tempo real
- **AND** a tela de alerta é encerrada
