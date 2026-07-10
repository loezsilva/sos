## Contexto

A `Buzina` já persiste todas as chamadas (remetente, destinatário, status, `created_at`, `mensagem`) e o fluxo em tempo real via WebSocket já emite `buzina_recebida`, `resposta_recebida` e `buzina_encerrada` (ver `presenca-tempo-real` e `garantir-entrega-buzina`). Hoje, porém, o card de `/circulos/` linka direto para `/circulos/<membro_id>/chamar/` e nada dessas atividades fica acessível depois que o overlay fecha.

Esta mudança reaproveita o modelo `Buzina` existente para (1) uma página de perfil por contato com histórico e botão de buzinar, e (2) uma central de notificações no navbar alimentada pelos mesmos eventos WebSocket.

Referências visuais: `docs/DESIGN.md` (tokens), `docs/sos/my_circles/code.html` (cards/listas) e `docs/sos/buzz_dashboard/code.html` (botão central). Reutiliza os componentes já padronizados: botão BUZZ com anel de progresso (`anel-progresso-*`), `efeito-vidro`, `sombra-neumorfica`.

## Objetivos / Não-objetivos

**Objetivos:**
- Card do círculo abre `/circulos/<membro_id>/` (perfil) em vez de ir direto para chamar.
- Perfil reúne status ao vivo, histórico com o contato e o botão BUZZ (segurar 2s) já existente.
- Sino no navbar com contador de não lidas atualizado em tempo real e painel de atividades recentes.
- Persistir leitura das buzinas para o contador (`lida_em`).

**Não-objetivos:**
- Chat/mensagens de texto reais (a central é só de atividades/notificações).
- Notificações push nativas / Web Push (roadmap separado).
- Alterar o mecanismo de presença ou o protocolo WebSocket (só consumir eventos já existentes).
- Paginação infinita do histórico nesta iteração (limite simples基, ex.: últimos N).

## Decisões

- **Reaproveitar `Buzina` como fonte do histórico** em vez de criar modelo novo: todos os dados já existem; basta um `BuzinaQuerySet` com `historico_de(usuario)`, `entre(usuario, contato)` e `nao_lidas_de(usuario)`. Fat model, sem boilerplate.
- **Campo `lida_em` (DateTimeField, null)** na `Buzina` para marcar leitura, em vez de tabela separada de notificações. Não lidas = buzinas recebidas/respostas com `lida_em is null`. Marcar como lida = `update(lida_em=now())` em massa (ORM, sem loop).
- **Rota do perfil `circulos/<uuid:membro_id>/`** com `PerfilContatoView(DetailView)`; a página de chamar continua em `circulos/<membro_id>/chamar/` e passa a ser acessada a partir do perfil (o botão BUZZ do perfil pode buzinar inline, reusando `data-segurar-buzina`/`data-buzinar`, mantendo o overlay `chamada_sainte`). Assim não duplicamos a lógica de chamar.
- **Central de notificações como dropdown no `partials/nav.html`**: contador renderizado no load (contexto via context processor ou incluído nas views), e incrementado ao vivo no `buzz.js` ao receber os eventos WebSocket já tratados. Abrir o dropdown faz `POST` para marcar como lidas e zera o contador.
- **Context processor `notificacoes`** para expor `nao_lidas` e itens recentes em todas as telas sem repetir em cada view — o navbar é global (`base.html`).
- **Endpoints REST simples** em `apps/dashboard/views.py` (CBVs `View`): `GET /api/notificacoes/` (lista recente) e `POST /api/notificacoes/marcar-lidas/`. Reutiliza o padrão de `EnviarBuzinaView`/CSRF já corrigido.
- **Atualização ao vivo do sino**: `buzz.js` já escuta `buzina_recebida`/`resposta_recebida`/`buzina_encerrada`; adiciona-se um incremento do contador nesses handlers (sem novo socket).

## Riscos / Trade-offs

- [Contador divergir do backend após várias abas] → o contador ao vivo é incremental; ao abrir a central, a lista vem do servidor e o contador é reconciliado (fonte de verdade = `nao_lidas_de`).
- [Migração adiciona coluna em tabela existente] → `lida_em` é nullable, migração aditiva e reversível; buzinas antigas ficam como não lidas — mitigar marcando como lidas na migração de dados (data migration opcional) ou aceitando o "catch-up" inicial.
- [Card servindo dois destinos (perfil vs. chamar)] → decisão: card → perfil; buzinar só via botão dedicado (perfil ou bolt). Evita cliques acidentais de chamada.
- [Histórico crescer muito] → limitar a consulta (ex.: últimos 50) nesta iteração; paginação fica para depois (não-objetivo).

## Plano de migração

1. Migração de schema aditiva: `Buzina.lida_em` (nullable). Reversível.
2. (Opcional) data migration marcando buzinas antigas como lidas para o contador não começar inflado.
3. Deploy sem downtime — mudanças são aditivas; rota `/chamar/` permanece válida.
4. Rollback: reverter migração e templates; nenhuma perda de dados de `Buzina`.

## Questões em aberto

- O bolt no card deve buzinar inline ou também levar ao perfil? (Proposta atual: bolt buzina; card abre perfil.)
- Limite de itens do histórico/central na primeira versão (sugestão: 50 no histórico, 15 na central).
- A central deve incluir chamadas que eu enviei e foram atendidas/recusadas, ou só o que "chega até mim"? (Proposta: recebidas + respostas às minhas envidas + perdidas.)
