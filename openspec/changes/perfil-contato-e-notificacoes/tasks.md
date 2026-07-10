## 1. Modelo e histórico (Buzina)

- [x] 1.1 Adicionar campo `lida_em` (DateTimeField, null=True, blank=True) à `Buzina`
- [x] 1.2 Criar e aplicar migração de schema (aditiva/reversível)
- [x] 1.3 Adicionar `BuzinaQuerySet` com `historico_de(usuario)` (enviadas+recebidas, ordenado por `-created_at`), `entre(usuario, contato)` e `nao_lidas_de(usuario)`
- [x] 1.4 Adicionar método/classmethod `marcar_lidas(usuario)` usando `update(lida_em=now())` (sem loop Python)
- [x] 1.5 (Opcional) data migration marcando buzinas antigas como lidas

## 2. Perfil do contato

- [x] 2.1 Criar `PerfilContatoView(DetailView)` em `apps/dashboard/views.py` (queryset restrito ao dono, `pk_url_kwarg='membro_id'`)
- [x] 2.2 Adicionar contexto: histórico `Buzina.objects.entre(request.user, membro.contato)` limitado (ex.: 50)
- [x] 2.3 Adicionar rota `circulos/<uuid:membro_id>/` (name `perfil_contato`) em `apps/dashboard/urls.py`
- [x] 2.4 Criar template `templates/dashboard/perfil_contato.html` (avatar, status ao vivo, botão BUZZ com `data-segurar-buzina="2"`/`data-buzinar`, seção de histórico)
- [x] 2.5 Criar parcial `templates/partials/item_historico.html` (direção, status, horário)
- [x] 2.6 Estado vazio quando não houver chamadas com o contato
- [x] 2.7 Ajustar `partials/card_membro.html`: card passa a linkar para o perfil; bolt continua para chamar

## 3. Central de notificações (navbar)

- [x] 3.1 Criar context processor `notificacoes` expondo `nao_lidas` (contagem) e itens recentes (ex.: 15) e registrá-lo em settings
- [x] 3.2 Adicionar sino + contador + painel dropdown no `partials/nav.html` (desktop e mobile), com tokens do design system
- [x] 3.3 Criar parcial `templates/partials/item_notificacao.html` (contato, tipo, horário, link para o perfil)
- [x] 3.4 Criar `NotificacoesView` (`GET /api/notificacoes/`) retornando itens recentes em JSON
- [x] 3.5 Criar `MarcarNotificacoesLidasView` (`POST /api/notificacoes/marcar-lidas/`) chamando `Buzina.marcar_lidas`
- [x] 3.6 Registrar rotas das duas views em `urls.py`

## 4. Tempo real e interações (buzz.js)

- [x] 4.1 Incrementar o contador do sino nos handlers já existentes de `buzina_recebida`, `resposta_recebida` e `buzina_encerrada` (perdida)
- [x] 4.2 Abrir/fechar o dropdown da central; ao abrir, `POST` marcar-lidas e zerar contador
- [x] 4.3 Atualizar status ao vivo no perfil (reusar `presenca_atualizada`) — indicador e estado do botão BUZZ
- [x] 4.4 Garantir reconciliação do contador ao abrir a central (fonte de verdade = backend)

## 5. Estilos e ajustes finais

- [x] 5.1 Estilos do sino/contador/dropdown e itens em `static/css/src/buzz.css`; recompilar com `npm run build:css`
- [x] 5.2 Revisar responsividade (mobile/desktop) e acessibilidade (aria-labels, foco)
- [x] 5.3 Testes pytest: `historico_de`/`entre`/`nao_lidas_de`, `marcar_lidas`, `PerfilContatoView`, endpoints de notificações
- [x] 5.4 Validar `openspec validate` e revisar fluxo ponta a ponta (card → perfil → buzinar → notificação → marcar lida)
