/* eslint-disable no-undef */
// Service Worker do Buzz — padrão PWABuilder PWA Starter + push de buzina.
// Servido em /sw.js (raiz) na implementação; arquivo-fonte em static/.

importScripts(
  'https://storage.googleapis.com/workbox-cdn/releases/7.3.0/workbox-sw.js'
);

workbox.setConfig({ debug: false });

// --- Handlers customizados (acima do precache, como no pwa-starter) ---

self.addEventListener('push', (event) => {
  if (!event.data) return;

  let dados = {};
  try {
    dados = event.data.json();
  } catch {
    dados = { titulo: 'Cutuca', corpo: event.data.text() };
  }

  const nome = dados.remetente_nome || 'Alguém';
  const msg = (dados.mensagem || '').trim();
  const titulo = dados.titulo || (msg ? `${nome} te cutucou` : `Chamada urgente — ${nome}`);
  const corpo = dados.corpo || (msg ? `"${msg}" — toque para responder agora` : `${nome} precisa da sua atenção. Toque para abrir.`);

  const opcoes = {
    body: corpo,
    tag: dados.buzina_id || 'cutuca-chamada',
    renotify: true,
    requireInteraction: true,
    silent: false,
    sound: '/static/sounds/buzina.wav',
    vibrate: [200, 100, 200, 100, 400],
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
    data: {
      url: dados.url || '/',
      buzina_id: dados.buzina_id,
      remetente_nome: dados.remetente_nome,
      mensagem: dados.mensagem,
    },
  };

  event.waitUntil(
    Promise.all([
      self.registration.showNotification(titulo, opcoes),
      self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientes) => {
        clientes.forEach((cliente) => {
          cliente.postMessage({ tipo: 'buzina_push', ...dados, titulo, corpo });
        });
      }),
    ]),
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';

  event.waitUntil(
    (async () => {
      const janelas = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true,
      });

      for (const cliente of janelas) {
        if ('focus' in cliente) {
          await cliente.focus();
          cliente.postMessage({
            tipo: 'notificacao_clicada',
            buzina_id: event.notification.data?.buzina_id,
            url,
          });
          return;
        }
      }

      await self.clients.openWindow(url);
    })()
  );
});

// Mensagem do client: suprimir push se app visível (deduplicação com WS)
self.addEventListener('message', (event) => {
  if (event.data?.tipo === 'app_visivel') {
    event.waitUntil(
      self.registration.getNotifications().then((notificacoes) => {
        const tag = event.data.buzina_id;
        if (!tag) return;
        notificacoes
          .filter((n) => n.tag === tag)
          .forEach((n) => n.close());
      })
    );
  }
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const cachesAntigos = ['paginas-buzz', 'workbox-precache-v2'];
      const nomes = await caches.keys();
      await Promise.all(
        nomes
          .filter((nome) => cachesAntigos.some((prefixo) => nome.includes(prefixo)))
          .map((nome) => caches.delete(nome)),
      );
      await self.clients.claim();
    })(),
  );
});

// --- Precache (manual — Django sem __WB_MANIFEST do Workbox build) ---
// Não precachear HTML (/) — evita UI antiga (ex.: texto "Cutuca" ao lado da logo).

const PRECACHE = [
  { url: '/static/css/buzz.css', revision: 'cutuca-v2' },
  { url: '/static/js/buzz.js', revision: 'cutuca-v2' },
  { url: '/static/js/push.js', revision: 'cutuca-v2' },
  { url: '/static/sounds/buzina.wav', revision: null },
  { url: '/static/icons/icon-192.png', revision: null },
  { url: '/static/icons/logo-cutuca-online.png', revision: 'cutuca-v2' },
];

workbox.precaching.precacheAndRoute(PRECACHE);

workbox.routing.registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new workbox.strategies.NetworkOnly()
);

workbox.routing.registerRoute(
  ({ request }) => request.mode === 'navigate',
  new workbox.strategies.NetworkFirst({
    cacheName: 'paginas-cutuca-v2',
    networkTimeoutSeconds: 5,
  })
);
