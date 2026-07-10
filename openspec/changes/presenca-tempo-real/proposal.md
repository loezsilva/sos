## Por quê

O status online/offline hoje é um campo estático em `MembroCirculo` (seed do demo), não a conexão real. Por isso um usuário pode estar com WebSocket aberto e o outro vê-lo como offline — a buzina parece “em vão” antes mesmo de ser enviada. Precisamos de presença simétrica em tempo real entre quem está no círculo um do outro, como base para o produto (atenção imediata) e para o roadmap de PWA/push.

## O que muda

- Presença derivada da conexão WebSocket (connect → online, disconnect → offline com debounce de abas)
- Propagação simétrica: quem me tem no círculo vê meu status atualizado ao vivo
- Contadores “X online” e cards do círculo refletem presença real, não seed
- Evento WS `presenca_atualizada` para atualizar UI sem reload
- Roadmap documentado (não implementado nesta change): Web Push → shell nativo (Capacitor) → CallKit/ConnectionService

## Capacidades

### Novas capacidades
- `presenca`: presença em tempo real baseada em conexão, simétrica no círculo, atualização live na UI

### Capacidades modificadas
- `buzz`: gerenciamento de círculo e nudge de status passam a usar presença real (online/ocupado/offline ao vivo)

## Impacto

- `BuzzConsumer`: registrar/desregistrar presença no connect/disconnect
- Redis (já usado pelo Channels) como fonte de verdade de sessões online
- `MembroCirculo.status`: espelho atualizado pela presença (ou leitura via presença + ocupado manual)
- Templates/JS: círculos, dashboard, página chamar — reagir a `presenca_atualizada`
- Sem push nativo, Service Worker ou CallKit nesta change (só design/roadmap)
