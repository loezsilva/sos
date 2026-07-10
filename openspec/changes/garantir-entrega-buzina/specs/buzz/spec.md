## Requisitos MODIFICADOS

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira, inclusive se a buzina tiver sido enviada enquanto ele estava desconectado (desde que ainda pendente e dentro do tempo máximo).

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina (ao vivo ou via catch-up no connect)
- **THEN** a tela de alerta ocupa 100% da viewport com vibração
- **AND** exibe o nome/foto do remetente, a mensagem curta se houver, e ações de resposta rápida

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente recebe a resposta em tempo real
- **AND** a tela de alerta é encerrada

#### Scenario: Chamada encerrada pelo remetente
- **WHEN** o remetente cancela ou a chamada expira enquanto o alerta está aberto
- **THEN** o alerta do destinatário é fechado automaticamente
- **AND** nenhuma resposta posterior é aceita para essa buzina
