## ADDED Requirements

### Requirement: App Capacitor instalável
O Buzz SHALL disponibilizar app nativo Android e iOS via Capacitor que carrega a aplicação web autenticada.

#### Scenario: Abrir app nativo
- **WHEN** o usuário abre o app Buzz instalado no celular
- **THEN** o WebView carrega a URL configurada do Buzz
- **AND** `window.BuzzNativo.ehAppNativo` é verdadeiro

### Requirement: Som e vibração nativos na buzina
O app nativo SHALL reproduzir som customizado e vibração ao receber buzina, sem exigir gesto prévio no WebView.

#### Scenario: Buzina com app em background (Android)
- **WHEN** o destinatário recebe buzina e possui app nativo com push ativo
- **THEN** o SO exibe notificação com som `buzina` e vibração
- **AND** ao interagir abre a tela de alerta da buzina

#### Scenario: Buzina com app em primeiro plano
- **WHEN** o app nativo está aberto e recebe push de buzina
- **THEN** o som e a vibração são acionados via plugin nativo
- **AND** o alerta fullscreen é exibido no WebView

### Requirement: Full-screen intent no Android
No Android, buzina não silenciada SHALL poder exibir interface de chamada em tela cheia sobre o lock screen.

#### Scenario: Tela bloqueada
- **WHEN** o dispositivo Android está bloqueado e recebe buzina
- **THEN** o full-screen intent exibe o alerta de chamada
- **AND** o usuário pode responder ou recusar
