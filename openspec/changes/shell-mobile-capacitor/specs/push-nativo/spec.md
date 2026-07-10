## ADDED Requirements

### Requirement: Inscrição de token nativo
O usuário autenticado no app nativo SHALL registrar token FCM (Android) ou APNs (iOS) no backend.

#### Scenario: Registrar após login
- **WHEN** o app nativo obtém token de push do SO
- **THEN** envia `POST /api/push/nativo/inscrever/` com token e plataforma
- **AND** o servidor persiste em `InscricaoNativa`

### Requirement: Envio nativo em buzina
O sistema SHALL enviar push nativo ao criar buzina não silenciada para tokens `InscricaoNativa` do destinatário.

#### Scenario: Buzina para usuário com app Android
- **WHEN** buzina não silenciada é criada e destinatário tem token FCM
- **THEN** FCM envia notificação de alta prioridade com som e dados da buzina
- **AND** payload inclui `buzina_id`, `remetente_nome`, `mensagem`, `url`

#### Scenario: Coexistência com Web Push
- **WHEN** destinatário tem inscrição VAPID e nativa
- **THEN** ambos os canais podem ser usados
- **AND** o app nativo prioriza handler nativo para som/vibração
