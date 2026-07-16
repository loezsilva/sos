## MODIFIED Requirements

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira, com a identidade sonora oficial e, quando disponível, a localização do remetente.

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina
- **THEN** a tela de alerta ocupa 100% da viewport com a assinatura sonora recebida e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida

#### Scenario: Receber com localização
- **WHEN** o cutucão inclui coordenadas válidas
- **THEN** o alerta exibe a localização e um atalho para abrir no mapa

### Requirement: Gerenciamento de contatos
O usuário SHALL visualizar e gerenciar pessoas conectadas sob a nomenclatura Contatos.

#### Scenario: Listar contatos
- **WHEN** o usuário acessa a tela de contatos
- **THEN** vê lista de contatos com status (online, ocupado, offline)
- **AND** a interface usa o termo Contatos em vez de Próximos
