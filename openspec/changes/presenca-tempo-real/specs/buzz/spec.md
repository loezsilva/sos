## Requisitos MODIFICADOS

### Requirement: Gerenciamento de círculo
O usuário SHALL visualizar e gerenciar pessoas do seu círculo íntimo com status de presença derivado da conexão real (online, ocupado, offline).

#### Scenario: Listar contatos
- **WHEN** o usuário acessa a tela de círculos
- **THEN** vê lista de contatos com status (online, ocupado, offline) refletindo presença efetiva
- **AND** pode adicionar ou remover membros do círculo

#### Scenario: Contato conecta enquanto a lista está aberta
- **WHEN** um contato do círculo abre o app
- **THEN** o card desse contato atualiza para online sem reload
