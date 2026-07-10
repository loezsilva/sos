## Por quê

Hoje a buzina só chega se o destinatário estiver com a aba aberta e o WebSocket conectado no instante do envio. Se a conexão cair, a aba estiver fechada ou o usuário abrir o app depois, o evento se perde — e quem está em “Buzinando…” fica aguardando em vão. Precisamos garantir que, dentro do app, quem recebe sempre veja quem está ligando, e que cancelamento/timeout fechem o ciclo dos dois lados.

## O que muda

- Catch-up ao conectar: ao abrir/reconectar o WebSocket, o destinatário recebe buzinas `pendente` ainda ativas
- Cancelamento simétrico: “Encerrar” do chamador cancela a buzina e remove o alerta do destinatário
- Timeout de chamada: após N segundos sem resposta, status `perdida`, feedback ao chamador e remoção do alerta no destinatário
- Feedback na tela “Buzinando…” para estados: aguardando, respondida, cancelada, perdida
- **Não inclui** push nativo / Service Worker (fora do escopo desta mudança)

## Capacidades

### Novas capacidades
- `entrega-buzina`: garantia de entrega e ciclo de vida da buzina (catch-up, cancelamento, timeout, estados simétricos)

### Capacidades modificadas
- `buzz`: tela de chamada recebida e fluxo de resposta passam a considerar recuperação de pendentes, cancelamento pelo remetente e chamada perdida

## Impacto

- Modelo `Buzina`: novo status `perdida` / `cancelada`, método de cancelar e consulta de pendentes
- `BuzzConsumer`: catch-up no `connect`; novos eventos WS (`buzina_cancelada`, `buzina_perdida`)
- API: endpoint ou ação para cancelar buzina sainte; possível job/timeout
- Templates/JS: `alerta_buzina.html`, `chamada_sainte.html`, `buzz.js` — estados e handlers novos
- Sem novas dependências externas nesta mudança
