## Contexto

A buzina hoje é fire-and-forget via Channels: `Buzina.enviar` cria o registro e faz `group_send` para `buzz_{destinatario_id}`. O overlay fullscreen já está no `base.html`, então qualquer página autenticada pode exibir o alerta — **desde que** o WebSocket esteja conectado naquele instante.

Gaps atuais:
- Evento WS perdido se o destinatário estiver offline/desconectado
- Sem recuperação de `Buzina` pendente ao reconectar
- “Encerrar” do chamador só fecha UI local
- Sem timeout → chamada pode ficar `pendente` indefinidamente

Referências: `apps/dashboard/models.py` (`Buzina`), `apps/dashboard/consumers.py`, `static/js/buzz.js`, overlays em `templates/partials/`.

## Objetivos / Não-objetivos

**Objetivos:**
- Destinatário com app aberto (qualquer tela) sempre vê alerta de buzina pendente (catch-up no connect)
- Cancelamento simétrico: encerrar no chamador remove alerta no destinatário
- Timeout (~45s): status `perdida`, feedback nos dois lados
- Tela “Buzinando…” reflete estados: aguardando / respondida / cancelada / perdida

**Não-objetivos:**
- Push nativo, Service Worker, notificações do SO
- Som real / vibração avançada
- Histórico de chamados (já especificado em `buzz`, fora desta mudança)
- Presença online real-time além do necessário para entrega

## Decisões

### 1. Catch-up no `connect` do WebSocket

No `BuzzConsumer.connect`, após `accept`, consultar `Buzina` com `status=pendente` e `destinatario=user`, ordenar por `created_at`, e enviar cada uma como `buzina_recebida` (mesmo payload do envio).

**Por quê:** reutiliza o handler JS existente; não precisa de endpoint HTTP extra para o happy path de recuperação.

**Alternativa rejeitada:** polling HTTP periódico — mais latência e carga desnecessária com WS já aberto.

### 2. Status `cancelada` e `perdida` no modelo

Estender `Buzina.Status` com `cancelada` e `perdida`. Métodos no model: `cancelar()` (só remetente, só se pendente) e `marcar_perdida()` (idempotente se ainda pendente).

**Por quê:** Fat Models; estados explícitos para histórico futuro e UI.

### 3. Timeout no cliente + confirmação no servidor

- Cliente do chamador: timer ~45s; ao expirar chama `POST /api/buzina/<id>/cancelar/` com flag `motivo=timeout` **ou** endpoint dedicado `expirar`.
- Preferência: `POST /api/buzina/<id>/encerrar/` com `motivo=usuario|timeout` que:
  - se ainda `pendente` → `cancelada` ou `perdida`
  - notifica destinatário (`buzina_encerrada`) e remetente (atualização local já tem o estado)

**Por quê:** sem Celery/cron nesta mudança; timeout confiável enquanto o chamador mantém a tela aberta. Catch-up no destinatário também filtra pendentes com `created_at` mais antigo que o timeout e marca como `perdida` antes de não reenviar.

### 4. Evento WS unificado `buzina_encerrada`

Payload: `{ tipo, buzina_id, motivo: 'cancelada'|'perdida' }`. Destinatário fecha alerta se `buzina_id` bater. Remetente atualiza overlay se ainda estiver na chamada.

**Alternativa rejeitada:** dois eventos separados — mais branches no JS sem ganho.

### 5. Uma buzina pendente por par (opcional nesta mudança)

Se já existir pendente do mesmo remetente→destinatário, reutilizar/atualizar em vez de criar outra — evita stack de alertas. Se simples demais no prazo: catch-up envia só a mais recente.

**Decisão:** catch-up envia apenas a pendente mais recente por remetente; envio novo cancela pendentes anteriores do mesmo par.

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Destinatário nunca abre o app | Fora do escopo (precisa push); chamador vê “perdida” após timeout |
| Timer só no cliente do chamador | Catch-up no destinatário descarta pendentes expiradas pelo `created_at` |
| Race: resposta e cancelamento simultâneos | `update` condicional `status=pendente`; quem ganha persiste |
| Múltiplas abas do destinatário | Ambas recebem WS; responder numa fecha nas outras via mesmo evento de resposta/encerramento |

## Plano de migração

1. Migration: novos choices em `status`
2. Model methods + API encerrar + consumer catch-up + eventos
3. Atualizar `buzz.js` e textos do overlay sainte
4. Testar: offline→online, encerrar, timeout, resposta normal

Rollback: reverter migration e consumer; JS ignora eventos desconhecidos.

## Questões em aberto

- Duração do timeout: **45 segundos** como padrão inicial (ajustável depois)
- Push / SW: change futura separada
