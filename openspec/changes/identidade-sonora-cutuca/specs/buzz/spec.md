## MODIFIED Requirements

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira e usa a identidade sonora oficial do Cutuca.

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina
- **THEN** a tela de alerta ocupa 100% da viewport com a assinatura sonora recebida e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente recebe a resposta em tempo real
- **AND** a tela de alerta e o som de alerta são encerrados
