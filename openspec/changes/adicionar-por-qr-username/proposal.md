## Por quê

A tela de círculos só lista membros já existentes; não há como convidar alguém pelo app. Sem isso, o produto depende de admin/seed e a spec de “adicionar ou remover membros” fica incompleta.

## O que muda

- Usuário pode **exibir um QR code** (e link) para outra pessoa se conectar
- Usuário pode **buscar por username** e enviar convite
- Destinatário **aceita ou recusa** (opt-in); ao aceitar, ambos entram no círculo um do outro
- Empty state da página Círculos deixa de apontar só para admin/demo

## Capacidades

### Novas capacidades
- `convite-circulo`: convite por QR/username com aceite mútuo no círculo

### Capacidades modificadas
- `buzz`: gerenciamento de círculo passa a incluir adicionar via convite (não só listar)

## Impacto

- Model/views/templates em `apps/dashboard`
- Dependência `qrcode` (PNG via Pillow)
- Rotas públicas de landing do QR (login required para confirmar)
