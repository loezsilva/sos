## ADDED Requirements

### Requirement: Toggle de disponibilidade no navbar
O usuário autenticado SHALL alternar entre Disponível e Não perturbe pelo pill do navbar enquanto estiver conectado.

#### Scenario: Ativar não perturbe
- **WHEN** o usuário toca no pill estando Disponível e conectado
- **THEN** o status efetivo passa a ocupado para quem o tem no círculo
- **AND** o pill exibe "Não perturbe" com indicador âmbar

#### Scenario: Voltar a disponível
- **WHEN** o usuário toca no pill estando em Não perturbe e conectado
- **THEN** o status efetivo passa a online
- **AND** o pill exibe "Disponível" com indicador ciano

#### Scenario: Desconectado
- **WHEN** o usuário não tem conexão WebSocket ativa
- **THEN** o pill indica Offline
- **AND** não permite alternar para Disponível até reconectar

### Requirement: Silenciamento de buzinas para não-favoritos
Quando o destinatário está em não perturbe (ocupado), buzinas de contatos que não são favoritos dele SHALL ser registradas sem alerta invasivo.

#### Scenario: Não-favorito buzina destinatário em não perturbe
- **WHEN** um contato não-favorito envia buzina a um usuário em não perturbe
- **THEN** a buzina é persistida no histórico
- **AND** o destinatário não recebe overlay fullscreen, som ou vibração
- **AND** a atividade aparece na central de notificações

#### Scenario: Favorito buzina destinatário em não perturbe
- **WHEN** um contato favorito (`eh_vip`) do destinatário envia buzina
- **THEN** o fluxo normal de alerta SHALL ocorrer (overlay, som, vibração)

### Requirement: Bloqueio de envio na UI para ocupado
O remetente que não é favorito do destinatário SHALL not see the contact as available for buzzing when the destination is in não perturbe.

#### Scenario: Card de contato ocupado
- **WHEN** o contato está em não perturbe e o usuário não é favorito dele
- **THEN** o card indica Ocupado
- **AND** o botão de buzina fica desabilitado

#### Scenario: Atualização ao vivo
- **WHEN** o contato ativa não perturbe com a lista ou perfil abertos
- **THEN** o indicador e o estado do botão atualizam via `presenca_atualizada` sem reload
