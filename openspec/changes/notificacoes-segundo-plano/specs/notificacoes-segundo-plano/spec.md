## ADDED Requirements

### Requirement: PWA instalável
O Buzz SHALL expor um manifest web e Service Worker para permitir instalação como PWA e recebimento de push em segundo plano.

#### Scenario: Manifest válido
- **WHEN** o navegador carrega qualquer página autenticada do Buzz
- **THEN** encontra `manifest.webmanifest` com `name`, `short_name`, `start_url`, `scope`, `theme_color`, ícones (192/512 + maskable) e `launch_handler.client_mode: focus-existing`
- **AND** o Service Worker é registrado em `/sw.js` com escopo na raiz do app

### Requirement: Inscrição Web Push
O usuário autenticado SHALL poder inscrever o dispositivo para receber Web Push via chaves VAPID do servidor.

#### Scenario: Ativar notificações
- **WHEN** o usuário concede permissão de notificação e confirma nas configurações
- **THEN** o cliente envia a `PushSubscription` ao backend
- **AND** o servidor persiste endpoint e chaves associadas ao usuário

#### Scenario: Desativar notificações
- **WHEN** o usuário desativa notificações em segundo plano nas configurações
- **THEN** a inscrição é removida no servidor
- **AND** o cliente cancela a subscription local

### Requirement: Push ao receber buzina em segundo plano
O sistema SHALL enviar notificação Web Push ao destinatário quando uma buzina não silenciada é criada.

#### Scenario: Buzina com app em segundo plano
- **WHEN** o destinatário possui inscrição push ativa e recebe uma buzina (não silenciada)
- **THEN** o Service Worker exibe notificação do SO com nome do remetente
- **AND** a notificação usa identificador único da buzina para deduplicação

#### Scenario: Buzina silenciada (não perturbe)
- **WHEN** a buzina é silenciada por não perturbe
- **THEN** nenhuma notificação Web Push é enviada
- **AND** apenas histórico/notificações in-app são atualizados

#### Scenario: Toque na notificação
- **WHEN** o usuário toca na notificação de buzina
- **THEN** o Buzz abre (ou foca aba existente) na URL da buzina
- **AND** o alerta fullscreen de chamada recebida é exibido se a buzina ainda estiver pendente

### Requirement: Sincronização ao retornar ao app
O cliente SHALL recuperar buzinas pendentes ao voltar ao primeiro plano.

#### Scenario: Aba volta ao foco
- **WHEN** o documento fica visível e existe buzina pendente não exibida
- **THEN** o overlay de alerta é mostrado como no fluxo WebSocket
- **AND** notificações do SO com o mesmo `tag` são dispensadas
