## MODIFIED Requirements

### Requirement: Modo não perturbe inteligente
O usuário SHALL controlar não perturbe pelo pill do navbar e bloquear alertas de buzina de não-favoritos enquanto estiver em modo ocupado, mantendo bypass para contatos VIP do destinatário.

#### Scenario: VIP em horário de silêncio
- **WHEN** o modo não perturbe está ativo e um contato não-VIP buzina
- **THEN** a buzina é silenciada e registrada no histórico e na central de notificações
- **AND** contatos VIP ainda recebem alerta normal

#### Scenario: Toggle no navbar
- **WHEN** o usuário alterna o pill de Disponível para Não perturbe
- **THEN** o círculo passa a vê-lo como ocupado em tempo real
- **AND** as regras de silenciamento passam a valer imediatamente

#### Scenario: Remetente não-favorito tenta buzinar
- **WHEN** o destinatário está em não perturbe e o remetente não é VIP dele
- **THEN** a interface impede o envio da buzina
- **AND** o backend rejeita ou silencia caso contornado
