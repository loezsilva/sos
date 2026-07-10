## Contexto

O Buzz precisa que quem está conectado apareça conectado para quem o tem no círculo. Hoje `MembroCirculo.status` é seed estático (`popular_circulo_demo`) e não reflete o WebSocket. Admin pode estar com WS aberto e Alex vê Offline — e vice-versa.

Já existe: Daphne + Channels + Redis (`buzz_{user_id}`), `BuzzConsumer`, overlays no `base.html`. A change `garantir-entrega-buzina` garante entrega com app aberto; presença é o pré-requisito de confiança (“posso buzinar?”).

Produto-alvo: PWA/app nas lojas com notificação e UI tipo chamada. Esta change é a **camada 1** desse caminho.

## Objetivos / Não-objetivos

**Objetivos:**
- Online = tem pelo menos uma conexão WS autenticada
- Offline = zero conexões (após debounce)
- Quem me tem como contato no círculo recebe `presenca_atualizada` em tempo real
- Cards, contador “X online” e página chamar refletem presença real
- `ocupado` permanece preferência manual (não sobrescrito por connect, salvo regra explícita)

**Não-objetivos (nesta change):**
- Web Push / Service Worker
- Capacitor, FCM, APNs
- CallKit / ConnectionService / full-screen intent
- Heartbeat de “app em background” sem WS
- Sincronizar presença entre usuários que **não** estão no círculo um do outro

## Decisões

### 1. Fonte da verdade: Redis set de conexões

Chave `presenca:conexoes:{user_id}` = set de `channel_name`.  
- `connect`: `SADD` + se passou de 0→1, marcar online e notificar círculo  
- `disconnect`: `SREM` + se ficou 0, marcar offline e notificar  

**Por quê:** Redis já está no stack do Channels; conta abas corretamente.

**Alternativa rejeitada:** só atualizar `MembroCirculo` no connect — quebra com múltiplas abas e não é simétrico (status é por dono).

### 2. Espelho no ORM para leitura nas views

Ao mudar presença efetiva (online/offline), atualizar com ORM em massa:

```python
MembroCirculo.objects.filter(contato=usuario).exclude(status=OCUPADO).update(status=ONLINE|OFFLINE)
```

Quem está `ocupado` não é forçado a online no connect (respeita “não perturbe” leve). No disconnect, se era ocupado e zerou conexões → offline.

**Por quê:** views/templates atuais já leem `membro.status`; evita reescrever todas as queries agora.

### 3. Notificação só para donos do círculo

Destinatários do evento: `MembroCirculo.objects.filter(contato=usuario).values_list('dono_id')` → `group_send` em cada `buzz_{dono}`.

Payload: `{ tipo: 'presenca_atualizada', usuario_id, status, nome? }`.

### 4. UI live no `buzz.js`

Handler `presenca_atualizada`: atualiza indicador do card (`data-contato-id`), contador online, e `#status-chamada` se for o contato da página.

### 5. Roadmap (documentado, não implementado)

```
Camada 1 (esta change)     Camada 2                    Camada 3
Presença via WS      →     Web Push (VAPID)      →     Shell nativo
App aberto                 App fechado (Android)       CallKit / ConnectionService
                           depois FCM/APNs via          Painel tipo telefone
                           Capacitor
```

PWA puro **não** garante segundo plano nem UI de chamada nas lojas. Backend Django/Channels permanece; o client ganha push e, depois, wrapper nativo.

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Disconnect falso (reload rápido) | Debounce curto (~2s) antes de marcar offline se set zerar |
| Redis reinicia → sets vazios | No connect sempre reconstrói; opcional sync periódico |
| Ocupado vs online | Não sobrescrever `ocupado` no connect; UI distingue os três estados |
| Círculo não mútuo | Só quem tem o usuário como contato vê o status (correto para o modelo atual) |
| Expectativa de “sempre online no celular” | Fora do escopo; push (camada 2) |

## Plano de migração

1. Serviço/helper `Presenca` (Redis + update ORM + notify)
2. Hook no `BuzzConsumer`
3. `data-contato-id` nos cards + handler JS
4. Ajustar demo seed (status inicial offline; presença sobe no login)

Rollback: remover hooks do consumer; UI volta ao campo estático.

## Questões em aberto

- Debounce de disconnect: **2 segundos** como padrão
- Toggle manual “Disponível/Ocupado” na nav: change futura (hoje é cosmético)
- Momento de Capacitor/push: change separada após presença estável
