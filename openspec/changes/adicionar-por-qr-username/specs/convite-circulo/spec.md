## ADDED Requirements

### Requirement: Convite por username
O usuário autenticado SHALL poder buscar outro usuário pelo username e enviar um convite para entrar no círculo.

#### Scenario: Enviar convite
- **WHEN** o usuário informa um username existente que ainda não está no seu círculo
- **THEN** o sistema cria um convite pendente para o destinatário
- **AND** não cria `MembroCirculo` até o aceite

#### Scenario: Username inexistente
- **WHEN** o username não existe
- **THEN** o sistema informa que não encontrou a pessoa

### Requirement: Convite por QR code
O usuário autenticado SHALL poder exibir um QR code (e link) para que outra pessoa o convide.

#### Scenario: Exibir QR
- **WHEN** o usuário abre “Meu QR” em Círculos
- **THEN** vê um QR apontando para a URL de conexão do seu username

#### Scenario: Escanear e convidar
- **WHEN** um usuário autenticado abre a URL de conexão de outro username
- **THEN** pode confirmar o envio do convite para essa pessoa

### Requirement: Aceite mútuo
O destinatário SHALL aceitar ou recusar o convite; ao aceitar, ambos passam a aparecer no círculo um do outro.

#### Scenario: Aceitar
- **WHEN** o destinatário aceita um convite pendente
- **THEN** existem `MembroCirculo` nos dois sentidos
- **AND** o status do convite fica aceito

#### Scenario: Recusar
- **WHEN** o destinatário recusa
- **THEN** não há novos membros no círculo
- **AND** o status do convite fica recusado
