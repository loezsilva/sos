## 1. Infraestrutura e dependências

- [x] 1.1 Adicionar `pywebpush` ao `requirements.txt` e documentar vars `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_ADMIN_EMAIL` no `.env-example`
- [x] 1.2 Gerar par de chaves VAPID para desenvolvimento e ler via `settings.py`
- [x] 1.3 Criar `static/manifest.webmanifest` seguindo [PWA Starter](https://github.com/pwa-builder/pwa-starter/blob/main/public/manifest.json): `id`, `scope`, `launch_handler`, `display_override`, shortcuts, ícones any + maskable; linkar em `base.html` com meta Apple
- [x] 1.4 Gerar ícones (192/512/maskable) e screenshot via [pwabuilder.com](https://www.pwabuilder.com/) ou PWABuilder Studio

## 2. Backend — inscrições e envio

- [x] 2.1 Modelo `InscricaoPush` (usuario, endpoint único, p256dh, auth, user_agent) + migração
- [x] 2.2 Serviço `Push` (ou métodos no model): `inscrever`, `desinscrever`, `enviar_buzina`, limpeza de endpoints inválidos (410)
- [x] 2.3 Views/API: `GET /api/push/vapid/`, `POST /api/push/inscrever/`, `DELETE /api/push/inscrever/` + rotas
- [x] 2.4 Hook em `Buzina.enviar`: chamar push apenas se `not silenciada`

## 3. Service Worker

- [x] 3.1 Criar `/sw.js` na raiz: Workbox 7.x CDN ([pwa-starter](https://github.com/pwa-builder/pwa-starter/blob/main/public/sw.js)), precache manual, `clients.claim()`, handlers `push` e `notificationclick`
- [x] 3.2 View ou config WhiteNoise para servir SW na raiz com headers corretos (`Service-Worker-Allowed`)
- [x] 3.3 Payload push com `buzina_id`, `remetente_nome`, `url`; `tag` e `requireInteraction` na notificação

## 4. Cliente — registro e sync

- [x] 4.1 Módulo JS: registrar SW, obter VAPID, subscribe/unsubscribe, POST ao backend
- [x] 4.2 Integrar registro após login em `buzz.js` (ou `push.js` importado)
- [x] 4.3 `visibilitychange`: catch-up de buzinas pendentes + fechar notificações duplicadas por tag
- [x] 4.4 Deep link `?buzina=<id>` na home: abrir alerta se pendente

## 5. Configurações e UX

- [x] 5.1 Seção em `configuracoes.html`: toggle/botão ativar notificações em segundo plano com estados (ativo, negado, não suportado)
- [x] 5.2 Mensagens em PT-BR para permissão negada e browsers sem suporte
- [x] 5.3 Banner opcional em iOS sugerindo "Adicionar à Tela de Início" para push

## 6. Testes e validação

- [x] 6.1 Testes: API inscrever/desinscrever, push não enviado em buzina silenciada, mock `pywebpush`
- [x] 6.2 Teste manual documentado: aba em segundo plano → buzina → notificação SO → clique abre alerta
- [x] 6.3 Validar PWA em [pwabuilder.com](https://www.pwabuilder.com/) (installability + manifest score)
- [x] 6.4 `openspec validate notificacoes-segundo-plano`
