## Contexto

O fluxo atual buzina direto do card via `data-buzinar` + `buzz.js`. Já existe overlay `chamada_sainte` para aguardar resposta, mas ele só aparece após o clique no bolt — sem tela intermediária de preparação.

Referência visual: overlay `chamada_sainte.html` e imagem 2 do usuário (avatar central, ripples, nome do contato).

## Objetivos / Não-objetivos

**Objetivos:**
- Página dedicada `/circulos/<membro_id>/chamar/` acessível ao clicar no card
- Layout fullscreen estilo chamada sainte com botão BUZZ redondo central
- Campo de mensagem curta (máx. 80 caracteres) editável antes de buzinar
- Placeholders desabilitados para som e vibração (UI pronta, lógica futura)
- Reutilizar overlay `chamada_sainte` após disparar buzina

**Não-objetivos:**
- Implementar sons ou vibrações reais
- Persistir preferências de som/vibração por contato
- Alterar fluxo do dashboard principal (continua buzinando direto)

## Decisões

### 1. Navegação pelo card inteiro

O `<article>` do card vira `<a href="...">` envolvendo conteúdo. O botão bolt vira ícone decorativo (sem `data-buzinar`).

**Por quê:** UX pedida — clicar no card abre a página de chamar, não buzina inline.

### 2. Página como rota Django (não modal)

`PaginaChamarContatoView` com `DetailView`/`get_object` filtrando `MembroCirculo` do usuário logado.

**Alternativa rejeitada:** Modal JS — perde URL compartilhável e histórico do browser.

### 3. Layout da página

```
┌─────────────────────────┐
│  [voltar]    Nome       │  ← nav mínima ou sem nav/menu
│                         │
│     ○ avatar + ripple   │
│       [nome pill]       │
│                         │
│   ┌─────────────────┐   │
│   │ mensagem curta  │   │  ← max 80 chars
│   └─────────────────┘   │
│   Som: [desabilitado]   │  ← placeholder
│   Vibração: [desab.]    │  ← placeholder
│                         │
│      ( BOTÃO BUZZ )     │  ← dispara buzina + overlay
└─────────────────────────┘
```

Reutiliza classes: `animacao-ripple-alerta`, `animacao-flutuar`, `container-ripple`, `botao-buzz`.

### 4. Mensagem curta

Campo `mensagem` opcional em `Buzina` (CharField max_length=80). Enviado no POST `/api/buzina/enviar/`.

**Por quê:** Prepara exibição futura no alerta do destinatário sem implementar agora.

### 5. base.html sem nav/menu na página chamar

`{% block nav %}{% endblock %}` e `{% block menu %}{% endblock %}` — foco total na ação.

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Card offline ainda navegável | Desabilitar link ou mostrar aviso na página de chamar |
| Duplicação visual com overlay | Página = preparação; overlay = aguardando resposta |
| Campos som/vibração confundem usuário | `disabled` + label "Em breve" |

## Plano de migração

1. Migration `mensagem` em Buzina
2. View + URL + template
3. Card clicável
4. JS envia mensagem no POST
5. Testar fluxo completo

Rollback: remover rota e reverter card para `data-buzinar`.

## Questões em aberto

- Limite de 80 caracteres para mensagem — confirmado como padrão inicial
- Dashboard principal também terá página dedicada? → **Não nesta mudança**
