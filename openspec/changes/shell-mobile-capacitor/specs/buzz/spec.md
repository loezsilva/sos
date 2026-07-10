## MODIFIED Requirements

### Requirement: Tela de chamada recebida
O destinatário SHALL receber interface de alta prioridade em tela cheia com som e vibração: via WebSocket/PWA quando no browser, e via push nativo com som do bundle e full-screen intent quando no app Capacitor (Android) ou notificação time-sensitive (iOS).

#### Scenario: Receber buzina no browser (aba visível)
- **WHEN** buzina chega com aba visível
- **THEN** alerta fullscreen com Web Audio (após gesto) e vibração (após gesto)

#### Scenario: Receber buzina no app nativo Android
- **WHEN** buzina chega com app em background ou tela bloqueada
- **THEN** notificação nativa com som customizado e vibração
- **AND** full-screen intent ou toque abre alerta com mensagem do remetente se houver

#### Scenario: Resposta rápida
- **WHEN** destinatário responde na tela de alerta
- **THEN** remetente recebe resposta em tempo real e alerta encerra
