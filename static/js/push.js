(function () {
  const URL_VAPID = '/api/push/vapid/';
  const URL_INSCREVER = '/api/push/inscrever/';
  const URL_DESINSCREVER = '/api/push/desinscrever/';
  const URL_PENDENTES = '/api/buzina/pendentes/';

  let registroSw = null;
  let inscricaoAtiva = null;

  function obterCsrfToken() {
    return document.cookie.match(/csrftoken=([^;]+)/)?.[1]
      || document.querySelector('[name=csrfmiddlewaretoken]')?.value
      || '';
  }

  function suportaPush() {
    return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  }

  function ehIos() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent)
      || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  }

  function pwaInstaladoIos() {
    return window.navigator.standalone === true
      || window.matchMedia('(display-mode: standalone)').matches;
  }

  function urlBase64ParaUint8Array(base64) {
    const padding = '='.repeat((4 - (base64.length % 4)) % 4);
    const base64Seguro = (base64 + padding).replace(/-/g, '+').replace(/_/g, '/');
    const raw = window.atob(base64Seguro);
    const arr = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i += 1) arr[i] = raw.charCodeAt(i);
    return arr;
  }

  async function postForm(url, dados) {
    const form = new FormData();
    Object.entries(dados).forEach(([chave, valor]) => form.append(chave, valor));
    const token = obterCsrfToken();
    if (token) form.append('csrfmiddlewaretoken', token);
    const resposta = await fetch(url, {
      method: 'POST',
      headers: token ? { 'X-CSRFToken': token } : {},
      body: form,
      credentials: 'same-origin',
    });
    const tipo = resposta.headers.get('content-type') || '';
    if (!tipo.includes('application/json')) {
      return { erro: resposta.ok ? 'Resposta inválida.' : `Erro ${resposta.status}` };
    }
    return resposta.json();
  }

  async function buscarJson(url, opcoes = {}) {
    const token = obterCsrfToken();
    const resposta = await fetch(url, {
      credentials: 'same-origin',
      headers: {
        ...(token ? { 'X-CSRFToken': token } : {}),
        ...(opcoes.headers || {}),
      },
      ...opcoes,
    });
    const tipo = resposta.headers.get('content-type') || '';
    if (!tipo.includes('application/json')) {
      return { erro: `Erro ${resposta.status}` };
    }
    return resposta.json();
  }

  async function registrarServiceWorker() {
    if (!suportaPush()) return null;
    registroSw = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
    await navigator.serviceWorker.ready;
    return registroSw;
  }

  async function obterChaveVapid() {
    const dados = await buscarJson(URL_VAPID);
    if (dados.erro || !dados.chave_publica) {
      throw new Error(dados.erro || 'Chave VAPID indisponível.');
    }
    return dados.chave_publica;
  }

  async function inscreverPush() {
    if (!suportaPush()) throw new Error('Seu navegador não suporta notificações em segundo plano.');

    const permissao = await Notification.requestPermission();
    if (permissao !== 'granted') {
      throw new Error('Permissão de notificação negada.');
    }

    const registro = registroSw || await registrarServiceWorker();
    const chave = await obterChaveVapid();
    inscricaoAtiva = await registro.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ParaUint8Array(chave),
    });

    const corpo = inscricaoAtiva.toJSON();
    const resposta = await postForm(URL_INSCREVER, {
      endpoint: corpo.endpoint,
      p256dh: corpo.keys.p256dh,
      auth: corpo.keys.auth,
    });
    if (resposta.erro) throw new Error(resposta.erro);
    return true;
  }

  async function desinscreverPush() {
    const registro = registroSw || await navigator.serviceWorker.getRegistration('/');
    if (registro) {
      const inscricao = await registro.pushManager.getSubscription();
      if (inscricao) {
        const endpoint = inscricao.endpoint;
        await inscricao.unsubscribe();
        await postForm(URL_DESINSCREVER, { endpoint });
      }
    }
    inscricaoAtiva = null;
    return true;
  }

  async function fecharNotificacoesPorTag(tag) {
    const registro = registroSw || await navigator.serviceWorker.getRegistration('/');
    if (!registro) return;
    const notificacoes = await registro.getNotifications({ tag });
    notificacoes.forEach((n) => n.close());
  }

  async function sincronizarPendentes(mostrarAlerta) {
    const dados = await buscarJson(URL_PENDENTES);
    if (!dados.ok || !dados.pendentes?.length) return;

    const params = new URLSearchParams(window.location.search);
    const buzinaDeepLink = params.get('buzina');

    dados.pendentes.forEach((payload) => {
      if (buzinaDeepLink && payload.buzina_id !== buzinaDeepLink) return;
      if (typeof mostrarAlerta === 'function') {
        mostrarAlerta(payload);
        fecharNotificacoesPorTag(payload.buzina_id);
      }
    });
  }

  function configurarMensagensServiceWorker(mostrarAlerta) {
    navigator.serviceWorker?.addEventListener('message', async (evento) => {
      const dados = evento.data || {};

      if (dados.tipo === 'buzina_push') {
        if (document.hidden) {
          await window.BuzzSom?.tocarRecebido();
        }
        return;
      }

      if (dados.tipo === 'notificacao_clicada') {
        await window.BuzzSom?.desbloquear();
        await sincronizarPendentes(mostrarAlerta);
      }
    });
  }

  function configurarVisibilityChange(mostrarAlerta) {
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState !== 'visible') return;
      await window.BuzzSom?.desbloquear();
      await sincronizarPendentes(mostrarAlerta);
      if (registroSw?.active) {
        registroSw.active.postMessage({ tipo: 'app_visivel' });
      }
    });
  }

  function atualizarUiConfiguracoes(estado) {
    const secao = document.getElementById('secao-push');
    if (!secao) return;

    const botao = document.getElementById('botao-push');
    const status = document.getElementById('status-push');
    const bannerIos = document.getElementById('banner-ios-pwa');

    if (!suportaPush()) {
      status.textContent = 'Seu navegador não suporta notificações em segundo plano.';
      if (botao) botao.disabled = true;
      return;
    }

    if (ehIos() && !pwaInstaladoIos() && bannerIos) {
      bannerIos.classList.remove('hidden');
    }

    if (estado === 'ativo') {
      status.textContent = 'Ativo — você receberá chamadas com o app em segundo plano.';
      if (botao) {
        botao.textContent = 'Desativar';
        botao.dataset.acao = 'desativar';
      }
    } else if (estado === 'negado') {
      status.textContent = 'Permissão negada. Ative nas configurações do navegador ou do sistema.';
      if (botao) {
        botao.textContent = 'Tentar novamente';
        botao.dataset.acao = 'ativar';
      }
    } else {
      status.textContent = 'Receba cutucões mesmo com a aba em segundo plano.';
      if (botao) {
        botao.textContent = 'Ativar notificações';
        botao.dataset.acao = 'ativar';
      }
    }
  }

  async function estadoPushAtual() {
    if (!suportaPush()) return 'nao_suportado';
    if (Notification.permission === 'denied') return 'negado';
    const registro = await navigator.serviceWorker.getRegistration('/');
    const inscricao = registro ? await registro.pushManager.getSubscription() : null;
    return inscricao ? 'ativo' : 'inativo';
  }

  function configurarPaginaConfiguracoes() {
    const botao = document.getElementById('botao-push');
    if (!botao) return;

    estadoPushAtual().then((estado) => {
      if (estado === 'nao_suportado') atualizarUiConfiguracoes('nao_suportado');
      else if (estado === 'negado') atualizarUiConfiguracoes('negado');
      else if (estado === 'ativo') atualizarUiConfiguracoes('ativo');
      else atualizarUiConfiguracoes('inativo');
    });

    botao.addEventListener('click', async () => {
      botao.disabled = true;
      try {
        if (botao.dataset.acao === 'desativar') {
          await desinscreverPush();
          atualizarUiConfiguracoes('inativo');
        } else {
          await inscreverPush();
          atualizarUiConfiguracoes('ativo');
        }
      } catch (erro) {
        if (Notification.permission === 'denied') {
          atualizarUiConfiguracoes('negado');
        }
        window.mostrarToastPush?.(erro.message || 'Não foi possível alterar as notificações.');
      } finally {
        botao.disabled = false;
      }
    });
  }

  const CHAVE_ALERTA_DISPENSADO = 'buzz_alerta_push_dispensado';

  function ocultarAlertaInicio() {
    document.getElementById('alerta-push-inicio')?.classList.add('hidden');
  }

  async function configurarAlertaInicio() {
    const alerta = document.getElementById('alerta-push-inicio');
    if (!alerta) return;

    if (localStorage.getItem(CHAVE_ALERTA_DISPENSADO) === '1') return;
    if (!suportaPush()) return;

    const vapid = await buscarJson(URL_VAPID);
    if (vapid.erro || !vapid.chave_publica) return;

    const estado = await estadoPushAtual();
    if (estado === 'ativo' || estado === 'negado') return;

    alerta.classList.remove('hidden');

    document.getElementById('alerta-push-dispensar')?.addEventListener('click', () => {
      localStorage.setItem(CHAVE_ALERTA_DISPENSADO, '1');
      ocultarAlertaInicio();
    });

    document.getElementById('alerta-push-ativar')?.addEventListener('click', async (evento) => {
      const botao = evento.currentTarget;
      botao.disabled = true;
      try {
        await inscreverPush();
        localStorage.removeItem(CHAVE_ALERTA_DISPENSADO);
        ocultarAlertaInicio();
      } catch (erro) {
        window.mostrarToastPush?.(erro.message || 'Não foi possível ativar as notificações.');
      } finally {
        botao.disabled = false;
      }
    });
  }

  async function iniciar(mostrarAlerta) {
    if (document.body.dataset.usuarioAutenticado !== 'true') return;
    if (window.BuzzPushNativo?.ehAppNativo?.()) {
      window.BuzzPushNativo.iniciar(mostrarAlerta);
      return;
    }
    if (!suportaPush()) return;

    try {
      await registrarServiceWorker();
      configurarMensagensServiceWorker(mostrarAlerta);
      configurarVisibilityChange(mostrarAlerta);
      configurarPaginaConfiguracoes();
      await configurarAlertaInicio();

      const estado = await estadoPushAtual();
      if (estado === 'ativo') {
        inscricaoAtiva = await (await navigator.serviceWorker.ready).pushManager.getSubscription();
      }

      await sincronizarPendentes(mostrarAlerta);

      const params = new URLSearchParams(window.location.search);
      if (params.get('buzina')) {
        await sincronizarPendentes(mostrarAlerta);
      }
    } catch {
      /* push opcional — não bloqueia o app */
    }
  }

  window.BuzzPush = {
    iniciar,
    inscreverPush,
    desinscreverPush,
    fecharNotificacoesPorTag,
    sincronizarPendentes,
    suportaPush,
    ehIos,
    pwaInstaladoIos,
  };
})();
