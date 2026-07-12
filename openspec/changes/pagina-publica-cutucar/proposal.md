## Por quê

Hoje alguém só consegue cutucar outra pessoa depois de criar uma conta e estabelecer uma conexão. Uma página pública compartilhável reduz essa barreira e permite que visitantes presenciais ou remotos chamem a atenção do dono do link, inclusive por QR Code, sem perder a identificação de quem está chamando.

## O que muda

- Cada usuário poderá disponibilizar um link público não previsível para receber cutucões.
- A página pública exibirá diretamente o botão de cutucar e a identidade do dono do link.
- Visitantes anônimos informarão um nickname simples antes de enviar o cutucão.
- Visitantes autenticados serão identificados pela própria conta, sem preencher nickname.
- O dono poderá copiar o link, exibir seu QR Code, desativar o acesso e gerar uma nova chave.
- O destinatário receberá alerta em tempo real e push com a identidade informada pelo visitante.
- O envio público terá cooldown, rate limiting e validações próprias para reduzir abuso.
- O acesso público não criará automaticamente uma conexão entre visitante e destinatário.

## Capacidades

### Novas capacidades

- `cutucao-publico`: publicação, compartilhamento e uso seguro de uma página pública para cutucar seu proprietário.

### Capacidades modificadas

- `buzz`: o alerta recebido passa a aceitar e identificar uma origem pública, autenticada ou anônima.

## Impacto

- Novos modelos e migration em `apps.dashboard` para o acesso compartilhável e seus eventos públicos.
- Novas CBVs, forms, URLs e templates Django públicos.
- Integração com WebSocket, Web Push e push nativo para notificar o proprietário.
- QR Code atual passa a apontar para a página pública de cutucão; o convite de conexão continua disponível separadamente.
- Novos controles de compartilhamento nas páginas de próximos/configurações.
- Testes de modelo, segurança, rate limiting, views, QR e notificações.
