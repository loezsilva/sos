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
    dados = { titulo: 'Buzz', corpo: event.data.text() };
  }

  const titulo = dados.titulo || `Buzz — ${dados.remetente_nome || 'Chamada'}`;
  const opcoes = {
    body: dados.corpo || dados.mensagem || 'Alguém está te chamando.',
    tag: dados.buzina_id || 'buzz-chamada',
    renotify: true,
    requireInteraction: true,
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
    data: {
      url: dados.url || '/',
      buzina_id: dados.buzina_id,
    },
  };

  event.waitUntil(self.registration.showNotification(titulo, opcoes));
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
  event.waitUntil(self.clients.claim());
});

// --- Precache (manual — Django sem __WB_MANIFEST do Workbox build) ---

const PRECACHE = [
  { url: '/static/css/buzz.css', revision: null },
  { url: '/static/js/buzz.js', revision: null },
  { url: '/static/icons/icon-192.png', revision: null },
  { url: '/', revision: null },
];

workbox.precaching.precacheAndRoute(PRECACHE);

workbox.routing.registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new workbox.strategies.NetworkOnly()
);

workbox.routing.registerRoute(
  ({ request }) => request.mode === 'navigate',
  new workbox.strategies.NetworkFirst({
    cacheName: 'paginas-buzz',
    networkTimeoutSeconds: 5,
  })
);
