## Contexto

O Buzz já possui:
- Três estados em `MembroCirculo.status`: `online`, `ocupado`, `offline`
- Presença em tempo real via Redis + WebSocket (`presenca_atualizada`), com `ocupado` preservado no connect (`presenca-tempo-real`)
- Favoritos (`eh_vip`) no círculo e buzina em massa na home
- Navbar com pill estático "Disponível" (`partials/nav.html`)
- Spec `buzz` com requisito "Modo não perturbe inteligente" ainda não implementado de ponta a ponta

O usuário pediu que o pill funcione como controle de **não perturbe** — documentado aqui como MVP funcional antes de horários automáticos.

## Objetivos / Não-objetivos

**Objetivos:**
- Pill clicável: **Disponível** ↔ **Não perturbe** (mapeado a `online` / `ocupado` enquanto conectado).
- Destinatário em não perturbe: buzina de **não-favorito** silenciada (histórico + notificação passiva, sem alerta invasivo).
- **Favoritos** do destinatário: buzina normal (overlay, som, vibração).
- Círculo vê status **Ocupado** ao vivo; remetente não-VIP não consegue buzinar (UI + backend).
- Persistir preferência no espelho ORM (`MembroCirculo` onde `contato = eu`) e notificar via WS.

**Não-objetivos (nesta change):**
- Horários automáticos (ex.: 22h–7h) — roadmap
- Nível "silenciar absolutamente tudo" (nem VIP) — futuro
- Push nativo / CallKit quando app fechado
- Alterar o mecanismo de presença por conexão (offline continua = sem WS)

## Decisões

### 1. Mapear não perturbe → `ocupado`

Reutilizar `StatusPresenca.OCUPADO` em vez de novo campo. A presença já não sobrescreve ocupado no connect.

**Alternativa rejeitada:** campo `nao_perturbe` separado no User — duplicaria semântica com `ocupado` já usado na UI dos cards.

### 2. Toggle via API + espelho ORM

`POST /api/disponibilidade/` com corpo `{ "modo": "disponivel" | "nao_perturbe" }`:

```python
# disponivel + conectado → online; disponivel + desconectado → offline
# nao_perturbe + conectado → ocupado
MembroCirculo.objects.filter(contato=usuario).update(status=..., updated_at=now())
Presenca.notificar_circulo(usuario.id, forcar_status=...)
```

Fat model em `Presenca` ou `MembroCirculo` — a view só orquestra.

### 3. Regra de entrega na `Buzina.enviar`

Antes de notificar o destinatário:

```python
if destinatario_esta_ocupado and not remetente_eh_favorito_do(destinatario):
    # cria buzina com status pendente ou flag silenciada; SEM _notificar WS de alerta
    # registra para histórico/notificações (lida_em null)
    return buzina  # remetente recebe ok com indicador de silenciada (opcional no JSON)
```

VIP = existe `MembroCirculo(dono=destinatario, contato=remetente, eh_vip=True)`.

**Por quê:** defesa em profundidade — mesmo que a UI falhe, o destinatário não é perturbado.

### 4. UI do remetente

- `MembroCirculo.pode_buzinar`: `False` se contato `ocupado` **e** eu não sou favorito dele.
- Cards, perfil e chamar já leem `pode_buzinar` e presença WS — pouca mudança de template.
- Mensagem: "Em não perturbe" / "Só favoritos podem chamar".

### 5. Pill no navbar

Estados visuais (tokens do design system):
- **Disponível**: ponto ciano pulsante, texto "Disponível"
- **Não perturbe**: ponto âmbar (`tertiary`), texto "Não perturbe", sem pulse
- **Offline** (desconectado): ponto cinza, texto "Offline", pill não alterna para disponível até reconectar

Clique alterna apenas entre disponível ↔ não perturbe quando há conexão WS ativa.

### 6. Resposta ao remetente de buzina silenciada

JSON de `enviar` inclui `silenciada: true` quando aplicável. Frontend pode mostrar toast curto: "Mensagem registrada — contato em não perturbe". Sem overlay de chamada sainte prolongado.

## Riscos / Trade-offs

- [Remetente acha que buzinou mas ninguém viu] → `silenciada: true` no JSON + item no histórico do remetente com rótulo claro.
- [Ocupado vs "estou ocupado" resposta rápida] → nomes distintos na UI ("Não perturbe" no pill vs resposta "Tô ocupado" na buzina).
- [Toggle com múltiplas abas] → última ação vence; estado único no ORM por usuário.
- [Favorito mútuo assimétrico] → VIP é sempre do ponto de vista do **destinatário** (`dono=destinatario`).

## Plano de migração

- Sem migração de schema (reutiliza `status` e `eh_vip`).
- Deploy aditivo: endpoint novo, pill interativo, regra em `enviar`.
- Rollback: reverter `enviar` e pill estático; ocupado volta a ser apenas manual via admin/seed.

## Questões em aberto

- Buzina silenciada fica `pendente` para sempre ou auto-`perdida` após timeout? (Sugestão: `perdida` após 45s sem leitura, como hoje.)
- Remetente silenciado deve ver animação de "chamando" ou feedback imediato? (Sugestão: feedback imediato curto, sem overlay.)
