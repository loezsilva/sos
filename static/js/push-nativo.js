(function () {
  const URL_INSCREVER = '/api/push/nativo/inscrever/';
  const URL_DESINSCREVER = '/api/push/nativo/desinscrever/';

  function obterCsrfToken() {
    return document.cookie.match(/csrftoken=([^;]+)/)?.[1]
      || document.querySelector('[name=csrfmiddlewaretoken]')?.value
      || '';
  }

  function ehAppNativo() {
    return window.Capacitor?.isNativePlatform?.() === true;
  }

  function obterPlataforma() {
    return window.Capacitor?.getPlatform?.() || 'web';
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

  async function vibrarNativo() {
    try {
      const Haptics = window.Capacitor?.Plugins?.Haptics;
      if (Haptics?.vibrate) {
        await Haptics.vibrate();
      }
    } catch {
      /* haptics opcional */
    }
  }

  async function inscreverPushNativo() {
    const Push = window.Capacitor?.Plugins?.PushNotifications;
    if (!Push) throw new Error('Push nativo indisponível.');

    const permissao = await Push.requestPermissions();
    if (permissao.receive !== 'granted') {
      throw new Error('Permissão de notificação negada.');
    }

    await Push.register();
  }

  async function desinscreverPushNativo(token) {
    await postForm(URL_DESINSCREVER, { token });
    const Push = window.Capacitor?.Plugins?.PushNotifications;
    if (Push?.removeAllListeners) await Push.removeAllListeners();
  }

  function configurarListeners(mostrarAlerta) {
    const Push = window.Capacitor?.Plugins?.PushNotifications;
    const App = window.Capacitor?.Plugins?.App;
    if (!Push) return;

    Push.addListener('registration', async (evento) => {
      const plataforma = obterPlataforma() === 'ios' ? 'ios' : 'android';
      await postForm(URL_INSCREVER, {
        token: evento.value,
        plataforma,
      });
    });

    Push.addListener('registrationError', (erro) => {
      console.error('Erro registro push nativo:', erro);
    });

    Push.addListener('pushNotificationReceived', async (notificacao) => {
      await vibrarNativo();
      const dados = notificacao.data || {};
      if (dados.tipo === 'buzina_recebida' && mostrarAlerta) {
        mostrarAlerta({
          buzina_id: dados.buzina_id,
          remetente_nome: dados.remetente_nome,
          remetente_avatar: '',
          mensagem: dados.mensagem || '',
        });
        window.BuzzSom?.tocarRecebido?.();
      }
    });

    Push.addListener('pushNotificationActionPerformed', async (acao) => {
      const dados = acao.notification?.data || {};
      if (dados.buzina_id && mostrarAlerta) {
        await window.BuzzPush?.sincronizarPendentes?.(mostrarAlerta);
      }
      if (dados.url) {
        const destino = dados.url.startsWith('/') ? dados.url : `/${dados.url}`;
        window.location.href = destino;
      }
    });

    App?.addListener?.('appUrlOpen', async (evento) => {
      const url = evento.url || '';
      const match = url.match(/[?&]buzina=([^&]+)/) || url.match(/buzina\/([^/?#]+)/);
      if (match && mostrarAlerta) {
        await window.BuzzPush?.sincronizarPendentes?.(mostrarAlerta);
        window.location.href = `/?buzina=${match[1]}`;
      }
    });
  }

  function atualizarUiConfiguracoesNativo(estado) {
    const secao = document.getElementById('secao-push');
    if (!secao || !ehAppNativo()) return;

    const botao = document.getElementById('botao-push');
    const status = document.getElementById('status-push');
    const bannerIos = document.getElementById('banner-ios-pwa');
    const bannerApp = document.getElementById('banner-app-nativo');

    if (bannerIos) bannerIos.classList.add('hidden');
    if (bannerApp) bannerApp.classList.remove('hidden');

    if (estado === 'ativo') {
      status.textContent = 'App nativo — chamadas com som e vibração do sistema.';
      if (botao) {
        botao.textContent = 'Desativar';
        botao.dataset.acao = 'desativar';
      }
    } else if (estado === 'negado') {
      status.textContent = 'Permissão negada. Ative nas configurações do Android/iOS.';
      if (botao) {
        botao.textContent = 'Tentar novamente';
        botao.dataset.acao = 'ativar';
      }
    } else {
      status.textContent = 'Ative para receber cutucões com som customizado, mesmo com o app fechado.';
      if (botao) {
        botao.textContent = 'Ativar notificações';
        botao.dataset.acao = 'ativar';
      }
    }
  }

  async function iniciar(mostrarAlerta) {
    if (document.body.dataset.usuarioAutenticado !== 'true') return;
    if (!ehAppNativo()) return;

    window.BuzzNativo = {
      ehAppNativo: true,
      plataforma: obterPlataforma(),
    };
    document.dispatchEvent(new CustomEvent('buzz-nativo-pronto'));

    configurarListeners(mostrarAlerta);

    const Push = window.Capacitor?.Plugins?.PushNotifications;
    if (!Push) return;

    try {
      const permissao = await Push.checkPermissions();
      if (permissao.receive === 'granted') {
        await Push.register();
        atualizarUiConfiguracoesNativo('ativo');
      } else {
        atualizarUiConfiguracoesNativo(permissao.receive === 'denied' ? 'negado' : 'inativo');
      }

      const botao = document.getElementById('botao-push');
      if (botao && !botao.dataset.nativoConfigurado) {
        botao.dataset.nativoConfigurado = 'true';
        botao.addEventListener('click', async () => {
          botao.disabled = true;
          try {
            if (botao.dataset.acao === 'desativar') {
              await desinscreverPushNativo();
              atualizarUiConfiguracoesNativo('inativo');
            } else {
              await inscreverPushNativo();
              atualizarUiConfiguracoesNativo('ativo');
            }
          } catch (erro) {
            window.mostrarToastPush?.(erro.message || 'Não foi possível alterar as notificações.');
          } finally {
            botao.disabled = false;
          }
        });
      }

      const params = new URLSearchParams(window.location.search);
      if (params.get('buzina')) {
        await window.BuzzPush?.sincronizarPendentes?.(mostrarAlerta);
      }
    } catch {
      /* push nativo opcional */
    }
  }

  window.BuzzPushNativo = {
    iniciar,
    ehAppNativo,
    inscreverPushNativo,
    desinscreverPushNativo,
    vibrarNativo,
  };
})();
